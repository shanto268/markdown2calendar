import json
import re
from datetime import datetime

from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate


class ActionItemExtractor:

    def __init__(self, llm, verbose=False):
        prompt_template = PromptTemplate(
            input_variables=["content"],
            template=
            ("You are an intelligent assistant. Your task is to extract time-sensitive action items "
             "from the following markdown content. "
             "{content}\n\n"
             "For each action item, provide a summary, start time, "
             "and end time if available. If the end time is not available, use the beginning of the next event as its end time or if it is more sensible allocate a more relevant and appropriate end time (include the `by` keyword in your response)"
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
                for item in action_items:
                    # Clean and format times
                    if 'start_time' in item:
                        item['start_time'] = self.format_time(
                            item['start_time'])
                    if 'end_time' in item:
                        item['end_time'] = self.format_time(item['end_time'])
                return action_items
            except json.JSONDecodeError:
                if self.verbose:
                    print("Failed to decode JSON response")
                return []
        else:
            if self.verbose:
                print("No JSON response found")
            return []

    def format_time(self, time_str):
        try:
            if "by" in time_str:
                time_str = time_str.replace('by ', '').strip()
            else:
                time_str = time_str.strip()
        except:
            pass

        try:
            time_str = time_str.strip()
            return datetime.strptime(time_str, '%I:%M %p').strftime('%H:%M')
        except ValueError:
            if self.verbose:
                print(f"Failed to parse time: {time_str}")
            try:
                return datetime.strptime(time_str, '%I %p').strftime('%H:%M')
            except ValueError:
                if self.verbose:
                    print(f"Failed to parse time again: {time_str}")
                return None
