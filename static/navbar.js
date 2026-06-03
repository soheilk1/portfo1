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
          <li><a href="./products.html" id="nav-products">06 : Products</a></li>
        </ul>
      </div>
    </div>
  </nav>
</header>
`;

// Inject the HTML
document.write(navbarHTML);

// Dynamically set the "active" class based on the current URL
window.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;

    if (path.endsWith('/') || path.includes('index.html')) {
        document.getElementById('nav-home').classList.add('active');
    } else if (path.includes('works.html')) {
        document.getElementById('nav-works').classList.add('active');
    } else if (path.includes('about.html')) {
        document.getElementById('nav-about').classList.add('active');
    } else if (path.includes('contact.html')) {
        document.getElementById('nav-contact').classList.add('active');
    } else if (path.includes('resume.html')) {
        document.getElementById('nav-resume').classList.add('active');
    } else if (path.includes('products.html') || path.includes('checkout.html')) {
        document.getElementById('nav-products').classList.add('active');
    }
});