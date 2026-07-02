# ... (Keep all your existing imports and setup code exactly as they are)

# ==========================================
# 5. BASIC PAGE ROUTING (Updated)
# ==========================================
@app.route("/")
@app.route("/index.html")
def home():
    return render_template('index.html')

# NEW CLEAN ROUTE FOR LANDING PAGE
@app.route("/services")
def services():
    return render_template('landing.html')

@app.route('/<string:page_name>')
def html_page(page_name):
    try:
        return render_template(page_name)
    except:
        return redirect("/")

# ... (Keep all your existing Security & Admin API code exactly as it is)

# ==========================================
# 10. Sitemap Route (Updated for Clean URL)
# ==========================================

@app.route('/sitemap.xml')
def sitemap():
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <!-- Home / Portal Page -->
  <url>
    <loc>https://soheilk.online/</loc>
    <lastmod>2026-07-02</lastmod>
    <changefreq>weekly</changefreq>
    <priority>1.0</priority>
  </url>

  <!-- Clean Product Landing URL -->
  <url>
    <loc>https://soheilk.online/services</loc>
    <lastmod>2026-07-02</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>

  <!-- Resume Page -->
  <url>
    <loc>https://soheilk.online/resume</loc>
    <lastmod>2026-07-02</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>

  <!-- Secure Portal -->
  <url>
    <loc>https://soheilk.online/portal</loc>
    <lastmod>2026-07-02</lastmod>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>"""
    return Response(xml_content, mimetype='application/xml')