import os
import sys
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from config import settings

PLIST_LABEL = "com.rudransh.dailybriefing"
LAUNCH_AGENTS_DIR = Path.home() / "Library" / "LaunchAgents"
PLIST_PATH = LAUNCH_AGENTS_DIR / f"{PLIST_LABEL}.plist"

def generate_plist_content(python_path: str, script_path: str, hour: int = 10, minute: int = 0) -> str:
    """Generate macOS launchd property list (plist) XML."""
    log_dir = settings.BASE_DIR / "briefings"
    log_dir.mkdir(parents=True, exist_ok=True)
    stdout_log = log_dir / "scheduler_stdout.log"
    stderr_log = log_dir / "scheduler_stderr.log"

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{PLIST_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>{script_path}</string>
        <string>--now</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{settings.BASE_DIR}</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>{hour}</integer>
        <key>Minute</key>
        <integer>{minute}</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>{stdout_log}</string>
    <key>StandardErrorPath</key>
    <string>{stderr_log}</string>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
"""

def install_schedule() -> bool:
    """Installs the macOS launchd job for 10:00 AM daily."""
    try:
        LAUNCH_AGENTS_DIR.mkdir(parents=True, exist_ok=True)
        python_path = sys.executable
        script_path = str(settings.BASE_DIR / "run.py")
        
        # Parse delivery hour and minute
        parts = settings.DAILY_DELIVERY_TIME.split(":")
        hour = int(parts[0]) if len(parts) > 0 else 10
        minute = int(parts[1]) if len(parts) > 1 else 0

        plist_content = generate_plist_content(python_path, script_path, hour, minute)
        with open(PLIST_PATH, "w", encoding="utf-8") as f:
            f.write(plist_content)

        # Unload existing if any, then load new
        subprocess.run(["launchctl", "unload", str(PLIST_PATH)], capture_output=True)
        res = subprocess.run(["launchctl", "load", str(PLIST_PATH)], capture_output=True, text=True)
        
        if res.returncode == 0:
            print(f"\n✅ Successfully registered daily schedule with macOS launchd!")
            print(f"⏰ Daily trigger time : {settings.DAILY_DELIVERY_TIME} AM/PM")
            print(f"📄 Plist configuration: {PLIST_PATH}")
            print(f"To monitor logs: tail -f {settings.BASE_DIR}/briefings/scheduler_stdout.log\n")
            return True
        else:
            print(f"⚠️ launchctl load reported: {res.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error setting up macOS schedule: {e}")
        return False

def uninstall_schedule() -> bool:
    """Unloads and deletes the macOS launchd job."""
    if not PLIST_PATH.exists():
        print(f"ℹ️ No active schedule found at {PLIST_PATH}")
        return True

    try:
        subprocess.run(["launchctl", "unload", str(PLIST_PATH)], capture_output=True)
        PLIST_PATH.unlink(missing_ok=True)
        print(f"✅ Successfully removed schedule from macOS launchd.")
        return True
    except Exception as e:
        print(f"❌ Error uninstalling schedule: {e}")
        return False

def check_status():
    """Checks the status of the macOS launchd schedule."""
    if not PLIST_PATH.exists():
        print(f"\n❌ macOS launchd schedule is NOT installed.")
        print("Run `python run.py --install-schedule` to activate it.\n")
        return

    res = subprocess.run(["launchctl", "list"], capture_output=True, text=True)
    is_active = PLIST_LABEL in res.stdout
    print(f"\n📋 Schedule Status:")
    print(f"   Plist File : {PLIST_PATH} (Present)")
    print(f"   Loaded in launchd: {'✅ ACTIVE' if is_active else '⚠️ Loaded file exists but not registered'}")
    print(f"   Delivery Time    : Every day at {settings.DAILY_DELIVERY_TIME}\n")

def run_foreground_loop():
    """Fallback foreground loop for systems or sessions that want in-process scheduling."""
    print(f"\n⏳ Starting in-process scheduler loop (Target: {settings.DAILY_DELIVERY_TIME} daily)...")
    print("Press Ctrl+C to stop.")

    parts = settings.DAILY_DELIVERY_TIME.split(":")
    target_hour = int(parts[0]) if len(parts) > 0 else 10
    target_minute = int(parts[1]) if len(parts) > 1 else 0

    while True:
        now = datetime.now()
        target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        if now >= target_time:
            target_time += timedelta(days=1)

        wait_seconds = (target_time - now).total_seconds()
        print(f"Next briefing scheduled for: {target_time.strftime('%Y-%m-%d %H:%M:%S')} (in {int(wait_seconds//3600)}h {int((wait_seconds%3600)//60)}m)")

        # Sleep in chunks to handle interruption
        while wait_seconds > 0:
            sleep_step = min(wait_seconds, 60)
            time.sleep(sleep_step)
            wait_seconds -= sleep_step

        print(f"\n⏰ Triggering daily briefing at {datetime.now().strftime('%H:%M:%S')}...")
        from run import execute_briefing_pipeline
        execute_briefing_pipeline(send_mail=True, preview=False)
