# Copyright (c) 2025, Tama Systems  and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator
from frappe.model.document import Document
from frappe.model.naming import make_autoname

# comppany name format should be like first six letters of company name + four digit number


class Company(Document):
    def autoname(self):
        self.name = make_autoname("COMP.####")

    def validate(self):
        if not self.company_id:
            self.company_id = self.name
