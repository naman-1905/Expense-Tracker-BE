# Expense Tracker Backend (Polyglot Microservices)

This project consists of **three independent backend services**:

* FastAPI → CRUD Service
* Express.js → Auth Service
* Flask → History Service

Each service connects to the same SQL database but runs independently with its **own environment configuration**.

---

## 📁 Project Structure

```
db/
 └── init.sql

express-auth/
fastapi-crud/
flask-history/
```

The `db/init.sql` file contains the schema required to initialize the database.

---

## ⚙️ Environment Setup

Each service requires its **own `.env` file**.

Create a `.env` file inside:

* `express-auth/`
* `fastapi-crud/`
* `flask-history/`

---

## 🔑 Required Environment Variables

Add the following inside **each service's `.env` file**:

```
DB_HOST=host
DB_PORT=port
DB_NAME=database_name
DB_USER=username
DB_PASSWORD=password
JWT_SECRET=your_secret
```

Service-specific ports:

### FastAPI (.env inside fastapi-crud)

```
PORT_FASTAPI=8000
```

### Express (.env inside express-auth)

```
PORT_EXPRESS=8001
```

### Flask (.env inside flask-history)

```
PORT_FLASK=8002
```

---

## 🗄️ Database Setup

1. Create a SQL database.
2. Run the schema:

```
db/init.sql
```

This will initialize all required tables.

---

## 🚀 Running the Services

### 1. FastAPI - CRUD Service

Navigate to:

```
cd fastapi-crud
```

Install dependencies:

```
pip install -r requirements.txt
```

Run:

```
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

### 2. Express - Auth Service

Navigate to:

```
cd express-auth
```

Install dependencies:

```
npm install
```

Run:

```
npm run dev
```

---

### 3. Flask - History Service

Navigate to:

```
cd flask-history
```

Install dependencies:

```
pip install -r requirements.txt
```

Run:

```
python app.py
```

---

## 🐳 Docker Support

Each service contains its own `Dockerfile`.

You can containerize and deploy them independently if required.

---

## 🧠 Architecture Overview

| Service | Framework  | Responsibility       |
| ------- | ---------- | -------------------- |
| Auth    | Express.js | Authentication & JWT |
| CRUD    | FastAPI    | Expense Operations   |
| History | Flask      | Expense History      |

All services:

* Share the same database schema
* Maintain independent configs
* Can scale individually

---

## 📝 Notes

* Ensure `.env` is present before running any service.
* Ports must be unique.
* JWT_SECRET must match across services.

---

## 📌 Default Ports

| Service | Port |
| ------- | ---- |
| FastAPI | 8000 |
| Express | 8001 |
| Flask   | 8002 |

---

You're now ready to run the Expense Tracker Backend 
