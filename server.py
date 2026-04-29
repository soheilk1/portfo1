# ... existing code ...
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
# ... existing code ...