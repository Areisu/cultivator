from flask import Flask, render_template, request, redirect, url_for, flash, g
import sqlite3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['DATABASE'] = 'crops.db'

# Connect to SQLite database
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
    return db

# Create table to store crop grid data
def init_db():
    with app.app_context():
        db = get_db()
        c = db.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS crop_grids (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        width INTEGER NOT NULL,
                        height INTEGER NOT NULL,
                        crops TEXT NOT NULL
                     )''')
        db.commit()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_grid', methods=['GET', 'POST'])
def add_grid():
    if request.method == 'POST':
        width = int(request.form['width'])
        height = int(request.form['height'])
        crops = request.form['crops']
        db = get_db()
        c = db.cursor()
        c.execute('''INSERT INTO crop_grids (width, height, crops) VALUES (?, ?, ?)''', (width, height, crops))
        db.commit()
        flash('Grid has been successfully created.', 'success')
        return redirect(url_for('index'))
    return render_template('add_grid.html')

@app.route('/display_grid')
def display_grid():
    db = get_db()
    c = db.cursor()
    c.execute('''SELECT * FROM crop_grids ORDER BY id DESC LIMIT 1''')
    grid = c.fetchone()
    return render_template('display_grid.html', grid=grid)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
