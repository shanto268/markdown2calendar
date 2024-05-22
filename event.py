from datetime import datetime, timedelta

from calendars import GoogleCalendarAPI
from extractor import ActionItemExtractor
from reader import MarkdownReader


class Event:
    def __init__(self, summary, start_time=None, end_time=None):
        self.summary = summary
        self.start_time = start_time
        self.end_time = end_time or (start_time + timedelta(hours=1)) if start_time else None

    def to_google_event(self):
        event = {
            'summary': self.summary,
            'start': {'dateTime': self.start_time.isoformat(), 'timeZone': 'America/Los_Angeles'} if self.start_time else None,
            'end': {'dateTime': self.end_time.isoformat(), 'timeZone': 'America/Los_Angeles'} if self.end_time else None
        }
        if not self.start_time:
            event.pop('start')
            event.pop('end')
        return event

class EventManager:
    def __init__(self, file_path, calendar_id, credentials_path, llm=None):
        self.markdown_reader = MarkdownReader(file_path)
        self.extractor = ActionItemExtractor(llm)
        self.calendar_api = GoogleCalendarAPI(credentials_path)
        self.calendar_id = calendar_id
        self.file_path = file_path

    def process_file(self, verbose=False):
        content = self.markdown_reader.parse_file(self.file_path)
        action_items = self.extractor.extract_action_items(content)
        
        if verbose:
            print(f"Content extracted: {content}")
            print(f"Action items extracted: {action_items}")
        
        for i, item in enumerate(action_items):
            summary = item.get('summary')
            start_time_str = item.get('start_time')
            start_time = self.parse_time(start_time_str) if start_time_str else None
            end_time_str = item.get('end_time')
            end_time = self.parse_time(end_time_str) if end_time_str else None

            # Set end time as the start time of the next event if not provided
            if not end_time and i < len(action_items) - 1:
                next_start_time_str = action_items[i + 1].get('start_time')
                end_time = self.parse_time(next_start_time_str) if next_start_time_str else None

            event = Event(summary, start_time, end_time)
            self.calendar_api.create_event(self.calendar_id, event)

    def parse_time(self, time_str):
        now = datetime.now()
        try:
            return datetime.strptime(f"{now.year}-{now.month}-{now.day} {time_str}", "%Y-%m-%d %H:%M")
        except ValueError:
            print(f"Failed to parse time: {time_str}")
            return None
