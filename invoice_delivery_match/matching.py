# Copyright (c) 2026, Ajnas and Contributors
# License: MIT

"""Sales Invoice ↔ Delivery Note period matching queries."""

from __future__ import annotations

import frappe
from frappe import _
from frappe.utils import getdate

from invoice_delivery_match.constants import (
	STATUS_ALL,
	STATUS_MATCHED,
	STATUS_MISMATCH,
	STATUS_MISSING_DN,
	STATUS_MISSING_SI,
)


def get_period_key(posting_date) -> str | None:
	if not posting_date:
		return None
	d = getdate(posting_date)
	return f"{d.year:04d}-{d.month:02d}"


def fetch_match_rows(
	*,
	company: str,
	fiscal_year: str | None = None,
	from_date: str | None = None,
	to_date: str | None = None,
	customer: str | None = None,
	status: str | None = None,
) -> dict:
	"""Return SI–DN relationship rows with period match status and summary counts.

	Counts always reflect the full scan for the date/customer filters (before status
	filter) so the summary stays useful when Status is Mismatch-only.
	"""
	company = (company or "").strip()
	if not company:
		frappe.throw(_("Company is required"))

	status = (status or STATUS_ALL).strip() or STATUS_ALL
	customer = (customer or "").strip() or None
	fiscal_year = (fiscal_year or "").strip() or None
	from_date = getdate(from_date) if from_date else None
	to_date = getdate(to_date) if to_date else None

	fy_from, fy_to = _fiscal_year_bounds(fiscal_year) if fiscal_year else (None, None)
	range_from = _max_date(from_date, fy_from)
	range_to = _min_date(to_date, fy_to)

	need_pairs = status in (STATUS_ALL, STATUS_MISMATCH, STATUS_MATCHED)
	need_missing_dn = status in (STATUS_ALL, STATUS_MISSING_DN)
	need_missing_si = status in (STATUS_ALL, STATUS_MISSING_SI)

	rows: list[dict] = []

	if need_pairs:
		for pair in _linked_pairs(
			company=company, customer=customer, range_from=range_from, range_to=range_to
		):
			si_period = get_period_key(pair.si_posting_date)
			dn_period = get_period_key(pair.dn_posting_date)
			row_status = STATUS_MATCHED if si_period == dn_period else STATUS_MISMATCH
			rows.append(
				_row(
					sales_invoice=pair.sales_invoice,
					si_posting_date=pair.si_posting_date,
					si_period=si_period,
					delivery_note=pair.delivery_note,
					dn_posting_date=pair.dn_posting_date,
					dn_period=dn_period,
					customer=pair.customer,
					customer_name=pair.customer_name,
					company=pair.company,
					grand_total=pair.grand_total,
					currency=pair.currency,
					status=row_status,
				)
			)

	if need_missing_dn:
		for inv in _invoices_without_delivery_note(
			company=company, customer=customer, range_from=range_from, range_to=range_to
		):
			rows.append(
				_row(
					sales_invoice=inv.name,
					si_posting_date=inv.posting_date,
					si_period=get_period_key(inv.posting_date),
					delivery_note=None,
					dn_posting_date=None,
					dn_period=None,
					customer=inv.customer,
					customer_name=inv.customer_name,
					company=inv.company,
					grand_total=inv.grand_total,
					currency=inv.currency,
					status=STATUS_MISSING_DN,
				)
			)

	if need_missing_si:
		for dn in _delivery_notes_without_invoice(
			company=company, customer=customer, range_from=range_from, range_to=range_to
		):
			rows.append(
				_row(
					sales_invoice=None,
					si_posting_date=None,
					si_period=None,
					delivery_note=dn.name,
					dn_posting_date=dn.posting_date,
					dn_period=get_period_key(dn.posting_date),
					customer=dn.customer,
					customer_name=dn.customer_name,
					company=dn.company,
					grand_total=dn.grand_total,
					currency=dn.currency,
					status=STATUS_MISSING_SI,
				)
			)

	counts = _count_by_status(rows)

	if status != STATUS_ALL:
		rows = [r for r in rows if r["status"] == status]

	rows.sort(
		key=lambda r: (
			r["status"] != STATUS_MISMATCH,
			r["status"] != STATUS_MISSING_DN,
			r["status"] != STATUS_MISSING_SI,
			r.get("si_posting_date") or r.get("dn_posting_date") or "",
			r.get("sales_invoice") or "",
			r.get("delivery_note") or "",
		)
	)
	return {"rows": rows, "counts": counts}


