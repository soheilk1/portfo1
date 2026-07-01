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

    // 3. BULLETPROOF CSS INJECTOR (Fixes PC disappearing and Mobile sticking)
    const fixCSS = document.createElement('style');
    fixCSS.innerHTML = `
        /* Desktop (PC) Failsafe: Forces menu to always be visible and left-aligned */
        @media (min-width: 768px) {
            #navbar-collapse.collapse {
                display: block !important;
                visibility: visible !important;
                height: auto !important;
                opacity: 1 !important;
            }
            .navbar-nav {
                float: left !important;
                margin-left: 0 !important;
            }
            .navbar-nav > li {
                float: left !important;
            }
        }

        /* Mobile Failsafe: Bypasses broken Bootstrap animations */
        @media (max-width: 767px) {
            #navbar-collapse.collapse {
                display: none !important;
                visibility: visible !important;
                height: auto !important;
            }
            #navbar-collapse.collapse.in {
                display: block !important;
            }
        }
    `;
    document.head.appendChild(fixCSS);
})();

const navbarHTML = `
<header>
  <nav class="navbar navbar-fixed-top navbar-inverse">
    <div class="container">
        <div class="navbar-header">
            <!-- Mobile Hamburger Button -->
            <button type="button" id="custom-mobile-btn" class="navbar-toggle collapsed" aria-expanded="false" style="border-color: #475569;">
              <span class="sr-only">Toggle navigation</span>
              <span class="icon-bar" style="background-color: white;"></span>
              <span class="icon-bar" style="background-color: white;"></span>
              <span class="icon-bar" style="background-color: white;"></span>
            </button>
            <a class="navbar-brand visible-xs" href="index.html" style="color: #38bdf8; font-weight: 900; font-family: 'JetBrains Mono', monospace; font-size: 14px;">SOHEIL-K //</a>
        </div>
      <div class="collapse navbar-collapse" id="navbar-collapse">
        <!-- Changed to navbar-left to ensure desktop alignment to the left -->
        <ul class="nav navbar-nav navbar-left" style="padding-left: 0;">
          <li><a href="./index.html" id="nav-home">01 : Home</a></li>
          <li><a href="./works.html" id="nav-works">02 : Works</a></li>
          <li><a href="./about.html" id="nav-about">03 : About me</a></li>
          <li><a href="./contact.html" id="nav-contact">04 : Contact</a></li>
          <li><a href="./resume.html" id="nav-resume">05 : Resume</a></li>
          <li><a href="./landing.html" id="nav-products">06 : Products</a></li>
        </ul>
      </div>
    </div>
  </nav>
</header>
`;

document.write(navbarHTML);

window.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;

    // --- BULLETPROOF MOBILE MENU FIX ---
    const mobileBtn = document.getElementById('custom-mobile-btn');
    const collapseMenu = document.getElementById('navbar-collapse');

    if (mobileBtn && collapseMenu) {
        mobileBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const isCurrentlyOpen = collapseMenu.classList.contains('in');

            if (isCurrentlyOpen) {
                collapseMenu.classList.remove('in');
                mobileBtn.classList.add('collapsed');
            } else {
                collapseMenu.classList.add('in');
                mobileBtn.classList.remove('collapsed');
            }
        });
    }

    // Ensure all active navigation states are stripped first
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
    } else if (path.includes('products.html') || path.includes('checkout.html') || path.includes('landing.html')) {
        const el = document.getElementById('nav-products');
        if (el) el.classList.add('active');
    }
});