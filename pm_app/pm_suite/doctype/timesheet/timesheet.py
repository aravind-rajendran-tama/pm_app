# Copyright (c) 2025, Tama Systems  and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import get_datetime, flt
from datetime import timedelta

ALLOW_OVERNIGHT = True  # set False if you want to forbid crossing midnight


class Timesheet(Document):
    def validate(self):
        """
        - Derive row.hours from work_date + from_time/to_time
        - Disallow overlapping time ranges within this Timesheet
        - Inherit child.project from parent if missing
        - Roll up total_hours
        """
        total = 0.0

        # For overlap checks: keep already-seen intervals per work_date
        # Structure: overlaps[date] = [(start_dt, end_dt, row_idx), ...]
        overlaps = {}

        for row in self.entries or []:
            # Inherit project from parent if empty
            if (
                hasattr(row, "project")
                and not row.project
                and getattr(self, "project", None)
            ):
                row.project = self.project

            # Compute hours if we have date + both times
            start_dt = end_dt = None
            if getattr(row, "work_date", None) and row.from_time and row.to_time:
                start_dt = get_datetime(f"{row.work_date} {row.from_time}")
                end_dt = get_datetime(f"{row.work_date} {row.to_time}")

                # Handle invalid or overnight spans
                if end_dt <= start_dt:
                    if ALLOW_OVERNIGHT:
                        end_dt = end_dt + timedelta(days=1)  # treat as next day
                    else:
                        frappe.throw(
                            f"In row #{row.idx}: To Time must be after From Time "
                            f"on the same date (overnight not allowed)."
                        )

                # === Overlap detection (within this Timesheet) ===
                key = row.work_date  # compare only inside the same work_date
                seen = overlaps.setdefault(key, [])
                for prev_start, prev_end, prev_idx in seen:
                    # Overlap if ranges intersect: max(starts) < min(ends)
                    if max(start_dt, prev_start) < min(end_dt, prev_end):
                        frappe.throw(
                            f"Time overlap on {row.work_date}: row #{row.idx} "
                            f"({start_dt.time()}–{(end_dt.time())}) "
                            f"conflicts with row #{prev_idx} "
                            f"({prev_start.time()}–{prev_end.time()})."
                        )
                # If no overlap, register this interval
                seen.append((start_dt, end_dt, row.idx))

                # Derive hours (2-dec precision)
                row.hours = flt((end_dt - start_dt).total_seconds() / 3600.0, 2)

            # Normalize hours even if user typed nothing
            row.hours = flt(row.hours or 0, 2)
            total += row.hours

        self.total_hours = flt(total, 2)
