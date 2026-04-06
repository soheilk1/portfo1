from flask import Flask, render_template, request, redirect, jsonify
import csv
import traceback
import os

app = Flask(__name__)

# --- SECURE API KEY LOADING ---
# Instead of hardcoding the key, we read it securely from a file called "api_key.txt"
try:
    # Look for the file in the same directory as server.py
    key_path = os.path.join(os.path.dirname(__file__), 'api_key.txt')
    with open(key_path, 'r') as key_file:
        my_secret_key = key_file.read().strip()

    import google.generativeai as genai

    genai.configure(api_key=my_secret_key)
    GEMINI_READY = True

except ImportError as e:
    GEMINI_READY = False
    GEMINI_ERROR = f"Library missing: {str(e)}"
except FileNotFoundError:
    GEMINI_READY = False
    GEMINI_ERROR = "Could not find 'api_key.txt'. Please create this file and paste your API key inside it."
except Exception as e:
    GEMINI_READY = False
    GEMINI_ERROR = f"Failed to load API key: {str(e)}"


@app.route("/")
@app.route("/index.html")
def home():
    return render_template('index.html')


# Route to handle AI requests from your resume page
@app.route('/ask_gemini', methods=['POST', 'OPTIONS'])
def ask_gemini():
    # 1. Handle CORS Preflight requests (prevents browser security blocks)
    if request.method == 'OPTIONS':
        return jsonify({}), 200, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type'
        }

    try:
        # 2. Check if the library/key successfully loaded
        if not GEMINI_READY:
            raise Exception(f"Setup Error: {GEMINI_ERROR}")

        # 3. Safely parse JSON data
        user_data = request.get_json(silent=True)
        if not user_data:
            raise Exception("Invalid or missing JSON data received from the browser.")

        user_prompt = user_data.get('prompt')
        if not user_prompt:
            raise Exception("No 'prompt' found in the received data.")

        # 4. AUTO-DISCOVERY: Find exactly which models your API key is allowed to use
        valid_models = []
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    valid_models.append(m.name)
        except Exception as e:
            raise Exception(f"Could not connect to Google to list models. Is your API key valid? Error: {str(e)}")

        if not valid_models:
            raise Exception("Your API key is valid, but it does not have permission to use ANY text generation models.")

        # 5. Pick the best available model (Prefer 1.5-flash)
        selected_model = valid_models[0]
        for m in valid_models:
            if '1.5-flash' in m:
                selected_model = m
                break

        clean_model_name = selected_model.replace('models/', '')

        # 6. Generate the content
        response = None
        try:
            model = genai.GenerativeModel(clean_model_name)
            response = model.generate_content(user_prompt)
        except Exception as e:
            raise Exception(
                f"Failed using model '{clean_model_name}'. Error: {str(e)} | Models available: {valid_models}")

        if not response or not response.text:
            raise Exception("The AI model returned an empty response.")

        # Return success with CORS headers
        return jsonify({"reply": response.text}), 200, {'Access-Control-Allow-Origin': '*'}

    except Exception as e:
        error_trace = traceback.format_exc()
        print(error_trace)
        return jsonify({"error": f"Python Crash: {str(e)}"}), 500, {'Access-Control-Allow-Origin': '*'}


@app.route('/<string:page_name>')
def html_page(page_name):
    return render_template(page_name)


# --- EXISTING DATABASE LOGIC ---
def write_to_csv(data):
    with open('database.csv', mode='a', newline='') as database:
        email = data["email"]
        subject = data["subject"]
        message = data["message"]
        csv_writer = csv.writer(database, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow([email, subject, message])


@app.route('/submit_form', methods=['POST', 'GET'])
def submit_form():
    if request.method == 'POST':
        try:
            data = request.form.to_dict()
            write_to_csv(data)
            return redirect('/thankyou.html')
        except:
            return 'Did not save to database'
    else:
        return 'something went wrong. try again!'