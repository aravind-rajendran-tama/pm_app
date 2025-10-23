# Copyright (c) 2025, Tama Systems  and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.model.naming import make_autoname
from frappe.utils import getdate


# YYMMDD format in date of joining for employee id
class Employee(Document):
    def autoname(self):
        date_of_joining_date = getdate(self.date_of_joining)
        self.name = make_autoname(
            "{company_id}-{date_of_joining}-.###".format(
                company_id=self.employee_id_generation(),
                date_of_joining=date_of_joining_date.strftime("%y%m%d"),
            )
        )

    # if the company name three words take first letter of each word and make it as company id, if two words take first two letters of each word and if one word take first four letters of the word for employee id
    def employee_id_generation(self):
        company_name = frappe.get_value("Company", self.company, "company_name")
        words = company_name.split()
        if len(words) >= 3:
            company_id = "".join([word[0].upper() for word in words[:3]])
        elif len(words) == 2:
            company_id = (words[0][:2] + words[1][:2]).upper()
        else:
            company_id = words[0][:4].upper()
        return company_id
