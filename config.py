# config.py

# --- UI COLORS (For the "Elite" CTk Look) ---
COLOR_THEME = "dark-blue" 

# Color Theme Presets
COLOR_THEMES = {
    "Executive Dark": {
        "TEXT": "#EAEAEA",
        "HEADER_BG": "#212F3D",
        "ACCENT_DANGER": "#E74C3C",
        "SUCCESS_GREEN": "#2ECC71",
        "ACCENT_PRIMARY": "#3498DB",
        "ACCENT_NEUTRAL": "#5DADE2",
        "PANEL_BG": "#2C3E50",
        "MAIN_BG": "#34495E",
        "GOLD": "#F1C40F"
    },
    "Midnight Blue": {
        "TEXT": "#E8F4F8",
        "HEADER_BG": "#0A1929",
        "ACCENT_DANGER": "#FF5252",
        "SUCCESS_GREEN": "#69F0AE",
        "ACCENT_PRIMARY": "#2196F3",
        "ACCENT_NEUTRAL": "#64B5F6",
        "PANEL_BG": "#1E3A5F",
        "MAIN_BG": "#132F4C",
        "GOLD": "#FFD700"
    },
    "Forest Green": {
        "TEXT": "#F0F4F0",
        "HEADER_BG": "#1B5E20",
        "ACCENT_DANGER": "#FF6B6B",
        "SUCCESS_GREEN": "#4CAF50",
        "ACCENT_PRIMARY": "#66BB6A",
        "ACCENT_NEUTRAL": "#81C784",
        "PANEL_BG": "#2E7D32",
        "MAIN_BG": "#388E3C",
        "GOLD": "#FFC107"
    },
    "Corporate Purple": {
        "TEXT": "#F3E5F5",
        "HEADER_BG": "#4A148C",
        "ACCENT_DANGER": "#F44336",
        "SUCCESS_GREEN": "#00E676",
        "ACCENT_PRIMARY": "#9C27B0",
        "ACCENT_NEUTRAL": "#BA68C8",
        "PANEL_BG": "#6A1B9A",
        "MAIN_BG": "#7B1FA2",
        "GOLD": "#FFEB3B"
    },
    "Slate Gray": {
        "TEXT": "#ECEFF1",
        "HEADER_BG": "#263238",
        "ACCENT_DANGER": "#EF5350",
        "SUCCESS_GREEN": "#66BB6A",
        "ACCENT_PRIMARY": "#607D8B",
        "ACCENT_NEUTRAL": "#90A4AE",
        "PANEL_BG": "#37474F",
        "MAIN_BG": "#455A64",
        "GOLD": "#FFB300"
    }
}

# Active theme colors (default to Executive Dark)
COLOR_TEXT = COLOR_THEMES["Executive Dark"]["TEXT"]
COLOR_HEADER_BG = COLOR_THEMES["Executive Dark"]["HEADER_BG"]
COLOR_ACCENT_DANGER = COLOR_THEMES["Executive Dark"]["ACCENT_DANGER"]
COLOR_SUCCESS_GREEN = COLOR_THEMES["Executive Dark"]["SUCCESS_GREEN"]
COLOR_ACCENT_PRIMARY = COLOR_THEMES["Executive Dark"]["ACCENT_PRIMARY"]
COLOR_ACCENT_NEUTRAL = COLOR_THEMES["Executive Dark"]["ACCENT_NEUTRAL"]
COLOR_PANEL_BG = COLOR_THEMES["Executive Dark"]["PANEL_BG"]
COLOR_MAIN_BG = COLOR_THEMES["Executive Dark"]["MAIN_BG"]
COLOR_GOLD = COLOR_THEMES["Executive Dark"]["GOLD"]

# --- FONT STYLES ---
FONT_FAMILY = 'Arial' 
FONT_TITLE = (FONT_FAMILY, 22, 'bold')
FONT_HEADER = (FONT_FAMILY, 16, 'bold')
FONT_BODY = (FONT_FAMILY, 12)
FONT_STAT_VALUE = (FONT_FAMILY, 14, 'bold')
FONT_MONO = ('Courier New', 11)

# --- GAME CONFIGURATION ---
PROJECT_LIMIT = 3
DAILY_SALARY_PER_DEPT = 50000 
INITIAL_DEPT_BUDGET = 20000000

