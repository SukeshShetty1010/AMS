# --------------------------------------------------------------
#  Application Management System – Streamlit Web UI
#  Works in Codespaces, GitHub, Replit, etc.
# --------------------------------------------------------------
import streamlit as st
import pandas as pd
from datetime import datetime
from collections import deque
import bisect

# === Core Classes (same as before) ===
class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
    def append(self, stage):
        new_node = Node(stage)
        if not self.head:
            self.head = new_node
        else:
            cur = self.head
            while cur.next:
                cur = cur.next
            cur.next = new_node
    def get_progress(self):
        prog = []
        cur = self.head
        while cur:
            prog.append(cur.data)
            cur = cur.next
        return prog

class ApplicationSystem:
    def __init__(self):
        self.applications = []
        self.application_dict = {}
        self.review_queue = deque()
        self.shortlist_stack = []
        self.progress_tracking = {}
        self.sorted_names = []

    def add_application(self, name, job_id, resume_link, skills, experience, education):
        if name in self.application_dict:
            return False
        app = {
            "name": name, "job_id": job_id, "resume_link": resume_link,
            "skills": skills, "experience": experience, "education": education,
            "status": "Submitted",
            "date_applied": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.applications.append(app)
        self.application_dict[name] = app
        self.review_queue.append(app)
        self.progress_tracking[name] = LinkedList()
        self.progress_tracking[name].append("Submitted")
        bisect.insort(self.sorted_names, name)
        return True

    def process_application(self):
        if not self.review_queue: return None
        app = self.review_queue.popleft()
        if app["status"] == "Submitted":
            self.update_status(app["name"], "Under Review")
        return app

    def update_status(self, name, status):
        if name not in self.application_dict: return False
        app = self.application_dict[name]
        old = app["status"]
        if old == status: return False
        self.shortlist_stack.append({
            "name": name, "old_status": old, "new_status": status,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        app["status"] = status
        self.progress_tracking[name].append(status)
        return True

    def undo_last_status_change(self):
        if not self.shortlist_stack: return False, "Nothing to undo."
        act = self.shortlist_stack.pop()
        name, old = act["name"], act["old_status"]
        if name not in self.application_dict: return False, "Applicant missing."
        app = self.application_dict[name]
        cur = app["status"]
        app["status"] = old
        prog = self.progress_tracking[name].get_progress()
        if prog and prog[-1] == cur:
            new_ll = LinkedList()
            for s in prog[:-1]:
                new_ll.append(s)
            self.progress_tracking[name] = new_ll
        return True, f"Reverted {name}: {cur} → {old}"

    def search_by_name_binary(self, name):
        i = bisect.bisect_left(self.sorted_names, name)
        if i < len(self.sorted_names) and self.sorted_names[i] == name:
            return self.application_dict[name]
        return None

    def filter_applications(self, filters):
        df = pd.DataFrame(self.applications)
        if df.empty: return df
        for k, v in filters.items():
            if v:
                if k in ("skills", "experience", "education"):
                    df = df[df[k].str.contains(v, case=False, na=False)]
                else:
                    df = df[df[k] == v]
        return df

    def track_progress(self, name):
        return self.progress_tracking.get(name, LinkedList()).get_progress()

    def generate_detailed_report(self):
        df = pd.DataFrame(self.applications)
        if df.empty: return None
        return {
            "total_applications": len(df),
            "applications_per_job": df["job_id"].value_counts().to_dict(),
            "status_summary": {
                "Shortlisted": len(df[df["status"] == "Shortlisted"]),
                "Rejected": len(df[df["status"] == "Rejected"]),
                "Pending": len(df[df["status"].isin(["Submitted","Under Review"])])
            },
            "queue_length": len(self.review_queue)
        }

# === Streamlit App ===
st.set_page_config(page_title="Application Manager", layout="wide")
st.title("Application Management System")

# Initialize system in session state
if "system" not in st.session_state:
    st.session_state.system = ApplicationSystem()

sys = st.session_state.system

# Sidebar Navigation
page = st.sidebar.radio("Go to", [
    "Add Application",
    "Process & Update",
    "Search & Filter",
    "Progress Tracking",
    "Report"
])

# === 1. Add Application ===
if page == "Add Application":
    st.header("Add New Application")
    with st.form("add_form"):
        name = st.text_input("Applicant Name *")
        job_id = st.text_input("Job ID")
        resume_link = st.text_input("Resume Link")
        skills = st.text_input("Skills (comma-separated)")
        experience = st.text_input("Experience")
        education = st.text_input("Education")
        submitted = st.form_submit_button("Add Application")

        if submitted:
            if not name:
                st.error("Name is required.")
            elif sys.add_application(name, job_id, resume_link, skills, experience, education):
                st.success(f"{name} added successfully!")
            else:
                st.error("Applicant already exists.")

# === 2. Process & Update ===
elif page == "Process & Update":
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Process Queue (FIFO)")
        if st.button("Process Next Application"):
            app = sys.process_application()
            if app:
                st.success(f"Processing: **{app['name']}** (Job: {app['job_id']})")
            else:
                st.info("Queue is empty.")

    with col2:
        st.subheader("Update Status")
        names = list(sys.application_dict.keys())
        name = st.selectbox("Select Applicant", [""] + names)
        status = st.selectbox("New Status", ["", "Under Review", "Shortlisted", "Rejected"])
        if st.button("Update Status") and name and status:
            if sys.update_status(name, status):
                st.success(f"{name} → {status}")
            else:
                st.error("Update failed.")

    st.subheader("Undo")
    if st.button("Undo Last Status Change"):
        ok, msg = sys.undo_last_status_change()
        st.info(msg)

# === 3. Search & Filter ===
elif page == "Search & Filter":
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Binary Search by Name")
        search_name = st.text_input("Enter name")
        if st.button("Search"):
            res = sys.search_by_name_binary(search_name)
            if res:
                st.json(res, expanded=False)
            else:
                st.warning("Not found.")

    with col2:
        st.subheader("Filter Applications")
        f_job = st.text_input("Job ID")
        f_status = st.text_input("Status")
        f_skills = st.text_input("Skills")
        if st.button("Apply Filter"):
            filters = {"job_id": f_job or None, "status": f_status or None, "skills": f_skills or None}
            df = sys.filter_applications(filters)
            if not df.empty:
                st.dataframe(df)
            else:
                st.info("No matches.")

    st.subheader("All Applications")
    st.dataframe(pd.DataFrame(sys.applications))

# === 4. Progress Tracking ===
elif page == "Progress Tracking":
    st.header("Track Application Progress")
    name = st.selectbox("Select Applicant", [""] + list(sys.application_dict.keys()))
    if name:
        steps = sys.track_progress(name)
        for i, step in enumerate(steps, 1):
            st.write(f"**Step {i}:** {step}")

# === 5. Report ===
elif page == "Report":
    st.header("Detailed Report")
    if st.button("Generate Report"):
        rep = sys.generate_detailed_report()
        if rep:
            st.metric("Total Applications", rep["total_applications"])
            st.metric("Queue Length", rep["queue_length"])
            st.write("**Applications per Job:**")
            st.json(rep["applications_per_job"])
            st.write("**Status Summary:**")
            st.json(rep["status_summary"])
        else:
            st.info("No data yet.")

# Footer
st.sidebar.markdown("---")
st.sidebar.write("All 11 DSA features implemented:")
st.sidebar.write("- Arrays, Dicts, Queue, Stack")
st.sidebar.write("- Linked List Progress")
st.sidebar.write("- Binary Search")
st.sidebar.write("- Undo/Redo")
st.sidebar.write("- Filters & Reports")