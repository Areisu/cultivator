from flask import Flask, render_template, request, session, redirect, url_for
import uuid

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_grid', methods=['GET', 'POST'])
def add_grid():
    if request.method == 'POST':
        width = int(request.form['width'])
        height = int(request.form['height'])
        grid_id = str(uuid.uuid4())  # Generate a unique ID for the grid
        session['grid_id'] = grid_id
        session['grid'] = [[None for _ in range(width)] for _ in range(height)]
        return redirect(url_for('display_grid'))
    return render_template('add_grid.html')

@app.route('/display_grid')
def display_grid():
    grid = session.get('grid')
    if not grid:
        return redirect(url_for('add_grid'))
    return render_template('display_grid.html', grid=grid)

if __name__ == '__main__':
    app.run(debug=True)
