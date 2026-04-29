# portfo1
Soheil Karami | DevSecOps Portfolio
🚀 Engineering Secure & Scalable Digital Solutions

Live Demo: soheilk.online
📌 Overview

This repository contains the source code and infrastructure configuration for my professional portfolio. Beyond a simple resume site, this project serves as a live demonstration of my transition from IT Help Desk to DevSecOps, showcasing my ability to build, secure, and automate web applications.
🛠 Tech Stack

    Frontend: HTML5, CSS3 (Modern, Responsive Design)

    Backend: Python

    Infrastructure: Google Cloud Platform (GCP)

    CI/CD: Google Cloud Build & Cloud Run

    Security: Cloud DNS (SSL/TLS), Identity & Access Management (IAM)

    Containerization: Docker

🛡 DevSecOps Features

As a DevSecOps-focused engineer, I have implemented the following to ensure the integrity and availability of this site:

    Automated Deployment: Every push to the main branch triggers a Google Cloud Build trigger, ensuring consistent and reproducible deployments.

    Container Security: The application is containerized using Docker, allowing for environment parity and reduced attack surface.

    Cloud-Native Architecture: Leveraging Serverless (Cloud Run) to ensure high availability and automatic scaling.

    Infrastructure as Code (IaC) Principles: Managed through GCP console with a focus on least-privilege access for service accounts.

📂 Project Structure
Bash

├── .github/          # GitHub Actions (if applicable)
├── src/              # Python source code & website assets
├── Dockerfile        # Containerization instructions
├── cloudbuild.yaml   # GCP CI/CD configuration
├── requirements.txt  # Python dependencies
└── README.md         # Project documentation

🚀 Deployment Process

The site is deployed using a modern CI/CD pipeline:

    Code Commit: Changes are pushed to GitHub.

    Build: Google Cloud Build pulls the source and builds the Docker image.

    Security Scan: (Optional/Planned) Integrating Snyk or Trivy for container vulnerability scanning.

    Deploy: The image is pushed to Artifact Registry and deployed to Cloud Run.

📈 Roadmap

    [ ] Integrate OWASP ZAP for automated DAST scanning.

    [ ] Implement Terraform for full Infrastructure as Code (IaC).

    [ ] Add a blog section managed by a Markdown-based CMS.

🤝 Contact

    Website: soheilk.online

    LinkedIn: [Your LinkedIn Profile Link]

    Email: [Your Email Address]

Built with ❤️ and a focus on security.
Tips for your GitHub Repository:

    Add a Thumbnail: In your GitHub repository settings, upload a "Social Preview" image. A screenshot of your website works best.

    Use Tags: Add topics to your repo like devsecops, python, google-cloud-platform, and portfolio.

    The "About" Section: Ensure the "Website" field in the GitHub sidebar points to soheilk.online.
