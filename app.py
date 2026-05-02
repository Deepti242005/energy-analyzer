from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime
from engine import analyze

app = Flask(__name__)
app.secret_key = "secret123"

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT DEFAULT 'user'
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS usage (
        id INTEGER PRIMARY KEY,
        username TEXT,
        appliance TEXT,
        power REAL,
        hours REAL,
        units REAL,
        date TEXT
    )
    ''')

    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users VALUES (NULL,'admin','admin','admin')")

    conn.commit()
    conn.close()

init_db()

@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (u,p))
        user = c.fetchone()
        conn.close()

        if user:
            session['user'] = user[1]
            session['role'] = user[3]

            if user[3] == 'admin':
                return redirect('/admin')
            return redirect('/home')

        return "Invalid credentials"

    return render_template('login.html')


@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=?", (u,))
        if c.fetchone():
            conn.close()
            return "User already exists"

        c.execute("INSERT INTO users (username,password,role) VALUES (?,?,?)", (u,p,'user'))
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('register.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


@app.route('/home')
def home():
    if 'user' not in session:
        return redirect('/')
    return render_template('index.html')


@app.route('/add', methods=['POST'])
def add():
    appliance = request.form['appliance']
    power = float(request.form['power'])
    hours = float(request.form['hours'])

    units = (power * hours) / 1000
    date = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("INSERT INTO usage VALUES (NULL,?,?,?,?,?,?)",
              (session['user'], appliance, power, hours, units, date))
    conn.commit()
    conn.close()

    return redirect('/dashboard')


@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT id, appliance, units, hours, date FROM usage WHERE username=?", (session['user'],))
    rows = c.fetchall()
    conn.close()

    data = [{"id":r[0], "appliance":r[1], "units":r[2], "hours":r[3], "date":r[4]} for r in rows]
    result = analyze(data)

    return render_template('dashboard.html', data=data, result=result)


@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM usage WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/dashboard')


@app.route('/reset')
def reset():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("DELETE FROM usage WHERE username=?", (session['user'],))
    conn.commit()
    conn.close()
    return redirect('/dashboard')


@app.route('/admin')
def admin():
    if session.get('role') != 'admin':
        return "Access Denied"

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT username, role FROM users")
    users = c.fetchall()

    c.execute("SELECT username, appliance, units FROM usage")
    usage = c.fetchall()

    conn.close()

    return render_template('admin.html', users=users, usage=usage)


if __name__ == '__main__':
    app.run(debug=True)