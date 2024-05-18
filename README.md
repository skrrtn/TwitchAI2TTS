# 🎤 SKRRTN's AI TTS Bot Thingy

Welcome to SKRRTN's AI Text-to-Speech (TTS) Bot! This project integrates a Twitch chat bot with OpenAI's GPT-3 API and a text-to-speech engine to provide real-time responses to questions asked in a Twitch chat. The bot reads out questions and answers, enhancing the interactive experience on your Twitch stream.

## 🌟 Features

- Connects to a Twitch chat and listens for questions.
- Uses OpenAI's GPT-3 to generate answers to the questions.
- Uses `pyttsx3` to convert text answers to speech.
- Displays questions and answers in a GUI.
- Speaks the answers using a TTS engine.

## 🛠️ Installation

### Prerequisites

- Python 3.x
- An OpenAI API key
- Twitch IRC credentials

### Steps

1. **Clone the repository:**
    ```sh
    git clone https://github.com/yourusername/your-repo-name.git
    cd your-repo-name
    ```

2. **Install the required Python packages:**
    ```sh
    pip install -r requirements.txt
    ```

3. **Create a `config.json` file in the root directory of the project:**
    ```json
    {
        "openai_api_key": "your_openai_api_key",
        "irc_server": "irc.chat.twitch.tv",
        "irc_port": 6667,
        "irc_nickname": "your_twitch_nickname",
        "irc_token": "your_twitch_oauth_token",
        "irc_channel": "#your_twitch_channel",
        "model": "gpt-3.5-turbo",
        "prompt": "You are a helpful assistant."
    }
    ```

## 🛠️ Configuration

Ensure your `config.json` file contains the correct credentials and settings. Replace the placeholder values with your actual API keys and Twitch credentials.

## 🚀 Usage

1. **Run the bot:**
    ```sh
    python main.py
    ```

2. **Interact with the bot on your Twitch channel:**
    - To ask a question, type `!q Your question here`.

## 🧩 Code Overview

### Importing Libraries

```python
import socket
import time
import queue
import threading
import openai
import tkinter as tk
import json
import os
import pyttsx3  # Import pyttsx3
from tkinter import font as tkfont
from openai import OpenAI
```

These are the necessary libraries for socket communication, threading, queue management, GUI creation, TTS, and OpenAI API integration.

### Loading Configuration

```python
script_dir = os.path.dirname(os.path.realpath(__file__))
config_file = os.path.join(script_dir, 'config.json')
with open(config_file) as f:
    config = json.load(f)
```

This section loads the configuration settings from the `config.json` file.

### Initializing OpenAI and TTS Engine

```python
openai.api_key = config['openai_api_key']
server = config['irc_server']
port = config['irc_port']
nickname = config['irc_nickname']
token = config['irc_token']
channel = config['irc_channel']
```

Sets the API key and Twitch IRC credentials.

### Message Queue and Question-Answer List

```python
message_queue = queue.Queue()
qa_list = []
```

A queue for managing incoming messages and a list to store questions and answers.

### Text-to-Speech Function

```python
def speak_message(user, question, response):
    message = f"{user} asks {question}. {response}"
    engine = pyttsx3.init()
    rate = engine.getProperty('rate')
    volume = engine.getProperty('volume')
    engine.setProperty('rate', 180)
    engine.setProperty('volume', 1)
    engine.say(message)
    engine.runAndWait()
```

This function converts the response to speech using `pyttsx3`.

### Processing Questions

```python
def process_question(question):
    status_message.set("📖 Reading response...")
    client = OpenAI(api_key=config['openai_api_key'])
    response = client.chat.completions.create(
        model=config['model'],
        messages=[
            {"role": "system", "content": config['prompt']},
            {"role": "user", "content": question},
        ]
    )
    generated_text = response.choices[0].message.content.strip()
    return generated_text
```

Sends the question to the OpenAI API and retrieves the generated response.

### Queue Processing

```python
def process_queue():
    while True:
        if not message_queue.empty():
            user, question = message_queue.get()
            response = process_question(question)
            qa_list.append((user, question, response))
            root.after(0, update_gui)
            speak_message(user, question, response)
            status_message.set("🔍 Waiting for a question...")
        time.sleep(10)
```

Processes the queue of incoming questions, generating and speaking responses.

### GUI Update Function

```python
def update_gui():
    text_widget.delete('1.0', tk.END)
    for user, question, response in qa_list:
        text_widget.insert(tk.END, f"@{user} asks: ", 'title')
        text_widget.insert(tk.END, f"{question}", 'text')
        text_widget.insert(tk.END, "Answer: ", 'title')
        text_widget.insert(tk.END, f"{response}\n\n", 'text')
```

Updates the GUI with the latest questions and answers.

### Main Window and Widgets

```python
root = tk.Tk()
root.title("SKRRTN's AI TTS BOT THINGY")
status_message = tk.StringVar()
status_message.set("🔍 Waiting for a question...")
text_widget = tk.Text(root, bg='gray20', fg='gray20', font=('Fira Code', 10), wrap=tk.WORD, padx=5)
status_bar = tk.Label(root, textvariable=status_message, bd=1, relief=tk.SUNKEN, anchor=tk.W)
text_widget.tag_configure('title', foreground='#06bbd9', font=('Fira Code', 12, 'bold'))
text_widget.tag_configure('text', foreground='white', font=('Fira Code', 10, 'bold'))
threading.Thread(target=process_queue).start()
```

Creates the main window and starts the queue processing thread.

### Twitch Connection

```python
def twitch_loop():
    sock = socket.socket()
    sock.connect((server, port))
    sock.send(f"PASS {token}\r\n".encode('utf-8'))
    sock.send(f"NICK {nickname}\r\n".encode('utf-8'))
    sock.send(f"JOIN {channel}\r\n".encode('utf-8'))
    while True:
        resp = sock.recv(2048).decode('utf-8')
        if resp.startswith('PING'):
            sock.send("PONG\n".encode('utf-8'))
        elif len(resp) > 0:
            print(resp)
            if "PRIVMSG" in resp:
                user = resp.split('!', 1)[0][1:]
                message = resp.split('PRIVMSG', 1)[1].split(':', 1)[1]
                if message.startswith('!q'):
                    question = message[3:]
                    message_queue.put((user, question))
                    status_message.set("⏳ Processing question...")
        else:
            break
        time.sleep(1/30)
threading.Thread(target=twitch_loop).start()
```

Handles connection to the Twitch IRC server and listens for messages.

### Finalizing GUI

```python
root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=0)
root.grid_columnconfigure(0, weight=1)
text_widget.grid(row=0, column=0, sticky="nsew")
status_bar.grid(row=1, column=0, sticky="ew")
root.mainloop()
```

Configures the GUI layout and starts the Tkinter main loop.

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## 📜 License

This project is licensed under the GNU General Public License. See the [LICENSE](LICENSE) file for details.
