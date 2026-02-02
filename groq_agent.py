"""
Groq Integration Module for UGA Nutrition Agent
This module handles all AI/LLM functionality using Groq's API
"""

import os
from typing import Optional
import json

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    print("Warning: groq package not installed. Run: pip install groq")


class NutritionAgent:
    """
    AI Agent for nutrition guidance using Groq's LLM API.
    Provides goal-based nutrition advice grounded in UGA Dining data.
    """
    
    SYSTEM_PROMPT = """You are a friendly and knowledgeable nutrition assistant for University of Georgia students. 
Your role is to help students achieve their nutrition goals using UGA Dining Services options.

## Your Capabilities:
1. Help students define nutrition goals (bulk/cut/maintenance, performance, energy, general health)
2. Propose daily targets (protein, calories, fiber, sodium)
3. Recommend specific meals from UGA Dining halls based on their menus
4. Reflect on logged meals and suggest adjustments
5. Answer general nutrition questions

## Important Guidelines:
- Always ground your meal recommendations in ACTUAL UGA Dining options provided in the context
- Be supportive and encouraging, never judgmental
- Use simple, actionable language
- When recommending meals, include specific items, dining halls, and meal periods
- Include approximate nutrition info when available
- Cite sources when providing nutrition advice (e.g., "According to UGA nutrition guidelines...")

## Safety Boundaries:
- You are NOT a medical professional - refer clinical questions to UGA's campus nutrition counseling
- Do NOT provide eating disorder coaching or extreme restriction advice
- If a user shows signs of disordered eating or risky behavior, respond supportively and recommend professional help
- Keep recommendations within safe, evidence-based ranges

## Response Format:
- Be conversational but informative
- Use bullet points for meal suggestions
- Include specific numbers (calories, protein grams) when available
- End with a helpful follow-up question or actionable next step
"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Nutrition Agent with Groq API.
        
        Args:
            api_key: Groq API key. If not provided, will look for GROQ_API_KEY env variable.
        """
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        self.client = None
        self.model = "llama-3.3-70b-versatile"  # Recommended model for this use case
        
        if GROQ_AVAILABLE and self.api_key:
            self.client = Groq(api_key=self.api_key)
    
    def is_available(self) -> bool:
        """Check if Groq API is properly configured"""
        return self.client is not None
    
    def build_context_message(self, context: dict) -> str:
        """
        Build a context message from user data to include in the prompt.
        
        Args:
            context: Dictionary containing user profile, goals, targets, and food log
        """
        parts = []
        
        # User profile
        if context.get('user_profile'):
            profile = context['user_profile']
            parts.append(f"""## User Profile:
- Weight: {profile.get('weight', 'Not set')} lbs
- Activity Level: {profile.get('activity_level', 'Not set')}
- Preferred Dining Halls: {', '.join(profile.get('dining_preference', ['Any']))}
- Dietary Restrictions: {', '.join(profile.get('dietary_restrictions', ['None']))}""")
        
        # Goals and targets
        if context.get('goals'):
            goals = context['goals']
            targets = context.get('targets', {})
            parts.append(f"""## Current Goals:
- Primary Goal: {goals.get('type', 'Not set')}
- Daily Calorie Target: {targets.get('calories', 'Not set')} kcal
- Daily Protein Target: {targets.get('protein', 'Not set')}g
- Daily Carb Target: {targets.get('carbs', 'Not set')}g
- Daily Fat Target: {targets.get('fat', 'Not set')}g""")
        
        # Today's food log
        if context.get('today_log'):
            log_items = context['today_log']
            totals = context.get('today_totals', {})
            
            log_text = "\n".join([
                f"- {item['name']} ({item['calories']} cal, {item['protein']}g protein) at {item.get('hall', 'N/A')}"
                for item in log_items
            ])
            
            parts.append(f"""## Today's Food Log:
{log_text if log_items else 'No items logged yet'}

## Today's Totals:
- Calories consumed: {totals.get('calories', 0)} kcal
- Protein consumed: {totals.get('protein', 0)}g""")
        
        # Available menu items (would come from database)
        parts.append("""## Today's UGA Dining Options (Sample):
### Bolton Dining Hall:
**Breakfast:**
- Scrambled Eggs: 180 cal, 14g protein, 2g carbs, 12g fat
- Greek Yogurt Parfait: 220 cal, 18g protein, 28g carbs, 4g fat

**Lunch:**
- Grilled Chicken Breast: 280 cal, 45g protein, 0g carbs, 8g fat
- Turkey Wrap: 380 cal, 28g protein, 35g carbs, 14g fat

**Dinner:**
- Grilled Salmon: 350 cal, 40g protein, 2g carbs, 18g fat
- Beef Stir Fry: 420 cal, 32g protein, 28g carbs, 22g fat

### Snelling Dining Hall:
**Breakfast:**
- Oatmeal with Berries: 280 cal, 8g protein, 52g carbs, 5g fat

**Lunch:**
- Brown Rice Bowl: 420 cal, 12g protein, 68g carbs, 8g fat
- Veggie Stir Fry: 320 cal, 15g protein, 42g carbs, 10g fat""")
        
        return "\n\n".join(parts)
    
    def get_response(
        self, 
        user_message: str, 
        context: dict,
        chat_history: list = None
    ) -> dict:
        """
        Get a response from the AI agent.
        
        Args:
            user_message: The user's question or request
            context: Dictionary with user profile, goals, targets, and food log
            chat_history: Previous messages in the conversation
            
        Returns:
            Dictionary with 'message', 'citation', and 'success' keys
        """
        if not self.is_available():
            return self._get_fallback_response(user_message, context)
        
        try:
            # Build messages array
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT}
            ]
            
            # Add context as a system message
            context_message = self.build_context_message(context)
            messages.append({
                "role": "system", 
                "content": f"## Current Context:\n{context_message}"
            })
            
            # Add chat history (last 10 messages to stay within limits)
            if chat_history:
                for msg in chat_history[-10:]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                top_p=0.9,
            )
            
            assistant_message = response.choices[0].message.content
            
            return {
                "message": assistant_message,
                "citation": "UGA Dining Services Data & Nutrition Guidelines",
                "success": True
            }
            
        except Exception as e:
            print(f"Groq API error: {e}")
            return self._get_fallback_response(user_message, context)
    
    def _get_fallback_response(self, user_message: str, context: dict) -> dict:
        """
        Provide a rule-based fallback response when API is unavailable.
        """
        user_input_lower = user_message.lower()
        targets = context.get('targets', {})
        goal_type = context.get('goals', {}).get('type', 'your goals')
        today_totals = context.get('today_totals', {})
        
        # Simple keyword-based responses
        if any(word in user_input_lower for word in ['protein', 'muscle', 'bulk']):
            remaining_protein = targets.get('protein', 150) - today_totals.get('protein', 0)
            return {
                "message": f"""Great question about protein! Based on your goal of **{goal_type}**, 
you should aim for **{targets.get('protein', 150)}g of protein** daily.

**You've logged {today_totals.get('protein', 0)}g so far**, which means you need about **{max(0, remaining_protein)}g more** today.

**Top high-protein options at UGA Dining:**
- 🍗 Grilled Chicken Breast (45g protein) - Bolton, Lunch
- 🐟 Grilled Salmon (40g protein) - Bolton, Dinner
- 🥛 Greek Yogurt Parfait (18g protein) - Bolton, Breakfast

Would you like me to suggest a meal plan to hit your protein target?""",
                "citation": "UGA Dining Services Menu Data",
                "success": True
            }
        
        elif any(word in user_input_lower for word in ['breakfast', 'morning']):
            return {
                "message": """Here are great breakfast options at UGA Dining:

**High Protein (Best for Muscle Building):**
- 🥚 Scrambled Eggs - 180 cal, 14g protein (Bolton)
- 🥛 Greek Yogurt Parfait - 220 cal, 18g protein (Bolton)

**High Energy (Best for Performance):**
- 🥣 Oatmeal with Berries - 280 cal, 8g protein, 52g carbs (Snelling)

**Balanced Option:**
- Eggs + Oatmeal combo gives you 22g protein and sustained energy!

What's your priority for breakfast - protein, energy, or a balance of both?""",
                "citation": "UGA Dining Services Menu",
                "success": True
            }
        
        elif any(word in user_input_lower for word in ['lunch', 'dinner', 'meal']):
            return {
                "message": f"""Let me suggest some meals based on your **{goal_type}** goal:

**For Lunch at Bolton:**
- Grilled Chicken Breast (280 cal, 45g protein) 
- Add a side of vegetables for fiber

**For Dinner at Bolton:**
- Grilled Salmon (350 cal, 40g protein) - excellent omega-3s!
- Beef Stir Fry (420 cal, 32g protein) - good for variety

**Lighter Options at Snelling:**
- Brown Rice Bowl (420 cal, 12g protein)
- Veggie Stir Fry (320 cal, 15g protein)

Your daily targets: {targets.get('calories', 2000)} cal | {targets.get('protein', 150)}g protein

Would you like a complete meal plan for today?""",
                "citation": "UGA Dining Services Menu",
                "success": True
            }
        
        elif any(word in user_input_lower for word in ['calories', 'cal', 'over', 'under']):
            remaining_cal = targets.get('calories', 2000) - today_totals.get('calories', 0)
            return {
                "message": f"""Let's look at your calorie status:

**Today's Progress:**
- Consumed: {today_totals.get('calories', 0)} kcal
- Target: {targets.get('calories', 2000)} kcal
- Remaining: {max(0, remaining_cal)} kcal

{'✅ You are on track!' if 0 <= remaining_cal <= 500 else ''}
{'⚠️ You have plenty of room for a full meal!' if remaining_cal > 500 else ''}
{'⚠️ You are over your target. Consider a lighter dinner or extra activity!' if remaining_cal < 0 else ''}

**Low-calorie, high-protein options if you need to stay under budget:**
- Grilled Chicken (280 cal) with vegetables
- Scrambled Eggs (180 cal) for a light meal

How can I help you adjust your remaining meals?""",
                "citation": "Calculated from your food log",
                "success": True
            }
        
        else:
            return {
                "message": f"""I'm here to help with your nutrition goals! 

**Your Current Setup:**
- 🎯 Goal: {goal_type}
- 🔥 Calorie Target: {targets.get('calories', 'Not set')} kcal/day
- 🥩 Protein Target: {targets.get('protein', 'Not set')}g/day

**I can help you with:**
1. 🍽️ **Meal suggestions** from UGA Dining halls
2. 💪 **Protein optimization** to hit your targets  
3. 📊 **Progress analysis** based on your food log
4. 🎯 **Goal adjustments** as you progress

What would you like to focus on?""",
                "citation": "",
                "success": True
            }
    
    def check_for_concerning_content(self, user_message: str) -> Optional[str]:
        """
        Check for signs of disordered eating or concerning behavior.
        Returns a supportive message if detected, None otherwise.
        """
        concerning_phrases = [
            'not eating', 'starving', 'purge', 'binge', 'hate my body',
            'too fat', 'disgusting', 'fast for days', 'laxative',
            'make myself throw up', 'eating disorder'
        ]
        
        message_lower = user_message.lower()
        
        if any(phrase in message_lower for phrase in concerning_phrases):
            return """I hear that you might be going through a difficult time with food and your body. 
            
Your wellbeing matters more than any nutrition goal. 💙

**UGA has free, confidential support available:**
- UGA Counseling & Psychiatric Services (CAPS): (706) 542-2273
- UGA Health Center Nutrition Services: (706) 542-8690

Would you like me to help you find more resources, or is there something else I can support you with today?"""
        
        return None


# Convenience function for Streamlit integration
def create_agent(api_key: Optional[str] = None) -> NutritionAgent:
    """Create and return a NutritionAgent instance"""
    return NutritionAgent(api_key)


# Example usage
if __name__ == "__main__":
    # Test the agent
    agent = NutritionAgent()
    
    test_context = {
        'user_profile': {
            'weight': 160,
            'activity_level': 'Moderate',
            'dining_preference': ['Bolton'],
            'dietary_restrictions': []
        },
        'goals': {'type': 'Build Muscle / Bulk Up'},
        'targets': {'calories': 2500, 'protein': 160, 'carbs': 280, 'fat': 80},
        'today_log': [],
        'today_totals': {'calories': 500, 'protein': 40}
    }
    
    response = agent.get_response("What should I eat for lunch to hit my protein goal?", test_context)
    print(response['message'])
