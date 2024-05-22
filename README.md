# Zettelkasten To Do Lists to Google Calendar Events

I use the [Zettelkasten]() note-taking philosophy (and [neovim plugin](https://github.com/Furkanzmc/zettelkasten.nvim)) to plan to make daily to-do lists. I wanted to use my local llama3 model to extract time-sensitive action items from my daily to-do lists and create Google Calendar events for them. This project automates that process. It runs as a background service on macOS, using `launchd` to schedule daily execution at 8 PM PDT.

## Features

- **Markdown Parsing**: Reads daily tasks from markdown files.
- **Action Item Extraction**: Uses a local LLM (e.g., Ollama) to extract time-sensitive action items.
- **Google Calendar Integration**: Creates events in Google Calendar based on extracted action items.
- **Scheduled Execution**: Runs as a `launchd` service on macOS, executing the script daily at 8 PM PDT.

## Requirements

- Python 3.x
- `google-auth`, `google-api-python-client`
- `dotenv`
- `langchain-community`
- A Google Cloud project with the Calendar API enabled and a service account with appropriate permissions.

## Setup

### 1. Clone the Repository

```sh
git clone https://github.com/shanto268/zettelkasten2calendar.git
cd zettelkasten2calendar
```

### 2. Install Dependencies

```sh
pip install -r requirements.txt
```

### 3. Configure Google Calendar API

- Create a Google Cloud project and enable the Calendar API.
- Create a service account and download the JSON credentials file.
- Share your calendar with the service account email.

### 4. Create `.secrets` File

Create a `.secrets` file in the project root directory with the following content:

```dotenv
GOOGLE_CALENDAR_ID=your_calendar_id@group.calendar.google.com
GOOGLE_CREDENTIALS_PATH=/path/to/your/credentials.json
```

### 5. Configure `launchd`

Create a plist file for `launchd` to schedule the Python script. Save it as `com.yourusername.zettelkasten_to_calendar.plist` in `~/Library/LaunchAgents/`.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
    <dict>
        <key>Label</key>
        <string>com.yourusername.zettelkasten_to_calendar</string>
        <key>ProgramArguments</key>
        <array>
            <string>/usr/local/bin/python3</string> <!-- Path to your Python interpreter -->
            <string>/path/to/zettelkasten_to_calendar.py</string> <!-- Path to your Python script -->
        </array>
        <key>StartCalendarInterval</key>
        <dict>
            <key>Hour</key>
            <integer>00</integer>
            <key>Minute</key>
            <integer>10</integer>
        </dict>
        <key>StandardOutPath</key>
        <string>/tmp/zettelkasten_to_calendar.log</string>
        <key>StandardErrorPath</key>
        <string>/tmp/zettelkasten_to_calendar.err</string>
        <key>RunAtLoad</key>
        <true/>
    </dict>
</plist>
```

Load the plist file into `launchd`:

```sh
launchctl load ~/Library/LaunchAgents/com.yourusername.zettelkasten_to_calendar.plist
```

### 6. Verify the Job

Ensure the job is scheduled:

```sh
launchctl list | grep com.yourusername.zettelkasten_to_calendar
```

## Usage

### Running the Script

The script will automatically run every day at 12:10 AM PDT, check for that day's markdown file, and create events in Google Calendar based on the extracted action items.

### Manual Execution

You can also run the script manually:

```sh
python main.py
```

## Troubleshooting

- Ensure the paths in your plist file are correct.
- Check `/tmp/zettelkasten_to_calendar.log` and `/tmp/zettelkasten_to_calendar.err` for logs and errors.

## License

This project is licensed under the MIT License.
