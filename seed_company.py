"""
Builds company.db: a large sample database for the merged SQL + handbook assistant.
Uses only Python's built-in sqlite3, so nothing needs installing.
The random seed is fixed, so you get the same data every time you run it.
"""
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

random.seed(42)
DB = "company.db"
TODAY = date(2026, 9, 28)


def iso(d):
    return d.isoformat()


def rand_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))


FIRST = ["Aarav", "Aditya", "Akash", "Ananya", "Anjali", "Arjun", "Bhavna", "Chetan", "Deepa", "Devika",
         "Dhruv", "Farhan", "Gauri", "Harish", "Isha", "Jayesh", "Kavya", "Kiran", "Lavanya", "Madhav",
         "Manoj", "Mohan", "Nandini", "Naveen", "Nikhil", "Omkar", "Pallavi", "Pranav", "Priya", "Rahul",
         "Rajesh", "Rashmi", "Rekha", "Sameer", "Sanjay", "Shreya", "Sneha", "Sunil", "Tanvi", "Uday",
         "Varun", "Vidya", "Yash", "Zoya", "Amit", "Bindu", "Chaitra", "Darshan", "Ganesh", "Hema",
         "Ishaan", "Jyoti", "Kabir", "Leela", "Mahesh", "Nisha", "Pooja", "Ramesh", "Sowmya", "Tejas"]
LAST = ["Acharya", "Bhat", "Chandra", "Gowda", "Hegde", "Iyer", "Joshi", "Kamath", "Kulkarni", "Menon",
        "Nair", "Naik", "Pai", "Patel", "Pillai", "Prabhu", "Rao", "Reddy", "Shetty", "Sharma",
        "Shenoy", "Singh", "Kumar", "Verma", "Gupta", "Khan", "Mehta", "Desai", "Bose", "Das",
        "Banerjee", "Fernandes", "George", "Thomas", "Varma", "Krishnan", "Subramanian", "Ramesh", "Kapoor", "Sheikh"]

# name, location, headcount, salary factor, titles for levels 1-4, head title
DEPTS = [
    ("Engineering", "Bengaluru", 95, 1.20,
     ["Software Engineer", "Software Engineer II", "Senior Engineer", "Engineering Manager"], "Director of Engineering"),
    ("Design", "Bengaluru", 25, 1.00,
     ["Junior Designer", "UX Designer", "Senior Designer", "Design Manager"], "Head of Design"),
    ("Sales", "Mumbai", 50, 1.05,
     ["Sales Associate", "Account Executive", "Senior Account Executive", "Sales Manager"], "Head of Sales"),
    ("Marketing", "Delhi", 30, 0.95,
     ["Marketing Associate", "Marketing Executive", "Senior Marketing Executive", "Marketing Manager"], "Head of Marketing"),
    ("HR", "Bengaluru", 18, 0.90,
     ["HR Associate", "HR Executive", "Senior HR Executive", "HR Manager"], "Head of HR"),
    ("Finance", "Mumbai", 22, 1.00,
     ["Accounts Assistant", "Accountant", "Senior Accountant", "Finance Manager"], "Head of Finance"),
    ("Operations", "Pune", 35, 0.95,
     ["Operations Associate", "Operations Executive", "Senior Operations Executive", "Operations Manager"], "Head of Operations"),
    ("Customer Support", "Chennai", 25, 0.85,
     ["Support Associate", "Support Executive", "Senior Support Executive", "Support Manager"], "Head of Support"),
]
LEVEL_SALARY = {1: (550000, 950000), 2: (950000, 1500000), 3: (1500000, 2400000), 4: (2400000, 3400000)}


def salary(level, factor):
    lo, hi = LEVEL_SALARY[level]
    return int(round(random.randint(lo, hi) * factor, -3))


def work_mode():
    return random.choices(["Office", "Hybrid", "Remote"], weights=[35, 45, 20])[0]


# ---------- departments ----------
departments = []
for i, (name, loc, headcount, factor, _titles, _head) in enumerate(DEPTS, start=1):
    budget = int(round(headcount * random.randint(1400000, 1900000), -4))
    departments.append((i, name, loc, budget))

