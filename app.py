from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # เปลี่ยนเป็น secret key ของคุณ
app.config['MYSQL_HOST'] = 'db'  # ตั้งค่าให้ตรงกับชื่อ service ใน docker-compose
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'banking_db'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        if user and check_password_hash(user[2], password):  # user[2] คือ password
            session['username'] = username
            return redirect(url_for('user_dashboard'))
        return 'Invalid credentials!'
    return render_template('login.html')

@app.route('/dashboard', methods=['GET'])
def user_dashboard():
    if 'username' in session:
        user_id = get_user_id(session['username'])
        
        # ดึงข้อมูลยอดเงิน
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT balance FROM users WHERE id = %s", (user_id,))
        balance = cursor.fetchone()

        if balance:
            balance = balance[0]  # เข้าถึงยอดเงินโดยใช้ดัชนี
        else:
            balance = 0  # ถ้ายอดเงินไม่พบ
        
        # ดึงข้อมูลการทำธุรกรรม
        cursor.execute("""
            SELECT created_at, transaction_type, amount, direction 
            FROM transactions 
            WHERE user_id = %s
        """, (user_id,))
        transactions = cursor.fetchall()
        cursor.close()

        # ตรวจสอบข้อมูลที่ถูกดึง
        if not transactions:
            transactions = []  # ถ้าไม่มีธุรกรรม

        return render_template('dashboard.html', username=session['username'], balance=balance, transactions=transactions)
    
    return redirect(url_for('login'))

def get_user_id(username):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
    user_id = cursor.fetchone()[0]
    cursor.close()
    return user_id

# Route for deposit
@app.route('/deposit', methods=['GET', 'POST'])
def deposit():
    if request.method == 'POST':
        if 'username' in session:
            user_id = get_user_id(session['username'])
            amount = request.form['amount']
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO transactions (user_id, transaction_type, amount) VALUES (%s, 'deposit', %s)", (user_id, amount))
            cursor.execute("UPDATE users SET balance = balance + %s WHERE id = %s", (amount, user_id))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('user_dashboard'))  # เปลี่ยนเป็น user_dashboard
        return redirect(url_for('login'))
    return render_template('deposit.html')  # เพิ่มการ render ฟอร์มในกรณีที่เป็น GET

# Route for transfer
@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if request.method == 'POST':
        if 'username' in session:
            user_id = get_user_id(session['username'])
            recipient = request.form['recipient']
            amount = request.form['amount']
            
            cursor = mysql.connection.cursor()
            cursor.execute("SELECT id FROM users WHERE username = %s", (recipient,))
            recipient_user = cursor.fetchone()

            if recipient_user:
                recipient_id = recipient_user[0]
                cursor.execute("INSERT INTO transactions (user_id, transaction_type, amount) VALUES (%s, 'transfer', %s)", (user_id, amount))
                cursor.execute("UPDATE users SET balance = balance - %s WHERE id = %s", (amount, user_id))
                cursor.execute("INSERT INTO transactions (user_id, transaction_type, amount) VALUES (%s, 'transfer', %s)", (recipient_id, amount))
                cursor.execute("UPDATE users SET balance = balance + %s WHERE id = %s", (amount, recipient_id))
                mysql.connection.commit()
            cursor.close()
            return redirect(url_for('user_dashboard'))
        return redirect(url_for('login'))
    return render_template('transfer.html')  # เพิ่มการ render ฟอร์มในกรณีที่เป็น GET


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