# EXECUTIVE OFFICERS (C-Suite)
EXECUTIVE_CANDIDATES = {
    "CFO": [
        {"name": "Sarah Chen", "personality": "Conservative", "cost": 25000000, "description": "Former Big 4 auditor. Focuses on cash preservation and risk management."},
        {"name": "Marcus Thompson", "personality": "Aggressive", "cost": 30000000, "description": "Wall Street veteran. Maximizes returns through bold financial moves."},
        {"name": "Elena Rodriguez", "personality": "Balanced", "cost": 22000000, "description": "Well-rounded finance leader with public company experience."}
    ],
    "CTO": [
        {"name": "Dr. Raj Patel", "personality": "Innovative", "cost": 28000000, "description": "PhD in Computer Science. Pioneering AI research background."},
        {"name": "Lisa Wu", "personality": "Balanced", "cost": 24000000, "description": "Ex-FAANG engineering director. Proven delivery track record."},
        {"name": "James Park", "personality": "Conservative", "cost": 26000000, "description": "Infrastructure expert. Focuses on stability and scalability."}
    ],
    "CMO": [
        {"name": "Amanda Foster", "personality": "Aggressive", "cost": 27000000, "description": "Viral marketing specialist. Takes big creative swings."},
        {"name": "David Kim", "personality": "Balanced", "cost": 23000000, "description": "Data-driven marketer with Fortune 500 experience."},
        {"name": "Sophia Martinez", "personality": "Innovative", "cost": 29000000, "description": "Brand storyteller. Builds emotional connections with customers."}
    ]
}

# R&D TRACKS
RND_TRACKS = {
    "AI Integration": {
        "max_points": 1000,
        "daily_cost_per_point": 100, 
        "effect_metric": "efficiency",
        "effect_dept": "R&D",
        "effect_amount": 5.0
    },
    "Supply Chain Automation": {
        "max_points": 800,
        "daily_cost_per_point": 80,
        "effect_metric": "efficiency",
        "effect_dept": "Operations",
        "effect_amount": 7.5
    },
    "Global PR Network": {
        "max_points": 500,
        "daily_cost_per_point": 50,
        "effect_metric": "base_tech", # Temporary use base_tech for a general boost
        "effect_dept": "Marketing", # Not used for base_tech
        "effect_amount": 5.0 
    }
}

# SCENARIOS
SCENARIOS = {
    "Stable Growth": {"desc": "The economy is steady and predictable.", "rev_mod": 1.0, "cost_mod": 1.0, "stock_mod": 1.0},
    "Tech Bubble": {"desc": "Tech stocks are overvalued. Revenue +10%, Stock Mod +20%.", "rev_mod": 1.1, "cost_mod": 1.0, "stock_mod": 1.2},
    "Global Recession": {"desc": "Consumer spending is down. Revenue -20%.", "rev_mod": 0.8, "cost_mod": 0.9, "stock_mod": 0.85},
    "Supply Chain Crisis": {"desc": "Operations are expensive. Costs +25%.", "rev_mod": 0.95, "cost_mod": 1.25, "stock_mod": 0.9},
    "Bull Market": {"desc": "Everything is going up! Stock prices inflated.", "rev_mod": 1.1, "cost_mod": 1.05, "stock_mod": 1.15},
}

# NEW: EARNINGS CALL CONFIGURATION
ANALYST_RATINGS = ["Strong Sell", "Sell", "Hold", "Buy", "Strong Buy"]

EARNINGS_QUESTIONS = [
    {
        "q": "Revenue growth has been volatile. How do you explain this quarter's performance?",
        "options": [
            ("Blame external market factors.", "safest"),
            ("Highlight our long-term R&D investment strategy.", "tech_focused"),
            ("Promise aggressive cost-cutting next quarter.", "profit_focused")
        ]
    },
    {
        # FIX: The string literal for "q" was not closed on the same line, causing a SyntaxError.
        "q": "Competitors are eating into our market share. What is your response?",
        "options": [
            ("We are ignoring them to focus on innovation.", "tech_focused"),
            ("We are launching a new marketing blitz.", "growth_focused"),
            ("Our product quality speaks for itself.", "safest")
        ]
    },
    {
        "q": "The board is concerned about our burn rate. Comments?",
        "options": [
            ("You have to spend money to make money.", "risky"),
            ("We are focused on efficiency and cost control.", "profit_focused"),
            ("Our investments will yield massive returns.", "growth_focused")
        ]
    },
    {
        "q": "What is the key to achieving a 'Strong Buy' rating in the next quarter?",
        "options": [
            ("Continued strong execution in our core business.", "safest"),
            ("A massive merger or acquisition event.", "risky"),
            ("A breakthrough in our key R&D track.", "tech_focused")
        ]
    }
]

# EMPLOYEE FACTORY
def EMPLOYEE_FACTORY(position, signing_bonus, daily_salary, skill):
    """Factory function to create Employee instances with random names."""
    from game_core import Employee
    return Employee(position, signing_bonus, daily_salary, skill)