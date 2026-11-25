from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-only-change-me')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('RENDER', '') == 'true'
DB = os.path.join(os.path.dirname(__file__), 'chat.db')

def db():
    conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row; return conn

def init_db():
    with db() as c:
        c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT, display_name TEXT)')
        c.execute('CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, user_id INTEGER, message TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(user_id) REFERENCES users(id))')

@app.route('/')
def home():
    return redirect(url_for('chat') if session.get('user_id') else url_for('login'))

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        name=request.form.get('name','').strip(); email=request.form.get('email','').strip().lower(); pw=request.form.get('password','')
        if not name or not email or len(pw)<6:
            flash('Enter all details. Password must be at least 6 characters.'); return render_template('register.html')
        try:
            with db() as c: c.execute('INSERT INTO users(email,password,display_name) VALUES(?,?,?)',(email,generate_password_hash(pw),name))
            flash('Account created. Please log in.'); return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('This email is already registered.')
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email=request.form.get('email','').strip().lower(); pw=request.form.get('password','')
        with db() as c: user=c.execute('SELECT * FROM users WHERE email=?',(email,)).fetchone()
        if user and check_password_hash(user['password'],pw):
            session['user_id']=user['id']; session['name']=user['display_name']; return redirect(url_for('chat'))
        flash('Invalid email or password.')
    return render_template('login.html')

@app.route('/chat')
def chat():
    if not session.get('user_id'): return redirect(url_for('login'))
    with db() as c: users=c.execute('SELECT display_name FROM users WHERE id != ? ORDER BY display_name',(session['user_id'],)).fetchall()
    return render_template('chat.html', name=session['name'], users=users)

@app.route('/messages', methods=['GET','POST'])
def messages():
    if not session.get('user_id'): return jsonify({'error':'login required'}),401
    with db() as c:
        if request.method=='POST':
            msg=request.json.get('message','').strip() if request.is_json else request.form.get('message','').strip()
            if msg and len(msg)<=1000: c.execute('INSERT INTO messages(user_id,message) VALUES(?,?)',(session['user_id'],msg))
        rows=c.execute('SELECT m.id,m.message,m.created_at,u.display_name,u.id AS uid FROM messages m JOIN users u ON u.id=m.user_id ORDER BY m.id DESC LIMIT 100').fetchall()
    return jsonify([dict(r) for r in reversed(rows)])

@app.route('/logout')
def logout(): session.clear(); return redirect(url_for('login'))

if __name__ == '__main__':
    init_db(); app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
else:
    init_db()
