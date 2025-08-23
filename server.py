from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Initialize database
def init_db():
    conn = sqlite3.connect('customers.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            aadhar TEXT NOT NULL UNIQUE,
            phone TEXT NOT NULL,
            months INTEGER NOT NULL,
            amount REAL NOT NULL,
            payment_date TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect('customers.db')
    conn.row_factory = sqlite3.Row
    return conn

# API Routes
@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({'status': 'ok', 'message': 'Server is running'})

@app.route('/api/customers', methods=['GET'])
def get_customers():
    conn = get_db_connection()
    customers = conn.execute('SELECT * FROM customers ORDER BY created_at DESC').fetchall()
    conn.close()
    
    customers_list = []
    for customer in customers:
        customers_list.append({
            'id': customer['id'],
            'name': customer['name'],
            'address': customer['address'],
            'aadhar': customer['aadhar'],
            'phone': customer['phone'],
            'months': customer['months'],
            'amount': customer['amount'],
            'payment_date': customer['payment_date'],
            'created_at': customer['created_at']
        })
    
    return jsonify({'success': True, 'customers': customers_list})

@app.route('/api/customers', methods=['POST'])
def add_customer():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'address', 'aadhar', 'phone', 'months', 'amount', 'payment_date']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'success': False, 'message': f'Missing required field: {field}'}), 400
        
        # Check if customer with same Aadhar already exists
        conn = get_db_connection()
        existing = conn.execute('SELECT * FROM customers WHERE aadhar = ?', (data['aadhar'],)).fetchone()
        if existing:
            conn.close()
            return jsonify({'success': False, 'message': 'Customer with this Aadhar number already exists'}), 400
        
        # Insert new customer
        created_at = datetime.now().isoformat()
        conn.execute(
            'INSERT INTO customers (name, address, aadhar, phone, months, amount, payment_date, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (data['name'], data['address'], data['aadhar'], data['phone'], data['months'], data['amount'], data['payment_date'], created_at)
        )
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Customer added successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Server error: {str(e)}'}), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)