import os
import json
import subprocess
import google.generativeai as genai
from dotenv import load_dotenv
import re

# --- CONFIGURATION ---
load_dotenv() # Load the .env file
API_KEY = os.getenv("GEMINI_API_KEY")
INPUT_FILE = "year_plan.txt"
DB_FILE = "reminders.json"

if not API_KEY:
    print("❌ Error: GEMINI_API_KEY not found in .env file")
    exit(1)

genai.configure(api_key=API_KEY)

def get_ai_schedule(plan_text):
    """
    Sends the plan to Gemini and asks for a JSON schedule.
    """
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    You are an autonomous scheduler for a developer named Nymo.
    Analyze the following 'Personal Development Plan'.
    
    RULES:
    1. Extract specific DAILY actions/habits required to achieve these 1-year goals.
    2. Ignore generic fluff. Focus on 'Steps or Actions'.
    3. specific specific times for each task in 24-hour format (HH:MM).
    4. CRITICAL: Tasks must be at least 1 HOUR apart. Start the day at 06:00 and end by 23:00.
    5. Output ONLY valid JSON. No markdown formatting, no explanations.
    
    Format:
    [
        {{"time": "06:00", "task": "Short task description"}},
        {{"time": "07:30", "task": "Another task"}}
    ]

    Here is the Plan:
    {plan_text}
    """

    print("🧠 Contacting the Brain (Gemini)...")
    response = model.generate_content(prompt)
    
    # Clean up response if the AI adds markdown backticks
    clean_text = response.text.strip()
    if clean_text.startswith("```json"):
        clean_text = clean_text[7:]
    if clean_text.endswith("```"):
        clean_text = clean_text[:-3]
        
    return clean_text.strip()

def verify_insertion(task_text):
    """Checks the JSON database to confirm the task exists."""
    if not os.path.exists(DB_FILE): return False
    try:
        with open(DB_FILE, 'r') as f:
            data = json.load(f)
            for item in data:
                # Simple check if the task string is inside the db task string
                if task_text in item['task']: 
                    return True
    except:
        return False
    return False

def run_autonomous_setup():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: {INPUT_FILE} not found.")
        return

    print(f"📂 Reading {INPUT_FILE}...")
    with open(INPUT_FILE, 'r') as f:
        plan_text = f.read()

    # Get JSON from AI
    try:
        json_str = get_ai_schedule(plan_text)
        schedule = json.loads(json_str)
    except Exception as e:
        print(f"❌ AI Decoding Error: {e}")
        print("Raw output:", json_str)
        return

    print(f"⚡ AI generated {len(schedule)} tasks. Programming REMBLE...")

    for item in schedule:
        time_val = item['time']
        task_val = item['task']

        print(f"   Processing: [{time_val}] -> {task_val}")
        
        # EXECUTE CLI COMMAND
        # We wrap the task in quotes for the CLI arg
        cmd = ["python", "remble.py", "-nr", time_val, task_val]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
             print(f"   ✅ [OK] Wired in.")
        else:
             print(f"   ❌ [ERR] CLI Failed: {result.stderr}")

if __name__ == "__main__":
    run_autonomous_setup()