"""
UGA Nutrition App - Enhanced Version with Groq Integration
A nutrition guidance application for UGA students using AI-powered recommendations
"""

import streamlit as st
from datetime import datetime, timedelta
import json
import os

# Import custom modules
try:
    from groq_agent import NutritionAgent, create_agent
    from data_models import get_sample_menu_data, get_sample_faq_data, search_menu_items
    MODULES_AVAILABLE = True
except ImportError:
    MODULES_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="UGA Nutrition Assistant",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for UGA branding
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .main-header {
        background: linear-gradient(135deg, #BA0C2F 0%, #000000 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
    }
    .main-header h1 {
        color: white !important;
        margin-bottom: 0.5rem;
    }
    .main-header p {
        color: rgba(255,255,255,0.9);
        margin: 0;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #BA0C2F;
        margin: 0.5rem 0;
    }
    .goal-card {
        background: linear-gradient(135deg, #BA0C2F 0%, #9a0a27 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .goal-card h4, .goal-card h2, .goal-card p {
        color: white !important;
    }
    .food-item {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border: 1px solid #e0e0e0;
        transition: all 0.2s;
    }
    .food-item:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        border-color: #BA0C2F;
    }
    .chat-user {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0 0.5rem 2rem;
    }
    .chat-assistant {
        background: #f5f5f5;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 2rem 0.5rem 0;
        border-left: 3px solid #BA0C2F;
    }
    .citation-box {
        font-size: 0.85rem;
        color: #666;
        background: #fff3cd;
        padding: 0.75rem;
        border-radius: 5px;
        margin-top: 0.5rem;
    }
    .tip-box {
        background: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    .warning-box {
        background: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
    }
    .tag {
        display: inline-block;
        background: #e0e0e0;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        margin: 0.1rem;
    }
    .tag-protein { background: #bbdefb; }
    .tag-vegetarian { background: #c8e6c9; }
    .tag-vegan { background: #a5d6a7; }
    .tag-gf { background: #ffe0b2; }
</style>
""", unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    defaults = {
        'user_profile': None,
        'goals': None,
        'daily_targets': None,
        'food_log': [],
        'chat_history': [],
        'current_page': 'home',
        'onboarding_complete': False,
        'groq_api_key': os.environ.get('GROQ_API_KEY', ''),
        'menu_data': get_sample_menu_data() if MODULES_AVAILABLE else []
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()


# Initialize Groq Agent
@st.cache_resource
def get_agent(api_key: str):
    """Get or create a Groq agent instance"""
    if MODULES_AVAILABLE and api_key:
        return create_agent(api_key)
    return None


# Helper function to build context
def build_agent_context(include_log=True):
    """Build context dictionary for the AI agent"""
    context = {
        'user_profile': st.session_state.user_profile,
        'goals': st.session_state.goals,
        'targets': st.session_state.daily_targets,
    }
    
    if include_log:
        today = str(datetime.now().date())
        today_log = [e for e in st.session_state.food_log if e.get('date') == today]
        context['today_log'] = today_log
        context['today_totals'] = {
            'calories': sum(e.get('calories', 0) * e.get('servings', 1) for e in today_log),
            'protein': sum(e.get('protein', 0) * e.get('servings', 1) for e in today_log),
            'carbs': sum(e.get('carbs', 0) * e.get('servings', 1) for e in today_log),
            'fat': sum(e.get('fat', 0) * e.get('servings', 1) for e in today_log),
        }
    
    return context


def get_agent_response(user_input: str, context: dict) -> dict:
    """Get response from Groq agent or fallback"""
    api_key = st.session_state.get('groq_api_key', '')
    
    if MODULES_AVAILABLE and api_key:
        agent = get_agent(api_key)
        if agent and agent.is_available():
            # Check for concerning content first
            concern_response = agent.check_for_concerning_content(user_input)
            if concern_response:
                return {"message": concern_response, "citation": "UGA Student Support Services", "success": True}
            
            return agent.get_response(
                user_input, 
                context, 
                st.session_state.chat_history
            )
    
    # Fallback to simple responses
    return fallback_response(user_input, context)


def fallback_response(user_input: str, context: dict) -> dict:
    """Provide responses when Groq is not available"""
    user_input_lower = user_input.lower()
    targets = context.get('targets', {})
    goal_type = context.get('goals', {}).get('type', 'your goals')
    today_totals = context.get('today_totals', {'calories': 0, 'protein': 0})
    
    if any(word in user_input_lower for word in ['protein', 'muscle', 'bulk']):
        remaining = targets.get('protein', 150) - today_totals.get('protein', 0)
        return {
            "message": f"""Based on your **{goal_type}** goal, you should aim for **{targets.get('protein', 150)}g protein** daily.

**Today's progress:** {today_totals.get('protein', 0)}g consumed, **{max(0, remaining)}g remaining**

**High-protein options at UGA Dining:**
• Grilled Chicken Breast (45g protein) - Bolton, Lunch
• Grilled Salmon (40g protein) - Bolton, Dinner  
• Greek Yogurt Parfait (18g protein) - Bolton, Breakfast
• Grilled Tofu (18g protein) - Snelling, Lunch

Would you like me to suggest a meal plan to hit your target?""",
            "citation": "UGA Dining Services Menu",
            "success": True
        }
    
    elif any(word in user_input_lower for word in ['breakfast', 'morning']):
        return {
            "message": """**Breakfast Options at UGA Dining:**

**🥚 High Protein:**
• Scrambled Eggs (180 cal, 14g protein) - Bolton
• Greek Yogurt Parfait (220 cal, 18g protein) - Bolton
• Veggie Omelet (240 cal, 16g protein) - Snelling

**🌾 High Energy:**
• Oatmeal with Berries (280 cal, 8g protein, 52g carbs) - Snelling
• Whole Wheat Toast (120 cal, 4g protein) - Bolton

**💡 Pro tip:** Combine eggs + oatmeal for 22g protein and sustained energy!

What's your priority - protein, energy, or balanced?""",
            "citation": "UGA Dining Services Menu",
            "success": True
        }
    
    elif any(word in user_input_lower for word in ['calories', 'over', 'under', 'budget']):
        remaining = targets.get('calories', 2000) - today_totals.get('calories', 0)
        status = "on track" if 0 <= remaining <= 500 else "over" if remaining < 0 else "under"
        return {
            "message": f"""**📊 Your Calorie Status:**

• Consumed: **{today_totals.get('calories', 0)} kcal**
• Target: **{targets.get('calories', 2000)} kcal**
• Remaining: **{max(0, remaining)} kcal**

{'✅ You are on track!' if status == 'on track' else ''}
{'⚠️ You are over budget. Consider lighter options or extra activity.' if status == 'over' else ''}
{'💡 You have room for a full meal!' if status == 'under' and remaining > 500 else ''}

**Lower-calorie, high-satiety options:**
• Grilled Chicken + Roasted Vegetables (400 cal, 49g protein)
• Caesar Salad (220 cal, 8g protein)
• Veggie Stir Fry (320 cal, 15g protein)""",
            "citation": "Calculated from your food log",
            "success": True
        }
    
    else:
        return {
            "message": f"""I'm here to help with your nutrition goals! 🐾

**Your Current Setup:**
• 🎯 Goal: {goal_type}
• 🔥 Calories: {targets.get('calories', 'Not set')} kcal/day
• 🥩 Protein: {targets.get('protein', 'Not set')}g/day

**I can help you with:**
1. **Meal suggestions** from UGA Dining halls
2. **Protein optimization** strategies
3. **Progress analysis** based on your log
4. **Dining hall recommendations** for specific goals

Try asking:
• "What should I eat for lunch at Bolton?"
• "How can I hit my protein goal?"
• "What are some healthy breakfast options?"
""",
            "citation": "",
            "success": True
        }


# Sidebar navigation
with st.sidebar:
    st.markdown("### 🐾 UGA Nutrition")
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        ["🏠 Home & Goals", "🍽️ Dining Finder", "📝 Food Log", "🤖 Ask the Agent", "📊 Progress", "⚙️ Settings"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Quick stats if goals are set
    if st.session_state.goals:
        st.markdown("### 📊 Today's Progress")
        targets = st.session_state.daily_targets or {}
        
        today = datetime.now().date()
        today_log = [entry for entry in st.session_state.food_log 
                     if entry.get('date') == str(today)]
        
        total_calories = sum(entry.get('calories', 0) * entry.get('servings', 1) for entry in today_log)
        total_protein = sum(entry.get('protein', 0) * entry.get('servings', 1) for entry in today_log)
        
        cal_target = targets.get('calories', 2000)
        protein_target = targets.get('protein', 150)
        
        cal_pct = min(total_calories / cal_target, 1.0) if cal_target > 0 else 0
        protein_pct = min(total_protein / protein_target, 1.0) if protein_target > 0 else 0
        
        st.progress(cal_pct)
        st.caption(f"🔥 Calories: {int(total_calories)}/{cal_target}")
        
        st.progress(protein_pct)
        st.caption(f"🥩 Protein: {int(total_protein)}g/{protein_target}g")
    
    # API status
    st.markdown("---")
    api_key = st.session_state.get('groq_api_key', '')
    if api_key:
        st.success("✅ AI Agent Active")
    else:
        st.warning("⚠️ Add Groq API key in Settings for AI features")


# ========================
# PAGE: Home & Goals
# ========================
if "Home" in page:
    st.markdown("""
    <div class="main-header">
        <h1>🐾 UGA Nutrition Assistant</h1>
        <p>Your personalized nutrition guide powered by UGA Dining Services</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.onboarding_complete:
        st.markdown("## 🎯 Let's Set Up Your Nutrition Goals")
        st.markdown("Answer a few quick questions to get personalized recommendations.")
        
        with st.form("goal_setup"):
            col1, col2 = st.columns(2)
            
            with col1:
                goal_type = st.selectbox(
                    "What's your primary goal?",
                    ["Build Muscle / Bulk Up", "Lose Fat / Cut", "Maintain Weight", 
                     "Improve Energy", "General Health", "Athletic Performance"]
                )
                
                weight = st.number_input("Current weight (lbs)", min_value=80, max_value=400, value=160)
                height_ft = st.number_input("Height (feet)", min_value=4, max_value=7, value=5)
                height_in = st.number_input("Height (inches)", min_value=0, max_value=11, value=9)
                
            with col2:
                activity_level = st.selectbox(
                    "Activity level",
                    ["Sedentary (little exercise)", "Light (1-3 days/week)", 
                     "Moderate (3-5 days/week)", "Active (6-7 days/week)", 
                     "Very Active (athlete/physical job)"]
                )
                
                dining_preference = st.multiselect(
                    "Preferred dining halls",
                    ["Bolton", "Snelling", "Village Summit", "Niche", "O-House"],
                    default=["Bolton"]
                )
                
                dietary_restrictions = st.multiselect(
                    "Dietary restrictions (optional)",
                    ["Vegetarian", "Vegan", "Gluten-Free", "Dairy-Free", 
                     "Nut Allergy", "Shellfish Allergy", "Halal", "Kosher"]
                )
            
            submitted = st.form_submit_button("🚀 Calculate My Targets", type="primary", use_container_width=True)
            
            if submitted:
                height_cm = (height_ft * 12 + height_in) * 2.54
                weight_kg = weight * 0.453592
                bmr = 10 * weight_kg + 6.25 * height_cm - 5 * 20 + 5
                
                activity_multipliers = {
                    "Sedentary (little exercise)": 1.2,
                    "Light (1-3 days/week)": 1.375,
                    "Moderate (3-5 days/week)": 1.55,
                    "Active (6-7 days/week)": 1.725,
                    "Very Active (athlete/physical job)": 1.9
                }
                
                tdee = bmr * activity_multipliers[activity_level]
                
                goal_adjustments = {
                    "Build Muscle / Bulk Up": (300, 1.0),
                    "Lose Fat / Cut": (-500, 1.0),
                    "Maintain Weight": (0, 0.8),
                    "Improve Energy": (0, 0.8),
                    "General Health": (0, 0.8),
                    "Athletic Performance": (200, 1.0)
                }
                
                cal_adj, protein_mult = goal_adjustments[goal_type]
                target_calories = int(tdee + cal_adj)
                target_protein = int(weight * protein_mult)
                
                st.session_state.user_profile = {
                    'weight': weight,
                    'height_ft': height_ft,
                    'height_in': height_in,
                    'activity_level': activity_level,
                    'dining_preference': dining_preference,
                    'dietary_restrictions': dietary_restrictions
                }
                
                st.session_state.goals = {
                    'type': goal_type,
                    'created_at': str(datetime.now())
                }
                
                st.session_state.daily_targets = {
                    'calories': target_calories,
                    'protein': target_protein,
                    'carbs': int(target_calories * 0.45 / 4),
                    'fat': int(target_calories * 0.25 / 9),
                    'fiber': 30,
                    'sodium': 2300
                }
                
                st.session_state.onboarding_complete = True
                st.rerun()
    
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📊 Your Daily Targets")
            targets = st.session_state.daily_targets
            
            t_cols = st.columns(4)
            with t_cols[0]:
                st.metric("🔥 Calories", f"{targets['calories']}")
            with t_cols[1]:
                st.metric("🥩 Protein", f"{targets['protein']}g")
            with t_cols[2]:
                st.metric("🍞 Carbs", f"{targets['carbs']}g")
            with t_cols[3]:
                st.metric("🧈 Fat", f"{targets['fat']}g")
            
            st.markdown("### ⚡ Quick Actions")
            action_cols = st.columns(3)
            with action_cols[0]:
                st.markdown("""
                <div class="metric-card">
                    <h4>🍽️ Find Meals</h4>
                    <p>Browse today's dining options</p>
                </div>
                """, unsafe_allow_html=True)
            with action_cols[1]:
                st.markdown("""
                <div class="metric-card">
                    <h4>📝 Log Food</h4>
                    <p>Track what you've eaten</p>
                </div>
                """, unsafe_allow_html=True)
            with action_cols[2]:
                st.markdown("""
                <div class="metric-card">
                    <h4>🤖 Get Help</h4>
                    <p>Ask the AI for recommendations</p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="goal-card">
                <h4>🎯 Current Goal</h4>
                <h2>{st.session_state.goals['type']}</h2>
                <p>Started: {st.session_state.goals['created_at'][:10]}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔄 Reset Goals", use_container_width=True):
                st.session_state.onboarding_complete = False
                st.session_state.goals = None
                st.session_state.daily_targets = None
                st.rerun()


# ========================
# PAGE: Dining Finder
# ========================
elif "Dining" in page:
    st.markdown("## 🍽️ UGA Dining Finder")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        selected_hall = st.selectbox("📍 Dining Hall", ["All", "Bolton", "Snelling", "Village Summit", "Niche", "O-House"])
    with col2:
        selected_date = st.date_input("📅 Date", datetime.now())
    with col3:
        selected_meal = st.selectbox("🕐 Meal Period", ["All", "Breakfast", "Lunch", "Dinner", "Late Night"])
    with col4:
        search_query = st.text_input("🔍 Search", placeholder="chicken, salmon...")
    
    # Advanced filters
    with st.expander("🎛️ Advanced Filters"):
        filter_cols = st.columns(3)
        with filter_cols[0]:
            min_protein = st.slider("Minimum Protein (g)", 0, 50, 0)
        with filter_cols[1]:
            max_calories = st.slider("Maximum Calories", 100, 800, 800)
        with filter_cols[2]:
            diet_filter = st.multiselect("Dietary Tags", ["High Protein", "Vegetarian", "Vegan", "Gluten-Free"])
    
    # Get menu data
    menu_data = st.session_state.menu_data
    
    # Apply filters
    filtered = menu_data.copy()
    if selected_hall != "All":
        filtered = [i for i in filtered if i['dining_hall'] == selected_hall]
    if selected_meal != "All":
        filtered = [i for i in filtered if i['meal_period'] == selected_meal]
    if search_query:
        filtered = [i for i in filtered if search_query.lower() in i['name'].lower()]
    if min_protein > 0:
        filtered = [i for i in filtered if i['nutrition']['protein'] >= min_protein]
    if max_calories < 800:
        filtered = [i for i in filtered if i['nutrition']['calories'] <= max_calories]
    if diet_filter:
        filtered = [i for i in filtered if any(t in i.get('tags', []) for t in diet_filter)]
    
    st.markdown(f"### 📋 {len(filtered)} items found")
    
    for item in filtered:
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            
            with col1:
                st.markdown(f"**{item['name']}**")
                st.caption(f"📍 {item['dining_hall']} • {item['meal_period']}")
                tags_html = " ".join([f"`{t}`" for t in item.get('tags', [])])
                st.caption(tags_html)
            
            with col2:
                nutr = item['nutrition']
                st.markdown(f"🔥 **{nutr['calories']}** cal | 🥩 **{nutr['protein']}g** protein")
                st.caption(f"🍞 {nutr['carbs']}g carbs | 🧈 {nutr['fat']}g fat")
            
            with col3:
                if st.button("➕ Add to Log", key=f"add_{item['item_id']}"):
                    log_entry = {
                        'date': str(datetime.now().date()),
                        'time': datetime.now().strftime("%H:%M"),
                        'name': item['name'],
                        'hall': item['dining_hall'],
                        'meal': item['meal_period'],
                        'calories': item['nutrition']['calories'],
                        'protein': item['nutrition']['protein'],
                        'carbs': item['nutrition']['carbs'],
                        'fat': item['nutrition']['fat'],
                        'servings': 1
                    }
                    st.session_state.food_log.append(log_entry)
                    st.toast(f"✅ Added {item['name']} to your log!")
            
            st.markdown("---")


# ========================
# PAGE: Food Log
# ========================
elif "Log" in page:
    st.markdown("## 📝 Food Log")
    
    selected_date = st.date_input("📅 View date", datetime.now())
    
    day_log = [e for e in st.session_state.food_log if e.get('date') == str(selected_date)]
    
    if day_log:
        total_cal = sum(e['calories'] * e.get('servings', 1) for e in day_log)
        total_protein = sum(e['protein'] * e.get('servings', 1) for e in day_log)
        total_carbs = sum(e['carbs'] * e.get('servings', 1) for e in day_log)
        total_fat = sum(e['fat'] * e.get('servings', 1) for e in day_log)
        
        targets = st.session_state.daily_targets or {'calories': 2000, 'protein': 150, 'carbs': 250, 'fat': 65}
        
        st.markdown("### 📊 Daily Summary")
        cols = st.columns(4)
        with cols[0]:
            delta = int(total_cal - targets['calories'])
            st.metric("🔥 Calories", f"{int(total_cal)}", f"{delta:+d}")
        with cols[1]:
            delta = int(total_protein - targets['protein'])
            st.metric("🥩 Protein", f"{int(total_protein)}g", f"{delta:+d}g")
        with cols[2]:
            st.metric("🍞 Carbs", f"{int(total_carbs)}g")
        with cols[3]:
            st.metric("🧈 Fat", f"{int(total_fat)}g")
        
        st.markdown("---")
        st.markdown("### 📋 Logged Items")
        
        for i, entry in enumerate(day_log):
            with st.container():
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.markdown(f"**{entry['name']}**")
                    st.caption(f"📍 {entry.get('hall', 'N/A')} • {entry.get('meal', 'N/A')} • {entry['time']}")
                with col2:
                    st.markdown(f"🔥 {entry['calories']} cal | 🥩 {entry['protein']}g")
                    servings = st.number_input(
                        "Servings", 
                        min_value=0.5, max_value=5.0,
                        value=float(entry.get('servings', 1)),
                        step=0.5, 
                        key=f"serv_{i}",
                        label_visibility="collapsed"
                    )
                    idx = st.session_state.food_log.index(entry)
                    st.session_state.food_log[idx]['servings'] = servings
                with col3:
                    if st.button("🗑️", key=f"del_{i}"):
                        st.session_state.food_log.remove(entry)
                        st.rerun()
                st.markdown("---")
        
        st.markdown("### 📥 Export")
        col1, col2 = st.columns(2)
        with col1:
            csv_data = "date,time,name,hall,meal,calories,protein,carbs,fat,servings\n"
            for e in day_log:
                csv_data += f"{e['date']},{e['time']},{e['name']},{e.get('hall','')},{e.get('meal','')},{e['calories']},{e['protein']},{e['carbs']},{e['fat']},{e.get('servings',1)}\n"
            st.download_button("📄 Download CSV", csv_data, "food_log.csv", "text/csv", use_container_width=True)
        with col2:
            st.download_button("📄 Download JSON", json.dumps(day_log, indent=2), "food_log.json", use_container_width=True)
    
    else:
        st.info("📭 No items logged for this date. Go to Dining Finder to add meals!")


# ========================
# PAGE: Ask the Agent
# ========================
elif "Agent" in page:
    st.markdown("## 🤖 Ask the Nutrition Agent")
    
    # Check API status
    if not st.session_state.get('groq_api_key'):
        st.markdown("""
        <div class="warning-box">
            <strong>⚠️ AI Agent Not Configured</strong><br>
            Add your Groq API key in Settings to enable AI-powered responses. 
            Basic responses are still available.
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="tip-box">
        💡 <strong>Try asking:</strong> "What should I eat at Bolton to hit my protein goal?" or 
        "How can I adjust my dinner to stay under calories?"
    </div>
    """, unsafe_allow_html=True)
    
    # Suggested prompts
    st.markdown("### 💬 Suggested Questions")
    prompt_cols = st.columns(2)
    prompts = [
        "What high-protein options are at Bolton today?",
        "How can I hit my protein goal with dinner?",
        "What are healthy breakfast options?",
        "Help me plan meals to stay under my calorie target"
    ]
    
    for i, prompt in enumerate(prompts):
        with prompt_cols[i % 2]:
            if st.button(prompt, key=f"prompt_{i}", use_container_width=True):
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                context = build_agent_context(True)
                response = get_agent_response(prompt, context)
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": response["message"],
                    "citation": response.get("citation", "")
                })
                st.rerun()
    
    st.markdown("---")
    
    use_log = st.checkbox("📝 Include my food log for context", value=True)
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"""<div class="chat-user"><strong>You:</strong> {message["content"]}</div>""", unsafe_allow_html=True)
        else:
            st.markdown(f"""<div class="chat-assistant"><strong>🤖 Agent:</strong><br>{message["content"]}</div>""", unsafe_allow_html=True)
            if message.get("citation"):
                st.markdown(f"""<div class="citation-box">📚 Source: {message["citation"]}</div>""", unsafe_allow_html=True)
    
    # Chat input
    user_input = st.chat_input("Ask about nutrition, dining options, or your goals...")
    
    if user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        context = build_agent_context(use_log)
        response = get_agent_response(user_input, context)
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": response["message"],
            "citation": response.get("citation", "")
        })
        st.rerun()
    
    if st.session_state.chat_history:
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()


# ========================
# PAGE: Progress
# ========================
elif "Progress" in page:
    st.markdown("## 📊 Progress Tracking")
    
    if not st.session_state.food_log:
        st.info("📭 Start logging meals to see your progress!")
    else:
        import pandas as pd
        from collections import defaultdict
        
        today = datetime.now().date()
        week_ago = today - timedelta(days=7)
        
        week_log = [e for e in st.session_state.food_log 
                    if week_ago <= datetime.strptime(e['date'], '%Y-%m-%d').date() <= today]
        
        if week_log:
            daily_totals = defaultdict(lambda: {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0})
            
            for entry in week_log:
                date = entry['date']
                servings = entry.get('servings', 1)
                daily_totals[date]['calories'] += entry['calories'] * servings
                daily_totals[date]['protein'] += entry['protein'] * servings
                daily_totals[date]['carbs'] += entry['carbs'] * servings
                daily_totals[date]['fat'] += entry['fat'] * servings
            
            df = pd.DataFrame([{'Date': k, **v} for k, v in sorted(daily_totals.items())])
            
            if not df.empty:
                st.markdown("### 📈 Weekly Calories")
                st.line_chart(df.set_index('Date')['calories'])
                
                st.markdown("### 📈 Weekly Macros")
                st.line_chart(df.set_index('Date')[['protein', 'carbs', 'fat']])
                
                st.markdown("### 📊 Averages")
                cols = st.columns(4)
                with cols[0]:
                    st.metric("Avg Calories", f"{int(df['calories'].mean())}")
                with cols[1]:
                    st.metric("Avg Protein", f"{int(df['protein'].mean())}g")
                with cols[2]:
                    st.metric("Days Logged", len(df))
                with cols[3]:
                    targets = st.session_state.daily_targets or {}
                    if targets.get('protein'):
                        days_hit = sum(1 for _, row in df.iterrows() if row['protein'] >= targets['protein'])
                        st.metric("Days Hit Protein", f"{days_hit}/{len(df)}")


# ========================
# PAGE: Settings
# ========================
elif "Settings" in page:
    st.markdown("## ⚙️ Settings")
    
    st.markdown("### 🔑 API Configuration")
    
    api_key = st.text_input(
        "Groq API Key",
        value=st.session_state.get('groq_api_key', ''),
        type="password",
        help="Get your API key at https://console.groq.com"
    )
    
    if api_key != st.session_state.get('groq_api_key', ''):
        st.session_state.groq_api_key = api_key
        st.success("✅ API key updated!")
    
    st.markdown("[🔗 Get your free Groq API key](https://console.groq.com)")
    
    st.markdown("---")
    st.markdown("### 📊 Current Profile")
    
    if st.session_state.user_profile:
        st.json(st.session_state.user_profile)
    else:
        st.info("No profile set. Go to Home to set up your goals.")
    
    st.markdown("---")
    st.markdown("### 🗑️ Data Management")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear All Data", type="secondary", use_container_width=True):
            for key in ['user_profile', 'goals', 'daily_targets', 'food_log', 'chat_history']:
                st.session_state[key] = [] if key in ['food_log', 'chat_history'] else None
            st.session_state.onboarding_complete = False
            st.success("✅ All data cleared!")
            st.rerun()
    
    with col2:
        if st.button("📥 Export All Data", use_container_width=True):
            all_data = {
                'profile': st.session_state.user_profile,
                'goals': st.session_state.goals,
                'targets': st.session_state.daily_targets,
                'food_log': st.session_state.food_log
            }
            st.download_button(
                "💾 Download Backup",
                json.dumps(all_data, indent=2),
                "uga_nutrition_backup.json",
                use_container_width=True
            )


# Footer
st.markdown("---")
st.caption("🐾 UGA Nutrition Assistant | Powered by UGA Dining Services Data | Not medical advice | Go Dawgs!")
