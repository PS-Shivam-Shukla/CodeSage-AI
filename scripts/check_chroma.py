import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / 'chroma_db' / 'chroma.sqlite3'
print('DB', DB)
print('Exists:', DB.exists())
if not DB.exists():
    raise SystemExit(1)

conn = sqlite3.connect(str(DB))
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
rows = cur.fetchall()
print('Tables:')
for (t,) in rows:
    print(' -', t)
    try:
        cur.execute(f'SELECT COUNT(*) FROM "{t}"')
        n = cur.fetchone()[0]
        print(f'   rows: {n}')
    except Exception as e:
        print('   count error:', e)
conn.close()
