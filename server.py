from mcp.server.fastmcp import FastMCP
from typing import List, Dict
from hr_services import *
from utils import seed_services
from emails import EmailSender
from dotenv import load_dotenv
from datetime import datetime
load_dotenv()

import os

employee_manager = EmployeeManager()
meeting_manager = MeetingManager()
leave_manager = LeaveManager()
ticket_manager = TicketManager()

seed_services(employee_manager, leave_manager, meeting_manager, ticket_manager)

mcp = FastMCP("hr-assist")

emailer = EmailSender(
    smtp_server="smtp.gmail.com",
    port=587,
    username=os.getenv("EMAIL"),
    password=os.getenv("EMAIL_PWD"),
    use_tls=True
)

@mcp.tool()
def add_employee(emp_name:str, manager_id:str, email:str) -> str:
    """
    Add a new employee to the HRMS system.
    :param emp_name: Employee name
    :param manager_id: Manager ID (optional)
    :return: Confirmation message
    """
    emp = EmployeeCreate(
        emp_id=employee_manager.get_next_emp_id(),
        name=emp_name,
        manager_id=manager_id,
        email=email
    )
    employee_manager.add_employee(emp)
    return f"Employee {emp_name} added successfully."

@mcp.tool()
def get_employee_details(name: str) -> Dict[str, str]:
    """
    Get employee details by name.
    :param name: Name of the employee
    :return: Employee ID and manager ID
    """
    matches = employee_manager.search_employee_by_name(name)

    if len(matches) == 0:
        raise ValueError(f"No employees found with name {name}.")

    emp_id = matches[0]
    emp_details = employee_manager.get_employee_details(emp_id)
    return emp_details

@mcp.tool()
def send_email(to_emails: List[str], subject: str, body: str, html: bool = False) -> str:
    emailer.send_email(subject, body, to_emails, from_email=emailer.username, html=html)
    return "Email sent successfully."

@mcp.tool()
def create_ticket(emp_id: str, item: str, reason:str) -> str:
    """
    Create a ticket for buying required items for an employee.
    :param emp_id: Employee ID
    :param item: Item requested (Laptop, ID Card, etc.)
    :param reason: Reason for the request
    :return: Confirmation message
    """
    ticket_req = TicketCreate(emp_id=emp_id, item=item, reason=reason)
    return ticket_manager.create_ticket(ticket_req)

@mcp.tool()
def update_ticket_status(ticket_id: str, status: str) -> str:
    """
    Update the status of a ticket.
    :param ticket_id: Ticket ID
    :param status: New status of the ticket
    :return: Confirmation message
    """
    ticket_status_update = TicketStatusUpdate(status=status)
    return ticket_manager.update_ticket_status(ticket_status_update, ticket_id)

@mcp.tool()
def list_tickets(employee_id: str, status: str) -> List[Dict[str, str]]:
    """
    List tickets for an employee with optional status filter.
    :param employee_id: Employee ID
    :param status: Ticket status (optional)
    :return: List of tickets
    """
    return ticket_manager.list_tickets(employee_id=employee_id, status=status)

@mcp.tool()
def schedule_meeting(emp_id: str, meeting_dt: str, topic: str) -> str:
    """
    Schedule a meeting for an employee.
    :param emp_id: Employee ID
    :param meeting_dt: Date and time of the meeting in ISO format
    :param topic: Topic of the meeting
    :return: Confirmation message
    """
    req = MeetingCreate(emp_id=emp_id, meeting_dt=datetime.fromisoformat(meeting_dt), topic=topic)
    return meeting_manager.schedule_meeting(req)

@mcp.tool()
def get_meetings(employee_id: str) -> List[Dict[str, str]]:
    """
    Get all meetings scheduled for an employee.
    :param employee_id: Employee ID
    :return: List of meetings
    """
    return meeting_manager.get_meetings(employee_id)

@mcp.tool()
def cancel_meeting(emp_id: str, meeting_dt: str, topic: str = None) -> str:
    """
    Cancel a scheduled meeting for an employee.
    :param emp_id: Employee ID
    :param meeting_dt: Date and time of the meeting in ISO format
    :param topic: Optional topic to match if multiple meetings at the same time
    :return: Confirmation message
    """
    req = MeetingCancelRequest(emp_id=emp_id, meeting_dt=datetime.fromisoformat(meeting_dt), topic=topic)
    return meeting_manager.cancel_meeting(req)

@mcp.tool()
def apply_leave(emp_id: str, leave_dates: List[str]) -> str:    
    """
    Apply for leave for an employee.
    :param emp_id: Employee ID
    :param leave_dates: List of leave dates in ISO format
    :return: Confirmation message
    """
    leave_dates_parsed = [datetime.fromisoformat(date).date() for date in leave_dates]
    req = LeaveApplyRequest(emp_id=emp_id, leave_dates=leave_dates_parsed)
    return leave_manager.apply_leave(req)

@mcp.tool()
def get_leave_balance(emp_id: str) -> str:
    """
    Get the leave balance for an employee.
    :param emp_id: Employee ID
    :return: Leave balance details
    """
    return leave_manager.get_leave_balance(emp_id)

@mcp.tool()
def get_leave_history(emp_id: str) -> str:
    """
    Get the leave history for an employee.
    :param emp_id: Employee ID
    :return: Leave history details
    """
    return leave_manager.get_leave_history(emp_id)


@mcp.prompt("onboard_new_employee")
def onboard_new_employee(employee_name: str, manager_name: str):
    return f"""Onboard a new employee with the following details:
    - Name: {employee_name}
    - Manager Name: {manager_name}
    Steps to follow:
    - Add the employee to the HRMS system.
    - Send a welcome email to the employee with their login credentials. (Format: employee_name@veltrix.com)
    - Notify the manager about the new employee's onboarding.
    - Raise tickets for a new laptop, id card, and other necessary equipment.
    - Schedule an introductory meeting between the employee and the manager.
    """

if __name__ == "__main__":
    mcp.run(transport="stdio")

