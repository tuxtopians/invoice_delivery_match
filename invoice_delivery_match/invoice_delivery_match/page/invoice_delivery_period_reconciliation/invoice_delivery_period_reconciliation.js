// Copyright (c) 2026, Ajnas and Contributors
// License: MIT

frappe.pages["invoice-delivery-period-reconciliation"].on_page_load = function (wrapper) {
	const page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("Invoice Delivery Period Reconciliation"),
		single_column: true,
	});
	frappe.invoice_delivery_match_page = new InvoiceDeliveryMatchPage(page);
};

class InvoiceDeliveryMatchPage {
	constructor(page) {
		this.page = page;
		this.rows = [];
		this.counts = {};
		this.has_scanned = false;
		this.$root = $('<div class="idm-page"></div>').appendTo(page.main);
		this.make_filters();
		this.$results = $('<div class="idm-results"></div>').appendTo(this.$root);
		this.sync_actions();
		this.render_empty();
	}

	sync_actions() {
		// Ticket: Scan → review/correct → Re-scan. One primary button; label flips after first run.
		const label = this.has_scanned ? __("Re-scan") : __("Scan");
		this.page.set_primary_action(label, () => this.scan());
		// Espresso dress can leave a stale visible label after the first click — force it.
		const $btn = this.page.btn_primary;
		if ($btn && $btn.length) {
			$btn.attr("data-label", label);
			$btn.find(".es-button__label").first().text(label);
		}
	}

	make_filters() {
		this.$filters = $('<div class="idm-filters"></div>').appendTo(this.$root);
		this.filter_group = new frappe.ui.FieldGroup({
			parent: this.$filters,
			fields: [
				{
					label: __("Company"),
					fieldtype: "Link",
					fieldname: "company",
					options: "Company",
					default: frappe.defaults.get_user_default("Company"),
					reqd: 1,
				},
				{
					label: __("Fiscal Year"),
					fieldtype: "Link",
					fieldname: "fiscal_year",
					options: "Fiscal Year",
					default: frappe.defaults.get_user_default("fiscal_year"),
				},
				{
					label: __("Customer"),
					fieldtype: "Link",
					fieldname: "customer",
					options: "Customer",
				},
				{
					label: __("From Date"),
					fieldtype: "Date",
					fieldname: "from_date",
				},
				{
					label: __("To Date"),
					fieldtype: "Date",
					fieldname: "to_date",
				},
				{
					label: __("Status"),
					fieldtype: "Select",
					fieldname: "status",
					options: [
						"All",
						"Mismatch",
						"Matched",
						"Missing Delivery Note",
						"Missing Invoice",
					].join("\n"),
					default: "Mismatch",
				},
			],
			body: this.$filters,
		});
		this.filter_group.make();
		// Stack label above input so 3-col grid fields aren't truncated.
		this.$filters.find(".form-group").removeClass("horizontal");
	}

	get_filter(name) {
		return this.filter_group.get_value(name);
	}

	render_empty() {
		this.rows = [];
		this.counts = {};
		this.$results.html(
			`<div class="idm-empty">${__(
				"Set Company (and optional filters), then click Scan to find Sales Invoices and Delivery Notes in different posting periods."
			)}</div>`
		);
	}

	scan() {
		const company = this.get_filter("company");
		if (!company) {
			frappe.msgprint(__("Company is required"));
			return;
		}

		frappe.call({
			method: "invoice_delivery_match.api.get_period_matches",
			args: {
				company,
				fiscal_year: this.get_filter("fiscal_year"),
				from_date: this.get_filter("from_date"),
				to_date: this.get_filter("to_date"),
				customer: this.get_filter("customer"),
				status: this.get_filter("status") || "All",
			},
			freeze: true,
			freeze_message: __("Scanning invoices and delivery notes..."),
			callback: (r) => {
				const data = r.message || {};
				this.rows = data.rows || [];
				this.counts = data.counts || {};
				this.has_scanned = true;
				this.sync_actions();
				this.render_results();
			},
		});
	}

