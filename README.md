# Application Management System (DSA Project)

A **Data Structures & Algorithms-powered** Applicant Tracking System (ATS) built in Python. Implements **queues, stacks, linked lists, binary search, filtering, and reporting**.

**Live Web GUI** using **Streamlit** — no terminal hassle!

---

## Features

- Add applications with resume links & skills
- FIFO queue for recruiter review
- Status updates: Submitted → Under Review → Shortlisted/Rejected
- **Undo** last action using stack
- **Binary search** by name (O(log n))
- Filter by Job ID, Status, Skills
- Progress tracking using **linked list**
- Detailed reports with analytics
- Export data to CSV
- **Web-based UI** — works in any browser!

---

## Tech Stack

- **Python 3.12**
- **Streamlit** (Web Interface)
- **Pandas** (Data Handling)
- **Collections** (deque, bisect)
- Custom **Linked List, Queue, Stack**

---

## Project Structure

```
DSA_Project/
├── application_management_system.py   ← Main app (Streamlit)
├── requirements.txt                   ← Dependencies
├── README.md                          ← This file
└── (data stored in memory)
```


---

### How to Run (Step-by-Step)

#### 1. Clone or Download
```bash
git clone <your-repo-url>
cd DSA_Project
```

#### 2. Create Virtual Environment
```bash
python -m venv venv
```

#### 3. Activate Virtual Environment

**On Windows:**
```bash
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
source venv/bin/activate
```

#### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 5. Run the App
```bash
streamlit run application_management_system.py
```

#### 6. Open in Browser
- URL will appear:  
  `http://localhost:8501`
- Click or paste in browser

**Your app is live!**

---

**One-liner to launch (after setup):**
```bash
streamlit run application_management_system.py
```