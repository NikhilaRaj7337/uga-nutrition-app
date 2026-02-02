"""
Data Models and Sample Data for UGA Nutrition App
Contains Pydantic models and sample UGA Dining data
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional
from enum import Enum
import json


# Enums
class MealPeriod(str, Enum):
    BREAKFAST = "Breakfast"
    LUNCH = "Lunch"
    DINNER = "Dinner"
    LATE_NIGHT = "Late Night"


class DiningHall(str, Enum):
    BOLTON = "Bolton"
    SNELLING = "Snelling"
    VILLAGE_SUMMIT = "Village Summit"
    NICHE = "Niche"
    OHOUSE = "O-House"


class GoalType(str, Enum):
    BULK = "Build Muscle / Bulk Up"
    CUT = "Lose Fat / Cut"
    MAINTAIN = "Maintain Weight"
    ENERGY = "Improve Energy"
    HEALTH = "General Health"
    PERFORMANCE = "Athletic Performance"


class DietaryTag(str, Enum):
    VEGETARIAN = "Vegetarian"
    VEGAN = "Vegan"
    GLUTEN_FREE = "Gluten-Free"
    DAIRY_FREE = "Dairy-Free"
    HIGH_PROTEIN = "High Protein"
    LOW_CARB = "Low Carb"
    HIGH_FIBER = "High Fiber"
    LOW_SODIUM = "Low Sodium"


# Data Classes
@dataclass
class NutritionProfile:
    """Nutritional information for a food item"""
    calories: int
    protein: float  # grams
    carbs: float    # grams
    fat: float      # grams
    fiber: float = 0.0      # grams
    sodium: float = 0.0     # mg
    added_sugar: float = 0.0  # grams
    
    def to_dict(self) -> dict:
        return {
            'calories': self.calories,
            'protein': self.protein,
            'carbs': self.carbs,
            'fat': self.fat,
            'fiber': self.fiber,
            'sodium': self.sodium,
            'added_sugar': self.added_sugar
        }


@dataclass
class Recipe:
    """UGA Dining recipe"""
    recipe_id: str
    name: str
    serving_size: str  # e.g., "1 cup", "4 oz"
    nutrition: NutritionProfile
    ingredients: list = field(default_factory=list)
    instructions: str = ""
    category: str = ""
    
    def to_dict(self) -> dict:
        return {
            'recipe_id': self.recipe_id,
            'name': self.name,
            'serving_size': self.serving_size,
            'nutrition': self.nutrition.to_dict(),
            'ingredients': self.ingredients,
            'category': self.category
        }


@dataclass
class MenuItem:
    """A menu item served at a dining location"""
    item_id: str
    name: str
    dining_hall: str
    meal_period: str
    date: str  # YYYY-MM-DD format
    nutrition: NutritionProfile
    tags: list = field(default_factory=list)
    allergens: list = field(default_factory=list)
    recipe_id: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            'item_id': self.item_id,
            'name': self.name,
            'dining_hall': self.dining_hall,
            'meal_period': self.meal_period,
            'date': self.date,
            'nutrition': self.nutrition.to_dict(),
            'tags': self.tags,
            'allergens': self.allergens,
            'recipe_id': self.recipe_id
        }


@dataclass
class UserProfile:
    """User profile information"""
    weight: float  # lbs
    height_ft: int
    height_in: int
    activity_level: str
    dining_preference: list
    dietary_restrictions: list = field(default_factory=list)
    
    def get_height_cm(self) -> float:
        return (self.height_ft * 12 + self.height_in) * 2.54
    
    def get_weight_kg(self) -> float:
        return self.weight * 0.453592


@dataclass
class UserGoal:
    """User nutrition goals"""
    goal_type: str
    created_at: datetime
    target_calories: int
    target_protein: int  # grams
    target_carbs: int    # grams
    target_fat: int      # grams
    target_fiber: int = 30   # grams
    target_sodium: int = 2300  # mg


@dataclass
class LogEntry:
    """Food log entry"""
    entry_id: str
    date: str
    time: str
    item_name: str
    dining_hall: str
    meal_period: str
    servings: float
    nutrition: NutritionProfile
    
    def get_adjusted_nutrition(self) -> dict:
        """Get nutrition values adjusted for servings"""
        return {
            'calories': int(self.nutrition.calories * self.servings),
            'protein': round(self.nutrition.protein * self.servings, 1),
            'carbs': round(self.nutrition.carbs * self.servings, 1),
            'fat': round(self.nutrition.fat * self.servings, 1),
            'fiber': round(self.nutrition.fiber * self.servings, 1),
            'sodium': round(self.nutrition.sodium * self.servings, 1),
        }


# Sample Data
def get_sample_menu_data() -> list[dict]:
    """Return sample UGA Dining menu data"""
    
    menu_items = [
        # Bolton - Breakfast
        MenuItem(
            item_id="bolt-001",
            name="Scrambled Eggs",
            dining_hall="Bolton",
            meal_period="Breakfast",
            date=str(date.today()),
            nutrition=NutritionProfile(calories=180, protein=14, carbs=2, fat=12, fiber=0, sodium=350),
            tags=["Vegetarian", "Gluten-Free", "High Protein"],
            allergens=["Eggs"]
        ),
        MenuItem(
            item_id="bolt-002",
            name="Greek Yogurt Parfait",
            dining_hall="Bolton",
            meal_period="Breakfast",
            date=str(date.today()),
            nutrition=NutritionProfile(calories=220, protein=18, carbs=28, fat=4, fiber=2, sodium=80),
            tags=["Vegetarian", "High Protein"],
            allergens=["Dairy"]
        ),
        MenuItem(
            item_id="bolt-003",
            name="Turkey Sausage",
            dining_hall="Bolton",
            meal_period="Breakfast",
            date=str(date.today()),
            nutrition=NutritionProfile(calories=160, protein=12, carbs=2, fat=11, fiber=0, sodium=480),
            tags=["High Protein", "Gluten-Free"],
            allergens=[]
        ),
        MenuItem(
            item_id="bolt-004",
            name="Whole Wheat Toast",
            dining_hall="Bolton",
            meal_period="Breakfast",
            date=str(date.today()),
            nutrition=NutritionProfile(calories=120, protein=4, carbs=22, fat=2, fiber=3, sodium=180),
            tags=["Vegetarian", "Vegan", "High Fiber"],
            allergens=["Wheat"]
        ),
        
        # Bolton - Lunch
        MenuItem(
            item_id="bolt-010",
            name="Grilled Chicken Breast",
            dining_hall="Bolton",
            meal_period="Lunch",
            date=str(date.today()),
            nutrition=NutritionProfile(calories=280, protein=45, carbs=0, fat=8, fiber=0, sodium=420),
            tags=["High Protein", "Low Carb", "Gluten-Free"],
            allergens=[]
        ),
        MenuItem(
            item_id="bolt-011",
            name="Turkey Wrap",
            dining_hall="Bolton",
            meal_period="Lunch",
            date=str(date.today()),
            nutrition=NutritionProfile(calories=380, protein=28, carbs=35, fat=14, fiber=3, sodium=680),
            tags=["High Protein"],
            allergens=["Wheat"]
        ),
        MenuItem(
            item_id="bolt-012",
            name="Caesar Salad",
            dining_hall="Bolton",
            meal_period="Lunch",
            date=str(date.today()),
            nutrition=NutritionProfile(calories=220, protein=8, carbs=12, fat=16, fiber=4, sodium=520),
            tags=["Vegetarian"],
            allergens=["Dairy", "Fish"]
        ),
        MenuItem(
            item_id="bolt-013",
            name="Black Bean Burger",
            dining_hall="Bolton",
            meal_period="Lunch",
            date=str(date.today()),
            nutrition=NutritionProfile(calories=350, protein=18, carbs=42, fat=12, fiber=8, sodium=580),
            tags=["Vegetarian", "Vegan", "High Fiber"],
            allergens=["Wheat"]
        ),
        
        # Bolton - Dinner
        MenuItem(
            item_id="bolt-020",
            name="Grilled Salmon",
            dining_hall="Bolton",
            meal_period="Dinner",
            date=str(date.today()),
            nutrition=NutritionProfile(calories=350, protein=40, carbs=2, fat=18, fiber=0, sodium=380),
            tags=["High Protein", "Gluten-Free"],
            allergens=["Fish"]
        ),
        MenuItem(
            item_id="bolt-021",
            name="Beef Stir Fry",
            dining_hall="Bolton",
            meal_period="Dinner",
            date=str(date.today()),
            nutrition=NutritionProfile(calories=420, protein=32, carbs=28, fat=22, fiber=3, sodium=720),
            tags=["High Protein"],
            allergens=["Soy", "Wheat"]
        ),
        MenuItem(
            item_id="bolt-022",
            name="Roasted Vegetables",
            dining_hall="Bolton",
            meal_period="Dinner",
            date=str(date.today()),
            nutrition=NutritionProfile(calories=120, protein=4, carbs=18, fat=5, fiber=6, sodium=180),
            tags=["Vegetarian", "Vegan", "Gluten-Free", "High Fiber"],
            allergens=[]
        ),
        MenuItem(
            item_id="bolt-023",
            name="Baked Sweet Potato",
            dining_hall="Bolton",
            meal_period="Dinner",
            date=str(date.today()),
            nutrition=NutritionProfile(calories=180, protein=4, carbs=42, fat=0, fiber=6, sodium=70),
            tags=["Vegetarian", "Vegan", "Gluten-Free", "High Fiber"],
            allergens=[]
        ),
        
        # Snelling - Breakfast
        MenuItem(
            item_id="snel-001",
            name="Oatmeal with Berries",
            dining_hall="Snelling",
            meal_period="Breakfast",
            date=str(date.today()),
            nutrition=NutritionProfile(calories=280, protein=8, carbs=52, fat=5, fiber=8, sodium=120),
            tags=["Vegetarian", "Vegan", "High Fiber"],
            allergens=[]
        ),
        MenuItem(
            item_id="snel-002",
            name="Veggie Omelet",
            dining_hall="Snelling",
            meal_period="Breakfast",
            date=str(date.today()),
            nutrition=NutritionProfile(calories=240, protein=16, carbs=8, fat=16, fiber=2, sodium=420),
            tags=["Vegetarian", "Gluten-Free", "High Protein"],
            allergens=["Eggs", "Dairy"]
        ),
        
        # Snelling - Lunch
        MenuItem(
            item_id="snel-010",
            name="Brown Rice Bowl",
            dining_hall="Snelling",
            meal_period="Lunch",
            date=str(date.today()),
            nutrition=NutritionProfile(calories=420, protein=12, carbs=68, fat=8, fiber=5, sodium=380),
            tags=["Vegetarian", "Vegan", "High Fiber"],
            allergens=[]
        ),
        MenuItem(
            item_id="snel-011",
            name="Grilled Tofu",
            dining_hall="Snelling",
            meal_period="Lunch",
            date=str(date.today()),
            nutrition=NutritionProfile(calories=180, protein=18, carbs=4, fat=10, fiber=2, sodium=280),
            tags=["Vegetarian", "Vegan", "Gluten-Free", "High Protein"],
            allergens=["Soy"]
        ),
        
        # Snelling - Dinner
        MenuItem(
            item_id="snel-020",
            name="Veggie Stir Fry",
            dining_hall="Snelling",
            meal_period="Dinner",
            date=str(date.today()),
            nutrition=NutritionProfile(calories=320, protein=15, carbs=42, fat=10, fiber=8, sodium=580),
            tags=["Vegetarian", "Vegan", "High Fiber"],
            allergens=["Soy"]
        ),
        
        # Village Summit - Lunch
        MenuItem(
            item_id="vs-010",
            name="Turkey Sandwich",
            dining_hall="Village Summit",
            meal_period="Lunch",
            date=str(date.today()),
            nutrition=NutritionProfile(calories=420, protein=32, carbs=38, fat=16, fiber=4, sodium=720),
            tags=["High Protein"],
            allergens=["Wheat"]
        ),
        MenuItem(
            item_id="vs-011",
            name="Chicken Tenders",
            dining_hall="Village Summit",
            meal_period="Lunch",
            date=str(date.today()),
            nutrition=NutritionProfile(calories=380, protein=28, carbs=24, fat=18, fiber=1, sodium=820),
            tags=["High Protein"],
            allergens=["Wheat"]
        ),
        
        # Niche - Dinner
        MenuItem(
            item_id="niche-020",
            name="Mediterranean Bowl",
            dining_hall="Niche",
            meal_period="Dinner",
            date=str(date.today()),
            nutrition=NutritionProfile(calories=480, protein=22, carbs=52, fat=20, fiber=8, sodium=680),
            tags=["Vegetarian", "High Fiber"],
            allergens=["Dairy"]
        ),
        MenuItem(
            item_id="niche-021",
            name="Falafel Plate",
            dining_hall="Niche",
            meal_period="Dinner",
            date=str(date.today()),
            nutrition=NutritionProfile(calories=520, protein=18, carbs=58, fat=24, fiber=10, sodium=720),
            tags=["Vegetarian", "Vegan", "High Fiber"],
            allergens=["Wheat"]
        ),
    ]
    
    return [item.to_dict() for item in menu_items]


def get_sample_faq_data() -> list[dict]:
    """Return sample FAQ/guidance data for RAG"""
    
    faqs = [
        {
            "question": "How much protein should I eat to build muscle?",
            "answer": "For muscle building, aim for 0.8-1.0 grams of protein per pound of body weight. For a 160 lb person, this is 128-160g of protein daily. Spread intake across 4-5 meals for optimal absorption.",
            "source": "UGA Nutrition Counseling Guidelines",
            "category": "Protein"
        },
        {
            "question": "What's a healthy rate of weight loss?",
            "answer": "A safe and sustainable rate of weight loss is 0.5-1 pound per week. This typically requires a caloric deficit of 250-500 calories per day. Extreme restriction can lead to muscle loss and nutrient deficiencies.",
            "source": "UGA Health Center",
            "category": "Weight Loss"
        },
        {
            "question": "How many calories should I eat?",
            "answer": "Daily calorie needs vary based on age, sex, weight, height, and activity level. Use the Mifflin-St Jeor equation as a starting point, then adjust based on your goals and progress.",
            "source": "UGA Nutrition Services",
            "category": "Calories"
        },
        {
            "question": "Is it okay to skip breakfast?",
            "answer": "Whether to eat breakfast depends on your preferences and schedule. Some people perform well with intermittent fasting, while others need morning fuel. Listen to your body and ensure you meet your daily nutrient needs.",
            "source": "UGA Nutrition Counseling",
            "category": "Meal Timing"
        },
        {
            "question": "What should I eat before a workout?",
            "answer": "Eat a meal with carbs and moderate protein 2-3 hours before exercise. If eating closer to your workout (30-60 min), choose easily digestible carbs like a banana or toast.",
            "source": "UGA Athletic Nutrition",
            "category": "Performance"
        },
        {
            "question": "How can I eat healthy at the dining hall?",
            "answer": "Focus on filling half your plate with vegetables, a quarter with lean protein, and a quarter with whole grains. Use the salad bar, choose grilled over fried options, and be mindful of portion sizes.",
            "source": "UGA Dining Services",
            "category": "Dining Hall Tips"
        },
        {
            "question": "What are good sources of fiber?",
            "answer": "Excellent fiber sources include whole grains (oatmeal, brown rice), legumes (black beans, lentils), vegetables (broccoli, Brussels sprouts), and fruits (berries, apples with skin). Aim for 25-30g daily.",
            "source": "UGA Nutrition Guidelines",
            "category": "Fiber"
        },
        {
            "question": "How much sodium is too much?",
            "answer": "The recommended limit is 2,300mg of sodium per day (about 1 teaspoon of salt). Dining hall foods can be high in sodium, so balance with fresh vegetables and fruits, and avoid adding extra salt.",
            "source": "UGA Health Center",
            "category": "Sodium"
        }
    ]
    
    return faqs


# Utility functions
def calculate_targets(profile: UserProfile, goal: str) -> dict:
    """Calculate daily nutrition targets based on profile and goal"""
    
    # Calculate BMR using Mifflin-St Jeor
    weight_kg = profile.get_weight_kg()
    height_cm = profile.get_height_cm()
    age = 20  # Assume average college age
    
    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5  # Male formula (simplified)
    
    # Activity multipliers
    activity_multipliers = {
        "Sedentary (little exercise)": 1.2,
        "Light (1-3 days/week)": 1.375,
        "Moderate (3-5 days/week)": 1.55,
        "Active (6-7 days/week)": 1.725,
        "Very Active (athlete/physical job)": 1.9
    }
    
    tdee = bmr * activity_multipliers.get(profile.activity_level, 1.55)
    
    # Goal adjustments
    goal_configs = {
        GoalType.BULK.value: {'cal_adjust': 300, 'protein_mult': 1.0},
        GoalType.CUT.value: {'cal_adjust': -500, 'protein_mult': 1.0},
        GoalType.MAINTAIN.value: {'cal_adjust': 0, 'protein_mult': 0.8},
        GoalType.ENERGY.value: {'cal_adjust': 0, 'protein_mult': 0.8},
        GoalType.HEALTH.value: {'cal_adjust': 0, 'protein_mult': 0.8},
        GoalType.PERFORMANCE.value: {'cal_adjust': 200, 'protein_mult': 1.0},
    }
    
    config = goal_configs.get(goal, {'cal_adjust': 0, 'protein_mult': 0.8})
    
    target_calories = int(tdee + config['cal_adjust'])
    target_protein = int(profile.weight * config['protein_mult'])
    target_carbs = int(target_calories * 0.45 / 4)  # 45% of calories
    target_fat = int(target_calories * 0.25 / 9)    # 25% of calories
    
    return {
        'calories': target_calories,
        'protein': target_protein,
        'carbs': target_carbs,
        'fat': target_fat,
        'fiber': 30,
        'sodium': 2300
    }


def search_menu_items(
    menu_data: list[dict],
    query: str = None,
    dining_hall: str = None,
    meal_period: str = None,
    tags: list[str] = None,
    max_calories: int = None,
    min_protein: int = None
) -> list[dict]:
    """Search and filter menu items"""
    
    results = menu_data.copy()
    
    if query:
        query_lower = query.lower()
        results = [item for item in results if query_lower in item['name'].lower()]
    
    if dining_hall and dining_hall != "All":
        results = [item for item in results if item['dining_hall'] == dining_hall]
    
    if meal_period and meal_period != "All":
        results = [item for item in results if item['meal_period'] == meal_period]
    
    if tags:
        results = [item for item in results if any(tag in item.get('tags', []) for tag in tags)]
    
    if max_calories:
        results = [item for item in results if item['nutrition']['calories'] <= max_calories]
    
    if min_protein:
        results = [item for item in results if item['nutrition']['protein'] >= min_protein]
    
    return results


# Export sample data to JSON for use in the app
if __name__ == "__main__":
    # Save sample menu data
    menu_data = get_sample_menu_data()
    with open('sample_menu_data.json', 'w') as f:
        json.dump(menu_data, f, indent=2)
    print(f"Saved {len(menu_data)} menu items to sample_menu_data.json")
    
    # Save FAQ data
    faq_data = get_sample_faq_data()
    with open('sample_faq_data.json', 'w') as f:
        json.dump(faq_data, f, indent=2)
    print(f"Saved {len(faq_data)} FAQs to sample_faq_data.json")
