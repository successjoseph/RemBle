# RemBle

![Language](https://img.shields.io/badge/language-Python-blue)

## Table of Contents
- [About](#about)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Testing](#testing)
- [Contributing](#contributing)
- [Authors and License](#authors-and-license)

## About

RemBle is a personal task-reminder toolkit made of three cooperating Python scripts (distinct from the similarly-themed `REMYBLE` and `Receipter` repos — this one has its own separate codebase and storage format). `data_manager.py` is the shared storage layer, persisting tasks to a local `reminders.json` file with time-window "due" logic (a task is due if its scheduled time has passed within the last 6 hours and hasn't been marked done today or snoozed). `remble.py` is a CLI (`argparse`-based) for adding (`-nr`) and listing (`-l`) reminders. `remble_daemon.py` is a PyQt6 background-thread daemon that polls for due tasks every few seconds and pops up a frameless, always-on-top "REMBLE ENFORCEMENT" overlay with "I Have Done This" and "Snooze 30m" buttons, only ever showing the single oldest outstanding task. `ai_processor.py` is an autonomous-scheduling add-on: it reads a personal `year_plan.txt`, sends it to Google's Gemini (`gemini-2.5-flash`) with a prompt asking for a JSON daily schedule of habits/actions (at least 1 hour apart, 06:00–23:00), then shells out to `remble.py -nr` for each generated item to populate the reminder database. This reads as a personal productivity-automation project built by and for its author.

## Prerequisites
- Python 3.x
- `PyQt6`, `google-generativeai`, `python-dotenv` (no `requirements.txt` is included in the repository; these are inferred from the imports in `remble_daemon.py` and `ai_processor.py`)
- A Google Gemini API key (only required for `ai_processor.py`)

## Installation
```bash
git clone https://github.com/successjoseph/RemBle.git
cd RemBle
pip install PyQt6 google-generativeai python-dotenv
```

## Configuration
- `.env` (git-ignored) must define `GEMINI_API_KEY` for `ai_processor.py` — it exits immediately with an error if this is missing.
- `ai_processor.py` reads a plain-text `year_plan.txt` (a personal development plan) as input; this file is not included in the repository (git-ignored, along with all `.txt`/`.json` files and `.env`).
- Task data lives in `reminders.json`, also git-ignored — it is created and managed at runtime by `data_manager.py`, not committed.

## Usage
Add a reminder via the CLI:
```bash
python remble.py -nr "14:30" "Take a walk"
```
List all reminders:
```bash
python remble.py -l
```
Run the enforcement overlay daemon in the background (polls `reminders.json` and shows a full always-on-top popup for the oldest due, unsnoozed task):
```bash
python remble_daemon.py
```
Auto-populate a day's schedule from a personal plan using Gemini (requires `year_plan.txt` and `GEMINI_API_KEY`):
```bash
python ai_processor.py
```

## Testing
No automated tests are currently included.

## Contributing
This is a personal automation project — these notes are for the author's own future reference rather than an open call for contributions.

## Authors and License
**Author:** [successjoseph](https://github.com/successjoseph)
No license file included in this repository — all rights reserved by default.
