# companies.py - Acquisition system for available companies

import random

class Company:
    """Represents an acquirable company that generates profit."""
    def __init__(self, name: str, industry: str, base_annual_profit: int, difficulty: str = "medium"):
        self.name = name
        self.industry = industry  # e.g., "SaaS", "Cloud", "Analytics", "AI", etc.
        self.base_annual_profit = base_annual_profit  # Annual profit in millions
        self.daily_profit = base_annual_profit / 365
        self.difficulty = difficulty  # "easy", "medium", "hard"
        self.acquired = False
        self.acquired_day = 0
        self.total_profit_earned = 0
    
    def generate_offers(self) -> list:
        """Generate 3 acquisition offers (cheap, medium, expensive) with acceptance probabilities."""
        cheap_price = self.base_annual_profit * 3  # 3x annual profit
        medium_price = self.base_annual_profit * 5  # 5x annual profit
        expensive_price = self.base_annual_profit * 8  # 8x annual profit
        
        return [
            {
                "label": "Aggressive Bid",
                "price": cheap_price,
                "acceptance_chance": 0.33,
                "risk": "High - Board may reject"
            },
            {
                "label": "Fair Market Price",
                "price": medium_price,
                "acceptance_chance": 0.66,
                "risk": "Medium - Standard offer"
            },
            {
                "label": "Premium Acquisition",
                "price": expensive_price,
                "acceptance_chance": 0.99,
                "risk": "Low - Almost certain"
            }
        ]
    
    def attempt_acquisition(self, offer_index: int) -> bool:
        """Try to acquire this company. Returns True if successful."""
        offers = self.generate_offers()
        offer = offers[offer_index]
        acceptance_chance = offer['acceptance_chance']
        
        # Add some randomness
        return random.random() < acceptance_chance
    
    def earn_daily_profit(self) -> float:
        """Calculate daily profit (2% of company's annual profit distributed daily to player)."""
        if not self.acquired:
            return 0
        # Add variance (±10%)
        variance = random.uniform(0.9, 1.1)
        return self.daily_profit * 0.02 * variance


# --- 10 ACQUIRABLE COMPANIES ---
ACQUIRABLE_COMPANIES = [
    Company("TechNova Solutions", "SaaS", 50, "hard"),
    Company("CloudPeak Analytics", "Cloud", 45, "hard"),
    Company("DataFlow Systems", "Big Data", 55, "hard"),
    Company("SecureNet Ltd", "Cybersecurity", 40, "hard"),
    Company("VentureLabs Inc", "AI/ML", 60, "hard"),
    Company("StreamHub Media", "Streaming", 35, "medium"),
    Company("AutoSync Logistics", "Automation", 42, "medium"),
    Company("NexGen Retail", "E-Commerce", 38, "medium"),
    Company("GreenPower Energy", "Renewable Energy", 48, "hard"),
    Company("DevTools Pro", "Developer Tools", 43, "medium"),
]

def get_company_by_name(name: str) -> Company:
    """Retrieve a company by name."""
    for company in ACQUIRABLE_COMPANIES:
        if company.name == name:
            return company
    return None
