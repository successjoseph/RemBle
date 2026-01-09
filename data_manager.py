import json
import os
from datetime import datetime, timedelta

DB_FILE = "reminders.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return []
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_db(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_next_id(tasks):
    if not tasks:
        return 1
    
    # Robustly extract IDs, ignoring invalid or missing ones
    valid_ids = []
    for task in tasks:
        try:
            # Handle cases where id might be missing, a string, or int
            val = task.get("id")
            if val is not None:
                valid_ids.append(int(val))
        except (ValueError, TypeError):
            continue
            
    return max(valid_ids) + 1 if valid_ids else 1

def add_reminder(time_str, task_text):
    db = load_db()
    rem_id = get_next_id(db)
    
    new_entry = {
        "id": rem_id,
        "time": time_str,
        "task": task_text,
        "status": "PENDING",
        "last_action_date": "",
        "snooze_until": 0 # Unix timestamp
    }
    db.append(new_entry)
    save_db(db)
    return rem_id

def snooze_task(task_id, minutes):
    """Updates the task to be ignored until a specific timestamp."""
    db = load_db()
    # Calculate future timestamp
    future_time = (datetime.now() + timedelta(minutes=minutes)).timestamp()
    
    for task in db:
        if task['id'] == task_id:
            task['snooze_until'] = future_time
            task['status'] = "SNOOZED"
            
    save_db(db)

def get_due_tasks():
    db = load_db()
    # Get current time as a full datetime object
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    
    due = []
    
    for task in db:
        # 1. Check if we already did it today
        if task['last_action_date'] == today_str:
            continue

        # 2. Check if it is currently Snoozed
        # Uses 'or 0' to handle nulls safely
        snooze_until = task.get('snooze_until') or 0
        if now.timestamp() < snooze_until:
            continue

        # 3. Time Window Logic
        try:
            # Parse the task's HH:MM time
            task_time_obj = datetime.strptime(task['time'], "%H:%M")
            
            # Combine task time with TODAY's date
            # This represents "This task, if it were to happen today"
            task_dt = now.replace(hour=task_time_obj.hour, minute=task_time_obj.minute, second=0, microsecond=0)
            
            # Calculate difference in hours
            diff = now - task_dt
            diff_hours = diff.total_seconds() / 3600
            
            # LOGIC:
            # diff_hours >= 0  : The time has passed (it's not in the future)
            # diff_hours <= 6  : It passed less than 6 hours ago (it's not stale)
            if 0 <= diff_hours <= 6:
                due.append(task)
                
        except ValueError:
            # Skip invalid time formats
            continue
            
    # Sort by time so earliest missed task comes first
    due.sort(key=lambda x: x['time'])
    return due

def mark_done(task_id):
    db = load_db()
    for task in db:
        if task['id'] == task_id:
            task['last_action_date'] = datetime.now().strftime("%Y-%m-%d")
            task['status'] = "DONE"
            task['snooze_until'] = 0 # Reset snooze
    save_db(db)