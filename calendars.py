from datetime import datetime, timedelta

from google.oauth2 import service_account
from googleapiclient.discovery import build


class GoogleCalendarAPI:
    def __init__(self, credentials_path):
        self.credentials_path = credentials_path
        self.service = self.authenticate()
        self.events_added = False

    def authenticate(self):
        credentials = service_account.Credentials.from_service_account_file(
            self.credentials_path,
            scopes=["https://www.googleapis.com/auth/calendar"]
        )
        service = build('calendar', 'v3', credentials=credentials)
        return service

    def create_event(self, calendar_id, event):
        event = self.service.events().insert(calendarId=calendar_id, body=event.to_google_event()).execute()
        print(f"Event created: {event.get('htmlLink')}")
        self.events_added = True

    def delete_all_events_for_day(self, calendar_id, date):
        # Convert the date to the start and end of the day 
        start_of_day = datetime.combine(date, datetime.min.time()) + timedelta(minutes=1)
        end_of_day = datetime.combine(date, datetime.max.time()) - timedelta(minutes=1)
        
        start_of_day_iso = start_of_day.isoformat() + 'Z'
        end_of_day_iso = end_of_day.isoformat() + 'Z'

        # Get all events for the specified day
        events_result = self.service.events().list(
            calendarId=calendar_id,
            timeMin=start_of_day_iso,
            timeMax=end_of_day_iso,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        if not events:
            print("No events found for the specified day.")
            return

        # Delete each event
        for event in events:
            self.service.events().delete(calendarId=calendar_id, eventId=event['id']).execute()
            print(f"Deleted event: {event['summary']}")
