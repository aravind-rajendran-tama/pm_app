# Copyright (c) 2025, Tama Systems  and contributors
# For license information, please see license.txt

import frappe
from frappe.website.website_generator import WebsiteGenerator
from frappe.model.document import Document
from frappe.model.naming import make_autoname


class Task(Document):
    def autoname(self):
        self.name = make_autoname("TASK.####")

    # def validate(self):
    #     if not self.task_id:
    #         self.task_id = self.name
