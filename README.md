# 📊 BRACU Gradesheet Analyzer

**BRACU Gradesheet Analyzer** is a powerful and privacy-respecting academic dashboard built with Streamlit for BRAC University students. Upload your transcript and unlock advanced features like CGPA tracking, projection, simulation, visual analytics, course planning, and more — all in one place.

🔗 **Live App**:  
👉 [https://bracu-gradesheet-analyzer.streamlit.app/](https://bracu-gradesheet-analyzer.streamlit.app/)

---

## 🔍 What Can This Tool Do?

This app is designed for **students who want full control over their academic planning**. It offers:

- ✅ **CGPA Calculator** with visualizations and trends  
- ✅ **Gradesheet Analyzer** (supports official BRACU transcripts in PDF)  
- ✅ **CGPA Projection & Simulation**  
- ✅ **Retake and Add Course Planner**  
- ✅ **Unlocked Courses Tracker** (based on prerequisites)  
- ✅ **COD/General Education Stream Progress Checker**  
- ✅ **Course Resource Viewer** (midterms, finals, PDFs, links)  
- ✅ **Smart Footer with Inspirational Quotes & Developer Info**

---

## 🧠 Why Use This?

Whether you're:
- Planning for a specific CGPA target
- Retaking courses and want to know the effect
- Tracking which courses you've unlocked
- Curious about graduation readiness
- Just want to visualize your academic journey

This tool gives you **data-backed insights** in a simple UI. Designed **for BRACU students, by a BRACU student**.

---

## 📈 Keywords (for search)

To make this project easily discoverable, here are some target terms:

- `bracu cgpa calculator`
- `brac university transcript analyzer`
- `bracu gradesheet analysis tool`
- `bracu academic dashboard`
- `cgpa simulator streamlit`
- `cgpa planner for brac university`
- `bracu unlocked course checker`
- `bracu cod stream tracker`
- `bracu course resources app`

These keywords are embedded naturally throughout this README and the app’s metadata.

---

## ✨ Features at a Glance

| Feature                            | Description |
|-----------------------------------|-------------|
| 🧾 Gradesheet Upload              | Upload your BRACU PDF transcript securely |
| 🧮 CGPA Calculator                | Instant CGPA and credits summary |
| 📈 Trend Graphs                   | GPA & CGPA visualized over semesters |
| 🎯 CGPA Planner & Simulator       | Predict your future CGPA based on goals |
| 🔁 Retake Simulation              | Simulate GPA impact of retaking any course |
| 🔓 Unlocked Course Finder         | Shows which core/COD courses you’ve unlocked |
| 📚 Course Resource Viewer         | Midterms, finals, links, PDFs for each course |
| 📊 COD Tracker                    | Check stream coverage and recommendations |
| 🌟 Quote of the Day               | Motivational quotes every 2 minutes |

---

## 🛠 Run Locally

### Option 1: Using Docker (Recommended) (Docker must be installed and configured)

```bash
git clone https://github.com/xDhruboVai/BRACU-Gradesheet-Analyzer-CSE-.git
cd BRACU-Gradesheet-Analyzer-CSE-/docker
./run.sh start
```

Access at **http://localhost:8501**

📋 **[Complete Docker Setup Guide](docker/DOCKER_LOCAL.md)** - Step-by-step instructions for Docker setup

### Option 2: Direct Python Setup

```bash
git clone https://github.com/xDhruboVai/transcript-analyzer.git
cd transcript-analyzer
pip install -r requirements.txt
streamlit run app.py
```

---

## 🧪 Built With

- **Python**  
- **Streamlit**  
- **Plotly**  
- **PyMuPDF** (for PDF parsing)
- **Docker** (for containerized deployment)

---

## 🐳 Docker Support

This project includes a complete Docker setup for easy local deployment:

- **Containerized Environment**: Run the app in an isolated Docker container
- **Simple Management**: Easy start/stop commands with included scripts
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **No Dependencies**: Only requires Docker - no Python setup needed

📋 **[Docker Setup Guide](docker/DOCKER_LOCAL.md)** - Complete instructions for Docker usage

---

## 🙌 Contributing

PRs are welcome. If you're a BRACU student or developer and want to improve the app — new features, better visuals, bug fixes — feel free to contribute.

---

## 🧑‍💻 Developer

Made with ❤️ by [Dihan Islam Dhrubo](https://www.linkedin.com/in/dihan-islam-dhrubo-79a904249/)  
[🔗 GitHub Repo](https://github.com/xDhruboVai/transcript-analyzer)

---

## 🧠 Quote of the Day (Footer Feature)

> This app displays a fresh quote every 2 minutes — from games, pop culture, and classics — to keep your study journey inspired.

---

## 📢 License

MIT License — use, modify, and share freely.