def _count_by_status(rows: list[dict]) -> dict:
	counts = {
		"total": len(rows),
		"mismatch": 0,
		"matched": 0,
		"missing_delivery_note": 0,
		"missing_invoice": 0,
	}
	for row in rows:
		key = {
			STATUS_MISMATCH: "mismatch",
			STATUS_MATCHED: "matched",
			STATUS_MISSING_DN: "missing_delivery_note",
			STATUS_MISSING_SI: "missing_invoice",
		}.get(row["status"])
		if key:
			counts[key] += 1
	return counts


def _row(**kwargs) -> dict:
	return kwargs


def _fiscal_year_bounds(fiscal_year: str) -> tuple:
	bounds = frappe.db.get_value(
		"Fiscal Year", fiscal_year, ["year_start_date", "year_end_date"], as_dict=True
	)
	if not bounds:
		frappe.throw(_("Fiscal Year {0} not found").format(fiscal_year))
	return getdate(bounds.year_start_date), getdate(bounds.year_end_date)


def _max_date(a, b):
	if a and b:
		return max(a, b)
	return a or b


def _min_date(a, b):
	if a and b:
		return min(a, b)
	return a or b


def _date_clause(alias: str, range_from, range_to, values: list) -> str:
	parts = []
	if range_from:
		parts.append(f"{alias}.posting_date >= %s")
		values.append(range_from)
	if range_to:
		parts.append(f"{alias}.posting_date <= %s")
		values.append(range_to)
	return (" AND " + " AND ".join(parts)) if parts else ""


def _linked_pairs(*, company: str, customer: str | None, range_from, range_to):
	"""Distinct SI–DN pairs via Sales Invoice Item.delivery_note or DN Item.against_sales_invoice."""
	customer_si = ""
	customer_dn = ""
	if customer:
		customer_si = " AND si.customer = %s"
		customer_dn = " AND dn.customer = %s"

	date_filter = ""
	if range_from or range_to:
		si_parts = []
		dn_parts = []
		if range_from:
			si_parts.append("si.posting_date >= %s")
			dn_parts.append("dn.posting_date >= %s")
		if range_to:
			si_parts.append("si.posting_date <= %s")
			dn_parts.append("dn.posting_date <= %s")
		si_clause = " AND ".join(si_parts)
		dn_clause = " AND ".join(dn_parts)
		date_filter = f" AND (({si_clause}) OR ({dn_clause}))"

	from_si = f"""
		SELECT DISTINCT
			si.name AS sales_invoice,
			si.posting_date AS si_posting_date,
			si.customer AS customer,
			si.customer_name AS customer_name,
			si.company AS company,
			si.grand_total AS grand_total,
			si.currency AS currency,
			dn.name AS delivery_note,
			dn.posting_date AS dn_posting_date
		FROM `tabSales Invoice` si
		INNER JOIN `tabSales Invoice Item` sii ON sii.parent = si.name
		INNER JOIN `tabDelivery Note` dn ON dn.name = sii.delivery_note AND dn.docstatus = 1
		WHERE si.docstatus = 1
			AND si.is_return = 0
			AND dn.is_return = 0
			AND si.company = %s
			AND IFNULL(sii.delivery_note, '') != ''
			{customer_si}
			{date_filter}
	"""

	from_dn = f"""
		SELECT DISTINCT
			si.name AS sales_invoice,
			si.posting_date AS si_posting_date,
			si.customer AS customer,
			si.customer_name AS customer_name,
			si.company AS company,
			si.grand_total AS grand_total,
			si.currency AS currency,
			dn.name AS delivery_note,
			dn.posting_date AS dn_posting_date
		FROM `tabDelivery Note` dn
		INNER JOIN `tabDelivery Note Item` dni ON dni.parent = dn.name
		INNER JOIN `tabSales Invoice` si
			ON si.name = dni.against_sales_invoice AND si.docstatus = 1
		WHERE dn.docstatus = 1
			AND dn.is_return = 0
			AND si.is_return = 0
			AND dn.company = %s
			AND IFNULL(dni.against_sales_invoice, '') != ''
			{customer_dn}
			{date_filter}
	"""

	arm1_values = [company]
	if customer:
		arm1_values.append(customer)
	if date_filter:
		arm1_values.extend(_duplicate_range_values(range_from, range_to))

	arm2_values = [company]
	if customer:
		arm2_values.append(customer)
	if date_filter:
		arm2_values.extend(_duplicate_range_values(range_from, range_to))

	query = f"""
		SELECT * FROM (
			{from_si}
			UNION
			{from_dn}
		) paired
		ORDER BY si_posting_date, sales_invoice, delivery_note
	"""
	return frappe.db.sql(query, arm1_values + arm2_values, as_dict=True)


