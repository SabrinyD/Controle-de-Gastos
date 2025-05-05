from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import os

app = Flask(__name__)
CORS(app)  


DATABASE = "expenses.db"

if not os.path.exists(DATABASE):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        date TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()
    print("Banco de dados criado com sucesso!")

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/expenses', methods=['POST'])
def add_expense():
    try:
        data = request.json
        
        if not data.get('description') or not data.get('amount') or not data.get('date'):
            return jsonify({"error": "Todos os campos são obrigatórios"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO expenses (description, amount, date) VALUES (?, ?, ?)",
            (data['description'], data['amount'], data['date'])
        )
        conn.commit()
        
        new_id = cursor.lastrowid
        conn.close()
        
        return jsonify({"message": "Gasto adicionado com sucesso", "id": new_id}), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
        expenses = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return jsonify(expenses), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return jsonify({"error": "Gasto não encontrado"}), 404
        
        conn.commit()
        conn.close()
        
        return jsonify({"message": "Gasto excluído com sucesso"}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/expenses/total', methods=['GET'])
def get_total():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(amount) as total FROM expenses")
        total = cursor.fetchone()['total'] or 0
        conn.close()
        
        return jsonify({"total": total}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
