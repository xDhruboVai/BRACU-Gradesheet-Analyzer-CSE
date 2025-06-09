# 📊 BRACU Gradesheet Analyzer

**BRACU Gradesheet Analyzer** is a privacy-focused academic dashboard for BRAC University students. Built with Streamlit, this tool enables advanced GPA analytics, course planning, simulation, and resource tracking — all in a sleek and intuitive interface.

🔗 **Live App**:  
👉 [https://bracu-gradesheet-analyzer.streamlit.app/](https://bracu-gradesheet-analyzer.streamlit.app/)

![MIT License](https://img.shields.io/badge/license-MIT-green.svg)

---

## 🔍 What Can This App Do?

Designed with BRACU students in mind, the analyzer allows you to:

- 📥 Upload your official gradesheet (PDF)
- 📈 Track and simulate CGPA changes (add, retake, remove courses)
- 📊 View GPA and CGPA trends across semesters
- 🔓 See which core and COD (General Education) courses are unlocked
- 📚 Access course resources: PDFs, midterms, finals, links
- 🧠 Plan ahead using COD stream requirements and credit simulations
- 💡 Get course-specific visual insights and motivational quotes

---

## ✨ Core Features

| Category               | Feature Description |
|------------------------|---------------------|
| 🧾 Gradesheet Upload   | Securely upload and extract academic data from official BRACU transcripts |
| 🧮 GPA Calculator      | Instant CGPA and credit calculation |
| 🔁 Course Simulation   | Add, retake, and remove courses — see real-time CGPA impact |
| 🎯 CGPA Planner        | Plan future semesters based on your CGPA goals |
| 📈 GPA Trends          | Interactive line charts showing GPA & CGPA progression |
| 📘 Unlocked Courses    | See all currently unlocked core and COD courses |
| 🧠 COD Stream Checker  | Visualize COD stream coverage and get suggestions |
| 📚 Course Resources    | Browse midterms, finals, links, folders for each course |
| ✅ Completed Breakdown | Categorized view of all completed courses by type |
| 🌟 Quote of the Hour   | Random academic or nerd-themed motivational quote

---

## 📦 Technologies Used

- **Python 3.9+**
- **Streamlit** — For the web UI
- **Plotly** — For interactive graphs
- **PyMuPDF** — For extracting data from transcripts
- **Pandas** — For processing and visualization
- **Docker** — For containerized deployment

---

## 📁 How to Run Locally

You can run the app locally using **either Docker (recommended)** or a direct Python setup.

### Option 1: Using Docker (Recommended)

> **Docker must be installed and configured on your machine.**

```bash
git clone https://github.com/xDhruboVai/BRACU-Gradesheet-Analyzer.git
cd BRACU-Gradesheet-Analyzer/docker
./run.sh start
```

Access at **http://localhost:8501**

📋 **[Complete Docker Setup Guide](docker/DOCKER_LOCAL.md)** — Step-by-step instructions for Docker setup

---

### Option 2: Direct Python Setup

```bash
# Clone the repository
git clone https://github.com/xDhruboVai/BRACU-Gradesheet-Analyzer.git
cd BRACU-Gradesheet-Analyzer

# (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py

# The app will open at http://localhost:8501/
# At any point if it says x: command not found, use python -m rest of the command
```