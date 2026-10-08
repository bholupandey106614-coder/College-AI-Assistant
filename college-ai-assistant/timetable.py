def find_classes(timetable, day: str):
    """
    Find classes for a particular day.

    Args:
        timetable: Timetable data.
        day: Day of the week.

    Returns:
        Classes scheduled on that day.
    """

    result = []

    for item in timetable:
        if item["day"].lower() == day.lower():
            result.append(item)

    return result
