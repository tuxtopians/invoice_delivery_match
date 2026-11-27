# Copyright (c) 2026, Ajnas and Contributors
# License: MIT

"""Named constants for Invoice Delivery Match."""

PAGE_NAME = "invoice-delivery-period-reconciliation"
PAGE_LABEL = "Invoice Delivery Period Reconciliation"

STATUS_ALL = "All"
STATUS_MISMATCH = "Mismatch"
STATUS_MATCHED = "Matched"
STATUS_MISSING_DN = "Missing Delivery Note"
STATUS_MISSING_SI = "Missing Invoice"

STATUS_OPTIONS = (
	STATUS_ALL,
	STATUS_MISMATCH,
	STATUS_MATCHED,
	STATUS_MISSING_DN,
	STATUS_MISSING_SI,
)

WORKSPACE_NAMES = ("Accounts", "Accounting")
SIDEBAR_NAMES = ("Financial Reports", "Accounts", "Accounting")
AFTER_LINKS = ("Sales Invoice", "Delivery Note", "Accounts Receivable")
