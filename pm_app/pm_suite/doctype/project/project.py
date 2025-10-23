# Copyright (c) 2025, Tama Systems  and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from pm_app.pm_suite.doctype.company import company

# Project Name should include company id,project name four letters and four digit number get company id from company doctype


class Project(Document):
    def autoname(self):
        self.name = make_autoname("PROJ.####")

    def validate(self):
        if not self.project_id:
            self.project_id = self.name
