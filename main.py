# Import necessary libraries
import socket  # For network connections
import time  # For time-related functions
import queue  # For queue data structure
import threading  # For multithreading
import openai  # For OpenAI API
import tkinter as tk  # For GUI
import json  # For JSON file handling
import os  # For OS related operations
import pyttsx3  # For text-to-speech
from tkinter import font as tkfont  # For font related operations in tkinter
from openai import OpenAI  # For OpenAI API

# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))

# Construct the full path to the config file
config_file = os.path.join(script_dir, 'config.json')

# Load the configuration file
with open(config_file) as f:
    config = json.load(f)

# Use the configuration values
openai.api_key = config['openai_api_key']
server = config['irc_server']
port = config['irc_port']
nickname = config['irc_nickname']
token = config['irc_token']
channel = config['irc_channel']

# Create a queue
message_queue = queue.Queue()

# Global list to store questions and answers
qa_list = []

# Function to convert text to speech
def speak_message(user, question, response):
    message = f"{user} asks {question}. {response}"
    
    # Initialize the pyttsx3 text-to-speech engine
    engine = pyttsx3.init()

    # Set the properties of the speech
    rate = engine.getProperty('rate')   # Speed percent (can go over 100)
    volume = engine.getProperty('volume') # Volume 0-1
    engine.setProperty('rate', 180)
    engine.setProperty('volume',1)

    # Speak the message
    engine.say(message)

    # Block while processing all the currently queued commands
    engine.runAndWait()

# Function to process a question using OpenAI API
def process_question(question):
    status_message.set("📖 Reading response...")
    client = OpenAI(api_key=config['openai_api_key'])
    # Call OpenAI API to generate response
    response = client.chat.completions.create(
        model=config['model'],  # Use the model from the config file
        messages=[
            {"role": "system", "content": config['prompt']},
            {"role": "user", "content": question},
        ]
    )
    generated_text = response.choices[0].message.content.strip()
    return generated_text

# Function to process the queue
def process_queue():
    while True:
        if not message_queue.empty():
            user, question = message_queue.get()
            response = process_question(question)

            # Add the question and answer to the list
            qa_list.append((user, question, response))

            # Update the GUI
            root.after(0, update_gui)

            speak_message(user, question, response)  # Speak the response
            status_message.set("🔍 Waiting for a question...")

        time.sleep(10)

# Function to update the GUI
def update_gui():
    # Clear the text widget
    text_widget.delete('1.0', tk.END)

    # Add items to the text widget
    for user, question, response in qa_list:
        text_widget.insert(tk.END, f"@{user} asks: ", 'title')
        text_widget.insert(tk.END, f"{question}", 'text') 
        text_widget.insert(tk.END, "Answer: ", 'title')
        text_widget.insert(tk.END, f"{response}\n\n", 'text') 

# Create the main window
root = tk.Tk()
root.title("SKRRTN's AI TTS BOT THINGY")

# Create a StringVar for the status message
status_message = tk.StringVar()
status_message.set("🔍 Waiting for a question...")

# Create a text widget with padding
text_widget = tk.Text(root, bg='gray20', fg='gray20', font=('Fira Code', 10), wrap=tk.WORD, padx=5)

# Create a status bar
status_bar = tk.Label(root, textvariable=status_message, bd=1, relief=tk.SUNKEN, anchor=tk.W)

# Define the tag configurations
text_widget.tag_configure('title', foreground='#06bbd9', font=('Fira Code', 12, 'bold'))
text_widget.tag_configure('text', foreground='white', font=('Fira Code', 10, 'bold'))

# Start the queue processing in a separate thread
threading.Thread(target=process_queue).start()

# Function to handle Twitch IRC server
def twitch_loop():
    # Connect to Twitch IRC server
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

                # Now you have the user's name and message. You can process the message here.
                if message.startswith('!q'):
                    question = message[3:]  # Remove '!q ' from the start of the message
                    message_queue.put((user, question))
                    status_message.set("⏳ Processing question...")

        else:
            break  # Break the loop if resp is empty

        time.sleep(1/30)  # Twitch limits rate to 30 messages per second

# Start the Twitch loop in a separate thread
threading.Thread(target=twitch_loop).start()

# Grid configuration
root.grid_rowconfigure(0, weight=1)  # Make the row containing the text widget expand
root.grid_rowconfigure(1, weight=0)  # Make the row containing the status bar not expand
root.grid_columnconfigure(0, weight=1)  # Make the column containing the widgets expand

# Widget placement
text_widget.grid(row=0, column=0, sticky="nsew")  # Make the text widget expand in both directions
status_bar.grid(row=1, column=0, sticky="ew")  # Make the status bar expand horizontally but not vertically

# Start the main loop
root.mainloop()