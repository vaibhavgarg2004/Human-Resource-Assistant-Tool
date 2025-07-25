from datetime import date, timedelta
import random
from hr_services import *

def seed_services(employee_manager, leave_manager, meeting_manager, ticket_manager):
    """
    Seeds all service classes with coherent dummy data.

    Args:
        employee_manager: Instance of EmployeeManager
        leave_manager: Instance of LeaveManager
        meeting_manager: Instance of MeetingManager
        ticket_manager: Instance of TicketManager

    Returns:
        None - services are modified in-place
    """

    employees_data = [
        # Leadership
        {"emp_id": "E001", "name": "Aarav Patel", "manager_id": None, "email": "aarav.patel@veltrix.com"},
        {"emp_id": "E002", "name": "Meera Das", "manager_id": None, "email": "meera.das@veltrix.com"},

        # Engineering team under Aarav
        {"emp_id": "E003", "name": "Rohan Verma", "manager_id": "E001", "email": "rohan.verma@veltrix.com"},
        {"emp_id": "E004", "name": "Sneha Reddy", "manager_id": "E003", "email": "sneha.reddy@veltrix.com"},
        {"emp_id": "E005", "name": "Karan Singh", "manager_id": "E003", "email": "karan.singh@veltrix.com"},

        # Product team under Meera
        {"emp_id": "E006", "name": "Anjali Menon", "manager_id": "E002", "email": "anjali.menon@veltrix.com"},
        {"emp_id": "E007", "name": "Dev Malik", "manager_id": "E006", "email": "dev.malik@veltrix.com"},
        {"emp_id": "E008", "name": "Priya Nair", "manager_id": "E006", "email": "priya.nair@veltrix.com"}
    ]

    # Populate employee manager
    for employee in employees_data:
        emp_id = employee["emp_id"]
        employee_manager.employees[emp_id] = employee
        employee_manager.manager_map[emp_id] = employee["manager_id"]

    # Create leave data
    # Set up some leave history for each employee
    current_date = date.today()
    request_id_counter = 1

    for employee in employees_data:
        emp_id = employee["emp_id"]

        # Set a random leave balance between 5 and 20 days
        leave_manager.employee_leaves[emp_id]["balance"] = random.randint(5, 20)

        # Create some leave history entries
        num_leaves = random.randint(1, 5)  # Random number of leave entries

        for i in range(num_leaves):
            # Generate a leave date in the past (1-90 days ago)
            days_ago = random.randint(1, 90)
            leave_date = current_date - timedelta(days=days_ago)

            # Add to leave history
            history_entry = {
                "history_id": len(leave_manager.employee_leaves[emp_id]["history"]) + 1,
                "emp_id": emp_id,
                "leave_date": leave_date.isoformat(),
                "request_id": request_id_counter
            }
            leave_manager.employee_leaves[emp_id]["history"].append(history_entry)

            # Sometimes add consecutive days for the same request
            if random.random() > 0.7:  # 30% chance of multi-day leave
                for j in range(1, random.randint(2, 5)):  # 1-4 additional days
                    consecutive_date = leave_date + timedelta(days=j)
                    consecutive_entry = {
                        "history_id": len(leave_manager.employee_leaves[emp_id]["history"]) + 1,
                        "emp_id": emp_id,
                        "leave_date": consecutive_date.isoformat(),
                        "request_id": request_id_counter
                    }
                    leave_manager.employee_leaves[emp_id]["history"].append(consecutive_entry)

            request_id_counter += 1

    # Create meeting data
    meeting_types = ["Team Sync", "Project Review", "Client Meeting", "1:1", "Planning"]

    # Generate meetings for each employee
    for employee in employees_data:
        emp_id = employee["emp_id"]
        num_meetings = random.randint(2, 6)

        for i in range(num_meetings):
            # Create a meeting in the next 10 days
            meeting_date = current_date + timedelta(days=random.randint(0, 10))
            meeting_hour = random.randint(9, 16)  # 9 AM to 4 PM

            meeting_dt = datetime.combine(meeting_date, datetime.min.time()).replace(hour=meeting_hour).isoformat()
            meeting = {
                "date": meeting_dt,
                "topic": random.choice(meeting_types)
            }
            meeting_manager.meetings[emp_id].append(meeting)

    # Create ticket data
    ticket_items = ["Laptop", "Monitor", "Keyboard", "Mouse", "Headset", "Office Chair", "Software License"]
    ticket_reasons = ["New hire setup", "Replacement for broken item", "Upgrade request", "Project requirement",
                      "Ergonomic needs"]

    # Generate some tickets
    num_tickets = random.randint(8, 15)
    for _ in range(num_tickets):
        employee = random.choice(employees_data)

        ticket = {
            "ticket_id": str(ticket_manager._next_id),
            "emp_id": employee["emp_id"],
            "item": random.choice(ticket_items),
            "reason": random.choice(ticket_reasons),
            "status": random.choice(["Open", "In Progress", "Closed"])
        }

        ticket_manager.tickets.append(ticket)
        ticket_manager._next_id += 1

    return {
        "employees": len(employee_manager.employees),
        "leave_records": sum(len(data["history"]) for data in leave_manager.employee_leaves.values()),
        "meetings": sum(len(meetings) for meetings in meeting_manager.meetings.values()),
        "tickets": len(ticket_manager.tickets)
    }

if __name__ == "__main__":
    # Initialize services
    employee_manager = EmployeeManager()
    leave_manager = LeaveManager()
    meeting_manager = MeetingManager()
    ticket_manager = TicketManager()

    # Seed the services with data
    result = seed_services(employee_manager, leave_manager, meeting_manager, ticket_manager)

    print(f"Seeded {result['employees']} employees")
    print(f"Seeded {result['leave_records']} leave records")
    print(f"Seeded {result['meetings']} meetings")
    print(f"Seeded {result['tickets']} tickets")
