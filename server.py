import csv
import json
import os
import traceback
import smtplib
from datetime import datetime
from email.message import EmailMessage
import google.generativeai as genai
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, jsonify, make_response

app = Flask(__name__)

# ==========================================
# 1. LOAD HIDDEN SECRETS (.env)
# ==========================================
load_dotenv()

# ==========================================
# 2. CONTACT FORM EMAIL CONFIGURATION
# ==========================================
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "soheil3005@gmail.com")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", "soheil3005@gmail.com")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

# ==========================================
# 3. SECURE API KEY LOADING
# ==========================================
my_api_key = os.getenv("MY_SECRET_API_KEY")

try:
    if not my_api_key:
        raise ValueError("Could not find MY_SECRET_API_KEY in the .env file.")
    genai.configure(api_key=my_api_key)
    GEMINI_READY = True
except Exception as e:
    GEMINI_READY = False
    GEMINI_ERROR = str(e)


# ==========================================
# 4. GLOBAL CORS FIX (Crucial for Portal)
# ==========================================
@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
    response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
    return response


# ==========================================
# 5. BASIC PAGE ROUTING
# ==========================================
@app.route("/")
@app.route("/index.html")
def home():
    return render_template('index.html')


@app.route('/<string:page_name>')
def html_page(page_name):
    try:
        return render_template(page_name)
    except:
        return redirect("/")


# ==========================================
# 6. PORTAL SECURITY & UTILS
# ==========================================
def get_client_ip():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    return ip.split(',')[0].strip() if ip else "Unknown IP"


def get_portal_password():
    # Looks for password.txt in the same folder as server.py
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pwd_file = os.path.join(base_dir, 'password.txt')
    if os.path.exists(pwd_file):
        with open(pwd_file, 'r') as f:
            return f.read().strip()
    return "admin"


# ==========================================
# 7. ADMIN API (TRACKING & STATS)
# ==========================================
@app.route("/api/track_view", methods=['POST', 'OPTIONS'])
def track_view():
    if request.method == 'OPTIONS': return jsonify({}), 200
    try:
        ip = get_client_ip()
        base_dir = os.path.dirname(os.path.abspath(__file__))
        log_file = os.path.join(base_dir, 'visitor_ips.csv')

        data = request.get_json(silent=True) or {}
        page = data.get('page', 'unknown')

        with open(log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([ip, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), page])

        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/get_views", methods=['POST', 'OPTIONS'])
def get_views():
    if request.method == 'OPTIONS': return jsonify({}), 200
    data = request.get_json(silent=True) or {}
    if data.get('password') != get_portal_password():
        return jsonify({"error": "Unauthorized"}), 401

    visitors = []
    stats = {"home": 0, "resume": 0, "total": 0}

    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(base_dir, 'visitor_ips.csv')

    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    page_name = row[2].lower() if len(row) > 2 else "unknown"
                    visitors.append({"ip": row[0], "time": row[1], "page": page_name})

                    # Update counters
                    stats["total"] += 1
                    if "home" in page_name or "index" in page_name:
                        stats["home"] += 1
                    elif "resume" in page_name:
                        stats["resume"] += 1

    visitors.reverse()  # Show newest first
    return jsonify({
        "visitors": visitors[:100],
        "stats": stats,
        "password_ok": True
    }), 200


@app.route("/api/clear_views", methods=['POST', 'OPTIONS'])
def clear_views():
    if request.method == 'OPTIONS': return jsonify({}), 200
    data = request.get_json()
    if data.get('password') == get_portal_password():
        base_dir = os.path.dirname(os.path.abspath(__file__))
        open(os.path.join(base_dir, 'visitor_ips.csv'), 'w').close()
        return jsonify({"success": True})
    return jsonify({"error": "Auth failed"}), 401


# ==========================================
# 8. AI API (FIXED MODEL SELECTION)
# ==========================================
@app.route('/ask_gemini', methods=['POST', 'OPTIONS'])
def ask_gemini():
    if request.method == 'OPTIONS': return jsonify({}), 200

    try:
        if not GEMINI_READY:
            return jsonify({"error": f"AI offline. Details: {GEMINI_ERROR}"}), 200

        data = request.get_json(silent=True) or {}
        user_prompt = data.get('prompt')
        if not user_prompt: return jsonify({"error": "No question provided."}), 200

        # DYNAMICALLY FIND COMPATIBLE MODEL (Fixes 404 Error)
        available_model_name = None
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_model_name = m.name
                    if 'flash' in available_model_name or 'pro' in available_model_name:
                        break
        except:
            available_model_name = 'gemini-pro'  # Fallback

        system_instruction = (
            "You are the AI assistant for Soheil Karami, a DevSecOps & Cloud Engineer. "
            "Keep your answers brief, professional, and tech-focused. "
            f"Please answer this question: {user_prompt}"
        )

        model = genai.GenerativeModel(available_model_name)
        response = model.generate_content(system_instruction)
        return jsonify({"reply": response.text}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Internal Error: {str(e)}"}), 200


# ==========================================
# 9. CONTACT HELPERS
# ==========================================
@app.route('/api/send_contact', methods=['POST', 'OPTIONS'])
def send_contact():
    if request.method == 'OPTIONS': return jsonify({}), 200
    try:
        data = request.get_json()
        csv_path = os.path.join(os.path.dirname(__file__), 'database.csv')
        with open(csv_path, mode='a', newline='') as database:
            csv.writer(database).writerow([data.get("email"), data.get("subject"), data.get("message"), datetime.now()])

        if SENDER_PASSWORD:
            email = EmailMessage()
            email['From'], email['To'], email['Subject'] = SENDER_EMAIL, RECEIVER_EMAIL, f"Alert: {data.get('subject')}"
            email.set_content(f"Sender: {data.get('email')}\n\n{data.get('message')}")
            with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
                smtp.starttls()
                smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
                smtp.send_message(email)

        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)