import json
import re
from datetime import datetime, timedelta

from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate


class ActionItemExtractor:

    def __init__(self, llm, verbose=True):
        prompt_template = PromptTemplate(
            input_variables=["content"],
            template=
            ("You are an intelligent assistant. Your task is to extract time-sensitive action items "
             "from the following markdown content. "
             "{content}\n\n"
             "For each action item, provide a summary, start time, "
             "and end time if available. If the end time is not available, use the beginning of the next event as its end time or if it is more sensible allocate a more relevant and appropriate end time. Ensure that the times are in the format HH:MM (24-hour clock) and that the start time is before the end time."
             "If a time is not specified, omit the start and end time."
             "\n\nRespond in valid JSON format with a key 'action_items', each having 'summary', 'start_time', and 'end_time' (if applicable)."
             "Absolutely do not include any additional text or comments in the response (before or after the JSON). If you do so you will be fired"
             ))
        self.chain = LLMChain(llm=llm, prompt=prompt_template)
        self.verbose = verbose

    def extract_action_items(self, content):
        response = self.chain.run({"content": content})
        if self.verbose:
            print(f"Raw response: {response}\n")
        return self.process_action_items(response)

    def process_action_items(self, response):
        # Extract the JSON part from the response
        match = re.search(r'\{.*\}', response, re.DOTALL)
        if match:
            json_str = match.group(0)
            try:
                response_json = json.loads(json_str)
                action_items = response_json.get('action_items', [])
                action_items = self.clean_and_format_times(action_items)
                action_items = self.fix_missing_end_times(action_items)
                action_items = self.filter_items_with_no_times(action_items)
                return action_items
            except json.JSONDecodeError:
                if self.verbose:
                    print("Failed to decode JSON response")
                return []
        else:
            if self.verbose:
                print("No JSON response found")
            return []

    def clean_and_format_times(self, action_items):
        for item in action_items:
            if 'start_time' in item:
                item['start_time'] = self.format_time(item['start_time'])
            if 'end_time' in item:
                item['end_time'] = self.format_time(item['end_time'])
        return action_items

    def format_time(self, time_str):
        if not time_str or time_str.strip() == "":
            return None
        try:
            return datetime.strptime(time_str.strip(),
                                     '%I:%M %p').strftime('%H:%M')
        except ValueError:
            try:
                return datetime.strptime(time_str.strip(),
                                         '%I %p').strftime('%H:%M')
            except ValueError:
                if self.verbose:
                    print(f"Failed to parse time: {time_str}")
                return None

    def fix_missing_end_times(self, action_items):
        for i in range(len(action_items) - 1):
            current_item = action_items[i]
            next_item = action_items[i + 1]

            if current_item.get(
                    'start_time') and not current_item.get('end_time'):
                if next_item.get('start_time'):
                    end_time = datetime.strptime(next_item['start_time'],
                                                 '%H:%M')
                    current_item['end_time'] = end_time.strftime('%H:%M')
                else:
                    current_item['end_time'] = (
                        datetime.strptime(current_item['start_time'], '%H:%M')
                        + timedelta(hours=1)).strftime('%H:%M')

        # Handle the last item
        last_item = action_items[-1]
        if last_item.get('start_time') and not last_item.get('end_time'):
            last_item['end_time'] = (
                datetime.strptime(last_item['start_time'], '%H:%M') +
                timedelta(hours=1)).strftime('%H:%M')

        return action_items

    def filter_items_with_no_times(self, action_items):
        return [item for item in action_items if item.get('start_time')]
