# Cron GUI

A modern, beautiful Linux desktop application for managing cron jobs with a graphical interface. Built with Python and GTK4.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)

## Features

✨ **Modern GTK4 Interface** - Beautiful, native Linux look with Adwaita styling  
📋 **Easy Job Management** - View, add, edit, and delete cron jobs with a few clicks  
🔍 **Search & Filter** - Quickly find jobs with the built-in search  
⏰ **Cron Expression Builder** - No need to remember cron syntax  
✅ **Real-time Validation** - Instant feedback on cron expressions  
🔮 **Next Run Preview** - See when your jobs will execute next  
🎨 **Quick Presets** - Common schedules (hourly, daily, weekly, monthly)  
🔄 **Enable/Disable Jobs** - Toggle jobs on and off without deleting  
💬 **Job Comments** - Add descriptions to your cron jobs  

## Screenshots

*Coming soon - run the app to see the beautiful interface!*

## Requirements

- **OS:** Linux (tested on Ubuntu/Debian-based distributions)
- **Python:** 3.8 or higher
- **GTK:** GTK4 and libadwaita
- **System packages:**

  ```bash
  sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1
  ```

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/cron_gui.git
   cd cron_gui
   ```

2. **Create and activate virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Python dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**

   ```bash
   python3 main.py
   ```

## Usage

### Running the Application

Simply execute:

```bash
python3 main.py
```

Or if you want to add it to your application menu:

```bash
# Copy the desktop file to your local applications directory
cp cron-gui.desktop ~/.local/share/applications/
# Update the Exec path in the file to match your installation location
```

### Managing Cron Jobs

**Adding a Job:**

1. Click the `+` button in the header bar
2. Enter the command to execute
3. Choose a preset or build a custom schedule
4. Add an optional comment
5. Click "Save"

**Editing a Job:**

1. Click the edit button (pencil icon) on any job
2. Modify the fields as needed
3. Click "Save"

**Deleting a Job:**

1. Click the delete button (trash icon) on any job
2. Confirm the deletion

**Enabling/Disabling a Job:**

- Use the toggle switch on each job row

**Searching:**

- Click the search icon or press `Ctrl+F`
- Type to filter jobs by command, schedule, or comment

## Cron Expression Guide

Cron expressions consist of 5 fields:

```
* * * * *
│ │ │ │ │
│ │ │ │ └─── Day of week (0-6, 0=Sunday)
│ │ │ └───── Month (1-12)
│ │ └─────── Day of month (1-31)
│ └───────── Hour (0-23)
└─────────── Minute (0-59)
```

**Examples:**

- `* * * * *` - Every minute
- `0 * * * *` - Every hour
- `0 0 * * *` - Daily at midnight
- `0 0 * * 0` - Weekly on Sunday at midnight
- `0 0 1 * *` - Monthly on the 1st at midnight
- `*/5 * * * *` - Every 5 minutes
- `0 */2 * * *` - Every 2 hours

## What Can You Do With Cron Jobs?

Here are some powerful ways to use Cron GUI:

### 🚀 System Maintenance

- **Backups:** Automatically zip and move files to a backup drive every night
  - `0 3 * * * /scripts/backup.sh`
- **Cleanup:** Delete temporary files older than 7 days
  - `0 4 * * * find /tmp -mtime +7 -delete`
- **Log Rotation:** Archive and clear log files to save space

### 🌐 Web & Development

- **Status Checks:** Ping your website every 5 minutes
  - `*/5 * * * * curl -s https://mysite.com > /dev/null`
- **Data Fetching:** Run a script to scrape a website or fetch API data every hour
- **Certificate Renewal:** Auto-renew SSL certificates

### 🏠 Personal Automation

- **Reminders:** Send yourself a desktop notification
  - `0 9 * * 1 notify-send "Weekly Meeting"`
- **Downloads:** Schedule heavy downloads for off-peak hours (e.g., 2 AM)
- **Wallpaper Switcher:** Change your desktop wallpaper every hour

## Development

### Project Structure

```
cron_gui/
├── cron_gui/
│   ├── __init__.py          # Package initialization
│   ├── cron_manager.py      # Backend cron management
│   ├── cron_parser.py       # Cron expression utilities
│   ├── job_dialog.py        # Add/Edit dialog
│   ├── job_list.py          # Job list view
│   └── window.py            # Main application window
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── setup.py                 # Package setup
├── cron-gui.desktop        # Desktop entry file
└── README.md               # This file
```

### Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Troubleshooting

**"Failed to initialize crontab"**

- Make sure you have cron installed: `sudo apt install cron`
- Check if the cron service is running: `systemctl status cron`

**GTK/Adwaita import errors**

- Install system packages: `sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1`

**Permission errors**

- The app manages your user's crontab by default
- For system-wide cron jobs, you may need elevated privileges

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with [GTK4](https://www.gtk.org/) and [libadwaita](https://gnome.pages.gitlab.gnome.org/libadwaita/)
- Uses [python-crontab](https://pypi.org/project/python-crontab/) for cron management
- Uses [croniter](https://pypi.org/project/croniter/) for cron expression parsing

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/yourusername/cron_gui/issues) on GitHub.
