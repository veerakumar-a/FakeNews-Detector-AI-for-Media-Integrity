import sqlite3
from pathlib import Path
from typing import Optional

DB_PATH = Path(__file__).resolve().parents[1] / "demo.db"


def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel TEXT NOT NULL,
            address TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS votes (
            item_id TEXT PRIMARY KEY,
            score INTEGER DEFAULT 0
        )
        """
    )
    conn.commit()
    conn.close()


def add_subscription(channel: str, address: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO subscriptions (channel, address) VALUES (?,?)", (channel, address))
    conn.commit()
    conn.close()


def add_vote(item_id: str, delta: int) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT score FROM votes WHERE item_id = ?", (item_id,))
    row = cur.fetchone()
    if row is None:
        cur.execute("INSERT INTO votes (item_id, score) VALUES (?,?)", (item_id, delta))
        score = delta
    else:
        score = row["score"] + delta
        cur.execute("UPDATE votes SET score = ? WHERE item_id = ?", (score, item_id))
    conn.commit()
    conn.close()
    return score


def get_score(item_id: str) -> Optional[int]:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT score FROM votes WHERE item_id = ?", (item_id,))
    row = cur.fetchone()
    conn.close()
    if row is None:
        return 0
    return int(row["score"])


def get_subscriptions():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, channel, address, created_at FROM subscriptions ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_all_votes():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT item_id, score FROM votes")
    rows = cur.fetchall()
    conn.close()
    return {r['item_id']: r['score'] for r in rows}
