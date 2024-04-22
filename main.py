from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

# Connect to SQLite database
conn = sqlite3.connect('crops.db')
c = conn.cursor()

# Create table to store crop grid data
c.execute('''CREATE TABLE IF NOT EXISTS crop_grids (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                width INTEGER NOT NULL,
                height INTEGER NOT NULL,
                crops TEXT NOT NULL
             )''')
conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_grid', methods=['GET', 'POST'])
def add_grid():
    if request.method == 'POST':
        width = int(request.form['width'])
        height = int(request.form['height'])
        crops = request.form['crops']
        c.execute('''INSERT INTO crop_grids (width, height, crops) VALUES (?, ?, ?)''', (width, height, crops))
        conn.commit()
        return redirect(url_for('display_grid'))
    return render_template('add_grid.html')

@app.route('/display_grid')
def display_grid():
    c.execute('''SELECT * FROM crop_grids ORDER BY id DESC LIMIT 1''')
    grid = c.fetchone()
    return render_template('display_grid.html', grid=grid)

if __name__ == '__main__':
    app.run(debug=True)
