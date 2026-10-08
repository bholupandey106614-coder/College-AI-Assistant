from datetime import date


def mark_attendance(
    subject: str,
    status: str,
    attendance_date: str = None
):
    """
    Mark attendance for a subject.

    Args:
        subject: Name of the subject.
        status: present or absent.
        attendance_date: Date of attendance.

    Returns:
        Attendance record.
    """

    if attendance_date is None:
        attendance_date = str(date.today())

    status = status.lower()

    if status not in ["present", "absent"]:
        return {
            "success": False,
            "message": "Status must be present or absent."
        }

    record = {
        "date": attendance_date,
        "subject": subject,
        "status": status
    }

    return {
        "success": True,
        "record": record
    }

