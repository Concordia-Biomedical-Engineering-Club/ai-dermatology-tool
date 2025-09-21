
# AI Dermatology Diagnostic Tool

An intelligent, cloud-native tool designed to assist in the preliminary analysis of dermatological conditions using a hybrid AI approach.

<!-- Optional: Add a build status badge here once you set up CI/CD -->
<!-- ![GitHub Actions CI](https://github.com/Concordia-Biomedical-Engineering-Club/ai-dermatology-tool/actions/workflows/ci.yml/badge.svg) -->

---

## 📖 Table of Contents

- [About The Project](#about-the-project)
- [✨ Key Features](#-key-features)
- [🛠️ Tech Stack](#️-tech-stack)
- [🏛️ System Architecture](#️-system-architecture)
- [🚀 Getting Started](#-getting-started)
- [📂 Project Structure](#-project-structure)
- [🤝 Contributing](#-contributing)
- [⚖️ License](#️-license)
- [📞 Contact](#-contact)

---

## ℹ️ About The Project

The AI Dermatology Diagnostic Tool is a **clinical decision-support system** designed to assist healthcare professionals—particularly in underserved and resource-limited areas—in making faster and more accurate preliminary dermatological diagnoses.

Developed by the Concordia Biomedical Engineering Club, this project combines a powerful visual analysis CNN with a symptom analysis engine to provide a comprehensive, evidence-based differential diagnosis.

---

## ✨ Key Features

- **Hybrid Diagnostic Engine:** Fuses CNN image predictions with a symptom-based algorithm for a more comprehensive analysis.
- **Broad Knowledge Base:** The symptom matcher covers over 320 conditions, while the CNN is trained to recognize 23 common visual classes.
- **Cloud-Native & Scalable:** Designed with a modern, serverless architecture on AWS for high performance and accessibility.
- **Built for the Edge:** Leverages an optimized TensorFlow Lite model, specifically designed for **offline inference on mobile devices**, ensuring functionality in areas with limited or no internet connectivity.
- **Developer-Friendly:** Containerized with Docker and includes a CI/CD pipeline for reliable and automated testing.

---

## 🛠️ Tech Stack

This project is built with a modern set of tools and frameworks:

- **Backend:** 🚀 FastAPI, 🐍 Python
- **Machine Learning:** 🧠 TensorFlow, Keras, TFLite
- **Frontend:** ⚛️ React.js
- **DevOps:** 🐳 Docker, 🐙 GitHub Actions
- **Cloud:** ☁️ AWS (SageMaker, Lambda, API Gateway)
- **Project Management:** 📋 GitHub Projects, Notion

---

## 🏛️ System Architecture

The application is designed as a modular, multi-component system:

1.  **Frontend (React):** The user interacts with a single-page application to input symptoms and upload images.
2.  **API Gateway:** All frontend requests are routed through a secure and scalable AWS API Gateway.
3.  **Backend (AWS Lambda):** The business logic is hosted in a serverless function. It receives the request, calls the appropriate service (symptom or image analysis), and returns the result.
4.  **Inference Service:** The TFLite model is loaded into the service for performing image-based predictions.
5.  **Scoring Service:** The keyword-matching algorithm runs to score conditions based on text inputs.

---

## 🚀 Getting Started

To get a local copy up and running, please follow these simple steps.

### Prerequisites

Make sure you have the following installed on your machine:
- [Git](https://git-scm.com/)
- [Python](https://www.python.org/downloads/) 3.9+
- [Docker](https://www.docker.com/products/docker-desktop/) (Optional, for containerization)

### Local Development Setup

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/Concordia-Biomedical-Engineering-Club/ai-dermatology-tool.git
    cd ai-dermatology-tool
    ```

2.  **Set up the Python Backend:**
    *   Create and activate a virtual environment:
        ```sh
        # For macOS/Linux
        python3 -m venv venv
        source venv/bin/activate

        # For Windows
        python -m venv venv
        .\venv\Scripts\activate
        ```
    *   Install the required dependencies:
        ```sh
        pip install -r api/requirements.txt
        ```

3.  **Run the API Server:**
    *   The server will run using Uvicorn. The `--reload` flag enables hot-reloading for development.
        ```sh
        uvicorn api.main:app --reload
        ```
    *   Your API is now running! You can view the interactive documentation at `http://127.0.0.1:8000/docs`.

4.  **Set up the Frontend (Coming Soon):**
    *   Instructions for starting the React development server will be added here once the frontend is initialized.

---

## 📂 Project Structure

```

/ai-dermatology-tool
├── .github/ # GitHub Actions workflows and templates
├── api/ # All FastAPI backend code, services, and models
├── docs/ # Project documentation and architectural decisions
├── reference_code/ # Legacy scripts used as a blueprint for refactoring
├── webapp/ # React frontend application (coming soon)
├── CONTRIBUTING.md   # Guidelines for contributors
└── README.md         # This file
```

---

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests to us.


---

## ⚠️ Disclaimer

This project is for educational and portfolio purposes only. The models and predictions generated by the AI Dermatology Diagnostic Tool are **not a substitute for professional medical judgment and diagnosis.**

This tool is designed to be an informational aid and a **preliminary decision-support tool for qualified healthcare professionals.** It is **not a certified medical device** and should not be used for primary diagnosis or treatment decisions.

**Always consult a qualified dermatologist for any health concerns.**

---

## ⚖️ License & Commercial Use

This project is licensed under the **GNU Affero General Public License v3.0 (AGPLv3)**. See the `LICENSE` file for the full text.

In simple terms, this means you are free to use, modify, and distribute this software, provided that any derivative work you make available over a network is also licensed under the AGPLv3 and you share its source code.

**For inquiries about alternative commercial licensing** for use in proprietary, closed-source applications, please contact the project lead.

---

## 📞 Contact

**Youssef Jedidi** - Project Lead

- **Email:** `youssefjedidi2022 [at] gmail [dot] com`
- **LinkedIn:** [Youssef Jedidi's Profile](https://www.linkedin.com/in/youssef-jedidi/)

**Concordia Biomedical Engineering Club**

Project Link: [https://github.com/Concordia-Biomedical-Engineering-Club/ai-dermatology-tool](https://github.com/Concordia-Biomedical-Engineering-Club/ai-dermatology-tool)

