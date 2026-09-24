#!/usr/bin/env python3
"""
Daily Tech & AI Briefing Agent
Curated for Rudransh Rastogi (IIM Rohtak - Finance & Tech)
"""

import argparse
import logging
import sys
from datetime import datetime
from config import settings
from src.fetcher import fetch_all_sources
from src.analyzer import analyze_and_synthesize
from src.formatter import render_briefing
from src.mailer import send_email, preview_in_browser
from src.scheduler import install_schedule, uninstall_schedule, check_status, run_foreground_loop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("NewsletterAgent")

def execute_briefing_pipeline(send_mail: bool = True, preview: bool = False):
    """Executes the full pipeline: Fetch -> Analyze -> Format -> Deliver/Preview."""
    print("\n" + "=" * 65)
    print("🚀 DAILY TECH & AI BRIEFING AGENT")
    print(f"👤 Curated for : {settings.RECIPIENT_NAME} ({settings.AFFILIATION})")
    print(f"📅 Date         : {datetime.now().strftime('%A, %B %d, %Y')}")
    print("=" * 65 + "\n")

    # Step 1: Fetch
    print("📡 [1/4] Aggregating latest stories from global tech & AI sources...")
    articles = fetch_all_sources()
    print(f"    ✓ Found {len(articles)} fresh articles from global feeds.")

    # Step 2: Analyze & Synthesize
    print("\n🧠 [2/4] Synthesizing executive briefing (Plain English + Finance/Tech)...")
    briefing_data = analyze_and_synthesize(articles)
    print(f"    ✓ Lead Story: {briefing_data.get('top_story', {}).get('headline', 'N/A')}")
    print(f"    ✓ Concept of the Day: {briefing_data.get('concept_of_the_day', {}).get('term', 'N/A')}")

    # Step 3: Format
    print("\n🎨 [3/4] Rendering responsive newsletter...")
    rendered = render_briefing(briefing_data)
    print(f"    ✓ Rendered HTML saved to: {rendered['filepath']}")

    # Step 4: Deliver or Preview
    print("\n📬 [4/4] Delivery & Output...")
    if preview:
        preview_in_browser(rendered["filepath"])
    elif send_mail:
        subject = f"⚡ Tech & AI Daily: {briefing_data.get('top_story', {}).get('headline', 'Global Intelligence')} | {datetime.now().strftime('%b %d')}"
        success = send_email(subject, rendered["html"], rendered["text"])
        if not success:
            # If email sending wasn't configured or failed, automatically open in browser so the user gets their briefing!
            print("💡 Tip: Opening briefing locally in your browser for immediate reading.")
            preview_in_browser(rendered["filepath"])

    print("\n✨ Done! Briefing process completed.\n")

def main():
    parser = argparse.ArgumentParser(
        description="Daily Tech & AI Briefing Agent for Rudransh Rastogi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py --preview              # Generate today's briefing & open in browser
  python run.py --now                  # Generate and send email immediately
  python run.py --install-schedule     # Setup automatic 10:00 AM daily macOS schedule
  python run.py --schedule-status      # Check status of daily schedule
  python run.py --uninstall-schedule   # Remove the daily schedule
        """
    )

    parser.add_argument("--now", action="store_true", help="Generate and send today's briefing immediately via email")
    parser.add_argument("--preview", action="store_true", help="Generate and open briefing in browser without sending email")
    parser.add_argument("--install-schedule", action="store_true", help="Register 10:00 AM daily briefing in macOS launchd")
    parser.add_argument("--uninstall-schedule", action="store_true", help="Unregister daily schedule from macOS launchd")
    parser.add_argument("--schedule-status", action="store_true", help="Check status of macOS launchd schedule")
    parser.add_argument("--schedule-loop", action="store_true", help="Run an in-process foreground loop for scheduling")

    args = parser.parse_args()

    if args.install_schedule:
        install_schedule()
    elif args.uninstall_schedule:
        uninstall_schedule()
    elif args.schedule_status:
        check_status()
    elif args.schedule_loop:
        run_foreground_loop()
    elif args.now:
        execute_briefing_pipeline(send_mail=True, preview=False)
    elif args.preview:
        execute_briefing_pipeline(send_mail=False, preview=True)
    else:
        # Default behavior when run with no arguments
        print("No specific action flag passed. Generating preview in browser...")
        execute_briefing_pipeline(send_mail=False, preview=True)

if __name__ == "__main__":
    main()
