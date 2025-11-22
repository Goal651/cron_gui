"""
Cron Manager - Backend logic for managing cron jobs using python-crontab.
"""

from crontab import CronTab
from typing import List, Dict, Optional
import os


class CronManager:
    """Manages cron jobs using python-crontab library."""

    def __init__(self, user: Optional[str] = None):
        """
        Initialize the CronManager.

        Args:
            user: Username for crontab. If None, uses current user.
        """
        self.user = user or os.getenv("USER")
        try:
            self.cron = CronTab(user=self.user)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize crontab: {e}")

    def list_jobs(self) -> List[Dict]:
        """
        Get all cron jobs.

        Returns:
            List of dictionaries containing job information.
        """
        jobs = []
        for idx, job in enumerate(self.cron):
            jobs.append(
                {
                    "id": idx,
                    "command": str(job.command),
                    "schedule": str(job.slices),
                    "comment": job.comment or "",
                    "enabled": job.is_enabled(),
                    "valid": job.is_valid(),
                }
            )
        return jobs

    def add_job(self, command: str, schedule: str, comment: str = "") -> bool:
        """
        Add a new cron job.

        Args:
            command: Command to execute
            schedule: Cron schedule expression (e.g., "0 * * * *")
            comment: Optional comment/description

        Returns:
            True if successful, False otherwise
        """
        try:
            job = self.cron.new(command=command, comment=comment)
            job.setall(schedule)

            if not job.is_valid():
                return False

            self.cron.write()
            return True
        except Exception as e:
            print(f"Error adding job: {e}")
            return False

    def update_job(
        self, job_id: int, command: str, schedule: str, comment: str = ""
    ) -> bool:
        """
        Update an existing cron job.

        Args:
            job_id: Index of the job to update
            command: New command
            schedule: New schedule expression
            comment: New comment

        Returns:
            True if successful, False otherwise
        """
        try:
            jobs = list(self.cron)
            if job_id < 0 or job_id >= len(jobs):
                return False

            job = jobs[job_id]
            job.set_command(command)
            job.setall(schedule)
            job.set_comment(comment)

            if not job.is_valid():
                return False

            self.cron.write()
            return True
        except Exception as e:
            print(f"Error updating job: {e}")
            return False

    def delete_job(self, job_id: int) -> bool:
        """
        Delete a cron job.

        Args:
            job_id: Index of the job to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            jobs = list(self.cron)
            if job_id < 0 or job_id >= len(jobs):
                return False

            self.cron.remove(jobs[job_id])
            self.cron.write()
            return True
        except Exception as e:
            print(f"Error deleting job: {e}")
            return False

    def toggle_job(self, job_id: int, enabled: bool) -> bool:
        """
        Enable or disable a cron job.

        Args:
            job_id: Index of the job to toggle
            enabled: True to enable, False to disable

        Returns:
            True if successful, False otherwise
        """
        try:
            jobs = list(self.cron)
            if job_id < 0 or job_id >= len(jobs):
                return False

            job = jobs[job_id]
            job.enable(enabled)
            self.cron.write()
            return True
        except Exception as e:
            print(f"Error toggling job: {e}")
            return False

    def reload(self):
        """Reload the crontab from disk."""
        try:
            self.cron = CronTab(user=self.user)
        except Exception as e:
            raise RuntimeError(f"Failed to reload crontab: {e}")
