import json
from enum import Enum
from datetime import datetime, timedelta
import os.path

class Message:
    class MessageContent:
        def __init__(self, message_obj):
            if 'content' in message_obj:
                self.content = message_obj['content']
            elif 'sticker' in message_obj:
                self.content = 'sticker'
            elif 'photos' in message_obj or 'gifs' in message_obj:
                self.content = 'photo'
            elif 'videos' in message_obj:
                self.content = 'video'
            elif 'audio_files' in message_obj:
                self.content = 'audio'
            else:
                print(f"unknown obj: {message_obj}")
                self.content = 'unknown'

        def __str__(self):
            return self.content

    def __init__(self, message_obj):
        self.sender = message_obj['sender_name']
        timestamp_sec = message_obj['timestamp_ms'] / 1000
        self.timestamp = datetime.fromtimestamp(timestamp_sec)
        self.content = Message.MessageContent(message_obj)

    def __str__(self):
        sender = self.sender
        content = self.content
        return f'{sender}: {content}'

def load_messages() -> list:
    TEMPLATE = 'data/message_{}.json'
    messages = []
    i = 1
    while True:
        path = TEMPLATE.format(i)
        if not os.path.exists(path):
            break
        FILE = open(path)
        messages.extend(json.loads(FILE.read())['messages'])
        FILE.close()
        i += 1
    messages = list(map(Message, reversed(messages)))
    return messages

# returns lists that correspond with the response times after sender transition
def response_times(messages) -> list:
    # get senders
    senders = {}
    for message in messages:
        sender = message.sender
        if sender not in senders:
            senders[sender] = []

    for i in range(1, len(messages)):
        message = messages[i]
        sender = message.sender
        # test if it's a sender transition
        previous_message = messages[i - 1]
        if previous_message.sender != sender:
            delta = message.timestamp - previous_message.timestamp
            senders[sender].append(delta)
    return senders

# https://stackoverflow.com/questions/3617170/average-timedelta-in-list
def average_timedelta(timedeltas):
    return sum(timedeltas, timedelta(0)) / len(timedeltas)

messages = load_messages()
times = response_times(messages)
