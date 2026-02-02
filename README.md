# 🐾 UGA Nutrition Assistant

A Streamlit-based nutrition guidance application for University of Georgia students, powered by AI and grounded in UGA Dining Services data.

![UGA Nutrition App](https://img.shields.io/badge/UGA-Nutrition%20App-red)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red)
![Groq](https://img.shields.io/badge/LLM-Groq-orange)

## 🎯 Features

- **AI-Powered Nutrition Agent**: Get personalized meal recommendations grounded in UGA Dining menus
- **Goal Setting**: Define your nutrition goals (bulk, cut, maintain, performance)
- **Dining Hall Finder**: Browse and search UGA Dining Services menus
- **Food Logging**: Track your daily nutrition intake
- **Progress Tracking**: Visualize your progress towards your goals
- **Export Capabilities**: Export your food log as CSV or JSON

## 🚀 Quick Start

### 1. Clone and Install

```bash
# Clone or download the project
cd uga_nutrition_app

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up Groq API (for AI features)

The app uses [Groq](https://groq.com/) for AI-powered chat functionality. Groq provides extremely fast inference with LLaMA models.

#### Get Your API Key:
1. Go to [https://console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Navigate to API Keys section
4. Create a new API key

#### Configure the API Key:

**Option A: Environment Variable (Recommended)**
```bash
# Linux/Mac
export GROQ_API_KEY="your-api-key-here"

# Windows PowerShell
$env:GROQ_API_KEY="your-api-key-here"

# Or create a .env file
echo "GROQ_API_KEY=your-api-key-here" > .env
```

**Option B: In the App**
Enter your API key in the Settings page of the application.

### 3. Run the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 🔌 Groq Integration Details

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                       │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────────┐ │
│  │  Goal   │  │ Dining  │  │  Food   │  │   AI Chat       │ │
│  │  Setup  │  │ Finder  │  │   Log   │  │   Interface     │ │
│  └─────────┘  └─────────┘  └─────────┘  └────────┬────────┘ │
└──────────────────────────────────────────────────┼──────────┘
                                                   │
                    ┌──────────────────────────────┼──────────┐
                    │          groq_agent.py       │          │
                    │  ┌───────────────────────────▼────────┐ │
                    │  │      NutritionAgent Class          │ │
                    │  │  - System Prompt (guidelines)      │ │
                    │  │  - Context Builder (user data)     │ │
                    │  │  - Safety Checks                   │ │
                    │  │  - Fallback Responses              │ │
                    │  └───────────────────────────┬────────┘ │
                    └──────────────────────────────┼──────────┘
                                                   │
                    ┌──────────────────────────────▼──────────┐
                    │              Groq API                    │
                    │   Model: llama-3.3-70b-versatile        │
                    │   Fast inference, low latency            │
                    └─────────────────────────────────────────┘
```

### Key Components

#### 1. NutritionAgent Class (`groq_agent.py`)

```python
from groq_agent import NutritionAgent

# Initialize the agent
agent = NutritionAgent(api_key="your-api-key")  # Or use env var

# Check if API is configured
if agent.is_available():
    print("Groq API is ready!")

# Build context from user data
context = {
    'user_profile': {...},
    'goals': {...},
    'targets': {...},
    'today_log': [...],
    'today_totals': {...}
}

# Get AI response
response = agent.get_response(
    user_message="What should I eat for lunch?",
    context=context,
    chat_history=[]
)

print(response['message'])
print(response['citation'])
```

#### 2. System Prompt

The agent uses a carefully crafted system prompt that:
- Defines its role as a UGA nutrition assistant
- Sets capabilities and boundaries
- Enforces safety guidelines
- Specifies response format

#### 3. Context Building

The agent receives rich context including:
- User profile (weight, activity level, preferences)
- Current goals and daily targets
- Today's food log and totals
- Available menu items from UGA Dining

### Customizing the Agent

#### Change the Model

```python
# In groq_agent.py
self.model = "llama-3.3-70b-versatile"  # Default

# Available models:
# - llama-3.3-70b-versatile (recommended)
# - llama-3.1-70b-versatile
# - llama-3.1-8b-instant (faster, less capable)
# - mixtral-8x7b-32768
```

#### Modify the System Prompt

Edit the `SYSTEM_PROMPT` in `groq_agent.py` to customize the agent's behavior:

```python
SYSTEM_PROMPT = """You are a friendly nutrition assistant...
# Add your customizations here
"""
```

#### Add RAG (Retrieval Augmented Generation)

For production, you'll want to add RAG for real-time menu data:

```python
# Example: Add vector search for menu items
from your_vector_db import search_similar_items

def get_relevant_menu_items(query, top_k=5):
    return search_similar_items(query, top_k)

# In build_context_message:
relevant_items = get_relevant_menu_items(user_message)
context['relevant_menu_items'] = relevant_items
```

## 📁 Project Structure

```
uga_nutrition_app/
├── app.py              # Main Streamlit application
├── groq_agent.py       # Groq AI integration module
├── data_models.py      # Data models and sample data
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── .env               # Environment variables (create this)
└── data/
    ├── sample_menu_data.json
    └── sample_faq_data.json
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Your Groq API key | Yes (for AI features) |
| `STREAMLIT_SERVER_PORT` | Custom port (default: 8501) | No |

### App Settings

Configurable in the Settings page:
- Groq API Key
- Default dining hall preference
- Dietary restrictions

## 📊 Data Integration

### UGA Dining Services Data

For production, you'll need to integrate real UGA Dining data:

1. **Menu API**: If available, connect to UGA's menu API
2. **CSV Import**: Import menu data from spreadsheets
3. **Web Scraping**: Last resort, scrape public menu pages

Example data format:
```json
{
  "item_id": "bolt-001",
  "name": "Grilled Chicken Breast",
  "dining_hall": "Bolton",
  "meal_period": "Lunch",
  "date": "2024-01-15",
  "nutrition": {
    "calories": 280,
    "protein": 45,
    "carbs": 0,
    "fat": 8
  },
  "tags": ["High Protein", "Gluten-Free"]
}
```

## 🛡️ Safety Features

The agent includes built-in safety measures:

1. **Not Medical Advice**: Clear disclaimers about not providing medical advice
2. **Eating Disorder Detection**: Flags concerning content and suggests resources
3. **Safe Recommendations**: Uses conservative, evidence-based ranges
4. **Professional Referrals**: Directs to UGA counseling when appropriate

## 🎨 Customization

### UGA Branding

The app uses UGA's official colors:
- Primary Red: `#BA0C2F`
- Secondary Black: `#000000`

Modify in `app.py`:
```python
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #BA0C2F 0%, #000000 100%);
    }
</style>
""", unsafe_allow_html=True)
```

## 📱 Deployment

### Streamlit Cloud (Recommended)

1. Push to GitHub
2. Connect at [share.streamlit.io](https://share.streamlit.io)
3. Add `GROQ_API_KEY` to Secrets

### Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

### Heroku

```bash
heroku create uga-nutrition-app
heroku config:set GROQ_API_KEY=your-key
git push heroku main
```

## 🧪 Testing

```bash
# Test the Groq integration
python groq_agent.py

# Test data models
python data_models.py
```

## 📝 API Rate Limits

Groq's free tier includes:
- Requests per minute: 30
- Requests per day: 14,400
- Tokens per minute: 7,000

For production, consider Groq's paid plans or implement caching.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is for educational purposes as part of the UGA GenAI Competition.

## 🆘 Support

- **UGA CAPS**: (706) 542-2273
- **UGA Health Center**: (706) 542-8690
- **UGA Dining Services**: dining.uga.edu

---

**Go Dawgs! 🐾**
