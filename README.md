# Terminal-Wrapped

*Inspired from Spotify Wrapped*

🚀 Terminal-Wrapped is a Python tool that generates insightful statistics and visualizations from your terminal command history. It supports Bash, Zsh, and Fish shells, and provides a web interface to display your command usage patterns in a fun and informative way.

## 🌟 Features

- **Multi-Shell Support**: Automatically detects and parses history files from Bash, Zsh, and Fish shells.
- **Usage Statistics**:
    - Most used commands.
    - Longest command typed.
    - Weirdest commands (commands used only once).
    - Total commands run.
    - Command journey (start and end dates).
    - Most active day.
    - Number of commands run on weekends.
- **Visualizations**:
    - Circle bar chart showing commands per month.
    - Circle bar chart showing peak productivity hours.
- **Local Web Interface**: Starts a Flask web server to display statistics and charts in a user-friendly interface.

## 🏃 Quickstart

To quickly set up and run Terminal-Wrapped, you can use the following command:

```bash
curl -s https://raw.githubusercontent.com/victor-gurbani/terminal-wrapped/main/quickstart.sh | bash
```

## 🚀 Installation

1. **Clone the repository**:

     ```bash
     git clone https://github.com/victor-gurbani/terminal-wrapped.git
     cd terminal-wrapped
     ```

2. **Create a virtual environment (optional but recommended)**:

     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

3. **Install the required dependencies**:

     ```bash
     pip install -r requirements.txt
     ```

## 📈 Usage

Run the main.py script to generate your terminal usage statistics:

```bash
python main.py
```

### Options

- **Specify Shell**: By default, the script attempts to detect your current shell. To specify a shell manually, use the `--shell` option:

    ```bash
    python main.py --shell bash
    ```

    Supported shells are `bash`, `zsh`, and `fish`.

- **Specify History File**: To use a custom history file, use the `--history` option:

    ```bash
    python main.py --history /path/to/history_file
    ```

## 🌐 Viewing the Results

The script outputs statistics to the console and starts a Flask web server at `http://0.0.0.0:8081`. 

Open your web browser and navigate to `http://localhost:8081` to view your terminal usage wrapped in an interactive web interface with charts.

> [!NOTE]
>
> To ensure time-specific statistics are shown, check that the following are enabled for your shell:
>
> - For Zsh - [EXTENDED_HISTORY](https://zsh.sourceforge.io/Doc/Release/Options.html#History) (oh-my-zsh has it enabled by default)
> - For Bash - [HISTTIMEFORMAT](https://www.gnu.org/software/bash/manual/bash.html#index-HISTTIMEFORMAT)
>
> **Commands executed before configuring the option won't be recorded with a timestamp, affecting the stats**.


## 📋 Dependencies

- Python 3.x
- Flask
- Collections (built-in)
- Datetime (built-in)
- Threading (built-in)
- Argparse (built-in)
- JSON (built-in)
- Regular Expressions (built-in)
- Chart.js (for rendering charts in the web interface)

## 📁 Project Structure

```
terminal-wrapped/
├── main.py
├── README.md
└── templates/
        └── index.html
```

- main.py: The main script that parses the history file, generates statistics, and starts the web server.
- index.html: The HTML template for the web interface.

## 🤝 Contributing

Contributions are welcome! Feel free to submit issues or pull requests to improve the project.

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=victor-gurbani/terminal-wrapped&type=Date)](https://star-history.com/#victor-gurbani/terminal-wrapped&Date)

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.
