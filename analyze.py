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
                self.content = '[sticker]'
            elif 'photos' in message_obj or 'gifs' in message_obj:
                self.content = '[photo]'
            elif 'videos' in message_obj:
                self.content = '[video]'
            elif 'audio_files' in message_obj:
                self.content = '[audio]'
            else:
                print(f"unknown obj: {message_obj}")
                self.content = '[unknown]'

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

# messages sent from the same person in succession
class MessageBlock:
    def __init__(self, message):
        self.messages = [message]

    def add_message(self, message):
        self.messages.append(message)

    @property
    def sender(self):
        return self.messages[0].sender

    @property
    def timestamps(self):
        return [m.timestamp for m in self.messages]

    def first_timestamp(self):
        return self.messages[0].timestamp

    def first_month(self):
        timestamp = self.first_timestamp()
        return timestamp.month

    def __str__(self) -> str:
        return '\n'.join(map(str, self.messages))


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

    # convert to message blocks
    first_block = MessageBlock(messages[0])
    message_blocks = [first_block]
    for message in messages[1:]:
        current_block = message_blocks[-1]
        if current_block.sender == message.sender:
            current_block.add_message(message)
        else:
            message_blocks.append(MessageBlock(message))
    return message_blocks

def group_messages_by_month(message_blocks):
    month_messages = {}
    for block in message_blocks:
        # just assume messages in the same block are in the same month
        month = block.first_month()
        if month not in month_messages:
            month_messages[month] = []
        month_messages[month].append(block)
    return month_messages

# returns lists that correspond with the response times after sender transition
# list has tuples of form (index, timedelta)
def calculate_response_times(message_blocks) -> list:
    # get senders
    senders = {}
    for block in message_blocks:
        sender = block.sender
        if sender not in senders:
            senders[sender] = []

    for i in range(1, len(message_blocks)):
        block = message_blocks[i]
        previous_block = message_blocks[i - 1]
        delta = block.first_timestamp() - previous_block.first_timestamp()
        senders[block.sender].append((i, delta))
    return senders
