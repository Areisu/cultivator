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

# Create tables to store crop grid data and grid cell data
def init_db():
    with app.app_context():
        db = get_db()
        c = db.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS crop_grids (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        width INTEGER NOT NULL,
                        height INTEGER NOT NULL
                     )''')
        c.execute('''CREATE TABLE IF NOT EXISTS grid_cells (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        grid_id INTEGER NOT NULL,
                        row_index INTEGER NOT NULL,
                        column_index INTEGER NOT NULL,
                        content TEXT,
                        FOREIGN KEY(grid_id) REFERENCES crop_grids(id)
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
        name = request.form['name']
        width = int(request.form['width'])  # Ensure width is an integer
        height = int(request.form['height'])  # Ensure height is an integer
        db = get_db()
        c = db.cursor()
        c.execute('''INSERT INTO crop_grids (name, width, height) VALUES (?, ?, ?)''', (name, width, height))
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
    
    width = grid[3]  # Assuming width is at index 3 in the database
    height = grid[2]  # Assuming height is at index 2 in the database

    # Retrieve the grid cells
    c.execute('''SELECT row_index, column_index, content FROM grid_cells WHERE grid_id = ?''', (grid_id,))
    cells = c.fetchall()

    # Create a dictionary to store cell contents using (row, column) as keys
    cell_contents = {(cell[0], cell[1]): cell[2] for cell in cells}

    return render_template('display_grid.html', width=width, height=height, cell_contents=cell_contents, grid_id=grid_id)


@app.route('/delete_grid/<int:grid_id>', methods=['POST'])
def delete_grid(grid_id):
    db = get_db()
    c = db.cursor()
    c.execute('''DELETE FROM crop_grids WHERE id = ?''', (grid_id,))
    db.commit()
    flash('Grid has been successfully deleted.', 'success')
    return redirect(url_for('index'))

@app.route('/update_grid_cell', methods=['POST'])
def update_grid_cell():
    grid_id = request.form['grid_id']
    row_index = request.form.get('row_index')
    column_index = request.form.get('column_index')
    cell_content = request.form['cell_content']

    db = get_db()
    c = db.cursor()

    # Check if the grid cell already exists
    c.execute('''SELECT * FROM grid_cells WHERE grid_id = ? AND row_index = ? AND column_index = ?''', (grid_id, row_index, column_index))
    existing_cell = c.fetchone()

    if existing_cell:
        # Update existing grid cell content
        c.execute('''UPDATE grid_cells SET content = ? WHERE id = ?''', (cell_content, existing_cell[0]))
    else:
        # Insert new grid cell content
        c.execute('''INSERT INTO grid_cells (grid_id, row_index, column_index, content) VALUES (?, ?, ?, ?)''', (grid_id, row_index, column_index, cell_content))
    db.commit()

    return 'Grid cell updated successfully', 200

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
