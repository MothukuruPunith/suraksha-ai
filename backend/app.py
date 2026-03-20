from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
import sys
import os

# Add root path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ai.risk_model import calculate_risk, calculate_premium
from ai.fraud_model import detect_fraud
from services.db import get_db_connection

app = Flask(__name__)

# ✅ Proper CORS
CORS(app, resources={r"/*": {"origins": "*"}})


# 🧠 CLAIM FUNCTION (NO CORS HERE)
def check_and_create_claim(user_id, risk_score, aqi, traffic):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        if risk_score > 0.7:

            is_fraud = detect_fraud(risk_score, aqi, traffic)
            payout = round(100 + (risk_score * 200), 2)

            status = "fraud" if is_fraud else "paid"

            query = """
            INSERT INTO claims (user_id, payout_amount, status)
            VALUES (%s, %s, %s)
            """
            cursor.execute(query, (user_id, payout, status))
            conn.commit()

            return {
                "claim_triggered": True,
                "payout": payout,
                "fraud": is_fraud
            }

        return {"claim_triggered": False}

    except Exception as e:
        return {"error": str(e)}


@app.route('/')
def home():
    return jsonify({"message": "SurakshaAI Backend Running 🚀"})


# 🔥 REGISTER
@app.route('/register', methods=['POST', 'OPTIONS'])
@cross_origin()
def register():
    try:
        data = request.get_json()

        name = data.get('name')
        password = data.get('password')
        location = data.get('location')
        worker_type = data.get('worker_type')

        conn = get_db_connection()
        cursor = conn.cursor()

        query = "INSERT INTO users (name, password, location, worker_type) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, password, location, worker_type))

        conn.commit()
        user_id = cursor.lastrowid

        return jsonify({
            "message": "User registered successfully",
            "user_id": user_id
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔥 LOGIN
@app.route('/login', methods=['POST', 'OPTIONS'])
@cross_origin()
def login():
    try:
        data = request.get_json()

        name = data.get('name')
        password = data.get('password')

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM users WHERE name=%s AND password=%s"
        cursor.execute(query, (name, password))

        user = cursor.fetchone()

        if user:
            return jsonify({
                "message": "Login successful",
                "user_id": user['id']
            })
        else:
            return jsonify({"error": "Invalid credentials"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 🔥 CREATE POLICY
@app.route('/create-policy', methods=['POST', 'OPTIONS'])
@cross_origin()
def create_policy():
    try:
        data = request.get_json()

        user_id = data.get('user_id')
        weather = data.get('weather')
        aqi = data.get('aqi')
        traffic = data.get('traffic')

        risk_score = calculate_risk(weather, aqi, traffic)
        premium = calculate_premium(risk_score)

        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
        INSERT INTO policies (user_id, weekly_premium, risk_score, status)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (user_id, premium, risk_score, "active"))
        conn.commit()

        claim_result = check_and_create_claim(user_id, risk_score, aqi, traffic)

        return jsonify({
            "message": "Policy created successfully",
            "risk_score": risk_score,
            "weekly_premium": premium,
            "claim": claim_result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)