
import sqlite3, json, time, os
from .config import CACHE_DB, CACHE_TTLS

def _ensure_dir():
    os.makedirs(os.path.dirname(CACHE_DB), exist_ok=True)

def cache_init():
    _ensure_dir()
    conn = sqlite3.connect(CACHE_DB)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS cache (
        provider TEXT,
        key TEXT,
        ts INTEGER,
        data TEXT,
        PRIMARY KEY(provider, key)
    )''')
    conn.commit()
    conn.close()

def cache_get(provider: str, key: str):
    try:
        conn = sqlite3.connect(CACHE_DB)
        cur = conn.cursor()
        cur.execute("SELECT ts, data FROM cache WHERE provider=? AND key=?", (provider, key))
        row = cur.fetchone()
        conn.close()
        if not row:
            return None, False
        ts, data = row
        ttl = CACHE_TTLS.get(provider, 7*24*3600)
        if (time.time() - ts) > ttl:
            return None, False
        return json.loads(data), True
    except Exception:
        return None, False

def cache_set(provider: str, key: str, data: dict) -> None:
    try:
        conn = sqlite3.connect(CACHE_DB)
        cur = conn.cursor()
        cur.execute("REPLACE INTO cache (provider, key, ts, data) VALUES (?, ?, ?, ?)",
                    (provider, key, int(time.time()), json.dumps(data)))
        conn.commit()
        conn.close()
    except Exception:
        pass

# Init on import
cache_init()
