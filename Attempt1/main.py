import os
import re
import argparse
import datetime
from collections import Counter
from flask import Flask, render_template
import threading

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

def generate_stats(commands):
    cmd_only = [cmd for ts, cmd in commands if cmd]
    total_commands = len(cmd_only)
    cmd_counts = Counter(cmd_only)
    most_common_cmds = cmd_counts.most_common()

    # Longest command
    longest_cmd = max(cmd_only, key=len)

    # Weirdest commands (used only once)
    weirdest_cmds = [cmd for cmd, count in cmd_counts.items() if count == 1]

    stats = {
        'total_commands': total_commands,
        'most_common_cmds': most_common_cmds,
        'longest_cmd': longest_cmd,
        'weirdest_cmds': weirdest_cmds,
    }

    # Additional stats if timestamps are available
    timestamps = [ts for ts, cmd in commands if ts]
    if timestamps:
        first_cmd_time = datetime.datetime.fromtimestamp(min(timestamps))
        last_cmd_time = datetime.datetime.fromtimestamp(max(timestamps))
        stats['first_cmd_time'] = first_cmd_time
        stats['last_cmd_time'] = last_cmd_time
    return stats

def print_stats(stats):
    print("🎉 **Most Used Commands:**")
    for cmd, count in stats['most_common_cmds'][:5]:
        print(f"- {cmd}: {count} times")
    print(f"\n🚀 **Longest Command Typed:**\n{stats['longest_cmd']}")
    print("\n🤪 **Weirdest Commands:**")
    for cmd in stats['weirdest_cmds'][:5]:
        print(f"- {cmd}")
    print(f"\n📊 **Total Commands Run During the Year:** {stats['total_commands']}")
    if 'first_cmd_time' in stats and 'last_cmd_time' in stats:
        print(f"\n📅 **Your bash adventure started on** {stats['first_cmd_time'].strftime('%Y-%m-%d')} **and ended on** {stats['last_cmd_time'].strftime('%Y-%m-%d')}")
    # Add more stats as needed

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

    app = create_app(stats)
    threading.Thread(target=start_server, args=(app,)).start()

if __name__ == '__main__':
    main()