import csv
import json
import os
import traceback
import smtplib
from datetime import datetime
from email.message import EmailMessage
import google.generativeai as genai
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, jsonify

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
# 4. BASIC PAGE ROUTING
# ==========================================
@app.route("/")
@app.route("/index.html")
def home():
    return render_template('index.html')


@app.route('/<string:page_name>')
def html_page(page_name):
    return render_template(page_name)


# ==========================================
# 5. PORTAL SECURITY & UTILS
# ==========================================
def get_client_ip():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    return ip.split(',')[0].strip() if ip else "Unknown IP"


def get_portal_password():
    pwd_file = os.path.join(os.path.dirname(__file__), 'password.txt')
    if os.path.exists(pwd_file):
        with open(pwd_file, 'r') as f:
            return f.read().strip()
    return "admin"


def is_ip_banned(ip):
    banned_file = os.path.join(os.path.dirname(__file__), 'banned_ips.txt')
    if os.path.exists(banned_file):
        with open(banned_file, 'r') as f:
            return ip in f.read().splitlines()
    return False


# ==========================================
# 6. ADMIN API (FOR PORTAL BUTTONS)
# ==========================================
@app.route("/api/track_view", methods=['POST', 'OPTIONS'])
def track_view():
    if request.method == 'OPTIONS': return jsonify({}), 200
    try:
        ip = get_client_ip()
        log_file = os.path.join(os.path.dirname(__file__), 'visitor_ips.csv')
        page = request.get_json(silent=True).get('page', 'unknown') if request.is_json else 'unknown'
        with open(log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([ip, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), page])

        # Update simple counter
        count_file = os.path.join(os.path.dirname(__file__), 'views.txt')
        count = int(open(count_file, 'r').read().strip() or 0) if os.path.exists(count_file) else 0
        with open(count_file, 'w') as f:
            f.write(str(count + 1))

        return jsonify({"success": True}), 200, {'Access-Control-Allow-Origin': '*'}
    except:
        return jsonify({"error": "fail"}), 500


@app.route("/api/get_views", methods=['POST', 'OPTIONS'])
def get_views():
    if request.method == 'OPTIONS': return jsonify({}), 200
    data = request.get_json(silent=True) or {}
    if data.get('password') != get_portal_password():
        return jsonify({"error": "Unauthorized"}), 401

    visitors = []
    log_file = os.path.join(os.path.dirname(__file__), 'visitor_ips.csv')
    if os.path.exists(log_file):
        with open(log_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 2:
                    visitors.append({"ip": row[0], "time": row[1], "page": row[2] if len(row) > 2 else "N/A"})

    visitors.reverse()
    return jsonify({"visitors": visitors[:100], "password_ok": True}), 200


@app.route("/api/clear_views", methods=['POST', 'OPTIONS'])
def clear_views():
    data = request.get_json()
    if data.get('password') == get_portal_password():
        open(os.path.join(os.path.dirname(__file__), 'visitor_ips.csv'), 'w').close()
        open(os.path.join(os.path.dirname(__file__), 'views.txt'), 'w').write("0")
        return jsonify({"success": True})
    return jsonify({"error": "Auth failed"}), 401


@app.route("/api/change_password", methods=['POST', 'OPTIONS'])
def change_password():
    data = request.get_json()
    if data.get('password') == get_portal_password():
        with open(os.path.join(os.path.dirname(__file__), 'password.txt'), 'w') as f:
            f.write(data.get('new_password').strip())
        return jsonify({"success": True})
    return jsonify({"error": "Auth failed"}), 401


# ==========================================
# 7. AI & CONTACT API
# ==========================================
@app.route('/api/send_contact', methods=['POST', 'OPTIONS'])
def send_contact():
    if request.method == 'OPTIONS': return jsonify({}), 200
    try:
        data = request.get_json()
        write_to_csv(data)
        send_email(data)
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/ask_gemini', methods=['POST', 'OPTIONS'])
def ask_gemini():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    try:
        # Check if the API key was successfully loaded at the top of the file
        if not GEMINI_READY:
            return jsonify({"error": "AI is currently offline (API key missing or invalid)."}), 500

        data = request.get_json()
        user_prompt = data.get('prompt')

        if not user_prompt:
            return jsonify({"error": "No question was provided."}), 400

        # Give the AI context so it answers intelligently about your portfolio
        system_instruction = (
            "You are the AI assistant for Soheil Karami, a DevSecOps & Cloud Engineer. "
            "Keep your answers brief, professional, and tech-focused. "
            "His core skills include Microsoft Azure, AWS, Python, Cybersecurity, and Linux. "
            f"Please answer this question from a recruiter/visitor: {user_prompt}"
        )

        # Call the Gemini model
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(system_instruction)

        # Send the generated text back to the frontend
        return jsonify({"reply": response.text}), 200

    except Exception as e:
        traceback.print_exc()  # Prints the exact error to your server logs
        return jsonify({"error": "AI encountered an internal error while processing the request."}), 500


# ==========================================
# 8. CONTACT HELPERS
# ==========================================
def write_to_csv(data):
    csv_path = os.path.join(os.path.dirname(__file__), 'database.csv')
    with open(csv_path, mode='a', newline='') as database:
        csv.writer(database).writerow([data.get("email"), data.get("subject"), data.get("message"), datetime.now()])


def send_email(data):
    if not SENDER_PASSWORD: return
    email = EmailMessage()
    email['From'] = SENDER_EMAIL
    email['To'] = RECEIVER_EMAIL
    email['Subject'] = f"Alert: {data.get('subject')}"
    email.set_content(f"Sender: {data.get('email')}\n\n{data.get('message')}")
    with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
        smtp.starttls()
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
        smtp.send_message(email)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)