(function() {
    // 1. Ensure Bootstrap 3 core CSS is loaded
    if (!document.querySelector('link[href*="bootstrap.min.css"]') && !document.querySelector('link[href*="bootstrap/3.3.7"]')) {
        const bootstrapCSS = document.createElement('link');
        bootstrapCSS.rel = 'stylesheet';
        bootstrapCSS.href = 'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css';
        document.head.appendChild(bootstrapCSS);
    }

    // 2. Ensure Inter and JetBrains Mono Google Fonts are loaded
    if (!document.querySelector('link[href*="fonts.googleapis.com"]')) {
        const fontsLink = document.createElement('link');
        fontsLink.rel = 'stylesheet';
        fontsLink.href = 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap';
        document.head.appendChild(fontsLink);
    }

    // 3. Ensure your local custom style rules (main.3f6952e4.css) are loaded
    if (!document.querySelector('link[href*="main.3f6952e4.css"]')) {
        const localCSS = document.createElement('link');
        localCSS.rel = 'stylesheet';
        localCSS.href = './static/main.3f6952e4.css';
        document.head.appendChild(localCSS);
    }
})();

const navbarHTML = `
<header>
  <nav class="navbar navbar-fixed-top navbar-inverse">
    <div class="container">
        <div class="navbar-header">
            <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar-collapse" aria-expanded="false" style="border-color: #475569;">
              <span class="sr-only">Toggle navigation</span>
              <span class="icon-bar" style="background-color: white;"></span>
              <span class="icon-bar" style="background-color: white;"></span>
              <span class="icon-bar" style="background-color: white;"></span>
            </button>
        </div>
      <div class="collapse navbar-collapse" id="navbar-collapse">
        <ul class="nav navbar-nav">
          <li><a href="./index.html" id="nav-home">01 : Home</a></li>
          <li><a href="./works.html" id="nav-works">02 : Works</a></li>
          <li><a href="./about.html" id="nav-about">03 : About me</a></li>
          <li><a href="./contact.html" id="nav-contact">04 : Contact</a></li>
          <li><a href="./resume.html" id="nav-resume">05 : Resume</a></li>
          <li><a href="./landing.html" id="nav-products">06 : landing</a></li>
        </ul>
      </div>
    </div>
  </nav>
</header>
`;

document.write(navbarHTML);

window.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;

    // Ensure all active navigation states are stripped first to avoid multiple highlights
    const navItems = ['nav-home', 'nav-works', 'nav-about', 'nav-contact', 'nav-resume', 'nav-products'];
    navItems.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.remove('active');
    });

    // Highlight the active element
    if (path.endsWith('/') || path.includes('index.html')) {
        const el = document.getElementById('nav-home');
        if (el) el.classList.add('active');
    } else if (path.includes('works.html')) {
        const el = document.getElementById('nav-works');
        if (el) el.classList.add('active');
    } else if (path.includes('about.html')) {
        const el = document.getElementById('nav-about');
        if (el) el.classList.add('active');
    } else if (path.includes('contact.html') || path.includes('thankyou.html')) {
        const el = document.getElementById('nav-contact');
        if (el) el.classList.add('active');
    } else if (path.includes('resume.html')) {
        const el = document.getElementById('nav-resume');
        if (el) el.classList.add('active');
    } else if (path.includes('landing.html') || path.includes('checkout.html')) {
        const el = document.getElementById('nav-products');
        if (el) el.classList.add('active');
    }
});