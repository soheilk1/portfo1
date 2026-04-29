# ==========================================
# 8. AI API (FIXED MODEL SELECTION & KNOWLEDGE BASE)
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
            f"Use the following profile data to answer questions about him:\n{soheil_profile}\n\n"
            f"Please answer this question from a recruiter/visitor: {user_prompt}"
        )

        model = genai.GenerativeModel(available_model_name)
        response = model.generate_content(system_instruction)
        return jsonify({"reply": response.text}), 200

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Internal Error: {str(e)}"}), 200