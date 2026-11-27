# Copyright (c) 2026, Ajnas and Contributors
# License: MIT

"""Install / migrate hooks for Invoice Delivery Match."""

import frappe

from invoice_delivery_match.constants import (
	AFTER_LINKS,
	PAGE_LABEL,
	PAGE_NAME,
	SIDEBAR_NAMES,
	WORKSPACE_NAMES,
)


def after_install():
	sync_navigation()


def after_migrate():
	sync_navigation()


def sync_navigation():
	"""Add the reconciliation page under Accounts workspaces."""
	try:
		link = {
			"label": PAGE_LABEL,
			"link_to": PAGE_NAME,
			"link_type": "Page",
		}
		for workspace_name in WORKSPACE_NAMES:
			_sync_workspace_link(workspace_name, link, AFTER_LINKS)
		for sidebar_name in SIDEBAR_NAMES:
			_sync_sidebar_link(sidebar_name, link, AFTER_LINKS)
		frappe.clear_cache()
	except Exception:
		frappe.log_error(title="invoice_delivery_match: failed to sync navigation")


def _child_as_dict(row):
	data = row.as_dict()
	for key in (
		"name",
		"owner",
		"creation",
		"modified",
		"modified_by",
		"parent",
		"parentfield",
		"parenttype",
		"idx",
		"docstatus",
	):
		data.pop(key, None)
	return data


def _insert_links_after(rows, after_link_tos, new_rows):
	if isinstance(after_link_tos, str):
		after_link_tos = (after_link_tos,)
	result = []
	inserted = False
	for row in rows:
		result.append(row)
		if (
			not inserted
			and row.get("type") == "Link"
			and (row.get("link_to") in after_link_tos or row.get("label") in after_link_tos)
		):
			result.extend(new_rows)
			inserted = True
	if not inserted:
		result.extend(new_rows)
	return result


def _link_exists(link):
	return frappe.db.exists("Page", link["link_to"])


def _workspace_link_row(link):
	return {
		"type": "Link",
		"label": link["label"],
		"link_type": link["link_type"],
		"link_to": link["link_to"],
		"onboard": 0,
		"hidden": 0,
		"is_query_report": 0,
	}


def _sidebar_link_row(link):
	return {
		"type": "Link",
		"label": link["label"],
		"link_type": link["link_type"],
		"link_to": link["link_to"],
		"child": 1,
		"collapsible": 1,
	}


def _sync_workspace_link(workspace_name, link, after_link_to):
	if not frappe.db.exists("Workspace", workspace_name):
		return
	if not _link_exists(link):
		return

	ws = frappe.get_doc("Workspace", workspace_name)
	existing = {row.link_to for row in ws.links if row.type == "Link" and row.link_to}
	if link["link_to"] in existing:
		return

	rows = [_child_as_dict(row) for row in ws.links]
	rows = _insert_links_after(rows, after_link_to, [_workspace_link_row(link)])

	ws.set("links", [])
	for row in rows:
		ws.append("links", row)

	ws.flags.ignore_permissions = True
	ws.flags.ignore_links = True
	_save_without_export(ws)


def _sync_sidebar_link(sidebar_name, link, after_link_to):
	if not frappe.db.exists("Workspace Sidebar", sidebar_name):
		return
	if not _link_exists(link):
		return

	sb = frappe.get_doc("Workspace Sidebar", sidebar_name)
	existing = {row.link_to for row in sb.items if row.type == "Link" and row.link_to}
	if link["link_to"] in existing:
		return

	rows = [_child_as_dict(row) for row in sb.items]
	rows = _insert_links_after(rows, after_link_to, [_sidebar_link_row(link)])

	sb.set("items", [])
	for row in rows:
		sb.append("items", row)

	sb.flags.ignore_permissions = True
	_save_without_export(sb)


def _save_without_export(doc):
	was_dev = frappe.conf.developer_mode
	frappe.conf.developer_mode = 0
	try:
		doc.save()
	finally:
		frappe.conf.developer_mode = was_dev
