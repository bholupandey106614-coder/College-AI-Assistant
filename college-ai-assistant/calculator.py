def calculate_attendance(attended: int, total: int):
    """
    Calculate attendance percentage.

    Args:
        attended: Number of classes attended.
        total: Total number of classes.

    Returns:
        Attendance percentage.
    """

    if total <= 0:
        return {
            "error": "Total classes must be greater than zero."
        }

    percentage = (attended / total) * 100

    return {
        "attended": attended,
        "total": total,
        "percentage": round(percentage, 2)
    }