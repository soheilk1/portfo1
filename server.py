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
# This tells Flask to look for the hidden .env file and load the keys inside it
load_dotenv()

# ==========================================
# 2. CONTACT FORM EMAIL CONFIGURATION
# ==========================================
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "soheil3005@gmail.com")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL", "soheil3005@gmail.com")

# SECURITY: Never hardcode passwords! We pull this from the .env file now.
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

except ImportError as e:
    GEMINI_READY = False
    GEMINI_ERROR = f"Library missing: {str(e)}"
except Exception as e:
    GEMINI_READY = False
    GEMINI_ERROR = f"Failed to load API key: {str(e)}"

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
# 5. PORTAL SECURITY & ANTI-BRUTE FORCE
# ==========================================
def get_client_ip():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    if ip:
        return ip.split(',')[0].strip()
    return "Unknown IP"

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
            if ip in f.read().splitlines():
                return True
    return False

def record_failed_attempt(ip):
    attempts_file = os.path.join(os.path.dirname(__file__), 'failed_attempts.json')
    attempts = {}
    if os.path.exists(attempts_file):
        try:
            with open(attempts_file, 'r') as f:
                attempts = json.load(f)
        except:
            pass

    attempts[ip] = attempts.get(ip, 0) + 1

    if attempts[ip] >= 3:
        banned_file = os.path.join(os.path.dirname(__file__), 'banned_ips.txt')
        with open(banned_file, 'a') as f:
            f.write(ip + '\n')

    with open(attempts_file, 'w') as f:
        json.dump(attempts, f)

def reset_failed_attempt(ip):
    attempts_file = os.path.join(os.path.dirname(__file__), 'failed_attempts.json')
    if os.path.exists(attempts_file):
        try:
            with open(attempts_file, 'r') as f:
                attempts = json.load(f)
            if ip in attempts:
                del attempts[ip]
                with open(attempts_file, 'w') as f:
                    json.dump(attempts, f)
        except:
            pass

