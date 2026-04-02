from flask import Flask, render_template, url_for, request, redirect, jsonify
import csv
import google.generativeai as genai  # Import the Gemini library

app = Flask(__name__)

# --- CONFIGURE GEMINI ---
# Replace with your real key if this one ever changes
genai.configure(api_key="AIzaSyB0V0lro7mpdEv6v3DK_TvxZOMsCw92SoU")

@app.route("/")
@app.route("/index.html")
def home():
    return render_template('index.html')

# New Route to handle AI requests from your resume page
@app.route('/ask_gemini', methods=['POST'])
def ask_gemini():
    try:
        # Get the prompt from the frontend JavaScript
        user_data = request.json
        user_prompt = user_data.get('prompt')

        # Auto-fallback list to handle Google's changing model names
        models_to_try = [
            'gemini-1.5-flash',
            'gemini-1.5-flash-latest',
            'gemini-1.5-pro',
            'gemini-pro'
        ]
        
        response = None
        last_error = ""

        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(user_prompt)
                break  # Success! Exit the fallback loop
            except Exception as e:
                last_error = str(e)
                # If it's a 404 (Not Found), the loop continues to try the next model
                if "404" not in last_error:
                    raise e  # Throw real errors (like 403 API Key Invalid) immediately
        
        if response is None:
            raise Exception(f"All models failed. Last error: {last_error}")

        return jsonify({"reply": response.text})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/<string:page_name>')
def html_page(page_name):
    return render_template(page_name)

# --- YOUR EXISTING DATABASE LOGIC ---
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
