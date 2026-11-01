# NexusERP-AI – Enterprise Workflow & Intelligent HRMS Platform

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.0-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/Django_REST_Framework-3.15-red?logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![React](https://img.shields.io/badge/React-19.0-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6?logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14%2B-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Vite](https://img.shields.io/badge/Vite-6.0-646CFF?logo=vite&logoColor=white)](https://vitejs.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## Overview

**NexusERP-AI** is a multi-tenant Enterprise Resource Planning (ERP) and Human Resource Management System (HRMS) engineered to centralize, automate, and streamline organizational workflows. Built on a strict tenant-isolated architecture powered by Django REST Framework and React with TypeScript, the platform unifies employee lifecycle management, attendance tracking, multi-tier leave administration, algorithmic payroll calculation, hardware asset auditing, and outbound financial disbursements into a unified single-pane interface. By integrating an autonomous AI Copilot with tool-calling capabilities (supporting both high-speed cloud inference via Groq and private on-premises execution via Ollama), NexusERP-AI transforms operational business data into predictive, actionable intelligence.

---

## Application Previews

### 1. Modern Enterprise Landing Experience
![NexusERP Landing Page](docs/screenshots/nexus_landing.png)

### 2. Multi-Tenant Executive Dashboard
![NexusERP Enterprise Dashboard](docs/screenshots/dashboard_overview.png)

### 3. Attendance Analytics & Audit Studio
![NexusERP Attendance Tracker](docs/screenshots/attendance_tracker.png)

---

## Core Modules

- **Multi-Tenant Identity & Automated Workspace Bootstrap**: Guarantees zero cross-tenant data contamination. Registering a new enterprise instantly bootstraps standard organizational structures, including 5 functional departments (Engineering, HR, Finance, Operations, Sales), standardized designations, and statutory leave policies.
- **Employee Directory & Personnel Management**: Comprehensive personnel profiles, role-based access control (Admin, HR, Manager, Employee), role resolution safeguards, and contact verification.
- **Attendance Tracking & Time-Clock Studio**: Daily check-in/check-out logs, real-time working hour calculations, grace-period late tracking, and unified daily distribution reports.
- **Leave Management Studio**: Entitlement balance tracking across Casual, Sick, and Paid leave categories, employee request workflows, and instant manager approvals/rejections with automated balance reconciliation.
- **Automated Payroll & Payslip Engine**: Parameterized salary computations (Base Salary, HRA, Special Allowances, PF, Professional Tax, and Deductions) with single-click batch generation and PDF payslip exporting.
- **Hardware & Asset Inventory**: Enterprise asset allocation, custodian tracking, serial number auditing, and condition monitoring.
- **Payments & Outbound Expense Hub**: Vendor disbursements, invoice records, expense approvals, payment status audits, and transaction logs.
- **Executive Analytics & Reports Studio**: Real-time reporting engine delivering departmental breakdowns, payroll commitments, attendance metrics, and downloadable operational datasets.
- **NexusERP AI Copilot**: Autonomous conversational assistant utilizing 20 schema-validated domain tools to query attendance KPIs and exceptions, employee directory records, leave balances and pending requests, payroll summaries and department costs, hardware asset assignments and maintenance logs, pending vendor payments, and historical headcount/payroll/maintenance trends.

---

## AI Attendance Analytics & Anomaly Detection

### How It Works
The **AI Attendance Analytics** system combines automated attendance anomaly detection with an agentic LLM tool-calling engine, allowing HR leaders to query workforce patterns and exceptions in plain English.

```
+--------------------------------------------------------------------------------+
|                   1. ATTENDANCE ANOMALY & KPI ENGINE                           |
|  - Live Daily KPIs: present, absent, on-leave, late arrivals, half-days        |
|  - Exception Tracking: late minutes past grace period, early exits, missing    |
|    check-ins/check-outs, manual entry modifications, pending approvals         |
|  - Per-Employee Monthly Summaries: total working, overtime, and late minutes   |
+--------------------------------------------------------------------------------+
                                       |
                                       v
+--------------------------------------------------------------------------------+
|                   2. AI COPILOT TOOL-CALLING ORCHESTRATOR                      |
|  - Intent Parsing: Maps natural language questions to specialized tools       |
|    (`attendance_dashboard`, `attendance_summary`, `attendance_exceptions`)    |
|  - Deterministic Keyword Fallback: Rules-based tool selector executes safely   |
|    if LLM inference is offline or unreachable                                  |
|  - Context Isolation: Queries strictly scoped to user's authenticated tenant   |
+--------------------------------------------------------------------------------+
                                       |
                                       v
+--------------------------------------------------------------------------------+
|                   3. LLM SYNTHESIS & PLAIN-ENGLISH NARRATION                   |
|  - Dual Inference Engine: Groq (llama-3.3-70b-versatile) or Ollama (qwen3:8b)  |
|  - Plain-English Narration: Translates database exception rows into actionable |
|    HR summaries and workforce insights                                         |
|  - Offline Formatter: Deterministic fallback message generator if offline      |
+--------------------------------------------------------------------------------+
```

1. **Deterministic Anomaly & Exception Detection**: The backend (`attendance/reports.py`) audits employee check-in logs against company shift configurations, flagging late arrivals against grace periods, unexcused absences, early departures, and missing check-outs.
2. **Agentic Tool Selection**: When an executive or HR manager interacts with the AI Copilot (`"Who came late today?"` or `"Which employees have attendance exceptions?"`), the AI planner (`ai/planner.py`) inspects the query and selects the appropriate tool from the tool registry.
3. **Rule-Based Fallback Planner**: If the LLM service is offline or unreachable, `_keyword_plan` in `ai/services.py` provides deterministic keyword routing directly to the appropriate attendance reports.
4. **LLM Synthesis & Narration**: The LLM client (`ai/llm/ollama_client.py`, supporting high-speed Groq inference and local Ollama) takes the structured JSON results from tool execution and generates a coherent, plain-English summary for HR decision-makers.

---

## Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend** | React 19, TypeScript, JavaScript (ESNext), Vite (configured on port 3000), Tailwind CSS, Lucide Icons, Axios |
| **Backend** | Python 3.12, Django 6.0, Django REST Framework (DRF), SimpleJWT, Django-Filter |
| **Database** | PostgreSQL 14+ (ACID compliant, relational schemas, indexed foreign keys, multi-tenant isolation) |
| **AI / LLM** | Groq API (`llama-3.3-70b-versatile`), Ollama (`qwen3:8b`), Schema-validated Tool Calling, Rule-based Fallback Planner |
| **Security** | JWT Authentication with token rotation, CORS origin isolation, Argon2/PBKDF2 hashing, tenant-isolated ORM queries |

---

## Local Setup & Installation

### Prerequisites
- **Python 3.12+**
- **Node.js 20+** and **npm**
- **PostgreSQL 14+** running locally or in cloud
- *(Optional)* **Ollama** installed locally OR a free **Groq Cloud API Key** for AI features

---

### 1. Clone the Repository
```bash
git clone https://github.com/krishpatelkp/NexusERP-AI.git
cd NexusERP-AI
```

---

### 2. Configure PostgreSQL Database
Open PostgreSQL via `psql` or pgAdmin and create the database:
```sql
CREATE DATABASE nexuserp;
```

---

### 3. Backend Setup

1. **Navigate to the backend directory and activate a virtual environment:**
   ```bash
   cd backend
   python -m venv venv
   
   # Windows (PowerShell):
   .\venv\Scripts\Activate.ps1

   # Linux / macOS:
   source venv/bin/activate
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` with your PostgreSQL credentials:
   ```env
   SECRET_KEY=your-dev-secret-key-change-in-production
   DEBUG=True
   ALLOWED_HOSTS=*
   
   DB_NAME=nexuserp
   DB_USER=postgres
   DB_PASSWORD=your_postgres_password
   DB_HOST=localhost
   DB_PORT=5432
   
   CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
   
   # Optional AI Copilot Configuration:
   # GROQ_API_KEY=gsk_your_groq_key_here
   # GROQ_MODEL=llama-3.3-70b-versatile
   ```

4. **Run Migrations & Seed Default Workspace:**
   ```bash
   python manage.py migrate
   ```

5. **(Optional) Run System Verification Suite:**
   Verify end-to-end multi-tenant isolation, leave balance deductions, and attendance APIs:
   ```bash
   python verify_system.py
   ```

6. **Start the Django Development Server:**
   ```bash
   python manage.py runserver 127.0.0.1:8000
   ```
   The backend API will be live at `http://127.0.0.1:8000/api/`  
   Interactive Swagger documentation is available at `http://127.0.0.1:8000/swagger/`

---

### 4. Frontend Setup

1. **Open a new terminal and navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node packages:**
   ```bash
   npm install
   ```

3. **Configure Environment Variables:**
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   Ensure `VITE_API_URL` points to your running backend:
   ```env
   VITE_API_URL=http://127.0.0.1:8000/api
   ```

4. **Start the Vite Development Server:**
   ```bash
   npm run dev
   ```
   The frontend application will be live at `http://localhost:3000` *(configured in `vite.config.js`)*.

---

## Security & Credential Hygiene

- **Environment Isolation**: Database credentials, tokens, and runtime configurations are kept out of source control and managed through `.env` files.
- **Sanitized Templates**: Only sanitized `.env.example` templates are tracked in version control for development and onboarding references.
- **Tenant Isolation**: Every database query is strictly filtered by the authenticated user's `company_id`. Cross-tenant data leakage is prevented at both the ORM and serializer layers.

---

## License

This project is licensed under the [MIT License](LICENSE).
