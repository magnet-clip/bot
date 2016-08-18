from threading import Lock
import vars
from tinydb import TinyDB, Query
from datetime import datetime, timedelta


class DatabaseManager:
    def __init__(self):
        self.lock = Lock()
        self.db_conn = TinyDB('./database.json')

    def add(self, items):
        with self.lock:
            self.db_conn.insert({
                vars.TIME: datetime.now().timestamp(),
                vars.CO2: items[vars.CO2],
                vars.GAS: items[vars.GAS],
                vars.LIGHT: items[vars.LIGHT],
                vars.MOTION: items[vars.MOTION],
                vars.CANCAM: items[vars.CANCAM],
                vars.HUMIDITY: items[vars.HUMIDITY],
                vars.TEMPERATURE: items[vars.TEMPERATURE]
            })

    def fetch_last(self, delta: timedelta, field: str):  # timedelta(seconds=5) for example
        threshold = (datetime.now() - delta).timestamp()
        with self.lock:
            record = Query()
            items = self.db_conn.search(record.time > threshold)
            return list([{'time': datetime.fromtimestamp(item['time']), 'value': item[field]} for item in items])
