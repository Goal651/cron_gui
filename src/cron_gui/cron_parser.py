"""
Cron Parser - Utilities for parsing and validating cron expressions.
"""

from croniter import croniter
from datetime import datetime
from typing import List, Optional


def validate_cron_expression(expression: str) -> bool:
    """
    Validate a cron expression.

    Args:
        expression: Cron expression to validate (e.g., "0 * * * *")

    Returns:
        True if valid, False otherwise
    """
    try:
        croniter(expression)
        return True
    except Exception:
        return False


def get_next_runs(expression: str, count: int = 5) -> List[str]:
    """
    Get the next N execution times for a cron expression.

    Args:
        expression: Cron expression
        count: Number of next runs to calculate

    Returns:
        List of formatted datetime strings
    """
    try:
        cron = croniter(expression, datetime.now())
        runs = []
        for _ in range(count):
            next_run = cron.get_next(datetime)
            runs.append(next_run.strftime("%Y-%m-%d %H:%M:%S"))
        return runs
    except Exception:
        return []


def cron_to_human_readable(expression: str) -> str:
    """
    Convert a cron expression to human-readable format.

    Args:
        expression: Cron expression (e.g., "0 * * * *")

    Returns:
        Human-readable description
    """
    try:
        parts = expression.split()
        if len(parts) != 5:
            return "Invalid cron expression"

        minute, hour, day, month, weekday = parts

        # Build human-readable description
        desc_parts = []

        # Minute
        if minute == "*":
            desc_parts.append("every minute")
        elif "/" in minute:
            interval = minute.split("/")[1]
            desc_parts.append(f"every {interval} minutes")
        else:
            desc_parts.append(f"at minute {minute}")

        # Hour
        if hour != "*":
            if "/" in hour:
                interval = hour.split("/")[1]
                desc_parts.append(f"every {interval} hours")
            else:
                desc_parts.append(f"at hour {hour}")

        # Day of month
        if day != "*":
            desc_parts.append(f"on day {day}")

        # Month
        if month != "*":
            months = [
                "Jan",
                "Feb",
                "Mar",
                "Apr",
                "May",
                "Jun",
                "Jul",
                "Aug",
                "Sep",
                "Oct",
                "Nov",
                "Dec",
            ]
            try:
                month_idx = int(month) - 1
                if 0 <= month_idx < 12:
                    desc_parts.append(f"in {months[month_idx]}")
            except ValueError:
                desc_parts.append(f"in month {month}")

        # Weekday
        if weekday != "*":
            days = [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
            ]
            try:
                day_idx = int(weekday)
                if 0 <= day_idx < 7:
                    desc_parts.append(f"on {days[day_idx]}")
            except ValueError:
                desc_parts.append(f"on weekday {weekday}")

        return ", ".join(desc_parts).capitalize()

    except Exception:
        return "Invalid cron expression"


def build_cron_expression(
    minute: str = "*",
    hour: str = "*",
    day: str = "*",
    month: str = "*",
    weekday: str = "*",
) -> str:
    """
    Build a cron expression from individual components.

    Args:
        minute: Minute field (0-59 or *)
        hour: Hour field (0-23 or *)
        day: Day of month field (1-31 or *)
        month: Month field (1-12 or *)
        weekday: Day of week field (0-6 or *)

    Returns:
        Cron expression string
    """
    return f"{minute} {hour} {day} {month} {weekday}"
