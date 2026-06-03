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
from flask import request, redirect

@app.before_request
def force_https():
    if request.headers.get('X-Forwarded-Proto') == 'http':
        return redirect(request.url.replace('http://', 'https://', 1), code=301)

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
# 4. GLOBAL CORS FIX
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
    base_dir = os.path.dirname(os.path.abspath(__file__))
    pwd_file = os.path.join(base_dir, 'password.txt')
    if os.path.exists(pwd_file):
        with open(pwd_file, 'r') as f:
            return f.read().strip()
    return "admin"


def is_ip_banned(ip):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    banned_file = os.path.join(base_dir, 'banned_ips.txt')
    if os.path.exists(banned_file):
        with open(banned_file, 'r') as f:
            return ip in f.read().splitlines()
    return False


# ==========================================
# 6.5 LOGIN & RATE LIMITING
# ==========================================
def get_failed_logins():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(base_dir, 'failed_logins.json')
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_failed_logins(data):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(base_dir, 'failed_logins.json')
    with open(filepath, 'w') as f:
        json.dump(data, f)


@app.route("/api/login", methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS': return jsonify({}), 200

    ip = get_client_ip()
    logins = get_failed_logins()

    # 1. Check if the IP is already permanently banned in the text file, or locked in json
    if is_ip_banned(ip) or logins.get(ip, 0) >= 3:
        return jsonify({"error": "Terminal Locked. Access permanently denied."}), 403

    data = request.get_json(silent=True) or {}
    password_attempt = data.get('password', '')

    # 2. Verify the password
    if password_attempt == get_portal_password():
        # Success: Reset the tracking counter for this IP
        logins[ip] = 0
        save_failed_logins(logins)
        return jsonify({"success": True}), 200
    else:
        # Failure: Increment the counter
        current_strikes = logins.get(ip, 0) + 1
        logins[ip] = current_strikes
        save_failed_logins(logins)

        attempts_left = 3 - current_strikes

        # 3. TRIGGER PERMANENT BAN IF THEY HIT 3 STRIKES
        if current_strikes >= 3:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            ban_file = os.path.join(base_dir, 'banned_ips.txt')

            # Append the IP to the banned file
            with open(ban_file, 'a') as f:
                f.write(ip + '\n')

            return jsonify({"error": "Maximum attempts exceeded. IP permanently logged and banned."}), 403

        return jsonify({"error": f"Invalid password. {attempts_left} attempts remaining."}), 401


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


@app.route("/api/change_password", methods=['POST', 'OPTIONS'])
def change_password():
    if request.method == 'OPTIONS': return jsonify({}), 200
    data = request.get_json()
    if data.get('password') == get_portal_password():
        base_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(base_dir, 'password.txt'), 'w') as f:
            f.write(data.get('new_password').strip())
        return jsonify({"success": True})
    return jsonify({"error": "Auth failed"}), 401


# ==========================================
# 8. AI API (KNOWLEDGE BASE & CHAT MEMORY)
# ==========================================
@app.route('/ask_gemini', methods=['POST', 'OPTIONS'])
def ask_gemini():
    if request.method == 'OPTIONS': return jsonify({}), 200

    try:
        if not GEMINI_READY:
            return jsonify({"error": f"AI offline. Details: {GEMINI_ERROR}"}), 200

        data = request.get_json(silent=True) or {}
        user_prompt = data.get('prompt')
        chat_history = data.get('history', [])  # Retrieve the chat history from Javascript

        if not user_prompt: return jsonify({"error": "No question provided."}), 200

        # DYNAMICALLY FIND COMPATIBLE MODEL
        available_model_name = None
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_model_name = m.name
                    if 'flash' in available_model_name or 'pro' in available_model_name:
                        break
        except:
            available_model_name = 'gemini-pro'  # Fallback

        # --- SOHEIL'S AI KNOWLEDGE BASE ---
        soheil_profile = """
        Name: Soheil Karami
        Role: Cloud Infrastructure & DevSecOps Engineer
        Location: Kuala Lumpur, Malaysia
        Summary: Forward-thinking IT professional and DevSecOps Engineer with extensive experience in infrastructure management, cloud solutions, and enterprise systems administration. Specializes in bridging the gap between development and operations with a strong focus on web and application security.
        Experience: Track record includes designing Microsoft Azure cloud solutions, managing complex VMware environments, and implementing robust cybersecurity policies to protect sensitive business data. Strong Python programmer with a security-first approach to backend development, continuous improvement, and scalable network design.
        Cloud & Infra Skills: Microsoft Azure, AWS Hosting, VMware, Windows Server.
        Net & Security Skills: Cisco Design, Firewall & LAN, Vulnerability Assessments, Forefront TMG.
        Programming Skills: Python (Backend), Flutter Mobile, Java, PHP, HTML5 Design.
        Databases & Ops Skills: MySQL, SQL, Disaster Recovery, Project Management, Active Directory.
        Education: Master of Science in Software Management AND Bachelor of Information & Communications Technology (Both from Limkokwing University of Creative Technology, Kuala Lumpur).
        Certifications: Google AI Professional Certificate, Certificate of Cyber Security, Certificate of Python Zero to Mastery, Info Systems Management Certificate.
        """

        system_instruction = (
            "You are the professional AI assistant for Soheil Karami. "
            "Keep your answers brief, professional, and confident. "
            f"Use the following profile data to answer questions about him:\n{soheil_profile}"
        )

        # Initialize the model with the system instruction
        model = genai.GenerativeModel(
            model_name=available_model_name,
            system_instruction=system_instruction
        )

        # Start the chat session passing the memory history!
        chat = model.start_chat(history=chat_history)

        # Send the user's new message
        response = chat.send_message(user_prompt)

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
            email['From'] = SENDER_EMAIL
            email['To'] = RECEIVER_EMAIL
            email['Subject'] = f"Alert: {data.get('subject')}"
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