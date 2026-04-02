from flask import Flask, render_template, url_for, request, redirect, jsonify
import csv
import google.generativeai as genai  # Import the Gemini library

app = Flask(__name__)

# --- CONFIGURE GEMINI ---
# Replace 'YOUR_ACTUAL_API_KEY' with your real key
genai.configure(api_key="AIzaSyB0V0lro7mpdEv6v3DK_TvxZOMsCw92SoU")
model = genai.GenerativeModel('gemini-1.5-flash')

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

        # Call Gemini via Python SDK (more reliable than URL)
        response = model.generate_content(user_prompt)
        
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
        csv_writer = csv.writer(database, delimiter=',', quotechar='&', quoting=csv.QUOTE_MINIMAL)
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
