#!/usr/bin/env python3
"""
Setup configuration for Cron GUI.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cron-gui",
    version="0.1.0",
    author="Cron GUI Team",
    description="A modern GTK4 desktop application for managing cron jobs on Linux",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/goal651/cron_gui",
    package_dir={"": "src"},
    packages=find_packages(where="src", exclude=["*__pycache__*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: POSIX :: Linux",
        "Environment :: X11 Applications :: GTK",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyGObject>=3.42.0",
        "python-crontab>=3.0.0",
        "croniter>=1.4.1",
    ],
    include_package_data=True,
    package_data={
        "cron_gui": ["../assets/*"],
    },
    entry_points={
        "console_scripts": [
            "cron-gui=main:main",
        ],
    },
)
