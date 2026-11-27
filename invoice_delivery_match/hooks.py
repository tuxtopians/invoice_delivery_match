app_name = "invoice_delivery_match"
app_title = "Invoice Delivery Match"
app_publisher = "Ajnas"
app_description = "Match Sales Invoice and Delivery Note posting periods for period closing"
app_email = "ajnaso10@gmail.com"
app_license = "mit"

# Apps
# ------------------

required_apps = ["erpnext"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "invoice_delivery_match",
# 		"logo": "/assets/invoice_delivery_match/logo.png",
# 		"title": "Invoice Delivery Match",
# 		"route": "/invoice_delivery_match",
# 		"has_permission": "invoice_delivery_match.api.permission.has_app_permission",
# 	}
# ]

# The dock, the rail down the left of the desk, is a document rather than a hook. Author it in
# Manage Dock on a developer-mode site and press Export to App, and it is written to
# `invoice_delivery_match/dock/invoice_delivery_match/invoice_delivery_match.json` for git to carry. An app that ships none has no
# rail: its sidebar gets a switcher in the header instead.
#
# A companion app, one that extends a host app rather than standing on its own, says so with
# `mount_on` on that same record, and its entries are appended to the host's rail. Mounting keeps
# the companion off the apps screen, so it takes precedence over any add_to_apps_screen above.

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = "/assets/invoice_delivery_match/css/invoice_delivery_match.css?v=13"
app_include_js = "/assets/invoice_delivery_match/js/invoice_delivery_match.js?v=13"

# include js, css files in header of web template
# web_include_css = "/assets/invoice_delivery_match/css/invoice_delivery_match.css"
# web_include_js = "/assets/invoice_delivery_match/js/invoice_delivery_match.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "invoice_delivery_match/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_kanban_js = {"doctype" : "public/js/doctype_kanban.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "invoice_delivery_match/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "invoice_delivery_match.utils.jinja_methods",
# 	"filters": "invoice_delivery_match.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "invoice_delivery_match.install.before_install"
after_install = "invoice_delivery_match.install.after_install"
after_migrate = "invoice_delivery_match.install.after_migrate"

# Uninstallation
# ------------

before_uninstall = "invoice_delivery_match.uninstall.before_uninstall"
after_uninstall = "invoice_delivery_match.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "invoice_delivery_match.utils.before_app_install"
# after_app_install = "invoice_delivery_match.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "invoice_delivery_match.utils.before_app_uninstall"
# after_app_uninstall = "invoice_delivery_match.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "invoice_delivery_match.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "invoice_delivery_match.notifications.get_notification_config"

# Awesome Bar
# -----------
# Extra search results: list of dicts with label, description, route, index.
# route: ["List", "ToDo"], "/desk/docs/some/page", or "https://example.com"
# awesomebar_search = ["invoice_delivery_match.search.awesomebar_results"]

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"invoice_delivery_match.tasks.all"
# 	],
# 	"daily": [
# 		"invoice_delivery_match.tasks.daily"
# 	],
# 	"hourly": [
# 		"invoice_delivery_match.tasks.hourly"
# 	],
# 	"weekly": [
# 		"invoice_delivery_match.tasks.weekly"
# 	],
# 	"monthly": [
# 		"invoice_delivery_match.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "invoice_delivery_match.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "invoice_delivery_match.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "invoice_delivery_match.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "invoice_delivery_match.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["invoice_delivery_match.utils.before_request"]
# after_request = ["invoice_delivery_match.utils.after_request"]

# Job Events
# ----------
# before_job = ["invoice_delivery_match.utils.before_job"]
# after_job = ["invoice_delivery_match.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"invoice_delivery_match.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

