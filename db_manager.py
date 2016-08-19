from threading import Lock
from measures import Measures
from tinydb import TinyDB, Query
from datetime import datetime, timedelta


class DatabaseManager:
    def __init__(self):
        self.lock = Lock()
        self.db_conn = TinyDB('./database.json')

    def add(self, items):
        with self.lock:
            self.db_conn.insert({
                Measures.TIME: datetime.now().timestamp(),
                Measures.CO2: items[Measures.CO2],
                Measures.GAS: items[Measures.GAS],
                Measures.LIGHT: items[Measures.LIGHT],
                Measures.MOTION: items[Measures.MOTION],
                Measures.CANCAM: items[Measures.CANCAM],
                Measures.HUMIDITY: items[Measures.HUMIDITY],
                Measures.TEMPERATURE: items[Measures.TEMPERATURE]
            })

    def fetch_last(self, delta: timedelta, field: str):  # timedelta(seconds=5) for example
        threshold = (datetime.now() - delta).timestamp()
        with self.lock:
            record = Query()
            items = self.db_conn.search(record.time > threshold)
            return list([{'time': datetime.fromtimestamp(item['time']), 'value': item[field]} for item in items])
