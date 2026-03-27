import os
from flask import Flask, render_template, request, redirect, session,send_file
import sqlite3
from datetime import timedelta,datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph
from engine import analyze

app = Flask(__name__)
app.secret_key = "secret123"

app.permanent_session_lifetime = timedelta(days=7)
# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect('database.db',timeout=10)
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE,
        password TEXT
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

    conn.commit()
    conn.close()

init_db()

# ---------------- AUTH ----------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        conn = sqlite3.connect('database.db',timeout=10)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users VALUES (NULL, ?, ?)", (u, p))
            conn.commit()
        except:
            return "User already exists"
        conn.close()
        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        conn = sqlite3.connect('database.db',timeout=10)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
        user = c.fetchone()
        conn.close()

        if user:
            session.permanent = True
            session['user'] = u
            return redirect('/')
        else:
            return "Invalid credentials"

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


# ---------------- HOME ----------------

@app.route('/')
def home():
    if 'user' not in session:
        return redirect('/login')
    return render_template('index.html')


# ---------------- ADD DATA ----------------
@app.route('/add', methods=['POST'])
def add():
    if 'user' not in session:
        return redirect('/login')

    try:
        conn = sqlite3.connect('database.db', timeout=10)
        c = conn.cursor()

        appliance = request.form['appliance']
        power = float(request.form['power'])
        hours = float(request.form['hours'])

        units = (power * hours) / 1000
        date = datetime.now().strftime("%Y-%m-%d")

        c.execute("""
            INSERT INTO usage VALUES (NULL, ?, ?, ?, ?, ?, ?)
        """, (session['user'], appliance, power, hours, units, date))

        conn.commit()
        conn.close()

    except Exception as e:
        return f"Error: {e}"

    return redirect('/dashboard')



# ---------------- DASHBOARD ----------------

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db',timeout=10)
    c = conn.cursor()
    c.execute("SELECT id, appliance, units, hours, date FROM usage WHERE username=?", (session['user'],))
    rows = c.fetchall()
    conn.close()
    data = [
    {
        "id": r[0],
        "appliance": r[1],
        "units": r[2],
        "hours": r[3],
        "date": r[4]
    }
    for r in rows
    ]
    result = analyze(data)

    return render_template('dashboard.html', data=data, result=result)


# ---------------- DELETE ----------------

@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('database.db',timeout=10)
    c = conn.cursor()
    c.execute("DELETE FROM usage WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect('/dashboard')

@app.route('/reset',methods=['POST'])
def reset():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db', timeout=10)
    c = conn.cursor()

    c.execute("DELETE FROM usage WHERE username=?", (session['user'],))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

@app.route('/report')
def report():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db', timeout=10)
    c = conn.cursor()
    c.execute("SELECT appliance, units, date FROM usage WHERE username=?", (session['user'],))
    rows = c.fetchall()
    conn.close()

    filename = "report.pdf"

    # Create PDF
    doc = SimpleDocTemplate(filename)

    content = []
    content.append(Paragraph("Energy Usage Report"))

    for r in rows:
        content.append(Paragraph(f"{r[0]} - {r[1]} units ({r[2]})"))

    doc.build(content)

    # ✅ Send file for download
    return send_file(filename, as_attachment=True)


# ---------------- ADMIN ----------------

@app.route('/admin')
def admin():
    # Admin password protection
    if 'admin' not in session:
        return redirect('/admin-login')
    
    conn = sqlite3.connect('database.db', timeout=10)
    c = conn.cursor()
    
    # Get all users
    c.execute("SELECT id, username FROM users")
    users = c.fetchall()
    
    # Get all usage records
    c.execute("SELECT id, username, appliance, power, hours, units, date FROM usage ORDER BY date DESC")
    usage_records = c.fetchall()
    
    conn.close()
    
    return render_template('admin.html', users=users, usage_records=usage_records)


@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'admin123':  # Change this to a secure password
            session['admin'] = True
            return redirect('/admin')
        else:
            return "Invalid admin password"
    return render_template('admin_login.html')


@app.route('/admin-logout')
def admin_logout():
    session.pop('admin', None)
    return redirect('/login')


# ---------------- RUN ----------------

if __name__ == '__main__':
    print("Server starting...")
    app.run(host="0.0.0.0", port=5000)