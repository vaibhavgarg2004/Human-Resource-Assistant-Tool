from collections import defaultdict
from typing import Dict
from datetime import date

from .schemas import LeaveApplyRequest


class LeaveManager:
    def __init__(self):
        self.request_counter = 10000
        self.employee_leaves: Dict[str, Dict] = defaultdict(
            lambda: {"balance": 20, "history": []}
        )

    def get_leave_balance(self, employee_id: str) -> str:
        data = self.employee_leaves.get(employee_id)
        if data:
            return f"{employee_id} has {data['balance']} leave days remaining."
        return "Employee ID not found."

    def apply_leave(self, req: LeaveApplyRequest) -> str:
        employee_id = req.emp_id
        leave_dates = [d.isoformat() for d in req.leave_dates]

        if employee_id not in self.employee_leaves:
            return "Employee ID not found."

        requested = len(leave_dates)
        available = self.employee_leaves[employee_id]["balance"]

        if available < requested:
            return f"Insufficient leave balance: requested {requested}, available {available}."

        self.employee_leaves[employee_id]["balance"] -= requested

        self.employee_leaves[employee_id]["history"].extend([
            {
                "history_id": len(self.employee_leaves[employee_id]["history"]) + i + 1,
                "emp_id": employee_id,
                "leave_date": d,
                "request_id": self.request_counter
            }
            for i, d in enumerate(leave_dates)
        ])

        self.request_counter += 1

        return (
            f"Leave applied for {requested} day(s). Remaining balance: "
            f"{self.employee_leaves[employee_id]['balance']}"
        )

    def get_leave_history(self, employee_id: str) -> str:
        data = self.employee_leaves.get(employee_id)
        if data:
            hist = data['history']
            dates = [
                date.fromisoformat(entry["leave_date"]).strftime("%B %d, %Y")
                for entry in hist
            ]
            return f"Leave history for {employee_id}: {', '.join(dates)}."
        return "Employee ID not found."