def _duplicate_range_values(range_from, range_to) -> list:
	"""Values for ((si from/to) OR (dn from/to))."""
	arm = []
	if range_from:
		arm.append(range_from)
	if range_to:
		arm.append(range_to)
	return arm + arm


def _invoices_without_delivery_note(*, company: str, customer: str | None, range_from, range_to):
	values: list = [company]
	customer_clause = ""
	if customer:
		customer_clause = " AND si.customer = %s"
		values.append(customer)
	date_clause = _date_clause("si", range_from, range_to, values)

	return frappe.db.sql(
		f"""
		SELECT
			si.name,
			si.posting_date,
			si.customer,
			si.customer_name,
			si.company,
			si.grand_total,
			si.currency
		FROM `tabSales Invoice` si
		WHERE si.docstatus = 1
			AND si.company = %s
			AND si.is_return = 0
			{customer_clause}
			{date_clause}
			AND NOT EXISTS (
				SELECT 1 FROM `tabSales Invoice Item` sii
				WHERE sii.parent = si.name AND IFNULL(sii.delivery_note, '') != ''
			)
			AND NOT EXISTS (
				SELECT 1 FROM `tabDelivery Note Item` dni
				INNER JOIN `tabDelivery Note` dn ON dn.name = dni.parent AND dn.docstatus = 1
				WHERE dni.against_sales_invoice = si.name
			)
		ORDER BY si.posting_date, si.name
		""",
		values,
		as_dict=True,
	)


def _delivery_notes_without_invoice(*, company: str, customer: str | None, range_from, range_to):
	values: list = [company]
	customer_clause = ""
	if customer:
		customer_clause = " AND dn.customer = %s"
		values.append(customer)
	date_clause = _date_clause("dn", range_from, range_to, values)

	return frappe.db.sql(
		f"""
		SELECT
			dn.name,
			dn.posting_date,
			dn.customer,
			dn.customer_name,
			dn.company,
			dn.grand_total,
			dn.currency
		FROM `tabDelivery Note` dn
		WHERE dn.docstatus = 1
			AND dn.company = %s
			AND dn.is_return = 0
			{customer_clause}
			{date_clause}
			AND NOT EXISTS (
				SELECT 1 FROM `tabDelivery Note Item` dni
				WHERE dni.parent = dn.name AND IFNULL(dni.against_sales_invoice, '') != ''
			)
			AND NOT EXISTS (
				SELECT 1 FROM `tabSales Invoice Item` sii
				INNER JOIN `tabSales Invoice` si ON si.name = sii.parent AND si.docstatus = 1
				WHERE sii.delivery_note = dn.name
			)
		ORDER BY dn.posting_date, dn.name
		""",
		values,
		as_dict=True,
	)
