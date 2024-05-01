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
        c.execute('''CREATE TABLE IF NOT EXISTS available_crops (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        crop_name TEXT NOT NULL
                     )''')
        db.commit()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def index():    
    db = get_db()
    c = db.cursor()
    c.execute('''SELECT * FROM crop_grids ORDER BY id DESC''')
    grids = c.fetchall()
    return render_template('index.html', grids=grids)


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

@app.route('/display_grid/<int:grid_id>', methods=['GET', 'POST'])
def display_grid(grid_id):
    db = get_db()
    c = db.cursor()
    
    # Retrieve the grid details
    c.execute('''SELECT * FROM crop_grids WHERE id = ?''', (grid_id,))
    grid = c.fetchone()
    
    # Retrieve available crops
    c.execute('''SELECT crop_name FROM available_crops''')
    crops = [row[0] for row in c.fetchall()]

    if request.method == 'POST':
        selected_crop = request.form['crop']
        new_crops = grid[3] + ', ' + selected_crop if grid[3] else selected_crop
        c.execute('''UPDATE crop_grids SET crops = ? WHERE id = ?''', (new_crops, grid_id))
        db.commit()

    return render_template('display_grid.html', grid=grid, crops=crops)


if __name__ == '__main__':
    init_db()
    app.run(debug=True)