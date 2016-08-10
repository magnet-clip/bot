from threading import Lock
from tinydb import TinyDB, Query
from datetime import datetime, timedelta


class DatabaseManager:
    def __init__(self):
        self.lock = Lock()
        self.db_conn = TinyDB('./database.json')

    def add(self, items):
        with self.lock:
            self.db_conn.insert({
                'time': datetime.now().timestamp(),
                'co2': items['co2'],
                'gas': items['gas'],
                'light': items['light'],
                'motion': items['motion'],
                'cameraAllowed': items['cameraAllowed'],
                'humidity': items['humidity'],
                'temperature': items['temperature']
            })

    def fetch_last(self, delta: timedelta, field: str):  # timedelta(seconds=5) for example
        threshold = (datetime.now() - delta).timestamp()
        with self.lock:
            record = Query()
            items = self.db_conn.search(record.time > threshold)
            return list([{'time': datetime.fromtimestamp(item['time']), 'value': item[field]} for item in items])
