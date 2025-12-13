import os
import re
import json
import threading
import argparse
from datetime import datetime
from collections import Counter, defaultdict
from flask import Flask, render_template

def detect_history_file(shell=None):
    history_file = ""
    shell = shell or os.path.basename(os.getenv('SHELL', ''))
    home = os.path.expanduser('~')

    if shell == "fish":
        fish_history = os.path.join(home, '.local', 'share', 'fish', 'fish_history')
        if os.path.isfile(fish_history):
            history_file = fish_history
    elif shell == "zsh":
        zsh_history = os.getenv('ZDOTDIR', home)
        zsh_history = os.path.join(zsh_history, '.zsh_history')
        if os.path.isfile(zsh_history):
            history_file = zsh_history
    elif shell == "bash":
        bash_history = os.path.join(home, '.bash_history')
        if os.path.isfile(bash_history):
            history_file = bash_history
    else:
        print(f"Your shell '{shell}' is not supported.")
        exit(1)

    if not history_file:
        print(f"The history file for shell '{shell}' was not found.")
        exit(1)
    return history_file

def parse_history(history_file, shell):
    commands = []
    if shell == "bash":
        commands = parse_bash_history(history_file)
    elif shell == "zsh":
        commands = parse_zsh_history(history_file)
    elif shell == "fish":
        commands = parse_fish_history(history_file)
    else:
        print(f"Unsupported shell: {shell}")
        exit(1)
    return commands

def parse_bash_history(file_path):
    with open(file_path, 'r', errors='ignore') as f:
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
        elif line and not line.startswith('#'):
            commands.append((None, line))
        i += 1
    return commands

def parse_zsh_history(file_path):
    regex = re.compile(r': (\d+):\d+;(.*)')
    commands = []
    with open(file_path, 'r', errors='ignore') as f:
        for line in f:
            match = regex.match(line)
            if match:
                ts = int(match.group(1))
                cmd = match.group(2).strip()
                commands.append((ts, cmd))
    return commands

def parse_fish_history(file_path):
    regex_cmd = re.compile(r'- cmd: (.*)')
    regex_when = re.compile(r'  when: (\d+)')
    commands = []
    with open(file_path, 'r', errors='ignore') as f:
        cmd = None
        ts = None
        for line in f:
            line = line.rstrip()
            cmd_match = regex_cmd.match(line)
            if cmd_match:
                cmd = cmd_match.group(1)
            ts_match = regex_when.match(line)
            if ts_match:
                ts = int(ts_match.group(1))
            if cmd and ts:
                commands.append((ts, cmd))
                cmd = None
                ts = None
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

    # New Statistics
    
    # 1. Sudo Usage
    sudo_count = sum(1 for cmd in cmd_only if cmd.strip().startswith('sudo'))
    sudo_percentage = (sudo_count / total_commands * 100) if total_commands > 0 else 0

    # 2. Pipe Master
    pipe_master_cmd = max(cmd_only, key=lambda x: x.count('|')) if cmd_only else ""
    pipe_count = pipe_master_cmd.count('|') if pipe_master_cmd else 0

    # 3. Git Addict
    git_count = sum(1 for cmd in cmd_only if cmd.strip().startswith('git'))
    git_percentage = (git_count / total_commands * 100) if total_commands > 0 else 0

    # 4. Night Owl vs Early Bird
    night_owl_cmds = sum(hours[0:6])
    early_bird_cmds = sum(hours[6:12])
    chronotype = "Night Owl 🦉" if night_owl_cmds > early_bird_cmds else "Early Bird 🌅"

    # 5. Directory Hopper (Approximate via 'cd')
    cd_cmds = [cmd.split()[1] for cmd in cmd_only if cmd.strip().startswith('cd ') and len(cmd.split()) > 1]
    top_directories = Counter(cd_cmds).most_common(3)

    # 6. Vocabulary Size
    vocab_size = len(unique_commands)

    # 7. The "Oops" Moment
    rm_count = sum(1 for cmd in cmd_only if cmd.strip().startswith('rm'))

    # 8. Editor Wars
    editors = ['vim', 'vi', 'nano', 'code', 'emacs', 'nvim']
    editor_counts = {ed: 0 for ed in editors}
    for cmd in cmd_only:
        first_word = cmd.split()[0] if cmd.split() else ""
        if first_word in editors:
            editor_counts[first_word] += 1
    favorite_editor = max(editor_counts, key=editor_counts.get) if any(editor_counts.values()) else "None"

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
        'sudo_percentage': round(sudo_percentage, 2),
        'pipe_master_cmd': pipe_master_cmd,
        'pipe_count': pipe_count,
        'git_percentage': round(git_percentage, 2),
        'chronotype': chronotype,
        'top_directories': top_directories,
        'vocab_size': vocab_size,
        'rm_count': rm_count,
        'editor_counts': editor_counts,
        'favorite_editor': favorite_editor
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
    print(f"\n📊 **Total Commands Run:** {stats['total_commands']}")
    if 'first_cmd_time' in stats and 'last_cmd_time' in stats:
        print(f"\n📅 **Your bash adventure started on** {stats['first_cmd_time'].strftime('%Y-%m-%d')} **to** {stats['last_cmd_time'].strftime('%Y-%m-%d')}")
    print(f"\n📈 **Most Active Day:** {stats['most_active_day']}")
    print(f"\n🗓️ **Weekend Commands:** {stats['weekend_commands']} commands run on weekends")

def create_app(stats):
    app = Flask(__name__)

    @app.route('/')
    def index():
        return render_template('index.html', stats=stats)

    @app.route('/bash_wrapped_data.json')
    def bash_wrapped_data():
        with open('bash_wrapped_data.json', 'r') as f:
            data = json.load(f)
        return data
    
    return app

def start_server(app):
    app.run(host='0.0.0.0', port=8081)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--shell', choices=['bash', 'zsh', 'fish'], help='Specify the shell')
    parser.add_argument('--history', help='Path to history file')
    args = parser.parse_args()

    shell = args.shell or os.path.basename(os.getenv('SHELL', ''))
    history_file = args.history or detect_history_file(shell)

    commands = parse_history(history_file, shell)
    stats = generate_stats(commands)
    print_stats(stats)

    # Save data to JSON for the web application
    with open('bash_wrapped_data.json', 'w') as f:
        json.dump(stats, f, default=str)

    app = create_app(stats)
    threading.Thread(target=start_server, args=(app,)).start()

if __name__ == '__main__':
    main()