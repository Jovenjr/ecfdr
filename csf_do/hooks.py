from . import __version__ as app_version

app_name = "csf_do"
app_title = "Dominican Republic ERPNext Customization"
app_publisher = "Navari Ltd (Original Author), Refactored for Dominican Republic"
app_description = (
    "ERPNext and FrappeHR Country Specific Customizations for Dominican Republic by Navari Ltd (Originally for Dominican Republic)"
)
app_icon = "drag"
app_color = "grey"
app_email = "support@navari.co.ke"
app_license = "GNU General Public License (v3)"
required_apps = ["erpnext", "hrms"]


fixtures = [
    {
        "doctype": "Custom Field",
        "filters": [               
            ["is_system_generated", "=", 0],
            ["module", "=", "CSF DO"],
        ],
    },
    {
        "doctype": "DocType Link",
        "filters": [
            [
                "link_doctype",
                "in",
                ("Employee Dependent and Beneficiary",),
            ]
        ],
    },
]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/csf_do/css/csf_do.css"
# app_include_js = "/assets/csf_do/js/csf_do.js"

# include js, css files in header of web template
# web_include_css = "/assets/csf_do/css/csf_do.css"
# web_include_js = "/assets/csf_do/js/csf_do.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "csf_do/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views

doctype_js = {"Customer": "csf_do/overrides/customer.js"}

# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

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

# Installation
# ------------

# before_install = "csf_do.install.before_install"
# after_install = "csf_do.install.after_install"
after_migrate = "csf_do.csf_do.doctype.ncf_hscode.ncf_hscode.insert_new_records"

# Uninstallation
# ------------

# before_uninstall = "csf_do.uninstall.before_uninstall"
# after_uninstall = "csf_do.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "csf_do.notifications.get_notification_config"

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

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
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

doc_events = {
    "Purchase Receipt": {
        "on_submit": "csf_do.csf_do.doctype.api.update_item_price_list.update_item_prices"
    },
    "Purchase Invoice": {
        "on_submit": "csf_do.csf_do.doctype.api.update_item_price_list.update_item_prices"
    },
    "Item": {
        "before_save": "csf_do.csf_do.utils.get_ncf_hscode.validate_mandatory_hscode"
    },
    "Item Group": {
        "before_save": "csf_do.csf_do.utils.get_ncf_hscode.validate_mandatory_hscode"
    },
    "Customer": {
        "before_save": "csf_do.csf_do.overrides.customer.validate_customer_rnc"
    },
    "Sales Order": {
        "before_submit": "csf_do.csf_do.overrides.sales_doc.validate_customer_rnc"
    },
    "Sales Invoice": {
        "before_submit": "csf_do.csf_do.overrides.sales_doc.validate_customer_rnc"
    },
    "Job Card": {"before_submit": "csf_do.csf_do.overrides.job_card.before_submit"},
}
# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"csf_do.tasks.all"
# 	],
# 	"daily": [
# 		"csf_do.tasks.daily"
# 	],
# 	"hourly": [
# 		"csf_do.tasks.hourly"
# 	],
# 	"weekly": [
# 		"csf_do.tasks.weekly"
# 	]
# 	"monthly": [
# 		"csf_do.tasks.monthly"
# 	]
# }


# Testing
# -------

# before_tests = "csf_do.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "csf_do.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "csf_do.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

user_data_fields = [
    {
        "doctype": "{doctype_1}",
        "filter_by": "{filter_by}",
        "redact_fields": ["{field_1}", "{field_2}"],
        "partial": 1,
    },
    {
        "doctype": "{doctype_2}",
        "filter_by": "{filter_by}",
        "partial": 1,
    },
    {
        "doctype": "{doctype_3}",
        "strict": False,
    },
    {"doctype": "{doctype_4}"},
]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"csf_do.auth.validate"
# ]

# add methods to jinja environment
jinja = {"methods": ["csf_do.csf_do.utils.qr_code_generator.get_qr_code"]}

# include js in doctype views
# doctype_js = {

# }
