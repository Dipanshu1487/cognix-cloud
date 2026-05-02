import sqlite3
import json
import os

def dump_data():
    conn = sqlite3.connect('cognix.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    def clean_path(p):
        if not p: return p
        # extract just the filename and make it relative to 'uploads/'
        basename = os.path.basename(p.replace('\\', '/'))
        return os.path.join('uploads', basename).replace('\\', '/')

    notes = [dict(row) for row in cur.execute("SELECT * FROM notes").fetchall()]
    for n in notes:
        n['file_path'] = clean_path(n.get('file_path'))

    questions = [dict(row) for row in cur.execute("SELECT * FROM questions").fetchall()]
    for q in questions:
        q['file_path'] = clean_path(q.get('file_path'))

    data = {
        "subjects": [dict(row) for row in cur.execute("SELECT * FROM subjects").fetchall()],
        "units": [dict(row) for row in cur.execute("SELECT * FROM units").fetchall()],
        "sections": [dict(row) for row in cur.execute("SELECT * FROM sections").fetchall()],
        "topics": [dict(row) for row in cur.execute("SELECT * FROM topics").fetchall()],
        "subtopics": [dict(row) for row in cur.execute("SELECT * FROM subtopics").fetchall()],
        "notes": notes,
        "questions": questions
    }

    with open('seed_data.json', 'w') as f:
        json.dump(data, f, indent=2)

    conn.close()
    print("Data dumped cleanly to seed_data.json")

if __name__ == '__main__':
    dump_data()
