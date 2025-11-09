🧠 Smart Financial Coach
An intelligent personal finance dashboard that helps users track spending, set savings goals, and gain insights into their financial habits.
Built with React (Vite), FastAPI, and Docker, it provides a modular and extensible architecture ready for real-time analytics or database integration.

🚀 Features
💰 Add and track transactions (income, expenses, savings)
📊 Automatic insights: category spending, subscriptions, and anomalies
🎯 Goal setting: set financial goals and see progress updates
💡 Smart tips: AI-ready section for personalized financial recommendations
🔄 Dockerized full-stack setup for easy deployment and local development

## 🏗️ Tech Stack

**Frontend**
- React (Vite)
- Tailwind CSS
- Axios for API calls

**Backend**
- FastAPI (Python)
- Pydantic for validation
- Pandas + Scikit-learn for analytics

**Infrastructure**
- Docker & Docker Compose
- PostgreSQL (optional for persistent storage)

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository
```bash
git clone https://github.com/Kinfernopixel/smart-financial-coach.git
cd smart-financial-coach

Build and start the containers
docker-compose up --build

🧩 Local Development (without Docker)

Backend
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

Frontend
cd frontend
npm install
npm run dev

🔮 Future Enhancements
Connect FastAPI backend to PostgreSQL for persistent storage
Add authentication and user profiles
Integrate charts for visualization (Recharts / Chart.js)
Expand goal forecasting using AI

🧑‍💻 Author
Kanan Shah
Smart Financial Coach — a modern full-stack project combining AI-driven insights, data visualization, and financial goal management.