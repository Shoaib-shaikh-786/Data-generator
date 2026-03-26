# 🚀 DataGen Platform (FastAPI)

A scalable **data generation and management platform** built using FastAPI. This application allows users to define schemas, generate structured and unstructured data, export it in multiple formats, and store it directly in AWS S3.

---

## ✨ Features

* 🔧 Schema-driven data generation
* 🧠 Supports **structured & nested unstructured data (up to 3 levels)**
* 🔑 Auto-increment & primary key uniqueness enforcement
* ✏️ Update and manage generated data
* 📁 Export data in multiple formats:

  * JSON
  * CSV
  * Excel
  * XML
  * Parquet
* ☁️ AWS S3 integration for direct uploads
* 🌐 Interactive UI for managing workflows
* ⚡ FastAPI backend with high performance

---

## 🏗️ Project Architecture

```
datagen/
├── app/
│   ├── main.py
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── repository/
│   ├── services/
│   ├── workers/
│   └── db/
├── templates/
├── static/
├── tests/
├── Dockerfile
└── requirements.txt
```

---

## ⚙️ Tech Stack

* **Backend:** FastAPI
* **Data Generation:** Faker
* **Data Processing:** Pandas
* **Storage:** AWS S3 (boto3)
* **Frontend:** HTML (Jinja2 templates)
* **Deployment:** Docker

---

## 🚀 Getting Started

### 1️⃣ Clone the repository

```
git clone https://github.com/your-username/datagen.git
cd datagen
```

---

### 2️⃣ Create Virtual Environment

```
python3.11 -m venv venv
source venv/bin/activate
```

---

### 3️⃣ Install Dependencies

```
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

---

### 4️⃣ Run the Application

```
uvicorn app.main:app --reload
```

---

## 🌐 Access the Application

* API Docs (Swagger UI):
  👉 http://127.0.0.1:8000/docs

* Web UI:
  👉 http://127.0.0.1:8000/

---

## 🔌 API Endpoints

| Endpoint   | Description            |
| ---------- | ---------------------- |
| `/tables`  | Manage schemas         |
| `/data`    | Generate & manage data |
| `/export`  | Export data            |
| `/storage` | Upload to AWS S3       |

---

## 📦 Example Use Cases

* Generate test datasets for applications
* Create mock APIs for frontend development
* Simulate production-like data
* Data engineering testing pipelines

---

## 🔐 Future Enhancements

* Database integration (PostgreSQL / MongoDB)
* Background job processing (Celery)
* Role-based authentication
* Schema versioning
* Real-time data preview

---

## 🧑‍💻 Author

**Shoaib**

---

## ⭐ Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---

## 📄 License

This project is open-source and available under the MIT License.

---
