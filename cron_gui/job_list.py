"""
Job List - GTK4 ListBox for displaying cron jobs.
"""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
from typing import List, Dict, Callable


class JobRow(Gtk.ListBoxRow):
    """Custom row widget for displaying a single cron job."""

    def __init__(
        self, job: Dict, on_edit: Callable, on_delete: Callable, on_toggle: Callable
    ):
        super().__init__()

        self.job = job
        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_toggle = on_toggle

        # Main horizontal box
        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        hbox.set_margin_start(12)
        hbox.set_margin_end(12)
        hbox.set_margin_top(8)
        hbox.set_margin_bottom(8)

        # Left side - job info
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        vbox.set_hexpand(True)

        # Command label (bold)
        command_label = Gtk.Label(label=job["command"])
        command_label.set_xalign(0)
        command_label.set_wrap(True)
        command_label.add_css_class("heading")

        # Schedule label (smaller, gray)
        from cron_gui.cron_parser import cron_to_human_readable

        schedule_text = f"{job['schedule']} - {cron_to_human_readable(job['schedule'])}"
        schedule_label = Gtk.Label(label=schedule_text)
        schedule_label.set_xalign(0)
        schedule_label.add_css_class("dim-label")
        schedule_label.add_css_class("caption")

        # Comment label if exists
        if job["comment"]:
            comment_label = Gtk.Label(label=f"💬 {job['comment']}")
            comment_label.set_xalign(0)
            comment_label.add_css_class("caption")
            vbox.append(comment_label)

        vbox.append(command_label)
        vbox.append(schedule_label)

        # Right side - action buttons
        action_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

        # Enable/Disable switch
        toggle_switch = Gtk.Switch()
        toggle_switch.set_active(job["enabled"])
        toggle_switch.set_valign(Gtk.Align.CENTER)
        toggle_switch.connect("state-set", self._on_toggle_clicked)

        # Edit button
        edit_button = Gtk.Button(icon_name="document-edit-symbolic")
        edit_button.set_valign(Gtk.Align.CENTER)
        edit_button.set_tooltip_text("Edit job")
        edit_button.connect("clicked", self._on_edit_clicked)

        # Delete button
        delete_button = Gtk.Button(icon_name="user-trash-symbolic")
        delete_button.set_valign(Gtk.Align.CENTER)
        delete_button.set_tooltip_text("Delete job")
        delete_button.add_css_class("destructive-action")
        delete_button.connect("clicked", self._on_delete_clicked)

        action_box.append(toggle_switch)
        action_box.append(edit_button)
        action_box.append(delete_button)

        hbox.append(vbox)
        hbox.append(action_box)

        self.set_child(hbox)

    def _on_edit_clicked(self, button):
        """Handle edit button click."""
        self.on_edit(self.job)

    def _on_delete_clicked(self, button):
        """Handle delete button click."""
        self.on_delete(self.job)

    def _on_toggle_clicked(self, switch, state):
        """Handle toggle switch change."""
        self.on_toggle(self.job, state)
        return False


class JobListView(Gtk.ScrolledWindow):
    """Scrollable list view for displaying cron jobs."""

    def __init__(self, on_edit: Callable, on_delete: Callable, on_toggle: Callable):
        super().__init__()

        self.on_edit = on_edit
        self.on_delete = on_delete
        self.on_toggle = on_toggle

        self.set_vexpand(True)
        self.set_hexpand(True)

        # Create ListBox
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        self.listbox.add_css_class("boxed-list")

        # Empty state
        self.empty_label = Gtk.Label(
            label="No cron jobs found.\nClick '+' to add a new job."
        )
        self.empty_label.set_valign(Gtk.Align.CENTER)
        self.empty_label.set_halign(Gtk.Align.CENTER)
        self.empty_label.add_css_class("dim-label")
        self.empty_label.add_css_class("title-2")
        self.empty_label.set_margin_top(60)
        self.empty_label.set_margin_bottom(60)

        # Stack to switch between list and empty state
        self.stack = Gtk.Stack()
        self.stack.add_named(self.listbox, "list")
        self.stack.add_named(self.empty_label, "empty")

        self.set_child(self.stack)

        # Filter function for search
        self.listbox.set_filter_func(self._filter_func)
        self.search_text = ""

    def update_jobs(self, jobs: List[Dict]):
        """
        Update the list with new jobs.

        Args:
            jobs: List of job dictionaries
        """
        # Clear existing rows
        while True:
            row = self.listbox.get_row_at_index(0)
            if row is None:
                break
            self.listbox.remove(row)

        # Add new rows
        for job in jobs:
            row = JobRow(job, self.on_edit, self.on_delete, self.on_toggle)
            self.listbox.append(row)

        # Show empty state if no jobs
        if len(jobs) == 0:
            self.stack.set_visible_child_name("empty")
        else:
            self.stack.set_visible_child_name("list")

    def set_search_text(self, text: str):
        """
        Set search filter text.

        Args:
            text: Search text
        """
        self.search_text = text.lower()
        self.listbox.invalidate_filter()

    def _filter_func(self, row):
        """Filter function for search."""
        if not self.search_text:
            return True

        if isinstance(row, JobRow):
            job = row.job
            # Search in command, schedule, and comment
            searchable = (
                f"{job['command']} {job['schedule']} {job.get('comment', '')}".lower()
            )
            return self.search_text in searchable

        return True
