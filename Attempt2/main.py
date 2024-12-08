import os
import re
import json
from datetime import datetime
from collections import Counter, defaultdict

def parse_bash_history(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    commands = []
    timestamps = []
    regex = re.compile(r'^#(\d+)$')

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        timestamp_match = regex.match(line)
        if timestamp_match and i + 1 < len(lines):
            ts = int(timestamp_match.group(1))
            i += 1
            cmd = lines[i].strip()
            commands.append((ts, cmd))
        else:
            commands.append((None, line))
        i += 1
    return commands

history_file = os.path.expanduser("~/.bash_history")
parsed_commands = parse_bash_history(history_file)
commands = [cmd for ts, cmd in parsed_commands]
timestamps = [ts for ts, cmd in parsed_commands]

command_counts = Counter()
longest_command = ""
unique_commands = set()
total_commands = len(commands)
first_command = commands[0] if commands else ""
last_command = commands[-1] if commands else ""
command_streaks = []  # List of (start_time, end_time, length)
idle_periods = []  # List of (start_time, end_time, duration)

prev_time = None
streak_start = None
streak_count = 0
idle_start = None

hours = [0] * 24  # For peak productivity hours
days = defaultdict(int)  # For most active day
weekend_commands = 0
late_night_commands = 0  # After 2 AM
early_morning_commands = 0  # Before 6 AM

for cmd, ts in zip(commands, timestamps):
    command_name = cmd.split()[0] if cmd else ""
    command_counts[command_name] += 1
    unique_commands.add(command_name)
    if len(cmd) > len(longest_command):
        longest_command = cmd
    if ts:
        dt = datetime.fromtimestamp(ts)
        hours[dt.hour] += 1
        day_str = dt.strftime('%Y-%m-%d')
        days[day_str] += 1
        if dt.weekday() >= 5:
            weekend_commands += 1
        if dt.hour >= 2 and dt.hour < 6:
            late_night_commands += 1
        if dt.hour >= 0 and dt.hour < 6:
            early_morning_commands += 1
        if prev_time:
            if ts - prev_time < 300:
                # Continuing streak
                if streak_start is None:
                    streak_start = prev_time
                streak_count += 1
            else:
                # Streak ended
                if streak_start:
                    command_streaks.append((streak_start, prev_time, streak_count))
                streak_start = None
                streak_count = 0
                # Idle period
                idle_periods.append((prev_time, ts, ts - prev_time))
        prev_time = ts

# Convert data to JSON for JavaScript
data = {
    'command_counts': command_counts.most_common(10),
    'longest_command': longest_command,
    'unique_commands': list(unique_commands),
    'total_commands': total_commands,
    'first_command': first_command,
    'last_command': last_command,
    'hours': hours,
    'most_active_day': max(days, key=days.get) if days else '',
    'weekend_commands': weekend_commands,
    'late_night_commands': late_night_commands,
    'early_morning_commands': early_morning_commands,
}

with open('bash_wrapped_data.json', 'w') as f:
    json.dump(data, f)