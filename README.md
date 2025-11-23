# SixtSense 🚗

**AI-Powered Car Rental Sales Assistant**

A hackaTUM 2025 project that helps SIXT customers find the perfect vehicle upgrade through natural conversation.

---

## 💡 The Problem

Choosing a car rental ai sales assistant is overwhelming. Customers face:
- Complex pricing tables and technical specifications
- Uncertainty about which vehicle truly fits their needs
- Generic upsell offers that don't consider their specific trip

## ✨ Our Solution

SixtSense uses conversational AI as a sales person to understand each customer's unique trip requirements and recommend upgrades that genuinely add value. No pressure, no confusion—just honest advice tailored to your journey.

---

## 🎯 What is SixtSense?

SixtSense is a conversational AI chatbot that recommends vehicle upgrades based on your specific trip needs. Instead of browsing through endless car options, just chat with our AI agent about your plans, and it will suggest the best upgrades for you.

### Key Features

- 💬 **Natural Conversation**: Chat naturally about your trip plans
- 🚙 **Smart Recommendations**: AI suggests vehicles that match your needs
- 🛡️ **Protection Guidance**: Get help choosing the right insurance coverage
- 🎒 **Add-on Suggestions**: Recommendations for extras like GPS or child seats

---

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.10+
- OpenAI API key

### Installation

#### Frontend
```bash
cd frontend/web
pnpm install
pnpm dev
```

#### Backend
```bash
cd backend/server
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

#### Environment Setup
Create `.env` files in both frontend and backend:

**Frontend `.env`:**
```bash
VITE_API_BASE_URL=http://localhost:8000
```

**Backend `.env`:**
```bash
OPENAI_API_KEY=your_key_here
SIXT_BASE_URL=https://api.sixt.com
```

---

## 📖 How It Works

1. **Start Chatting**: The AI asks about your trip (passengers, luggage, plans)
2. **Get Recommendations**: Receive 2-3 vehicle options with clear explanations
3. **Choose Extras**: Select protection and add-ons that fit your needs
4. **Book**: Complete your upgrade

---

## 👥 Team

Built at hackaTUM 2025 for the SIXT challenge.

---

## 📄 License

Created for hackaTUM 2025.
