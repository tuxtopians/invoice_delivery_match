# Copyright (c) 2026, Ajnas and Contributors
# License: MIT

"""Whitelisted APIs for Invoice Delivery Period Reconciliation."""

from __future__ import annotations

import frappe
from frappe import _

from invoice_delivery_match.constants import STATUS_ALL, STATUS_OPTIONS
from invoice_delivery_match.matching import fetch_match_rows


@frappe.whitelist()
def get_period_matches(
	company: str | None = None,
	fiscal_year: str | None = None,
	from_date: str | None = None,
	to_date: str | None = None,
	customer: str | None = None,
	status: str | None = None,
) -> dict:
	"""Scan Sales Invoices and Delivery Notes for posting-period mismatches."""
	frappe.has_permission("Sales Invoice", "read", throw=True)
	frappe.has_permission("Delivery Note", "read", throw=True)

	company = _as_str(company)
	fiscal_year = _as_str(fiscal_year) or None
	from_date = _as_str(from_date) or None
	to_date = _as_str(to_date) or None
	customer = _as_str(customer) or None
	status = _as_str(status) or STATUS_ALL

	if not company:
		frappe.throw(_("Company is required"))
	if status not in STATUS_OPTIONS:
		frappe.throw(_("Invalid status filter"))

	return fetch_match_rows(
		company=company,
		fiscal_year=fiscal_year,
		from_date=from_date,
		to_date=to_date,
		customer=customer,
		status=status,
	)


def _as_str(value) -> str:
	if value is None:
		return ""
	if not isinstance(value, str):
		frappe.throw(_("Invalid parameter type"))
	return value.strip()