# ==========================================
# 6. ADMIN DASHBOARD & ANALYTICS
# ==========================================
@app.route("/api/track_view", methods=['POST', 'OPTIONS'])
def track_view():
    if request.method == 'OPTIONS':
        return jsonify({}), 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*'}
    try:
        ip = get_client_ip()
        log_file = os.path.join(os.path.dirname(__file__), 'visitor_ips.csv')
        with open(log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([ip, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

        count = 0
        count_file = os.path.join(os.path.dirname(__file__), 'views.txt')
        if os.path.exists(count_file):
            with open(count_file, 'r') as f:
                content = f.read().strip()
                if content.isdigit():
                    count = int(content)
        count += 1
        with open(count_file, 'w') as f:
            f.write(str(count))
        return jsonify({"views": count}), 200, {'Access-Control-Allow-Origin': '*'}
    except Exception as e:
        return jsonify({"error": str(e)}), 500, {'Access-Control-Allow-Origin': '*'}

@app.route("/api/get_views", methods=['POST', 'OPTIONS'])
def get_views():
    if request.method == 'OPTIONS':
        return jsonify({}), 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*'}
    try:
        ip = get_client_ip()

        if is_ip_banned(ip):
            return jsonify({"error": "IP Banned"}), 403, {'Access-Control-Allow-Origin': '*'}

        data = request.get_json(silent=True) or {}
        if data.get('password') != get_portal_password():
            record_failed_attempt(ip)
            return jsonify({"error": "Unauthorized"}), 401, {'Access-Control-Allow-Origin': '*'}

        reset_failed_attempt(ip)

        count = 0
        count_file = os.path.join(os.path.dirname(__file__), 'views.txt')
        if os.path.exists(count_file):
            with open(count_file, 'r') as f:
                content = f.read().strip()
                if content.isdigit():
                    count = int(content)

        visitors = []
        log_file = os.path.join(os.path.dirname(__file__), 'visitor_ips.csv')
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 2:
                        visitors.append({"ip": row[0], "time": row[1]})

        visitors.reverse()
        recent_visitors = visitors[:100]

        return jsonify({"views": count, "visitors": recent_visitors}), 200, {'Access-Control-Allow-Origin': '*'}
    except Exception as e:
        return jsonify({"error": str(e)}), 500, {'Access-Control-Allow-Origin': '*'}

@app.route("/api/clear_views", methods=['POST', 'OPTIONS'])
def clear_views():
    if request.method == 'OPTIONS':
        return jsonify({}), 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*'}
    try:
        ip = get_client_ip()
        if is_ip_banned(ip):
            return jsonify({"error": "IP Banned"}), 403, {'Access-Control-Allow-Origin': '*'}

        data = request.get_json(silent=True) or {}
        if data.get('password') != get_portal_password():
            record_failed_attempt(ip)
            return jsonify({"error": "Unauthorized"}), 401, {'Access-Control-Allow-Origin': '*'}

        reset_failed_attempt(ip)

        count_file = os.path.join(os.path.dirname(__file__), 'views.txt')
        with open(count_file, 'w') as f:
            f.write("0")

        log_file = os.path.join(os.path.dirname(__file__), 'visitor_ips.csv')
        with open(log_file, 'w') as f:
            pass

        return jsonify({"success": True}), 200, {'Access-Control-Allow-Origin': '*'}
    except Exception as e:
        return jsonify({"error": str(e)}), 500, {'Access-Control-Allow-Origin': '*'}

@app.route("/api/change_password", methods=['POST', 'OPTIONS'])
def change_password():
    if request.method == 'OPTIONS':
        return jsonify({}), 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': '*'}
    try:
        ip = get_client_ip()
        if is_ip_banned(ip):
            return jsonify({"error": "IP Banned"}), 403, {'Access-Control-Allow-Origin': '*'}

        data = request.get_json(silent=True) or {}
        if data.get('password') != get_portal_password():
            record_failed_attempt(ip)
            return jsonify({"error": "Unauthorized"}), 401, {'Access-Control-Allow-Origin': '*'}

        reset_failed_attempt(ip)

        new_pwd = data.get('new_password')
        if not new_pwd:
            return jsonify({"error": "Invalid password"}), 400, {'Access-Control-Allow-Origin': '*'}

        pwd_file = os.path.join(os.path.dirname(__file__), 'password.txt')
        with open(pwd_file, 'w') as f:
            f.write(new_pwd.strip())

        return jsonify({"success": True}), 200, {'Access-Control-Allow-Origin': '*'}
    except Exception as e:
        return jsonify({"error": str(e)}), 500, {'Access-Control-Allow-Origin': '*'}

# ==========================================
# 7. AI RESUME LOGIC (With Persona Jailbreak)
# ==========================================
@app.route('/ask_gemini', methods=['POST', 'OPTIONS'])
def ask_gemini():
    if request.method == 'OPTIONS':
        return jsonify({}), 200, {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Content-Type'}

    try:
        if not GEMINI_READY:
            raise Exception(f"Setup Error: {GEMINI_ERROR}")

        user_data = request.get_json(silent=True)
        if not user_data:
            raise Exception("Invalid or missing JSON data received from the browser.")

        user_prompt = user_data.get('prompt')
        if not user_prompt:
            raise Exception("No 'prompt' found in the received data.")

        # --- THE JAILBREAK CONTEXT ---
        system_context = """
        You are an AI assistant built into the portfolio website of Soheil Karami. 
        You MUST act as his professional representative. 

        CRITICAL RULES:
        1. Soheil Karami is NOT a football player. 
        2. Soheil Karami is a highly skilled Cloud Infrastructure & DevSecOps Engineer.
        3. His top skills are: Python backend development, Microsoft Azure, AWS, VMware, Cybersecurity, and Linux server administration.
        4. He has built projects like an Automated Server Threat Detector and an AWS/Azure IaC Cloud Provisioner.
        5. He has a Master of Science in Software Management.
        6. Be professional, concise, and highly technical. Do not invent information that is not listed here.

        User Question: 
        """

        full_prompt = system_context + user_prompt

        valid_models = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    valid_models.append(m.name)
        except Exception as e:
            raise Exception(f"Could not connect to Google to list models. Error: {str(e)}")

        if not valid_models:
            raise Exception("No text generation models available.")

        selected_model = valid_models[0]
        for m in valid_models:
            if '1.5-flash' in m:
                selected_model = m
                break

        clean_model_name = selected_model.replace('models/', '')

        response = None
        try:
            model = genai.GenerativeModel(clean_model_name)
            response = model.generate_content(full_prompt)
        except Exception as e:
            raise Exception(f"Failed using model '{clean_model_name}'. Error: {str(e)}")

        if not response or not response.text:
            raise Exception("The AI model returned an empty response.")

        return jsonify({"reply": response.text}), 200, {'Access-Control-Allow-Origin': '*'}

    except Exception as e:
        error_trace = traceback.format_exc()
        print(error_trace)
        return jsonify({"error": f"Python Crash: {str(e)}"}), 500, {'Access-Control-Allow-Origin': '*'}

# ==========================================
# 8. CONTACT FORM DATABASE & EMAIL LOGIC
# ==========================================
def write_to_csv(data):
    csv_path = os.path.join(os.path.dirname(__file__), 'database.csv')
    with open(csv_path, mode='a', newline='') as database:
        email = data.get("email", "Unknown")
        subject = data.get("subject", "No Subject")
        message = data.get("message", "")
        csv_writer = csv.writer(database, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([email, subject, message, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

def send_email(data):
    user_email = data.get("email", "Unknown")
    user_subject = data.get("subject", "No Subject")
    user_message = data.get("message", "")

    if not SENDER_PASSWORD:
        raise Exception("SENDER_PASSWORD is not set in the .env file")

    email = EmailMessage()
    email['From'] = SENDER_EMAIL
    email['To'] = RECEIVER_EMAIL
    email['Subject'] = f"PORTFOLIO ALERT: {user_subject}"
    email.set_content(
        f"You received a new secure transmission from your portfolio!\n\nSENDER: {user_email}\n\nMESSAGE:\n{user_message}")

    with smtplib.SMTP(host='smtp.gmail.com', port=587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
        smtp.send_message(email)

@app.route('/submit_form', methods=['POST', 'GET'])
def submit_form():
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            write_to_csv(data)  # Save to CSV Database

            try:
                send_email(data)
            except Exception as email_err:
                # Log the error on the server quietly, but don't crash the website for the user
                print(f"Warning: Email failed to send. Google says: {email_err}")

            # Send them to the Thank You page regardless of email success, since the CSV saved properly
            return redirect('/thankyou.html')
            
        except Exception as e:
            return f'Did not save to database. Error: {str(e)}'
    else:
        return 'Something went wrong. Try again!'

# ==========================================
# 9. GOOGLE CLOUD EXECUTION
# ==========================================
if __name__ == '__main__':
    # Google Cloud dynamically assigns the port via environment variables
    port = int(os.environ.get('PORT', 8080))
    # host='0.0.0.0' is required to make the server accessible publicly in the Cloud
    app.run(host='0.0.0.0', port=port, debug=False)
