"""
Main Window - Primary application window with GTK4.
"""

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, GLib, Gio, GObject
from cron_gui.job_list import JobListView
from cron_gui.job_dialog import JobDialog
from cron_gui.cron_manager import CronManager


class CronGuiWindow(Adw.ApplicationWindow):
    """Main application window."""

    def __init__(self, app):
        super().__init__(application=app)

        self.set_title("Cron GUI")
        self.set_default_size(800, 600)

        # Initialize cron manager
        try:
            self.cron_manager = CronManager()
        except Exception as e:
            self._show_error_dialog(f"Failed to initialize cron manager: {e}")
            return

        # Main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Header bar
        header = Adw.HeaderBar()

        # Add button
        add_button = Gtk.Button(icon_name="list-add-symbolic")
        add_button.set_tooltip_text("Add new cron job")
        add_button.connect("clicked", self._on_add_clicked)
        header.pack_start(add_button)

        # Refresh button
        refresh_button = Gtk.Button(icon_name="view-refresh-symbolic")
        refresh_button.set_tooltip_text("Refresh job list")
        refresh_button.connect("clicked", self._on_refresh_clicked)
        header.pack_start(refresh_button)

        # Menu button
        menu_button = Gtk.MenuButton(icon_name="open-menu-symbolic")
        menu_button.set_tooltip_text("Main menu")

        # Create menu
        menu = Gio.Menu()
        menu.append("About", "app.about")
        menu_button.set_menu_model(menu)

        header.pack_end(menu_button)

        main_box.append(header)

        # Search bar
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_placeholder_text("Search jobs...")
        self.search_entry.connect("search-changed", self._on_search_changed)

        search_bar = Gtk.SearchBar()
        search_bar.set_child(self.search_entry)
        search_bar.set_key_capture_widget(self)

        # Toggle search with Ctrl+F
        self.search_button = Gtk.ToggleButton(icon_name="system-search-symbolic")
        self.search_button.set_tooltip_text("Search (Ctrl+F)")
        search_bar.bind_property(
            "search-mode-enabled",
            self.search_button,
            "active",
            GObject.BindingFlags.BIDIRECTIONAL,
        )
        header.pack_end(self.search_button)

        main_box.append(search_bar)

        # Job list view
        self.job_list = JobListView(
            on_edit=self._on_edit_job,
            on_delete=self._on_delete_job,
            on_toggle=self._on_toggle_job,
        )

        main_box.append(self.job_list)

        # Status bar
        self.status_label = Gtk.Label()
        self.status_label.set_xalign(0)
        self.status_label.set_margin_start(12)
        self.status_label.set_margin_end(12)
        self.status_label.set_margin_top(6)
        self.status_label.set_margin_bottom(6)
        self.status_label.add_css_class("dim-label")

        main_box.append(self.status_label)

        self.set_content(main_box)

        # Load initial jobs
        self._refresh_jobs()

    def _refresh_jobs(self):
        """Reload jobs from crontab."""
        try:
            self.cron_manager.reload()
            jobs = self.cron_manager.list_jobs()
            self.job_list.update_jobs(jobs)

            # Update status
            count = len(jobs)
            enabled_count = sum(1 for j in jobs if j["enabled"])
            self.status_label.set_text(f"{count} job(s) total, {enabled_count} enabled")
        except Exception as e:
            self._show_error_dialog(f"Failed to load jobs: {e}")

    def _on_add_clicked(self, button):
        """Handle add button click."""
        dialog = JobDialog(self)
        dialog.connect("response", self._on_dialog_response, None)
        dialog.present()

    def _on_edit_job(self, job):
        """Handle edit job request."""
        dialog = JobDialog(self, job)
        dialog.connect("response", self._on_dialog_response, job)
        dialog.present()

    def _on_dialog_response(self, dialog, response, original_job):
        """Handle dialog response."""
        if response == Gtk.ResponseType.OK:
            job_data = dialog.get_job_data()

            if job_data:
                if original_job:
                    # Update existing job
                    success = self.cron_manager.update_job(
                        original_job["id"],
                        job_data["command"],
                        job_data["schedule"],
                        job_data["comment"],
                    )
                    action = "updated"
                else:
                    # Add new job
                    success = self.cron_manager.add_job(
                        job_data["command"], job_data["schedule"], job_data["comment"]
                    )
                    action = "added"

                if success:
                    self._refresh_jobs()
                    self._show_toast(f"Job {action} successfully")
                else:
                    self._show_error_dialog(f"Failed to {action.rstrip('d')} job")

        dialog.close()

    def _on_delete_job(self, job):
        """Handle delete job request."""
        # Confirmation dialog
        dialog = Adw.MessageDialog.new(self)
        dialog.set_heading("Delete Job?")
        dialog.set_body(
            f"Are you sure you want to delete this job?\n\n{job['command']}"
        )
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("delete", "Delete")
        dialog.set_response_appearance("delete", Adw.ResponseAppearance.DESTRUCTIVE)
        dialog.set_default_response("cancel")
        dialog.set_close_response("cancel")

        dialog.connect("response", self._on_delete_confirmed, job)
        dialog.present()

    def _on_delete_confirmed(self, dialog, response, job):
        """Handle delete confirmation."""
        if response == "delete":
            if self.cron_manager.delete_job(job["id"]):
                self._refresh_jobs()
                self._show_toast("Job deleted successfully")
            else:
                self._show_error_dialog("Failed to delete job")

        dialog.close()

    def _on_toggle_job(self, job, enabled):
        """Handle job enable/disable toggle."""
        if self.cron_manager.toggle_job(job["id"], enabled):
            self._refresh_jobs()
            status = "enabled" if enabled else "disabled"
            self._show_toast(f"Job {status}")
        else:
            self._show_error_dialog("Failed to toggle job")

    def _on_refresh_clicked(self, button):
        """Handle refresh button click."""
        self._refresh_jobs()
        self._show_toast("Jobs refreshed")

    def _on_search_changed(self, entry):
        """Handle search text change."""
        text = entry.get_text()
        self.job_list.set_search_text(text)

    def _show_toast(self, message):
        """Show a toast notification."""
        toast = Adw.Toast.new(message)
        toast.set_timeout(2)

        # Get the toast overlay (we'll need to add this)
        # For now, just print to console
        print(f"Toast: {message}")

    def _show_error_dialog(self, message):
        """Show an error dialog."""
        dialog = Adw.MessageDialog.new(self)
        dialog.set_heading("Error")
        dialog.set_body(message)
        dialog.add_response("ok", "OK")
        dialog.set_default_response("ok")
        dialog.present()
