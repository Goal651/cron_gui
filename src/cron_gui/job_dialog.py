"""
Job Dialog - Modal dialog for adding and editing cron jobs.
"""

import gi
import datetime

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from typing import Optional, Dict
from cron_gui.cron_parser import (
    validate_cron_expression,
    get_next_runs,
    build_cron_expression,
)


class JobDialog(Gtk.Dialog):
    """Dialog for adding or editing a cron job."""

    def __init__(self, parent, job: Optional[Dict] = None):
        super().__init__(
            title="Edit Job" if job else "Add Job", transient_for=parent, modal=True
        )

        self.job = job
        self.set_default_size(500, 500)

        # Add buttons
        self.add_button("Cancel", Gtk.ResponseType.CANCEL)
        save_button = self.add_button("Save", Gtk.ResponseType.OK)
        save_button.add_css_class("suggested-action")

        # Content area
        content = self.get_content_area()
        content.set_spacing(12)
        content.set_margin_start(12)
        content.set_margin_end(12)
        content.set_margin_top(12)
        content.set_margin_bottom(12)

        # Command entry
        command_label = Gtk.Label(label="Command:")
        command_label.set_xalign(0)
        command_label.add_css_class("heading")

        self.command_entry = Gtk.Entry()
        self.command_entry.set_placeholder_text("e.g., /usr/bin/backup.sh")
        if job:
            self.command_entry.set_text(job["command"])

        content.append(command_label)
        content.append(self.command_entry)

        # ==== Simple scheduling UI ====
        schedule_label = Gtk.Label(label="Schedule:")
        schedule_label.set_xalign(0)
        schedule_label.add_css_class("heading")
        schedule_label.set_margin_top(12)
        content.append(schedule_label)

        # Recurrence selector
        recurrence_label = Gtk.Label(label="Recurrence:")
        recurrence_label.set_xalign(0)
        self.recurrence_combo = Gtk.ComboBoxText()
        for label in ["Daily", "Weekly", "Monthly", "Yearly", "Once"]:
            self.recurrence_combo.append_text(label)
        self.recurrence_combo.set_active(0)  # default to Daily
        self.recurrence_combo.connect("changed", self._on_simple_changed)
        content.append(recurrence_label)
        content.append(self.recurrence_combo)

        # Time selection (always visible)
        time_label = Gtk.Label(label="Time:")
        time_label.set_xalign(0)
        simple_time_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.simple_hour_spin = Gtk.SpinButton.new_with_range(0, 23, 1)
        self.simple_minute_spin = Gtk.SpinButton.new_with_range(0, 59, 1)
        self.simple_hour_spin.set_value(0)
        self.simple_minute_spin.set_value(0)
        self.simple_hour_spin.connect("value-changed", self._on_simple_changed)
        self.simple_minute_spin.connect("value-changed", self._on_simple_changed)
        simple_time_box.append(self.simple_hour_spin)
        simple_time_box.append(Gtk.Label(label=":"))
        simple_time_box.append(self.simple_minute_spin)
        content.append(time_label)
        content.append(simple_time_box)

        # Day of week selector (for Weekly)
        self.weekday_label = Gtk.Label(label="Day of week:")
        self.weekday_label.set_xalign(0)
        self.weekday_combo = Gtk.ComboBoxText()
        weekdays = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ]
        for day in weekdays:
            self.weekday_combo.append_text(day)
        self.weekday_combo.set_active(0)  # default to Sunday
        self.weekday_combo.connect("changed", self._on_simple_changed)
        content.append(self.weekday_label)
        content.append(self.weekday_combo)

        # Day of month selector (for Monthly)
        self.monthday_label = Gtk.Label(label="Day of month:")
        self.monthday_label.set_xalign(0)
        self.monthday_spin = Gtk.SpinButton.new_with_range(1, 31, 1)
        self.monthday_spin.set_value(1)
        self.monthday_spin.connect("value-changed", self._on_simple_changed)
        content.append(self.monthday_label)
        content.append(self.monthday_spin)

        # Calendar widget (for Once and Yearly)
        self.calendar_label = Gtk.Label(label="Date:")
        self.calendar_label.set_xalign(0)
        self.calendar = Gtk.Calendar()
        self.calendar.connect("day-selected", self._on_simple_changed)
        content.append(self.calendar_label)
        content.append(self.calendar)

        # Advanced options section (hidden by default)
        self.show_advanced_check = Gtk.CheckButton(label="Show advanced options")
        self.show_advanced_check.connect("toggled", self._on_advanced_toggled)
        self.show_advanced_check.set_margin_top(12)
        content.append(self.show_advanced_check)

        # Quick presets (in advanced section)
        self.preset_label = Gtk.Label(label="Quick presets:")
        self.preset_label.set_xalign(0)
        self.preset_label.set_visible(False)

        self.preset_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.preset_box.set_visible(False)

        presets = [
            ("Every minute", "* * * * *"),
            ("Every hour", "0 * * * *"),
            ("Daily midnight", "0 0 * * *"),
            ("Weekly Sun", "0 0 * * 0"),
            ("Monthly 1st", "0 0 1 * *"),
        ]

        for name, expr in presets:
            btn = Gtk.Button(label=name)
            btn.connect("clicked", lambda b, e=expr: self._set_preset(e))
            self.preset_box.append(btn)

        content.append(self.preset_label)
        content.append(self.preset_box)

        # Manual cron expression (in advanced section)
        self.manual_label = Gtk.Label(label="Manual cron expression:")
        self.manual_label.set_xalign(0)
        self.manual_label.set_margin_top(6)
        self.manual_label.set_visible(False)

        self.schedule_entry = Gtk.Entry()
        self.schedule_entry.set_placeholder_text("e.g., 0 */2 * * *")
        self.schedule_entry.set_visible(False)
        if job:
            self.schedule_entry.set_text(job["schedule"])
        self.schedule_entry.connect("changed", self._on_schedule_changed)

        content.append(self.manual_label)
        content.append(self.schedule_entry)

        # Schedule builder grid (in advanced section)
        self.builder_label = Gtk.Label(label="Advanced builder:")
        self.builder_label.set_xalign(0)
        self.builder_label.set_margin_top(6)
        self.builder_label.set_visible(False)
        content.append(self.builder_label)

        self.grid = Gtk.Grid()
        self.grid.set_row_spacing(6)
        self.grid.set_column_spacing(12)
        self.grid.set_visible(False)

        # Minute
        self.grid.attach(Gtk.Label(label="Minute:", xalign=0), 0, 0, 1, 1)
        self.minute_entry = Gtk.Entry()
        self.minute_entry.set_placeholder_text("* or 0-59")
        self.minute_entry.set_text("*")
        self.minute_entry.connect("changed", self._on_builder_changed)
        self.grid.attach(self.minute_entry, 1, 0, 1, 1)

        # Hour
        self.grid.attach(Gtk.Label(label="Hour:", xalign=0), 0, 1, 1, 1)
        self.hour_entry = Gtk.Entry()
        self.hour_entry.set_placeholder_text("* or 0-23")
        self.hour_entry.set_text("*")
        self.hour_entry.connect("changed", self._on_builder_changed)
        self.grid.attach(self.hour_entry, 1, 1, 1, 1)

        # Day
        self.grid.attach(Gtk.Label(label="Day:", xalign=0), 0, 2, 1, 1)
        self.day_entry = Gtk.Entry()
        self.day_entry.set_placeholder_text("* or 1-31")
        self.day_entry.set_text("*")
        self.day_entry.connect("changed", self._on_builder_changed)
        self.grid.attach(self.day_entry, 1, 2, 1, 1)

        # Month
        self.grid.attach(Gtk.Label(label="Month:", xalign=0), 0, 3, 1, 1)
        self.month_entry = Gtk.Entry()
        self.month_entry.set_placeholder_text("* or 1-12")
        self.month_entry.set_text("*")
        self.month_entry.connect("changed", self._on_builder_changed)
        self.grid.attach(self.month_entry, 1, 3, 1, 1)

        # Weekday
        self.grid.attach(Gtk.Label(label="Weekday:", xalign=0), 0, 4, 1, 1)
        self.weekday_entry = Gtk.Entry()
        self.weekday_entry.set_placeholder_text("* or 0-6 (0=Sun)")
        self.weekday_entry.set_text("*")
        self.weekday_entry.connect("changed", self._on_builder_changed)
        self.grid.attach(self.weekday_entry, 1, 4, 1, 1)

        content.append(self.grid)

        # Validation message
        self.validation_label = Gtk.Label()
        self.validation_label.set_xalign(0)
        self.validation_label.set_wrap(True)
        self.validation_label.set_margin_top(12)
        content.append(self.validation_label)

        # Next runs preview
        self.next_runs_label = Gtk.Label()
        self.next_runs_label.set_xalign(0)
        self.next_runs_label.set_wrap(True)
        self.next_runs_label.add_css_class("dim-label")
        content.append(self.next_runs_label)

        # Comment entry
        comment_label = Gtk.Label(label="Comment (optional):")
        comment_label.set_xalign(0)
        comment_label.set_margin_top(12)

        self.comment_entry = Gtk.Entry()
        self.comment_entry.set_placeholder_text("e.g., Daily backup job")
        if job:
            self.comment_entry.set_text(job.get("comment", ""))

        content.append(comment_label)
        content.append(self.comment_entry)

        # Initialize schedule entry with a default value
        if not job:
            self.schedule_entry.set_text("0 0 * * *")  # Daily at midnight

        # Initial validation
        if job:
            self._parse_schedule_to_builder(job["schedule"])

        # Update UI visibility and validate
        self._update_ui_visibility()
        self._validate_schedule()

    def _set_preset(self, expression: str):
        """Set a preset cron expression."""
        self.schedule_entry.set_text(expression)
        self._parse_schedule_to_builder(expression)
        self._sync_simple_from_expression(expression)

    def _parse_schedule_to_builder(self, schedule: str):
        """Parse schedule into builder fields and simple UI fields."""
        parts = schedule.split()
        if len(parts) == 5:
            self.minute_entry.set_text(parts[0])
            self.hour_entry.set_text(parts[1])
            self.day_entry.set_text(parts[2])
            self.month_entry.set_text(parts[3])
            self.weekday_entry.set_text(parts[4])

            # Update simple UI based on parsed schedule
            try:
                minute = int(parts[0])
                hour = int(parts[1])
                day = parts[2]
                month = parts[3]
                weekday = parts[4]

                self.simple_hour_spin.set_value(hour)
                self.simple_minute_spin.set_value(minute)

                # Determine recurrence type
                if day == "*" and month == "*" and weekday == "*":
                    self.recurrence_combo.set_active(1)  # Daily
                elif day == "*" and month == "*" and weekday != "*":
                    self.recurrence_combo.set_active(2)  # Weekly
                elif day != "*" and month == "*" and weekday == "*":
                    self.recurrence_combo.set_active(3)  # Monthly
                elif day != "*" and month != "*" and weekday == "*":
                    self.recurrence_combo.set_active(4)  # Yearly
                else:
                    self.recurrence_combo.set_active(0)  # Once or custom

                # Set calendar date if applicable
                if day.isdigit() and month.isdigit():
                    try:
                        # Gtk.Calendar month is 0-indexed
                        self.calendar.select_month(
                            int(month) - 1, self.calendar.get_date().get_year()
                        )
                        self.calendar.select_day(int(day))
                    except Exception:
                        pass  # Invalid date for calendar
            except ValueError:
                pass  # Not a simple numeric schedule

    def _on_builder_changed(self, entry):
        """Handle builder field changes."""
        expression = build_cron_expression(
            self.minute_entry.get_text() or "*",
            self.hour_entry.get_text() or "*",
            self.day_entry.get_text() or "*",
            self.month_entry.get_text() or "*",
            self.weekday_entry.get_text() or "*",
        )
        self.schedule_entry.set_text(expression)
        self._sync_simple_from_expression(
            expression
        )  # Sync simple UI when advanced fields change

    def _on_schedule_changed(self, entry):
        """Handle schedule entry changes."""
        self._validate_schedule()
        # Also update simple UI if manual entry changes
        self._sync_simple_from_expression(entry.get_text())

    def _validate_schedule(self):
        """Validate the current schedule."""
        schedule = self.schedule_entry.get_text()

        if not schedule:
            self.validation_label.set_markup(
                "<span foreground='red'>⚠ Schedule cannot be empty</span>"
            )
            self.next_runs_label.set_text("")
            return False

        if validate_cron_expression(schedule):
            self.validation_label.set_markup(
                "<span foreground='green'>✓ Valid cron expression</span>"
            )

            # Show next runs
            next_runs = get_next_runs(schedule, 3)
            if next_runs:
                runs_text = "Next runs:\n" + "\n".join(
                    f"  • {run}" for run in next_runs
                )
                self.next_runs_label.set_text(runs_text)

            return True
        else:
            self.validation_label.set_markup(
                "<span foreground='red'>⚠ Invalid cron expression</span>"
            )
            self.next_runs_label.set_text("")
            return False

    def _update_ui_visibility(self):
        """Update visibility of UI elements based on recurrence type."""
        recurrence_idx = self.recurrence_combo.get_active()
        # 0=Daily, 1=Weekly, 2=Monthly, 3=Yearly, 4=Once

        # Hide all optional elements first
        self.weekday_label.set_visible(False)
        self.weekday_combo.set_visible(False)
        self.monthday_label.set_visible(False)
        self.monthday_spin.set_visible(False)
        self.calendar_label.set_visible(False)
        self.calendar.set_visible(False)

        # Show elements based on recurrence type
        if recurrence_idx == 0:  # Daily - only time (already visible)
            pass
        elif recurrence_idx == 1:  # Weekly - time + day of week
            self.weekday_label.set_visible(True)
            self.weekday_combo.set_visible(True)
        elif recurrence_idx == 2:  # Monthly - time + day of month
            self.monthday_label.set_visible(True)
            self.monthday_spin.set_visible(True)
        elif recurrence_idx == 3:  # Yearly - time + calendar
            self.calendar_label.set_visible(True)
            self.calendar.set_visible(True)
        elif recurrence_idx == 4:  # Once - time + calendar
            self.calendar_label.set_visible(True)
            self.calendar.set_visible(True)

    def _on_simple_changed(self, widget=None):
        """Handle changes in simple UI elements (recurrence, time, date)."""
        # Update UI visibility first
        self._update_ui_visibility()

        recurrence_idx = self.recurrence_combo.get_active()
        hour = int(self.simple_hour_spin.get_value())
        minute = int(self.simple_minute_spin.get_value())

        # Build cron expression based on recurrence type
        if recurrence_idx == 0:  # Daily
            expression = f"{minute} {hour} * * *"
        elif recurrence_idx == 1:  # Weekly - use day of week selector
            weekday_idx = self.weekday_combo.get_active()
            expression = f"{minute} {hour} * * {weekday_idx}"
        elif recurrence_idx == 2:  # Monthly - use day of month
            day = int(self.monthday_spin.get_value())
            expression = f"{minute} {hour} {day} * *"
        elif recurrence_idx == 3:  # Yearly - use calendar
            date = self.calendar.get_date()
            day = date.get_day_of_month()
            month = date.get_month() + 1  # Gtk.Calendar month is 0-indexed
            expression = f"{minute} {hour} {day} {month} *"
        elif recurrence_idx == 4:  # Once - use calendar (same as yearly for cron)
            date = self.calendar.get_date()
            day = date.get_day_of_month()
            month = date.get_month() + 1  # Gtk.Calendar month is 0-indexed
            expression = f"{minute} {hour} {day} {month} *"
        else:
            expression = "* * * * *"

        # Update the schedule entry
        self.schedule_entry.set_text(expression)
        self._validate_schedule()

    def _sync_simple_from_expression(self, expression: str):
        """Sync simple UI elements from a cron expression."""
        parts = expression.split()
        if len(parts) != 5:
            return

        try:
            minute_part, hour_part, day_part, month_part, weekday_part = parts

            # Update time spinners if they're numeric
            if minute_part.isdigit():
                self.simple_minute_spin.set_value(int(minute_part))
            if hour_part.isdigit():
                self.simple_hour_spin.set_value(int(hour_part))

            # Update recurrence combo and related widgets based on pattern
            # Order: 0=Daily, 1=Weekly, 2=Monthly, 3=Yearly, 4=Once
            if day_part == "*" and month_part == "*" and weekday_part == "*":
                self.recurrence_combo.set_active(0)  # Daily
            elif day_part == "*" and month_part == "*" and weekday_part != "*":
                self.recurrence_combo.set_active(1)  # Weekly
                if weekday_part.isdigit():
                    self.weekday_combo.set_active(int(weekday_part))
            elif day_part != "*" and month_part == "*" and weekday_part == "*":
                self.recurrence_combo.set_active(2)  # Monthly
                if day_part.isdigit():
                    self.monthday_spin.set_value(int(day_part))
            elif day_part != "*" and month_part != "*":
                # Could be Yearly or Once - default to Yearly
                self.recurrence_combo.set_active(3)  # Yearly
                if day_part.isdigit() and month_part.isdigit():
                    day = int(day_part)
                    month = int(month_part)
                    year = self.calendar.get_date().get_year()
                    try:
                        # Gtk.Calendar month is 0-indexed
                        self.calendar.select_month(month - 1, year)
                        self.calendar.select_day(day)
                    except Exception:
                        pass  # Invalid date
            else:
                self.recurrence_combo.set_active(0)  # Default to Daily

            # Update UI visibility after setting recurrence
            self._update_ui_visibility()

        except (ValueError, IndexError):
            pass  # Invalid expression format

    def _on_advanced_toggled(self, check_button):
        """Toggle visibility of advanced options."""
        show_advanced = check_button.get_active()
        # Show/hide all advanced elements
        self.preset_label.set_visible(show_advanced)
        self.preset_box.set_visible(show_advanced)
        self.manual_label.set_visible(show_advanced)
        self.schedule_entry.set_visible(show_advanced)
        self.builder_label.set_visible(show_advanced)
        self.grid.set_visible(show_advanced)

    def get_job_data(self) -> Optional[Dict]:
        """
        Get the job data from the dialog.

        Returns:
            Dictionary with command, schedule, and comment, or None if invalid
        """
        command = self.command_entry.get_text().strip()
        schedule = self.schedule_entry.get_text().strip()
        comment = self.comment_entry.get_text().strip()

        if not command:
            return None

        if not self._validate_schedule():
            return None

        return {"command": command, "schedule": schedule, "comment": comment}
