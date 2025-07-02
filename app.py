from flask import Flask, render_template, request, redirect
import sqlite3


conn = sqlite3.connect('votes.db')
cur = conn.cursor()

# Drop old table if exists
cur.execute('DROP TABLE IF EXISTS votes')

# Create new simple table without IP
cur.execute('''
CREATE TABLE votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    option TEXT
)
''')

app = Flask(__name__)

def get_db():
    return sqlite3.connect('votes.db')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vote', methods=['POST'])
def vote():
    option = request.form['option']

    conn = get_db()
    cur = conn.cursor()

    # Insert vote (no IP restriction)
    cur.execute('INSERT INTO votes (option) VALUES (?)', (option,))
    conn.commit()
    conn.close()
    return redirect('/results')

@app.route('/results')
def results():
    conn = get_db()
    cur = conn.cursor()

    # Fixed options
    options = ['PMLN', 'PPP', 'PTI']

    # Votes per option
    data = {}
    for option in options:
        cur.execute('SELECT COUNT(*) FROM votes WHERE option = ?', (option,))
        count = cur.fetchone()[0]
        data[option] = count

    # Total votes
    cur.execute('SELECT COUNT(*) FROM votes')
    total_votes = cur.fetchone()[0]

    conn.close()

    # Prepare data for chart
    result = [(opt, data[opt]) for opt in options]

    return render_template('results.html', data=result, total_votes=total_votes)




if __name__ == '__main__':
    app.run(debug=True)
