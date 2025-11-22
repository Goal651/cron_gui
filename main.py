#!/usr/bin/env python3
"""
Cron GUI - Main entry point for the application.
"""

import sys
import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")
from gi.repository import Gtk, Adw, Gio

from cron_gui.window import CronGuiWindow


class CronGuiApplication(Adw.Application):
    """Main GTK application."""

    def __init__(self):
        super().__init__(
            application_id="com.github.cron_gui", flags=Gio.ApplicationFlags.FLAGS_NONE
        )

        # Create actions
        self.create_action("quit", self.on_quit, ["<primary>q"])
        self.create_action("about", self.on_about)

    def do_activate(self):
        """Called when the application is activated."""
        win = self.props.active_window
        if not win:
            win = CronGuiWindow(self)
        win.present()

    def create_action(self, name, callback, shortcuts=None):
        """Create an application action."""
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)

    def on_quit(self, action, param):
        """Quit the application."""
        self.quit()

    def on_about(self, action, param):
        """Show the about dialog."""
        about = Adw.AboutWindow(
            transient_for=self.props.active_window,
            application_name="Cron GUI",
            application_icon="com.github.cron_gui",
            developer_name="Cron GUI Team",
            version="0.1.0",
            developers=["Cron GUI Team"],
            copyright="© 2025 Cron GUI Team",
            license_type=Gtk.License.MIT_X11,
            website="https://github.com/yourusername/cron_gui",
            issue_url="https://github.com/yourusername/cron_gui/issues",
        )
        about.present()


def main():
    """Main entry point."""
    app = CronGuiApplication()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
