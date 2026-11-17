# Aether Personal Assistant

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![aiogram](https://img.shields.io/badge/aiogram-3.x-2CA5E0?logo=telegram&logoColor=white)](https://docs.aiogram.dev/)
[![SQLite](https://img.shields.io/badge/SQLite-aiosqlite-003B57?logo=sqlite&logoColor=white)](https://aiosqlite.omnilib.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Aether Personal Assistant** is a production-ready Telegram bot that turns your chat into a calm, structured command center for everyday life. Tasks, notes, and finances live in one place, with a clean async architecture and a database that keeps everything fast and reliable.

> Built as a portfolio project to demonstrate modern Python backend development, Telegram bot UX, FSM-driven workflows, and clean modular architecture.

---

## ✨ Features

### 📋 Task Management
- Create tasks with deadlines
- View all active tasks grouped by deadline
- Mark tasks as completed
- Delete tasks instantly

### 📝 Smart Notes
- Save notes with tags
- Search notes by tag
- Browse notes grouped by tag
- Delete individual notes

### 💰 Finance Tracking
- Record expenses with amount, category, and comment
- View monthly summaries grouped by category
- Automatic totals and clean reporting

### 🧠 Bot UX
- Reply keyboard for main navigation
- Inline keyboards for actions
- Step-by-step input via FSM
- Input validation and friendly error messages

---

## 🏗 Architecture

```text
aether-personal-assistant/
├── main.py                 # Application entry point
├── config.py               # Environment configuration
├── database.py             # Async SQLite data layer
├── handlers/
│   ├── start.py            # Start, help, navigation
│   ├── tasks.py            # Task workflows
│   ├── notes.py            # Note workflows
│   └── finances.py         # Expense workflows
├── keyboards/
│   ├── reply.py            # Main reply keyboard
│   └── inline.py           # Inline action keyboards
├── requirements.txt
├── .env.example
└── README.md
```

The project follows a modular router-based architecture:

- **Handlers** are split by domain
- **Keyboards** are isolated from business logic
- **Database** is a dedicated async data layer
- **FSM states** make multi-step input safe and predictable

---

## 🛠 Tech Stack

- **Python 3.11+**
- **aiogram 3.x** — async Telegram Bot API framework
- **aiosqlite** — non-blocking SQLite access
- **python-dotenv** — environment-based configuration
- **SQLite** — lightweight embedded database

---

## 🚀 Quick Start

### 1. Create a bot

Talk to [@BotFather](https://t.me/BotFather) on Telegram and create a new bot. Copy the token.

### 2. Configure environment

```bash
Copy-Item .env.example .env
```

Open `.env` and set your token:

```env
BOT_TOKEN=your_telegram_bot_token_here
DB_PATH=assistant.db
```

### 3. Install dependencies

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Run

```bash
python main.py
```

The SQLite database is created automatically on first launch.

---

## 📌 Example Workflow

```text
/start
📋 Задачи → ➕ Добавить задачу
→ "Подготовить портфолио"
→ "2026-12-01"

📝 Заметки → ➕ Добавить заметку
→ "Идея для pet-проекта"
→ "идеи"

💰 Финансы → ➕ Добавить расход
→ 1200
→ Еда
→ "Обед с командой"
```

---

## 🗄 Database Schema

The bot uses four core tables:

- `users` — registered Telegram users
- `tasks` — personal tasks with deadlines and status
- `notes` — tagged notes
- `expenses` — categorized spending records

All user data is isolated by `user_id`.

---

## 🔒 Security Notes

- Secrets are loaded from `.env`
- `.env` is ignored by Git
- Database files are ignored by Git
- No credentials are stored in source code

---

## 📈 Portfolio Value

This project demonstrates:

- Async Python development
- Telegram bot architecture with aiogram 3
- FSM-based multi-step user flows
- SQLite schema design
- Clean separation of concerns
- Production-style error handling
- User-friendly bot UX

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
