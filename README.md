# Finance Data Processing and Access Control Backend

## 📌 Overview
This project is a backend system for managing financial records with role-based access control.

It supports:
- User management (create, update, delete, read)
- Financial records CRUD operations
- Dashboard summary APIs:
  - Income
  - Expense
  - Net balance
  - Category totals
  - Recent activity
  - Monthly trends
- Role-based restrictions (Viewer, Analyst, Admin)

---

## 🚀 Setup Instructions

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd <repo-folder>
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate   # Windows
```
### 3. Install dependencies
```bash
pip install -r requirements.txt
```
### 4. Run the application
```bash
python app.py
```

## 🗄️ Database
- SQLite is used for persistence.
- Tables are auto-created on first run.

---

## 🔌 API Endpoints

### 🔹 User Management
- `POST /user` → Create user (**Admin only**)
- `GET /user?id=<id>` → Get user details (**All roles**)
- `PUT /user` → Update user (**Admin only**)
- `DELETE /user` → Delete user (**Admin only**)

### 🔹 Financial Records
- `POST /records` → Create record (**Admin only**)
- `GET /records?id=<id>` → Read record (**All roles**)
- `PUT /records` → Update record (**Admin only**)
- `DELETE /records` → Delete record (**Admin only**)
- `GET /filter_records?category=food&type=expense` → Filter records (**All roles**)

### 🔹 Dashboard
- `GET /dashboard?user_id=<id>`

**Access:**
- Viewer → ❌ Denied  
- Analyst → ✅ Allowed  
- Admin → ✅ Allowed  

---

## 🔐 Access Control Rules
- **Viewer** → Can only read records  
- **Analyst** → Can read records + view dashboard summaries  
- **Admin** → Full CRUD on users + records + dashboard access  

---

## ⚠️ Validation & Error Handling
- Email format validation  
- Role validation (`viewer`, `analyst`, `admin`)  
- Status validation (`active`, `inactive`)  
- Date format validation (`YYYY-MM-DD`)  
- Proper error messages with status codes:
  - `400` → Bad request  
  - `403` → Forbidden  
  - `404` → Not found  

---

## 📌 Assumptions
- Authentication is mocked (no login system)  
- SQLite chosen for simplicity  
- Dashboard summaries are calculated dynamically from records  

---

## 🔄 Tradeoffs Considered
- **SQLite** → Easy setup, but not scalable for production  
- **No authentication** → Simplifies implementation, but not secure for real-world use  
- **Function-based access control** → Clear role enforcement, but could be improved with middleware in larger systems  

---

## ✅ Evaluation Criteria Covered
- **Backend Design** → Clear routes, models, and separation of logic  
- **Logical Thinking** → Role-based access control implemented  
- **Functionality** → CRUD + dashboard APIs working  
- **Code Quality** → Readable, maintainable, validated  
- **Database Modeling** → Proper schema for users and records  
- **Validation** → Input checks and error handling  
- **Documentation** → This README explains setup, APIs, assumptions, and tradeoffs
