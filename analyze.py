import json
from enum import Enum
from datetime import datetime

class Message:
    class MessageContent:
        def __init__(self, message_obj):
            if 'content' in message_obj:
                self.content = message_obj['content']
            elif 'sticker' in message_obj:
                self.content = 'sticker'
            else:
                raise NotImplementedError(f'unhandled type for obj {message_obj}')

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

# TODO: write a load messages loop
FILE = open('message_1.json')
messages = json.loads(FILE.read())['messages']
FILE.close()
FILE = open('message_2.json')
messages.extend(json.loads(FILE.read())['messages'])

for i in reversed(range(-20, 0)):
    message_obj = messages[i]
    print(Message(message_obj))