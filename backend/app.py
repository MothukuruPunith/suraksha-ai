from flask import Flask, jsonify, request
from flask_cors import CORS
import sys, os

# Path fix
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.risk_model import calculate_risk, calculate_premium
from ai.fraud_model import detect_fraud
from services.db import get_db_connection

app = Flask(__name__)
CORS(app)

# ---------------- REGISTER ----------------
@app.route('/register', methods=['POST'])
def register():
    data = request.json

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "INSERT INTO users (name, password, location, worker_type) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (
        data['name'],
        data['password'],
        data['location'],
        data['worker_type']
    ))

    conn.commit()

    return jsonify({"message": "User registered successfully"})


# ---------------- LOGIN ----------------
@app.route('/login', methods=['POST'])
def login():
    data = request.json

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM users WHERE name=%s AND password=%s"
    cursor.execute(query, (data['name'], data['password']))

    user = cursor.fetchone()

    if user:
        return jsonify({
            "message": "Login successful",
            "user_id": user['id']
        })
    else:
        return jsonify({"error": "Invalid credentials"}), 401


# ---------------- CREATE POLICY ----------------
@app.route('/create-policy', methods=['POST'])
def create_policy():
    data = request.json

    user_id = data['user_id']
    weather = data['weather']
    aqi = data['aqi']
    traffic = data['traffic']

    risk_score = calculate_risk(weather, aqi, traffic)
    premium = calculate_premium(risk_score)

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO policies (user_id, weekly_premium, risk_score, status) VALUES (%s,%s,%s,%s)",
        (user_id, premium, risk_score, "active")
    )

    conn.commit()

    # 🔥 CLAIM LOGIC
    claim_data = {"claim_triggered": False}

    if risk_score > 0.7:
        is_fraud = detect_fraud(risk_score, aqi, traffic)
        payout = round(100 + (risk_score * 200), 2)

        status = "fraud" if is_fraud else "paid"

        cursor.execute(
            "INSERT INTO claims (user_id, payout_amount, status) VALUES (%s,%s,%s)",
            (user_id, payout, status)
        )
        conn.commit()

        claim_data = {
            "claim_triggered": True,
            "payout": payout,
            "fraud": is_fraud
        }

    return jsonify({
        "risk_score": risk_score,
        "weekly_premium": premium,
        "claim": claim_data
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
