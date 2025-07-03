from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ---------------------
# Get client IP address
# ---------------------
def get_ip():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.remote_addr
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']

# ------------------------
# Initialize or reset DB
# ------------------------
conn = sqlite3.connect('votes.db')
cur = conn.cursor()

# Drop old table if exists
cur.execute('DROP TABLE IF EXISTS votes')

# New table with IP address and UNIQUE constraint
cur.execute('''
CREATE TABLE votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    option TEXT,
    ip_address TEXT UNIQUE
)
''')

conn.commit()
conn.close()

# ----------------------
# Reusable DB connection
# ----------------------
def get_db():
    return sqlite3.connect('votes.db')

# ----------------------
# Index page
# ----------------------
@app.route('/')
def index():
    return render_template('index.html')

# ----------------------
# Vote submission route
# ----------------------
@app.route('/vote', methods=['POST'])
def vote():
    option = request.form['option']
    ip = get_ip()

    conn = get_db()
    cur = conn.cursor()

    # Check if IP has already voted
    cur.execute('SELECT * FROM votes WHERE ip_address = ?', (ip,))
    if cur.fetchone():
        conn.close()
        return "<h3 style='color:red;'>⚠️ You have already voted from this IP address!</h3><a href='/'>Back</a>"

    # Save vote
    cur.execute('INSERT INTO votes (option, ip_address) VALUES (?, ?)', (option, ip))
    conn.commit()
    conn.close()

    return redirect('/results')

# ----------------------
# Results route
# ----------------------
@app.route('/results')
def results():
    conn = get_db()
    cur = conn.cursor()

    options = ['PMLN', 'PPP', 'PTI']
    data = {}

    for option in options:
        cur.execute('SELECT COUNT(*) FROM votes WHERE option = ?', (option,))
        count = cur.fetchone()[0]
        data[option] = count

    cur.execute('SELECT COUNT(*) FROM votes')
    total_votes = cur.fetchone()[0]

    conn.close()

    result = [(opt, data[opt]) for opt in options]

    return render_template('results.html', data=result, total_votes=total_votes)

# ----------------------
# Run the app
# ----------------------
if __name__ == '__main__':
    app.run(debug=True)
