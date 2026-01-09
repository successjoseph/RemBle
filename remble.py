import argparse
import sys
from data_manager import add_reminder, load_db

def main():
    parser = argparse.ArgumentParser(description="Remble CLI")
    
    # Argument: New Reminder (-nr time "task")
    parser.add_argument("-nr", "--new_reminder", nargs=2, metavar=('TIME', 'TASK'),
                        help="Add new reminder. Format: HH:MM 'Task String'")
    
    # Argument: List Reminders
    parser.add_argument("-l", "--list", action="store_true", help="List all reminders")

    args = parser.parse_args()

    if args.new_reminder:
        time_val = args.new_reminder[0]
        task_val = args.new_reminder[1]
        
        # Validation
        try:
            # Simple check if format is roughly HH:MM
            if ":" not in time_val:
                raise ValueError
        except:
            print("Error: Time must be in HH:MM format (e.g., 14:30)")
            sys.exit(1)

        rid = add_reminder(time_val, task_val)
        print(f"[OK] Success: Added '{task_val}' at {time_val} (ID: {rid})")

    elif args.list:
        db = load_db()
        print(f"{'ID':<15} {'TIME':<10} {'STATUS':<10} {'TASK'}")
        print("-" * 60)
        for item in db:
            print(f"{item['id']:<15} {item['time']:<10} {item['status']:<10} {item['task']}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()