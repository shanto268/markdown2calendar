import os
from datetime import datetime, timedelta

from dotenv import load_dotenv
from langchain_community.llms import Ollama
# comment out the following import for your code to work
from shanto_utils import notify

from event import EventManager

# Load secrets from .secrets file
load_dotenv('.secrets')


def process_to_do_list_for_tmrw():
    """
    Process the to-do list for tomorrow.

    This function retrieves the to-do list for tomorrow from a markdown file and processes it to create events in a Google Calendar.

    Returns:
        bool: True if events were added to the calendar, False otherwise
    """
    tomorrow_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    markdown_file = f"/Users/shanto/zettelkasten/daily/{tomorrow_date}.md"

    if not os.path.exists(markdown_file):
        print(f"No markdown file for {tomorrow_date}")
        return

    llm = Ollama(model="llama3:8b-instruct-q5_0")
    calendar_id = os.getenv("GOOGLE_CALENDAR_ID")
    credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH")

    manager = EventManager(markdown_file, calendar_id, credentials_path, llm)
    manager.process_file(verbose=True)

    return manager.calendar_api.events_added


def process_to_do_list_for_today():
    """
    Process the to-do list for today.

    This function reads a markdown file for the current date and processes the tasks
    listed in the file. It uses the Ollama model for natural language processing,
    the Google Calendar API for adding events to a calendar, and the credentials.json
    file for authentication.

    Returns:
        bool: True if events were added to the calendar, False otherwise
    """
    today_date = (datetime.now()).strftime('%Y-%m-%d')
    markdown_file = f"/Users/shanto/zettelkasten/daily/{today_date}.md"

    if not os.path.exists(markdown_file):
        print(f"No markdown file for {today_date}")
        return

    llm = Ollama(model="llama3:8b-instruct-q5_0")
    calendar_id = os.getenv("GOOGLE_CALENDAR_ID")
    credentials_path = os.getenv(
        "GOOGLE_CREDENTIALS_PATH")  # absolute path to credentials.json

    manager = EventManager(markdown_file, calendar_id, credentials_path, llm)
    manager.process_file(verbose=True)

    return manager.calendar_api.events_added


if __name__ == "__main__":
    events_added = process_to_do_list_for_today()
    """
    try:
        events_added = process_to_do_list_for_today()
        if events_added:
            notify("To-Do List Processed", "Events added to Google Calendar")
        else:
            notify("To-Do List Processed",
                   "No events added to Google Calendar")
    except Exception as e:
        print(f"Error processing to-do list for today: {e}")
        notify(
            "To-Do List Processing Failed",
            "No time sensitive action items found in the to-do list for today")
    """
