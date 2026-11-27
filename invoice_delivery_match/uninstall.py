# Copyright (c) 2026, Ajnas and Contributors
# License: MIT

"""Uninstall cleanup for Invoice Delivery Match."""

import frappe

from invoice_delivery_match.constants import PAGE_NAME, SIDEBAR_NAMES, WORKSPACE_NAMES

PAGES = (PAGE_NAME,)


def before_uninstall():
	try:
		_remove_navigation()
		for name in PAGES:
			if frappe.db.exists("Page", name):
				frappe.delete_doc("Page", name, force=True, ignore_permissions=True)
		frappe.clear_cache()
	except Exception:
		frappe.log_error(title="Invoice Delivery Match: before_uninstall failed")


def after_uninstall():
	try:
		frappe.clear_cache()
	except Exception:
		frappe.log_error(title="Invoice Delivery Match: after_uninstall failed")


def _remove_navigation():
	for workspace_name in WORKSPACE_NAMES:
		if not frappe.db.exists("Workspace", workspace_name):
			continue
		ws = frappe.get_doc("Workspace", workspace_name)
		kept = [row for row in ws.links if not (row.type == "Link" and row.link_to in PAGES)]
		if len(kept) == len(ws.links):
			continue
		ws.set("links", [])
		for row in kept:
			ws.append("links", row.as_dict())
		ws.flags.ignore_permissions = True
		ws.flags.ignore_links = True
		_save_without_export(ws)

	for sidebar_name in SIDEBAR_NAMES:
		if not frappe.db.exists("Workspace Sidebar", sidebar_name):
			continue
		sb = frappe.get_doc("Workspace Sidebar", sidebar_name)
		kept = [row for row in sb.items if not (row.type == "Link" and row.link_to in PAGES)]
		if len(kept) == len(sb.items):
			continue
		sb.set("items", [])
		for row in kept:
			sb.append("items", row.as_dict())
		sb.flags.ignore_permissions = True
		_save_without_export(sb)


def _save_without_export(doc):
	was_dev = frappe.conf.developer_mode
	frappe.conf.developer_mode = 0
	try:
		doc.save()
	finally:
		frappe.conf.developer_mode = was_dev