# ---------- employees ----------
names = random.sample([f"{f} {l}" for f in FIRST for l in LAST], sum(d[2] for d in DEPTS))
name_iter = iter(names)
employees = []  # id, name, job_title, department_id, manager_id, salary, hire_date, work_mode
next_id = 1
for dept_id, (dname, loc, headcount, factor, titles, head_title) in enumerate(DEPTS, start=1):
    head_id = next_id
    head_salary = int(round(random.randint(3500000, 5000000) * factor, -3))
    employees.append((head_id, next(name_iter), head_title, dept_id, None, head_salary,
                      iso(rand_date(date(2013, 1, 1), date(2018, 12, 31))), work_mode()))
    next_id += 1
    n_mgr = max(1, headcount // 12)
    manager_ids = []
    for _ in range(n_mgr):
        employees.append((next_id, next(name_iter), titles[3], dept_id, head_id, salary(4, factor),
                          iso(rand_date(date(2015, 1, 1), date(2021, 12, 31))), work_mode()))
        manager_ids.append(next_id)
        next_id += 1
    for _ in range(headcount - 1 - n_mgr):
        level = random.choices([1, 2, 3], weights=[35, 40, 25])[0]
        earliest = {1: date(2022, 1, 1), 2: date(2018, 1, 1), 3: date(2014, 1, 1)}[level]
        employees.append((next_id, next(name_iter), titles[level - 1], dept_id, random.choice(manager_ids),
                          salary(level, factor), iso(rand_date(earliest, date(2026, 8, 31))), work_mode()))
        next_id += 1

# ---------- projects ----------
PREFIX = ["Customer", "Payments", "Mobile", "Data", "Hiring", "Vendor", "Analytics", "Onboarding",
          "Billing", "Support", "Inventory", "Partner", "Loyalty", "Compliance", "Security"]
SUFFIX = ["Portal", "Platform", "Revamp", "Automation", "Dashboard", "Migration", "Campaign", "Pipeline", "Toolkit"]
project_names = random.sample([f"{p} {s}" for p in PREFIX for s in SUFFIX], 40)
projects = []  # id, name, department_id, status, start_date, end_date
for i, pname in enumerate(project_names, start=1):
    dept_id = random.randint(1, len(DEPTS))
    status = random.choices(["Completed", "Active", "Planned"], weights=[35, 45, 20])[0]
    if status == "Completed":
        start = rand_date(date(2023, 1, 1), date(2025, 3, 31))
        end = min(start + timedelta(days=random.randint(90, 400)), date(2026, 8, 31))
        projects.append((i, pname, dept_id, status, iso(start), iso(end)))
    elif status == "Active":
        start = rand_date(date(2025, 6, 1), date(2026, 8, 31))
        projects.append((i, pname, dept_id, status, iso(start), None))
    else:
        start = rand_date(date(2026, 10, 1), date(2027, 3, 31))
        projects.append((i, pname, dept_id, status, iso(start), None))

# ---------- assignments ----------
ROLES = ["Developer", "Tester", "Analyst", "Designer", "Coordinator", "Reviewer", "Support"]
by_dept = {}
for e in employees:
    by_dept.setdefault(e[3], []).append(e[0])
all_ids = [e[0] for e in employees]
assignments = []  # employee_id, project_id, role, hours_per_week
for (pid, _n, dept_id, status, _s, _e) in projects:
    size = random.randint(4, 14) if status != "Planned" else random.randint(2, 5)
    team = set()
    while len(team) < size:
        pool = by_dept[dept_id] if random.random() < 0.7 else all_ids
        team.add(random.choice(pool))
    lead = random.choice(sorted(team))
    for emp in sorted(team):
        role = "Lead" if emp == lead else random.choice(ROLES)
        assignments.append((emp, pid, role, random.choice([5, 10, 10, 15, 20, 25, 30])))

# ---------- leave requests ----------
leaves = []  # id, employee_id, leave_type, start_date, end_date, status
for i in range(1, 901):
    emp = random.choice(employees)
    hired = date.fromisoformat(emp[6])
    leave_type = random.choices(["Casual", "Sick"], weights=[65, 35])[0]
    start = rand_date(max(hired, date(2025, 10, 1)), date(2026, 12, 15))
    days = random.randint(1, 5) if leave_type == "Casual" else random.randint(1, 3)
    end = start + timedelta(days=days - 1)
    if start < TODAY:
        status = random.choices(["Approved", "Rejected"], weights=[90, 10])[0]
    else:
        status = random.choices(["Pending", "Approved", "Rejected"], weights=[55, 40, 5])[0]
    leaves.append((i, emp[0], leave_type, iso(start), iso(end), status))

# ---------- performance reviews ----------
PERIODS = [("2024-H2", date(2024, 7, 1)), ("2025-H1", date(2025, 1, 1)),
           ("2025-H2", date(2025, 7, 1)), ("2026-H1", date(2026, 1, 1))]
reviews = []  # employee_id, review_period, rating
for e in employees:
    hired = date.fromisoformat(e[6])
    for period, start in PERIODS:
        if hired < start and random.random() < 0.92:
            rating = random.choices([1, 2, 3, 4, 5], weights=[4, 11, 38, 33, 14])[0]
            reviews.append((e[0], period, rating))

# ---------- write the database ----------
Path(DB).unlink(missing_ok=True)
con = sqlite3.connect(DB)
cur = con.cursor()
cur.executescript("""
CREATE TABLE departments (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL, location TEXT NOT NULL, budget INTEGER NOT NULL
);
CREATE TABLE employees (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL, job_title TEXT NOT NULL,
    department_id INTEGER NOT NULL REFERENCES departments(id),
    manager_id INTEGER REFERENCES employees(id),
    salary INTEGER NOT NULL, hire_date TEXT NOT NULL, work_mode TEXT NOT NULL
);
CREATE TABLE projects (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL,
    department_id INTEGER NOT NULL REFERENCES departments(id),
    status TEXT NOT NULL, start_date TEXT NOT NULL, end_date TEXT
);
CREATE TABLE assignments (
    employee_id INTEGER NOT NULL REFERENCES employees(id),
    project_id INTEGER NOT NULL REFERENCES projects(id),
    role TEXT NOT NULL, hours_per_week INTEGER NOT NULL
);
CREATE TABLE leave_requests (
    id INTEGER PRIMARY KEY, employee_id INTEGER NOT NULL REFERENCES employees(id),
    leave_type TEXT NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL, status TEXT NOT NULL
);
CREATE TABLE performance_reviews (
    id INTEGER PRIMARY KEY, employee_id INTEGER NOT NULL REFERENCES employees(id),
    review_period TEXT NOT NULL, rating INTEGER NOT NULL
);
CREATE INDEX idx_emp_dept ON employees(department_id);
CREATE INDEX idx_assign_emp ON assignments(employee_id);
CREATE INDEX idx_leave_emp ON leave_requests(employee_id);
CREATE INDEX idx_review_emp ON performance_reviews(employee_id);
""")
cur.executemany("INSERT INTO departments VALUES (?,?,?,?)", departments)
cur.executemany("INSERT INTO employees VALUES (?,?,?,?,?,?,?,?)", employees)
cur.executemany("INSERT INTO projects VALUES (?,?,?,?,?,?)", projects)
cur.executemany("INSERT INTO assignments VALUES (?,?,?,?)", assignments)
cur.executemany("INSERT INTO leave_requests VALUES (?,?,?,?,?,?)", leaves)
cur.executemany("INSERT INTO performance_reviews VALUES (NULL,?,?,?)", reviews)
con.commit()

print(f"Created {DB}")
for table in ["departments", "employees", "projects", "assignments", "leave_requests", "performance_reviews"]:
    print(f"  {table}: {cur.execute(f'SELECT COUNT(*) FROM {table}').fetchone()[0]} rows")
con.close()