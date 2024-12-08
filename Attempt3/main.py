import os
import re
import json
import threading
import argparse
from datetime import datetime
from collections import Counter, defaultdict
from flask import Flask, render_template

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
    cmd_only = [cmd for ts, cmd in commands if cmd]
    total_commands = len(cmd_only)
    cmd_counts = Counter(cmd_only)
    most_common_cmds = cmd_counts.most_common(10)

    # Longest command
    longest_cmd = max(cmd_only, key=len) if cmd_only else ""

    # Weirdest commands (used only once)
    weirdest_cmds = [cmd for cmd, count in cmd_counts.items() if count == 1][:5]

    unique_commands = set(cmd_only)

    # Time-based statistics
    timestamps = [ts for ts, cmd in commands if ts]
    hours = [0] * 24
    days = defaultdict(int)
    months = [0] * 12
    weekend_commands = 0

    for ts in timestamps:
        dt = datetime.fromtimestamp(ts)
        hours[dt.hour] += 1
        days[dt.strftime('%Y-%m-%d')] += 1
        months[dt.month - 1] += 1
        if dt.weekday() >= 5:
            weekend_commands += 1

    most_active_day = max(days, key=days.get) if days else ""

    stats = {
        'total_commands': total_commands,
        'most_common_cmds': most_common_cmds,
        'longest_cmd': longest_cmd,
        'weirdest_cmds': weirdest_cmds,
        'unique_commands': list(unique_commands),
        'first_command': cmd_only[0] if cmd_only else "",
        'last_command': cmd_only[-1] if cmd_only else "",
        'hours': hours,
        'most_active_day': most_active_day,
        'weekend_commands': weekend_commands,
        'months': months,
    }

    # Additional stats if timestamps are available
    if timestamps:
        stats['first_cmd_time'] = datetime.fromtimestamp(min(timestamps))
        stats['last_cmd_time'] = datetime.fromtimestamp(max(timestamps))

    return stats

def print_stats(stats):
    print("🎉 **Most Used Commands:**")
    for cmd, count in stats['most_common_cmds']:
        print(f"- {cmd}: {count} times")
    print(f"\n🚀 **Longest Command Typed:**\n{stats['longest_cmd']}")
    print("\n🤪 **Weirdest Commands:**")
    for cmd in stats['weirdest_cmds']:
        print(f"- {cmd}")
    print(f"\n📊 **Total Commands Run During the Year:** {stats['total_commands']}")
    if 'first_cmd_time' in stats and 'last_cmd_time' in stats:
        print(f"\n📅 **Your bash adventure started on** {stats['first_cmd_time'].strftime('%Y-%m-%d')} **and ended on** {stats['last_cmd_time'].strftime('%Y-%m-%d')}")
    print(f"\n📈 **Most Active Day:** {stats['most_active_day']}")
    print(f"\n🗓️ **Weekend Commands:** {stats['weekend_commands']} commands run on weekends")

def create_app(stats):
    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template('index.html', stats=stats)

    return app

def start_server(app):
    app.run(host='0.0.0.0', port=8081)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--history', default=os.path.expanduser('~/.bash_history'), help='Path to bash history file')
    args = parser.parse_args()

    commands = parse_bash_history(args.history)
    stats = generate_stats(commands)
    print_stats(stats)

    # Save data to JSON for the web application
    with open('bash_wrapped_data.json', 'w') as f:
        json.dump(stats, f, default=str)

    app = create_app(stats)
    threading.Thread(target=start_server, args=(app,)).start()

if __name__ == '__main__':
    main()