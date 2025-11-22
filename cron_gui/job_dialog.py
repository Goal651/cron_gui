"""
Job Dialog - Modal dialog for adding and editing cron jobs.
"""

import gi

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
        self.set_default_size(500, 450)

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

        # Schedule section
        schedule_label = Gtk.Label(label="Schedule:")
        schedule_label.set_xalign(0)
        schedule_label.add_css_class("heading")
        schedule_label.set_margin_top(12)
        content.append(schedule_label)

        # Quick presets
        preset_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        preset_label = Gtk.Label(label="Quick presets:")
        preset_label.set_xalign(0)

        presets = [
            ("Every minute", "* * * * *"),
            ("Every hour", "0 * * * *"),
            ("Daily at midnight", "0 0 * * *"),
            ("Weekly (Sunday)", "0 0 * * 0"),
            ("Monthly", "0 0 1 * *"),
        ]

        for name, expr in presets:
            btn = Gtk.Button(label=name)
            btn.connect("clicked", lambda b, e=expr: self._set_preset(e))
            preset_box.append(btn)

        content.append(preset_label)
        content.append(preset_box)

        # Manual cron expression
        manual_label = Gtk.Label(label="Or enter cron expression manually:")
        manual_label.set_xalign(0)
        manual_label.set_margin_top(12)

        self.schedule_entry = Gtk.Entry()
        self.schedule_entry.set_placeholder_text("e.g., 0 */2 * * * (every 2 hours)")
        if job:
            self.schedule_entry.set_text(job["schedule"])
        self.schedule_entry.connect("changed", self._on_schedule_changed)

        content.append(manual_label)
        content.append(self.schedule_entry)

        # Schedule builder grid
        builder_label = Gtk.Label(label="Schedule builder:")
        builder_label.set_xalign(0)
        builder_label.set_margin_top(12)
        content.append(builder_label)

        grid = Gtk.Grid()
        grid.set_row_spacing(6)
        grid.set_column_spacing(12)

        # Minute
        grid.attach(Gtk.Label(label="Minute:", xalign=0), 0, 0, 1, 1)
        self.minute_entry = Gtk.Entry()
        self.minute_entry.set_placeholder_text("* or 0-59")
        self.minute_entry.set_text("*")
        self.minute_entry.connect("changed", self._on_builder_changed)
        grid.attach(self.minute_entry, 1, 0, 1, 1)

        # Hour
        grid.attach(Gtk.Label(label="Hour:", xalign=0), 0, 1, 1, 1)
        self.hour_entry = Gtk.Entry()
        self.hour_entry.set_placeholder_text("* or 0-23")
        self.hour_entry.set_text("*")
        self.hour_entry.connect("changed", self._on_builder_changed)
        grid.attach(self.hour_entry, 1, 1, 1, 1)

        # Day
        grid.attach(Gtk.Label(label="Day:", xalign=0), 0, 2, 1, 1)
        self.day_entry = Gtk.Entry()
        self.day_entry.set_placeholder_text("* or 1-31")
        self.day_entry.set_text("*")
        self.day_entry.connect("changed", self._on_builder_changed)
        grid.attach(self.day_entry, 1, 2, 1, 1)

        # Month
        grid.attach(Gtk.Label(label="Month:", xalign=0), 0, 3, 1, 1)
        self.month_entry = Gtk.Entry()
        self.month_entry.set_placeholder_text("* or 1-12")
        self.month_entry.set_text("*")
        self.month_entry.connect("changed", self._on_builder_changed)
        grid.attach(self.month_entry, 1, 3, 1, 1)

        # Weekday
        grid.attach(Gtk.Label(label="Weekday:", xalign=0), 0, 4, 1, 1)
        self.weekday_entry = Gtk.Entry()
        self.weekday_entry.set_placeholder_text("* or 0-6 (0=Sun)")
        self.weekday_entry.set_text("*")
        self.weekday_entry.connect("changed", self._on_builder_changed)
        grid.attach(self.weekday_entry, 1, 4, 1, 1)

        content.append(grid)

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

        # Initial validation
        if job:
            self._parse_schedule_to_builder(job["schedule"])
        self._validate_schedule()

    def _set_preset(self, expression: str):
        """Set a preset cron expression."""
        self.schedule_entry.set_text(expression)
        self._parse_schedule_to_builder(expression)

    def _parse_schedule_to_builder(self, schedule: str):
        """Parse schedule into builder fields."""
        parts = schedule.split()
        if len(parts) == 5:
            self.minute_entry.set_text(parts[0])
            self.hour_entry.set_text(parts[1])
            self.day_entry.set_text(parts[2])
            self.month_entry.set_text(parts[3])
            self.weekday_entry.set_text(parts[4])

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

    def _on_schedule_changed(self, entry):
        """Handle schedule entry changes."""
        self._validate_schedule()

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
