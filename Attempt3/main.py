import os
import re
import json
from datetime import datetime
from collections import Counter, defaultdict
from flask import Flask, render_template
import threading

def parse_bash_history(file_path):
    with open(file_path, 'r') as f:
        lines = f.readlines()

    commands = []
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

def generate_stats(commands):
    command_counts = Counter()
    longest_command = ""
    unique_commands = set()
    total_commands = len(commands)
    first_command = commands[0][1] if commands else ""
    last_command = commands[-1][1] if commands else ""

    command_streaks = []
    idle_periods = []
    prev_time = None
    streak_start = None
    streak_count = 0

    hours = [0] * 24
    days = defaultdict(int)
    weekend_commands = 0
    late_night_commands = 0
    early_morning_commands = 0

    for ts, cmd in commands:
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
            if 2 <= dt.hour < 6:
                late_night_commands += 1
            if 0 <= dt.hour < 6:
                early_morning_commands += 1

            if prev_time:
                if ts - prev_time < 300:
                    if streak_start is None:
                        streak_start = prev_time
                    streak_count += 1
                else:
                    if streak_start:
                        command_streaks.append((streak_start, prev_time, streak_count))
                    streak_start = None
                    streak_count = 0
                    idle_periods.append((prev_time, ts, ts - prev_time))
            prev_time = ts

    stats = {
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
        'command_streaks': command_streaks,
        'idle_periods': idle_periods,
    }
    return stats

def print_stats(stats):
    print("🎉 Most Used Commands:")
    for cmd, count in stats['command_counts']:
        print(f"- {cmd}: {count} times")
    print(f"\n🚀 Longest Command Typed:\n{stats['longest_command']}")
    print(f"\n📊 Total Commands Run: {stats['total_commands']}")
    print(f"\nFirst Command: {stats['first_command']}")
    print(f"Last Command: {stats['last_command']}")
    print(f"\nMost Active Day: {stats['most_active_day']}")
    print(f"Weekend Commands: {stats['weekend_commands']}")
    print(f"Late Night Commands (2AM-6AM): {stats['late_night_commands']}")
    print(f"Early Morning Commands (0AM-6AM): {stats['early_morning_commands']}")

def create_app():
    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/data')
    def data_route():
        with open('bash_wrapped_data.json') as f:
            data = json.load(f)
        return data

    return app

def start_server(app):
    app.run(host='0.0.0.0', port=8081)

def main():
    history_file = os.path.expanduser('~/.bash_history')
    commands = parse_bash_history(history_file)
    stats = generate_stats(commands)
    print_stats(stats)

    with open('bash_wrapped_data.json', 'w') as f:
        json.dump(stats, f)

    app = create_app()
    threading.Thread(target=start_server, args=(app,)).start()

if __name__ == '__main__':
    main()