	render_results() {
		if (!this.rows.length) {
			this.$results.html(
				`<div class="idm-empty">${__(
					"No records found for the selected filters."
				)}</div>`
			);
			return;
		}

		const c = this.counts || {};
		const badges = [
			["idm-mismatch", __("Mismatch"), c.mismatch],
			["idm-matched", __("Matched"), c.matched],
			["idm-missing", __("Missing Delivery Note"), c.missing_delivery_note],
			["idm-missing", __("Missing Invoice"), c.missing_invoice],
		]
			.filter(([, , n]) => n > 0)
			.map(
				([cls, label, n]) =>
					`<span class="idm-badge ${cls}">${label}: ${n}</span>`
			)
			.join("");

		const summary = `
			<div class="idm-summary">
				<span class="idm-summary-total">${__("Showing")}: <strong>${
					this.rows.length
				}</strong></span>
				${badges}
			</div>
		`;

		const body = this.rows
			.map((row) => {
				const status_class = this.status_class(row.status);
				const amount =
					row.grand_total == null
						? ""
						: frappe.format(row.grand_total, {
								fieldtype: "Currency",
								options: row.currency || undefined,
						  });
				return `<tr class="${status_class}">
					<td class="idm-col-doc">${this.doc_link("Sales Invoice", row.sales_invoice)}</td>
					<td class="idm-col-date">${this.format_date(row.si_posting_date)}</td>
					<td class="idm-col-period">${frappe.utils.escape_html(row.si_period || "—")}</td>
					<td class="idm-col-doc">${this.doc_link("Delivery Note", row.delivery_note)}</td>
					<td class="idm-col-date">${this.format_date(row.dn_posting_date)}</td>
					<td class="idm-col-period">${frappe.utils.escape_html(row.dn_period || "—")}</td>
					<td class="idm-col-customer" title="${frappe.utils.escape_html(
						row.customer_name || row.customer || ""
					)}">${frappe.utils.escape_html(row.customer_name || row.customer || "")}</td>
					<td class="text-right idm-col-amount">${amount}</td>
					<td class="idm-col-status"><span class="idm-status">${__(row.status)}</span></td>
				</tr>`;
			})
			.join("");

		this.$results.html(`
			${summary}
			<div class="idm-table-wrap">
				<table class="table table-bordered idm-table">
					<thead>
						<tr>
							<th>${__("Sales Invoice")}</th>
							<th>${__("Invoice Date")}</th>
							<th>${__("Invoice Period")}</th>
							<th>${__("Delivery Note")}</th>
							<th>${__("Delivery Date")}</th>
							<th>${__("Delivery Period")}</th>
							<th>${__("Customer")}</th>
							<th class="text-right">${__("Amount")}</th>
							<th>${__("Status")}</th>
						</tr>
					</thead>
					<tbody>${body}</tbody>
				</table>
			</div>
			<div class="idm-hint text-muted">
				${__(
					"Open a document to correct its posting date manually. Re-scan after saving to refresh the list. Dates are never changed automatically."
				)}
			</div>
		`);
	}

	doc_link(doctype, name) {
		if (!name) {
			return "—";
		}
		const escaped = frappe.utils.escape_html(name);
		const href = frappe.utils.get_form_link(doctype, name);
		return `<a href="${href}">${escaped}</a>`;
	}

	format_date(value) {
		if (!value) {
			return "—";
		}
		return frappe.datetime.str_to_user(value);
	}

	status_class(status) {
		if (status === "Mismatch") {
			return "idm-row-mismatch";
		}
		if (status === "Matched") {
			return "idm-row-matched";
		}
		if (status === "Missing Delivery Note" || status === "Missing Invoice") {
			return "idm-row-missing";
		}
		return "";
	}
}
