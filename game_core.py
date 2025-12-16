# game_core.py
import random
from collections import deque
import pickle
import os
import config
from companies import ACQUIRABLE_COMPANIES 

# Helper for object.__setattr__
_set = object.__setattr__

# --- BOARD MEMBER CLASS ---
class BoardMember:
    """Represents a board member with unique personality and voting preferences."""
    def __init__(self, name: str, title: str, personality: str, background: str):
        self.name = name
        self.title = title
        self.personality = personality  # Conservative, Progressive, Investor-Focused, Employee-Advocate, Risk-Taker
        self.background = background
        self.trust = 50  # 0-100 scale
        self.satisfaction = 50  # 0-100 scale
        
        # Voting tendencies based on personality
        self.voting_preferences = self._set_voting_preferences()
    
    def _set_voting_preferences(self):
        """Define voting tendencies based on personality."""
        preferences = {
            "Conservative": {
                "acquisitions": -20,  # Less likely to approve
                "debt": -30,
                "layoffs": 10,
                "expansion": -10,
                "dividends": 20
            },
            "Progressive": {
                "acquisitions": 10,
                "debt": 5,
                "layoffs": -30,
                "expansion": 20,
                "dividends": -10
            },
            "Investor-Focused": {
                "acquisitions": 15,
                "debt": 10,
                "layoffs": 20,
                "expansion": 10,
                "dividends": 25
            },
            "Employee-Advocate": {
                "acquisitions": -5,
                "debt": -15,
                "layoffs": -40,
                "expansion": 15,
                "dividends": -20
            },
            "Risk-Taker": {
                "acquisitions": 30,
                "debt": 25,
                "layoffs": 0,
                "expansion": 35,
                "dividends": -15
            }
        }
        return preferences.get(self.personality, {})
    
    def vote(self, decision_type: str, company_performance: float = 0) -> bool:
        """
        Vote on a decision. Returns True for approval, False for rejection.
        decision_type: 'acquisitions', 'debt', 'layoffs', 'expansion', 'dividends'
        company_performance: -100 to 100 (affects voting based on trust/satisfaction)
        """
        base_chance = 50
        preference_modifier = self.voting_preferences.get(decision_type, 0)
        trust_modifier = (self.trust - 50) * 0.5  # Trust affects voting
        satisfaction_modifier = (self.satisfaction - 50) * 0.3
        performance_modifier = company_performance * 0.2
        
        total_chance = base_chance + preference_modifier + trust_modifier + satisfaction_modifier + performance_modifier
        total_chance = max(0, min(100, total_chance))  # Clamp to 0-100
        
        return random.random() * 100 < total_chance
    
    def update_satisfaction(self, delta: int):
        """Update satisfaction level (clamped 0-100)."""
        self.satisfaction = max(0, min(100, self.satisfaction + delta))
    
    def update_trust(self, delta: int):
        """Update trust level (clamped 0-100)."""
        self.trust = max(0, min(100, self.trust + delta))

# --- EXECUTIVE CLASS (C-Suite Officers) ---
class Executive:
    """Represents a C-suite executive (CFO, CTO, CMO) with strategic bonuses."""
    def __init__(self, name: str, role: str, cost: int, personality: str = "Balanced"):
        self.name = name
        self.role = role  # "CFO", "CTO", "CMO"
        self.cost = cost  # One-time hiring cost
        self.personality = personality  # "Aggressive", "Conservative", "Balanced", "Innovative"
        self.hired_day = 0
        self.satisfaction = 80  # 0-100, affects retention
        
        # Define passive bonuses each executive provides
        self.bonuses = {
            "CFO": {"cash_flow_bonus": 0.05, "debt_cost_reduction": 0.10, "budget_efficiency": 5},
            "CTO": {"tech_boost": 0.10, "rnd_efficiency": 10, "project_risk_reduction": 0.15},
            "CMO": {"customer_growth": 0.08, "marketing_efficiency": 10, "reputation_boost": 5}
        }.get(role, {})
    
    def get_advice(self, situation: str) -> str:
        """Return personality-based advice for key decisions."""
        advice_map = {
            "Aggressive": "Push hard. Take risks for maximum returns.",
            "Conservative": "Play it safe. Preserve cash and minimize exposure.",
            "Balanced": "Weigh the options carefully before committing.",
            "Innovative": "This is a chance to disrupt. Think outside the box."
        }
        return advice_map.get(self.personality, "No strong opinion.")
    
    def apply_passive_bonuses(self, corp):
        """Apply ongoing bonuses to corporation metrics."""
        if self.role == "CFO":
            # CFO reduces debt interest and boosts budget efficiency
            return
        elif self.role == "CTO":
            # CTO handled in R&D efficiency calculations
            return
        elif self.role == "CMO":
            # CMO handled in marketing efficiency and customer growth
            return

# --- EMPLOYEE CLASS ---
class Employee:
    """Represents a hired employee who performs daily automated work."""
    
    # First and last name pools for random generation
    FIRST_NAMES = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Avery", "Quinn", 
                   "Parker", "Blake", "Hayden", "Cameron", "Skylar", "Drew", "Reese",
                   "Dakota", "Sage", "River", "Phoenix", "Rowan"]
    
    LAST_NAMES = ["Chen", "Rodriguez", "Smith", "Johnson", "Williams", "Brown", "Davis",
                  "Martinez", "Garcia", "Miller", "Wilson", "Moore", "Taylor", "Anderson",
                  "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson"]
    
    def __init__(self, position: str, signing_bonus: int, daily_salary: int, skill_level: float = 1.0):
        # Generate random name
        self.name = f"{random.choice(self.FIRST_NAMES)} {random.choice(self.LAST_NAMES)}"
        self.position = position  # "Marketing Analyst", "Finance Manager", etc.
        self.employee_type = position  # Keep for backwards compatibility
        self.signing_bonus = signing_bonus
        self.daily_salary = daily_salary
        self.skill_level = skill_level
        self.hired_day = 0
        self.tasks_completed = 0
        self.assigned_action = None
        
        # Define work tasks by position
        self.auto_actions = {
            "Marketing Analyst": ["marketing", "customer_outreach"],
            "Finance Manager": ["budget", "cash_management"],
            "R&D Specialist": ["rnd", "innovation"],
            "Operations Manager": ["efficiency", "cost_reduction"],
            "HR Coordinator": ["morale", "hiring_support", "wellness"],
            "Project Manager": ["launch_project"],
            "Executive Assistant": ["email", "marketing", "rnd", "budget", "wellness"]
        }.get(position, [])
    
    def can_perform_action(self, action_name: str) -> bool:
        return action_name in self.auto_actions

    def set_assignment(self, action_name: str | None):
        if action_name is not None and action_name not in self.auto_actions:
            raise ValueError("Action not available for this employee.")
        self.assigned_action = action_name


# --- UNIFIED PROJECT CLASS ---
class Product:
    """Unified project system: Development phase → Market lifecycle (Launch/Growth/Maturity/Decline)"""
    
    LIFECYCLE_STAGES = {
        "Development": {"duration": None, "revenue_mult": 0, "growth_rate": 1.0},  # Custom duration
        "Launch": {"duration": 30, "revenue_mult": 0.5, "growth_rate": 1.05},
        "Growth": {"duration": 90, "revenue_mult": 1.2, "growth_rate": 1.03},
        "Maturity": {"duration": 180, "revenue_mult": 1.5, "growth_rate": 1.0},
        "Decline": {"duration": 90, "revenue_mult": 0.8, "growth_rate": 0.97}
    }
    
    def __init__(self, name, investment, base_price, development_days, project_type, risk):
        self.name = name
        self.initial_investment = investment
        self.base_price = base_price
        self.development_days = development_days
        self.type = project_type  # 1=R&D, 2=Marketing, 3=Operations
        self.risk = risk
        
        # Development phase tracking
        self.lifecycle_stage = "Development"
        self.days_in_stage = 0
        self.total_days_live = 0
        self.is_retired = False
        
        # Financial tracking
        self.daily_cost = investment / development_days  # Costs during development
        self.daily_revenue = 0  # Revenue after launch
        self.total_revenue = 0
        self.total_costs_paid = 0
        
        # Market performance (set after development)
        self.quality_score = 0
        self.market_share = 0
        self.customer_satisfaction = 50
        self.units_sold = 0
        
        # Completion bonus potential
        self.completion_bonus_paid = False
    
    def launch(self, corp_tech_level):
        """Called when project completes development - transitions to Launch phase."""
        # Quality based on tech level + project type bonus
        type_bonus = {1: 10, 2: 5, 3: 3}.get(self.type, 0)  # R&D projects get better quality
        self.quality_score = min(100, corp_tech_level + type_bonus + random.uniform(-5, 15))
        self.market_share = random.uniform(0.5, 2.0)  # Start with small market share
        self.customer_satisfaction = min(100, 40 + self.quality_score * 0.5)
        self.lifecycle_stage = "Launch"
        self.days_in_stage = 0
    
    def update_day(self, customer_base, competitors_count, corp_efficiency):
        """Update project each day - development costs OR market revenue."""
        if self.is_retired:
            return 0, 0
        
        self.total_days_live += 1
        self.days_in_stage += 1
        
        # DEVELOPMENT PHASE: Costs money, no revenue
        if self.lifecycle_stage == "Development":
            cost = self.daily_cost
            self.total_costs_paid += cost
            
            # Check if development complete
            if self.days_in_stage >= self.development_days:
                # Development complete! Will transition to Launch in Corporation.complete_project()
                pass
            
            return cost, 0  # cost, revenue
        
        # MARKET PHASES: Generate revenue
        self._update_lifecycle_stage()
        
        stage_data = self.LIFECYCLE_STAGES[self.lifecycle_stage]
        base_revenue = self.base_price * self.market_share * (customer_base / 100)
        
        # Quality and efficiency bonuses
        quality_bonus = 1 + (self.quality_score - 50) / 100
        efficiency_bonus = 1 + (corp_efficiency - 50) / 200  # Small boost from efficiency
        lifecycle_mult = stage_data["revenue_mult"]
        
        # Competition pressure
        competition_factor = 1 / (1 + competitors_count * 0.1)
        
        self.daily_revenue = base_revenue * quality_bonus * efficiency_bonus * lifecycle_mult * competition_factor
        self.total_revenue += self.daily_revenue
        
        # Market share growth/decline
        growth = stage_data["growth_rate"]
        self.market_share *= growth
        self.market_share = min(30, self.market_share)  # Cap at 30%
        
        # Units sold
        self.units_sold += int(self.daily_revenue / self.base_price) if self.base_price > 0 else 0
        
        return 0, self.daily_revenue  # cost, revenue
    
    def _update_lifecycle_stage(self):
        """Progress through market lifecycle stages."""
        if self.lifecycle_stage == "Development":
            return  # Handled separately
        elif self.lifecycle_stage == "Launch" and self.days_in_stage >= 30:
            self.lifecycle_stage = "Growth"
            self.days_in_stage = 0
        elif self.lifecycle_stage == "Growth" and self.days_in_stage >= 90:
            self.lifecycle_stage = "Maturity"
            self.days_in_stage = 0
        elif self.lifecycle_stage == "Maturity" and self.days_in_stage >= 180:
            self.lifecycle_stage = "Decline"
            self.days_in_stage = 0
    
    def retire(self):
        """Retire this project from the market."""
        self.is_retired = True


# --- COMPETITOR CLASS ---
class Competitor:
    """Represents a competing company in the market"""
    def __init__(self, name, initial_stock_price, strategy):
        self.name = name
        self.stock_price = initial_stock_price
        self.strategy = strategy  # "aggressive", "balanced", "conservative"
        self.market_share = random.uniform(15, 25)
        self.stock_history = [initial_stock_price]
        
    def update_stock_price(self, player_actions):
        """Update competitor stock based on their strategy and player pressure"""
        base_change = 0
        
        # Strategy-based movement
        if self.strategy == "aggressive":
            base_change = random.uniform(-1.5, 2.5)  # Volatile
        elif self.strategy == "balanced":
            base_change = random.uniform(-0.5, 1.0)  # Steady growth
        else:  # conservative
            base_change = random.uniform(-0.3, 0.8)  # Slow and stable
        
        # React to player marketing pressure
        if player_actions.get('marketing_pressure', 0) > 0:
            base_change -= random.uniform(0.2, 0.8)
        
        self.stock_price = max(10.0, self.stock_price + base_change)
        self.stock_history.append(self.stock_price)
        if len(self.stock_history) > 90:
            self.stock_history.pop(0)

# --- CORPORATION CLASS ---
class Corporation:
    def __init__(self, difficulty="Easy"):
        self.day = 1
        self.quarter = 1
        self.year = 1
        self.corp_name = ""
        self.ceo_name = ""
        self.email_system = None
        self.log = deque(maxlen=200)
        self.recent_changes = deque(maxlen=5)  # Track last 5 impactful changes
        self.difficulty = difficulty  # Easy only (simplified)

        # Apply difficulty modifiers to starting values
        diff_mods = self._get_difficulty_modifiers()

        # Metrics
        self.cash = int(35000000 * diff_mods['cash'])
        self.debt = 0
        self.max_debt_limit = int(50000000 * diff_mods['debt_limit'])
        self.stock_price = 10.0
        self.shares_outstanding = 5000000
        self.market_cap = self.stock_price * self.shares_outstanding

        self.reputation = int(35 * diff_mods['starting_stats'])
        self.employee_morale = int(38 * diff_mods['starting_stats'])
        self.ceo_health = int(50 * diff_mods['starting_stats'])
        self.board_confidence = int(40 * diff_mods['starting_stats'])
        self.customer_base = 25
        self.technology_level = 25
        self.market_mood = "Neutral"
        
        # Initialize Board of Directors (5 members with diverse personalities)
        self.board_members = [
            BoardMember("Margaret Chen", "Chairwoman", "Conservative", 
                       "Former Goldman Sachs partner with 30 years in finance. Prioritizes fiscal responsibility."),
            BoardMember("David Rodriguez", "Vice Chair", "Progressive", 
                       "Tech entrepreneur and sustainability advocate. Champions innovation and employee welfare."),
            BoardMember("Sarah Blackwood", "Board Member", "Investor-Focused", 
                       "Hedge fund manager representing major shareholders. Demands strong returns."),
            BoardMember("James Mitchell", "Board Member", "Employee-Advocate", 
                       "Former union leader and labor attorney. Fights for worker protections."),
            BoardMember("Dr. Raj Patel", "Board Member", "Risk-Taker", 
                       "Serial entrepreneur with multiple IPO exits. Embraces bold strategies.")
        ]
        
        # Initialize competitors (12 rival companies - Wall Street Leaderboard)
        # Player starts FAR behind at ~$10 stock price
        self.competitors = [
            Competitor("Goldman Technologies", 485.0, "conservative"),
            Competitor("Morgan Digital", 441.0, "balanced"),
            Competitor("BlackRock Industries", 398.0, "conservative"),
            Competitor("Vanguard Systems", 362.0, "balanced"),
            Competitor("JP Morgan Tech", 329.0, "balanced"),
            Competitor("Berkshire Innovations", 294.0, "conservative"),
            Competitor("Fidelity Dynamics", 261.0, "balanced"),
            Competitor("NovaTech Systems", 228.0, "aggressive"),
            Competitor("Apex Digital Corp", 195.0, "balanced"),
            Competitor("Titan Industries", 162.0, "conservative"),
            Competitor("Quantum Dynamics", 129.0, "aggressive"),
            Competitor("Horizon Solutions", 96.0, "balanced")
        ]
        self.stock_history = [25.0]  # Track player stock price history
        self.has_won_game = False  # Track if player reached #1 on leaderboard 
        
        # NEW: Global Scenario System
        self.current_scenario = "Stable Growth"
        self.scenario_duration = 0
        
        # NEW: Wall Street Metrics
        self.analyst_rating = "Hold"
        self.credit_rating = "B"  # AAA, AA, A, BBB, BB, B, CCC (investment grade to junk)
        self.quarterly_revenue = 0
        self.quarterly_costs = 0
        self.previous_quarter_revenue = 45000000  # Scaled 50%
        
        self.corp_card_limit = 5000000  # Scaled 50% 
        self.corp_card_used = 0
        # Multiplier for long-duration projects/actions (1.0 = normal). Can be tuned via settings.
        self.long_timer_multiplier = 1.0

        # NEW: Annual Department Budgets (track spending per year)
        budget_multiplier = diff_mods['budget']
        self.annual_budget = {
            "R&D": int(50000000 * budget_multiplier),
            "Marketing": int(50000000 * budget_multiplier),
            "Operations": int(50000000 * budget_multiplier),
            "HR": int(50000000 * budget_multiplier),
        }
        self.budget_spent = {
            "R&D": 0,
            "Marketing": 0,
            "Operations": 0,
            "HR": 0,
        }
        
        # Reduce department base costs significantly
        self.departments = {
            "R&D": int((config.INITIAL_DEPT_BUDGET // 4) * budget_multiplier),  # Reduced from //2 to //4
            "Marketing": int((config.INITIAL_DEPT_BUDGET // 4) * budget_multiplier),
            "Operations": int((config.INITIAL_DEPT_BUDGET // 4) * budget_multiplier),
            "HR": int((config.INITIAL_DEPT_BUDGET // 4) * budget_multiplier),
        }
        self.dept_efficiency = {
            "R&D": 35, "Marketing": 35, "Operations": 35, "HR": 35  # Scaled 50%
        }
        self.permanent_efficiency_boosts = {
            "R&D": 0, "Marketing": 0, "Operations": 0, "HR": 0
        }
        
        self.market_segments = {"B2B": 25, "Consumer": 25}  # Scaled 50%
        self.daily_rnd_investment = {}
        self.daily_rnd_cost = 0
        self.rnd_points = {}  # Track actual progress points for each R&D track
        
        # Competitor pressure tracking
        self.days_without_marketing = 0  # Track days since last marketing investment

        # NEW: ACTION POINTS SYSTEM (3 per day, 4 on Easy)
        diff_mods = self._get_difficulty_modifiers()
        self.action_points = diff_mods['action_points']
        self.max_action_points = diff_mods['action_points']
        
        # NEW: EMPLOYEE AUTOMATION SYSTEM
        self.employees = []  # List of hired Employee objects
        self.automation_log = deque(maxlen=50)  # Track employee auto-actions
        
        # NEW: PRODUCT PORTFOLIO
        self.products = []  # List of launched Product objects
        self.total_product_revenue = 0  # Daily revenue from all products
        
        # NEW: EXECUTIVE TEAM (C-Suite)
        self.executives = []  # List of hired Executive objects
        self.cfo = None
        self.cto = None
        self.cmo = None
        
        # NEW: UNION SYSTEM
        self.union_status = None  # None, "Forming", "Active"
        self.union_strength = 0  # 0-100, increases with low morale
        self.union_demands = []  # List of current demands
        self.strike_countdown = 0  # Days until strike if demands unmet
        self.last_union_check_day = 0

        # NEW: ACQUISITION SYSTEM
        self.acquired_companies = []  # List of acquired companies
        # Create fresh instances to avoid shared state
        from companies import Company
        self.available_companies = [
            Company(c.name, c.industry, c.base_annual_profit, c.difficulty) 
            for c in ACQUIRABLE_COMPANIES
        ]
        self.total_acquisition_profit = 0  # Track cumulative profit from acquisitions

        # NEW: EXECUTIVE POINTS & UPGRADE SYSTEM
        self.executive_points = 0  # Currency for permanent upgrades
        self.purchased_upgrades = []  # List of upgrade IDs already purchased
        self.upgrade_bonuses = {  # Active permanent bonuses from upgrades
            'revenue_boost': 0,
            'cost_reduction': 0,
            'stock_boost': 0,
            'project_success': 0,
            'debt_limit_mult': 0,
            'interest_reduction': 0,
            'customer_growth': 0,
            'tech_speed': 0,
            'action_points_bonus': 0,
            'health_regen': 0,
        }

        # Game State
        self.projects = []
        
        # R&D Tracks Status
        self.technology_tracks = {
            track: {"progress": 0, "completed": False} 
            for track in config.RND_TRACKS
        }
        
        # --- FIX: POPULATED POPUP_EVENTS DICTIONARY ---
        self.POPUP_EVENTS = {
            # Critical low-confidence event
            "Critical_Decision_1": {
                "title": "CRITICAL EXECUTIVE DECISION!",
                "body": "Your low Board Confidence score is causing market instability. You must act to stabilize it.",
                "color": "red",
                "options": [
                    {"text": "Launch a massive PR campaign ($5M)", "action": lambda c: (c.use_corp_card('PR_Campaign'), c._set(c, 'board_confidence', min(100, c.board_confidence + 10)))},
                    {"text": "Execute a small share repurchase ($10M)", "action": lambda c: c.manage_debt_equity(10000000, 'Repurchase_Shares')},
                    {"text": "Do nothing (Risk is High)", "action": lambda c: c.log.append("Decision: Ignored Board Confidence Warning.")}
                ],
                'type': 'BAD'
            }
        }
    
    def _get_difficulty_modifiers(self):
        """Return difficulty multipliers for game parameters.
        Difficulty simplified to Easy-only and made more forgiving.
        """
        # Easy-only mode (boosted)
        return {
            'cash': 3.0,              # Start with 3x cash ($105M)
            'debt_limit': 2.0,        # 2x higher debt limit
            'starting_stats': 1.5,    # 50% better starting stats
            'action_points': 3,       # 3 action points per day
            'interest_rate': 0.5,     # 50% lower interest rates
            'revenue': 1.5,           # 50% more revenue
            'costs': 0.7,             # 30% lower costs
            'risk_reduction': 0.5,    # 50% lower project risks
            'budget': 2.0,            # 2x larger budgets
            'market_volatility': 0.6, # Less volatile markets
        }

    def get_budget_remaining(self, dept: str) -> float:
        """Return remaining annual budget for a department."""
        return self.annual_budget.get(dept, 0) - self.budget_spent.get(dept, 0)
    
    def can_afford_action(self, dept: str, cost: float) -> bool:
        """Check if a department can afford an action from its annual budget."""
        # Require both budget headroom and actual cash on hand
        return self.get_budget_remaining(dept) >= cost and self.cash >= cost
    
    def spend_from_budget(self, dept: str, cost: float) -> bool:
        """Deduct cost from department's annual budget. Return True if successful."""
        if not self.can_afford_action(dept, cost):
            return False
        self.budget_spent[dept] += cost
        return True
    
    def adjust_budget(self, new_budgets: dict) -> None:
        """Adjust annual department budgets. Call when user reallocates budgets."""
        current_total = sum(self.annual_budget.values())
        new_total = sum(new_budgets.values())
        delta = new_total - current_total
        if delta > 0 and self.cash < delta:
            raise ValueError("Insufficient cash to increase budgets")
        # Apply cash movement
        self.cash -= delta
        for dept, new_amount in new_budgets.items():
            if dept in self.annual_budget:
                self.annual_budget[dept] = new_amount

    def check_unionization_threat(self) -> bool:
        """Check if employees are forming a union based on morale and working conditions."""
        # Only check every 30 days
        if self.day - self.last_union_check_day < 30:
            return False
        
        self.last_union_check_day = self.day
        
        # Union forms if: low morale + many employees + poor working conditions
        if len(self.employees) >= 5 and self.employee_morale < 40:
            if self.union_status is None:
                self.union_status = "Forming"
                self.union_strength = 20
                self.log.append("⚠️ ALERT: Employees are discussing unionization due to low morale!")
                return True
            elif self.union_status == "Forming":
                self.union_strength += 10
                if self.union_strength >= 50:
                    self.union_status = "Active"
                    self._generate_union_demands()
                    self.log.append("🪧 UNION FORMED! Employees have organized and are presenting demands.")
                    return True
        elif self.employee_morale > 65 and self.union_status == "Forming":
            # Morale improved, union threat dissipates
            self.union_status = None
            self.union_strength = 0
            self.log.append("✅ Union organizing efforts have dissolved due to improved morale.")
        
        return False
    
    def _generate_union_demands(self):
        """Generate union demands based on current conditions."""
        demands = []
        if self.employee_morale < 40:
            demands.append({"type": "morale_boost", "description": "10% salary increase", "cost": 10000000, "morale_gain": 15})
        if self.ceo_health < 50:
            demands.append({"type": "work_life_balance", "description": "Reduced overtime (lose 1 action point/day)", "cost": 0, "action_point_penalty": 1})
        if any(self.dept_efficiency[d] < 40 for d in self.dept_efficiency):
            demands.append({"type": "better_tools", "description": "Upgrade equipment ($15M)", "cost": 15000000, "efficiency_boost": 10})
        
        self.union_demands = demands[:2]  # Max 2 demands
        self.strike_countdown = 14  # 14 days to respond
    
    def resolve_union_demand(self, demand_index: int, action: str):
        """Resolve a union demand with Accept, Counter, or Ignore."""
        if demand_index >= len(self.union_demands):
            return "Invalid demand index."
        
        demand = self.union_demands[demand_index]
        
        if action == "Accept":
            cost = demand.get('cost', 0)
            if self.cash < cost:
                return "Insufficient cash to meet demand."
            
            self.cash -= cost
            self.employee_morale = min(100, self.employee_morale + demand.get('morale_gain', 10))
            
            if 'action_point_penalty' in demand:
                self.max_action_points = max(1, self.max_action_points - demand['action_point_penalty'])
            
            if 'efficiency_boost' in demand:
                for dept in self.dept_efficiency:
                    self.permanent_efficiency_boosts[dept] += demand['efficiency_boost']
            
            self.log.append(f"✅ Accepted union demand: {demand['description']}")
            self.union_demands.pop(demand_index)
            
            if len(self.union_demands) == 0:
                self.union_status = None
                self.strike_countdown = 0
                self.log.append("🤝 Union negotiations concluded successfully.")
            
            return "Demand accepted. Union satisfied."
        
        elif action == "Counter":
            # 50% chance union accepts counter-offer (reduced cost, reduced benefit)
            if random.random() < 0.5:
                cost = demand.get('cost', 0) * 0.6
                self.cash -= cost
                self.employee_morale = min(100, self.employee_morale + demand.get('morale_gain', 5))
                self.log.append(f"🤝 Counter-offer accepted: {demand['description']} at reduced terms.")
                self.union_demands.pop(demand_index)
                return "Counter-offer accepted."
            else:
                self.employee_morale -= 5
                self.strike_countdown -= 3
                self.log.append("❌ Union rejected counter-offer. Tensions rising.")
                return "Counter-offer rejected. Strike risk increased."
        
        elif action == "Ignore":
            self.employee_morale -= 10
            self.reputation -= 5
            self.strike_countdown -= 5
            
            if self.strike_countdown <= 0:
                return self._trigger_strike()
            
            self.log.append(f"⚠️ Ignored union demand. Strike in {self.strike_countdown} days if unresolved.")
            return f"Demand ignored. Strike countdown: {self.strike_countdown} days."
        
        return "Invalid action."
    
    def _trigger_strike(self) -> str:
        """Trigger a strike event with severe consequences."""
        self.union_status = "Strike"
        strike_duration = random.randint(7, 21)
        
        # Massive productivity loss
        for dept in self.dept_efficiency:
            self.dept_efficiency[dept] = max(10, self.dept_efficiency[dept] - 40)
        
        # Revenue loss
        revenue_loss = self.quarterly_revenue * 0.3
        self.cash -= revenue_loss
        self.quarterly_costs += revenue_loss
        
        # Reputation damage
        self.reputation = max(10, self.reputation - 20)
        self.board_confidence = max(10, self.board_confidence - 15)
        
        self.log.append(f"🪧 STRIKE! Employees have walked out for {strike_duration} days. Massive productivity loss and reputation damage.")
        return f"STRIKE INITIATED! Duration: {strike_duration} days. Severe operational impact."

    def set_identity(self, corp_name, ceo_name, email_system, difficulty=None):
        _set(self, 'corp_name', corp_name)  # ✅ FIXED
        _set(self, 'ceo_name', ceo_name)
        _set(self, 'email_system', email_system)
        if difficulty:
            _set(self, 'difficulty', difficulty)
            # Re-apply difficulty modifiers if changed after init
            diff_mods = self._get_difficulty_modifiers()
            _set(self, 'cash', int(35000000 * diff_mods['cash']))
            _set(self, 'max_debt_limit', int(50000000 * diff_mods['debt_limit']))
            _set(self, 'reputation', int(35 * diff_mods['starting_stats']))
            _set(self, 'employee_morale', int(38 * diff_mods['starting_stats']))
            _set(self, 'ceo_health', int(50 * diff_mods['starting_stats']))
            _set(self, 'board_confidence', int(40 * diff_mods['starting_stats']))
            _set(self, 'action_points', diff_mods['action_points'])
            _set(self, 'max_action_points', diff_mods['action_points'])
        self.log.append(f"Game started as **{corp_name}** under CEO **{ceo_name}**.\")")

    def calculate_daily_rnd_cost(self):
        cost = 0
        for track, amount in self.daily_rnd_investment.items():
            if not self.technology_tracks[track]['completed']:
                cost += amount
        _set(self, 'daily_rnd_cost', cost)
        return cost

    def process_daily_rnd(self):
        cost = self.calculate_daily_rnd_cost()
        if self.cash < cost:
            self.log.append(f"WARNING: R&D Cost of ${cost:,.0f} skipped due to insufficient cash.")
            return

        _set(self, 'cash', self.cash - cost)
        _set(self, 'quarterly_costs', self.quarterly_costs + cost)
        
        for track, amount in self.daily_rnd_investment.items():
            if amount > 0 and not self.technology_tracks[track]['completed']:
                data = config.RND_TRACKS[track]
                # Calculate points gained: investment / cost_per_point
                points_gained = amount / data['daily_cost_per_point']
                
                # Apply R&D Efficiency bonus
                efficiency_mod = self.dept_efficiency['R&D'] / 100
                points_gained *= efficiency_mod

                self.technology_tracks[track]['progress'] += points_gained

                # Check for completion
                if self.technology_tracks[track]['progress'] >= data['max_points']:
                    self.technology_tracks[track]['completed'] = True
                    self.technology_tracks[track]['progress'] = data['max_points'] # Cap it
                    
                    # Apply permanent effect
                    if data['effect_metric'] == 'efficiency':
                        self.permanent_efficiency_boosts[data['effect_dept']] += data['effect_amount']
                        self.log.append(f"**TECH COMPLETE:** {track} unlocked! Permanent +{data['effect_amount']:.0f}% {data['effect_dept']} Efficiency.")
                    elif data['effect_metric'] == 'base_tech':
                        _set(self, 'technology_level', min(100, self.technology_level + data['effect_amount']))
                        self.log.append(f"**TECH COMPLETE:** {track} unlocked! Technology Level permanently increased by +{data['effect_amount']:.1f}.")

                    # Stop investment in completed track
                    self.daily_rnd_investment[track] = 0

    def calculate_efficiency(self):
        for dept in self.dept_efficiency.keys():
            # Base efficiency + Permanent Boosts (from projects/R&D)
            base_eff = 70 + self.permanent_efficiency_boosts[dept]
            # Employees contribute targeted bonuses by department
            base_eff += self._employee_dept_bonus(dept)
            # Market Mood modifier (R&D/Tech benefits from bullish mood)
            if dept == 'R&D' and self.market_mood == 'Bullish':
                base_eff += 5
            
            # Health/Morale modifiers
            if self.ceo_health < 50: base_eff -= 5 
            if self.employee_morale < 50: base_eff -= 5
            
            # Clamp the value between 1 and 100
            self.dept_efficiency[dept] = max(1, min(100, base_eff))

    def _process_projects(self):
        """Process all active projects - both development and market phases."""
        total_costs = 0
        total_revenue = 0
        completed_dev_projects = []

        for i, proj in enumerate(self.projects):
            # Determine efficiency for this project type
            if proj.type == 1:
                eff = self.dept_efficiency['R&D']
            elif proj.type == 2:
                eff = self.dept_efficiency['Marketing']
            elif proj.type == 3:
                eff = self.dept_efficiency['Operations']
            else:
                eff = 70
            
            # Update project (development or market phase)
            cost, revenue = proj.update_day(self.customer_base, len(self.competitors), eff)
            total_costs += cost
            total_revenue += revenue
            
            # Check if development completed (transition to Launch)
            if proj.lifecycle_stage == "Development" and proj.days_in_stage >= proj.development_days:
                proj.launch(self.technology_level)
                
                # Risk check - did development succeed?
                adjusted_risk = proj.risk * (1 - self.technology_level / 200)
                if random.random() < adjusted_risk:
                    # Development failed!
                    failure_cost = proj.initial_investment * random.uniform(0.2, 0.5)
                    _set(self, 'cash', self.cash - failure_cost)
                    _set(self, 'quarterly_costs', self.quarterly_costs + failure_cost)
                    self.log.append(f"⚠️ Project **{proj.name}** development FAILED. Lost ${failure_cost:,.0f}")
                    completed_dev_projects.append(i)
                else:
                    # Success! Now in market
                    tech_boost = proj.initial_investment / 10000000 * random.uniform(2, 5)
                    _set(self, 'technology_level', min(100, self.technology_level + tech_boost))
                    
                    # Efficiency boost for R&D projects
                    if proj.type == 1:
                        self.permanent_efficiency_boosts['R&D'] += 1
                        self.log.append(f"Project '{proj.name}' boosted R&D Efficiency by +1%")
                    
                    self.log.append(f"✅ Project **{proj.name}** launched! Quality: {proj.quality_score:.0f}/100, Tech +{tech_boost:.1f}")
        
        # Remove failed projects
        for i in reversed(completed_dev_projects):
            self.projects.pop(i)
        
        # Apply net financial impact
        net = total_revenue - total_costs
        _set(self, 'cash', self.cash + net)
        _set(self, 'quarterly_revenue', self.quarterly_revenue + total_revenue)
        _set(self, 'quarterly_costs', self.quarterly_costs + total_costs)
        
        if total_revenue > 0 or total_costs > 0:
            self.log.append(f"Projects: Rev ${total_revenue:,.0f}, Cost ${total_costs:,.0f}, Net ${net:+,.0f}")

    def _generate_costs(self):
        # Daily salary costs per department (deduct from annual budgets)
        daily_salary = sum(self.departments.values()) / 365  # Changed from /30 to /365 - YEARLY not monthly!
        
        # Deduct salary cost from each department proportionally
        for dept in self.departments.keys():
            dept_daily_salary = self.departments[dept] / 365  # Changed from /30 to /365
            self.budget_spent[dept] += dept_daily_salary
        
        # Employee daily salaries (deduct from HR budget)
        employee_daily_cost = sum(emp.daily_salary for emp in self.employees)
        if employee_daily_cost > 0:
            self.budget_spent['HR'] += employee_daily_cost
            daily_salary += employee_daily_cost
        
        # Debt interest (variable rate based on credit rating)
        interest_rate = self._get_interest_rate()
        debt_interest = self.debt * (interest_rate / 365)
        
        # Minimum debt payment (0.1% daily = ~36.5% per year)
        min_debt_payment = self.debt * 0.001  # Reduced from 0.01 to 0.001
        
        total_costs = daily_salary + debt_interest + min_debt_payment
        
        # Apply scenario modifier
        scenario = config.SCENARIOS.get(self.current_scenario)
        cost_mod = scenario.get('cost_mod', 1.0)
        total_costs *= cost_mod
        
        # Apply difficulty modifier to reduce costs on Easy/Medium
        diff_mods = self._get_difficulty_modifiers()
        total_costs *= diff_mods['costs']
        
        # Apply upgrade bonuses for cost reduction
        cost_multiplier = 1.0 - (self.upgrade_bonuses['cost_reduction'] / 100)
        total_costs *= cost_multiplier
        
        _set(self, 'cash', self.cash - total_costs)
        _set(self, 'quarterly_costs', self.quarterly_costs + total_costs)
        _set(self, 'corp_card_used', max(0, self.corp_card_used - (self.corp_card_limit * 0.01))) # 1% of limit paid off daily
        
        # Apply minimum debt payment to reduce debt
        if self.debt > 0:
            debt_reduction = min(min_debt_payment, self.debt)
            self.debt -= debt_reduction
        
        self.log.append(f"Costs: ${total_costs:,.0f} (Debt payment: ${min_debt_payment:,.0f})")

        # Profit cushion: rebate part of losses to keep the company healthier
        profit_gap = self.quarterly_costs - self.quarterly_revenue
        if profit_gap > 0:
            cushion = profit_gap * 0.25  # 25% rebate on losses
            _set(self, 'cash', self.cash + cushion)
            _set(self, 'quarterly_costs', max(0, self.quarterly_costs - cushion))
            self.log.append(f"💡 Profit cushion applied: ${cushion:,.0f} rebate to ease losses")

    def _generate_revenue(self):
        # Revenue is proportional to market cap, technology, and customer base
        base_revenue = self.market_cap * 0.004  # Increased further to help stay profitable
        
        tech_mod = 0.5 + (self.technology_level / 100) * 0.5  # Min 0.5x, max 1.0x
        cust_mod = 0.5 + (self.customer_base / 100) * 0.5  # Min 0.5x, max 1.0x
        
        # Apply Market Mood and Scenario modifiers
        if self.market_mood == 'Bullish':
            market_mod = 1.2
        elif self.market_mood == 'Bearish':
            market_mod = 0.8
        else:
            market_mod = 1.0
            
        scenario = config.SCENARIOS.get(self.current_scenario)
        scenario_mod = scenario.get('rev_mod', 1.0)
        
        # Apply difficulty modifier for Easy/Medium
        diff_mods = self._get_difficulty_modifiers()
        
        # Apply upgrade bonuses
        revenue_multiplier = 1.0 + (self.upgrade_bonuses['revenue_boost'] / 100)
        customer_growth_bonus = self.upgrade_bonuses['customer_growth']
        
        total_revenue = base_revenue * tech_mod * cust_mod * market_mod * scenario_mod * diff_mods['revenue'] * revenue_multiplier * random.uniform(0.95, 1.05)
        
        # Log revenue upgrade bonus (after total_revenue is calculated)
        if self.upgrade_bonuses['revenue_boost'] > 0:
            bonus_amount = total_revenue * (self.upgrade_bonuses['revenue_boost'] / 100)
            if bonus_amount > 100000:  # Only log if significant
                self.recent_changes.append(("positive", f"Revenue +${bonus_amount/1000000:.1f}M from upgrades"))
        
        # Apply customer growth bonus from upgrades
        if customer_growth_bonus > 0 and random.random() < 0.3:  # 30% chance daily
            old_base = self.customer_base
            self.customer_base = min(100, self.customer_base + (customer_growth_bonus / 10))
            if self.customer_base > old_base:
                self.recent_changes.append(("positive", f"Customers +{(self.customer_base - old_base):.1f}% from growth upgrades"))
        
        _set(self, 'cash', self.cash + total_revenue)
        _set(self, 'quarterly_revenue', self.quarterly_revenue + total_revenue)
        self.log.append(f"Revenue: ${total_revenue:,.0f} (Scen Mod: {scenario_mod}x)")
        
        # Competitor pressure - lose market share if not investing in marketing
        self._apply_competitor_pressure()

    def _apply_competitor_pressure(self):
        """Competitors steal market share if you don't invest in marketing regularly."""
        self.days_without_marketing += 1
        
        # If you haven't invested in marketing for 5+ days, start losing market share
        if self.days_without_marketing >= 5:
            # Market share loss increases with time
            days_overdue = self.days_without_marketing - 5
            base_loss = 0.3  # Base 0.3% loss per day after 5 days
            
            # Loss accelerates the longer you wait
            if days_overdue > 20:
                loss = base_loss * 2.5  # 0.75% per day after 25 days total
            elif days_overdue > 10:
                loss = base_loss * 1.5  # 0.45% per day after 15 days total
            else:
                loss = base_loss  # 0.3% per day for days 5-15
            
            # Customer base erodes
            old_customer_base = self.customer_base
            _set(self, 'customer_base', max(10, self.customer_base - loss))
            
            # Log warning every 5 days
            if self.days_without_marketing % 5 == 0:
                self.log.append(f"⚠️ COMPETITOR ALERT: No marketing for {self.days_without_marketing} days. Customer base: {old_customer_base:.1f}% → {self.customer_base:.1f}%")

    def _update_stock_market(self):
        # Basic Stock Price Fluctuation
        
        # Analyst Rating Factor (Most significant driver)
        rating_index = config.ANALYST_RATINGS.index(self.analyst_rating)
        rating_factor = (rating_index - 2) * 0.025  # Increased to 0.025 for easier stock growth
        
        # Performance Factor (Revenue vs. Previous Quarter Revenue)
        performance_factor = (self.quarterly_revenue - self.previous_quarter_revenue) / self.previous_quarter_revenue if self.previous_quarter_revenue else 0
        performance_factor = min(0.04, max(-0.01, performance_factor * 0.08))  # Higher reward, lower punishment
        
        # Player Action Bonuses (NEW - reward active play)
        action_bonus = 0
        bonus_sources = []
        if self.cash > 0:  # Just staying solvent is good
            action_bonus += 0.004
            bonus_sources.append("solvency")
        if self.quarterly_revenue > self.quarterly_costs:  # Profitable
            action_bonus += 0.010
            bonus_sources.append("profitability")
        if self.customer_base > 30:  # Growing market share
            action_bonus += 0.006
            bonus_sources.append("customers")
        if len(self.projects) > 0:  # Active innovation
            action_bonus += 0.007
            bonus_sources.append("innovation")
        if self.technology_level > 30:  # Investing in tech
            action_bonus += 0.005
            bonus_sources.append("tech")
        
        # General Sentiment Factor (Market Mood & Confidence)
        confidence_factor = (self.board_confidence - 40) / 1500  # Boosted from 2000 for easier stock growth
        
        daily_change = (rating_factor + performance_factor + action_bonus + confidence_factor) * self.stock_price
        
        # Track stock changes from player actions
        if action_bonus > 0 and len(bonus_sources) > 0:
            stock_increase = action_bonus * self.stock_price
            if stock_increase > 0.10:  # Only log if significant
                reasons = ", ".join(bonus_sources)
                if hasattr(self, 'recent_changes'):
                    self.recent_changes.append(("positive", f"Stock +${stock_increase:.2f} from {reasons}"))
        
        # Apply upgrade bonuses to stock growth
        stock_boost = 1.0 + (self.upgrade_bonuses['stock_boost'] / 100)
        if self.upgrade_bonuses['stock_boost'] > 0 and daily_change > 0:
            boost_amount = daily_change * (self.upgrade_bonuses['stock_boost'] / 100)
            if boost_amount > 0.10 and hasattr(self, 'recent_changes'):
                self.recent_changes.append(("positive", f"Stock +${boost_amount:.2f} from Stock Momentum upgrade"))
        daily_change *= stock_boost
        
        # Apply Scenario Impact
        scenario = config.SCENARIOS.get(self.current_scenario)
        stock_mod = scenario.get('stock_mod', 1.0)
        daily_change *= stock_mod
        
        # Reduce random noise for more consistent growth
        new_price = self.stock_price + daily_change + random.uniform(-0.02, 0.02)
        
        _set(self, 'stock_price', max(1.0, new_price))
        _set(self, 'market_cap', self.stock_price * self.shares_outstanding)
        
        # Track stock history (last 90 days)
        self.stock_history.append(self.stock_price)
        if len(self.stock_history) > 90:
            self.stock_history.pop(0)
        
        # Update competitors
        player_actions = {'marketing_pressure': 1 if self.days_without_marketing < 2 else 0}
        for competitor in self.competitors:
            competitor.update_stock_price(player_actions)

    def _update_metrics(self):
        # Health: Always decays, but less if debt/morale is good
        decay = 1.0
        if self.debt > self.cash: decay += 0.5
        if self.employee_morale < 40: decay += 0.5
        
        # Apply health regen from upgrades
        health_regen = self.upgrade_bonuses['health_regen']
        decay -= health_regen
        
        _set(self, 'ceo_health', max(0, self.ceo_health - decay))
        
        # Board Confidence: Improves with high cash/stock price, decays with low
        confidence_change = 0
        if self.cash > 1500000000: confidence_change += 1
        if self.stock_price < 40: confidence_change -= 1
        _set(self, 'board_confidence', max(0, min(100, self.board_confidence + confidence_change)))
        
        # Morale: Improves with high HR budget/low project risk
        morale_change = 0
        if self.departments['HR'] > 30000000: morale_change += 1
        if any(p.risk > 0.8 for p in self.projects): morale_change -= 1
        # Larger engaged workforce boosts morale slightly each day
        morale_change += 0.1 * len(self.employees)
        # Strong manager bench steadies the board
        board_nudge = 0.05 * sum(1 for e in self.employees if e.employee_type in ["Manager", "Automation Expert"])
        _set(self, 'board_confidence', max(0, min(100, self.board_confidence + board_nudge)))
        _set(self, 'employee_morale', max(0, min(100, self.employee_morale + morale_change)))
        
        # Technology: Slow decay if R&D investment is low
        if self.daily_rnd_cost < 100000:
            _set(self, 'technology_level', max(10, self.technology_level - 0.1))
            
        # Market Mood: Changes based on Tech/Customer base
        if self.technology_level > 80 and self.customer_base > 80:
            _set(self, 'market_mood', 'Bullish')
        elif self.technology_level < 30 or self.customer_base < 30:
            _set(self, 'market_mood', 'Bearish')
        else:
            _set(self, 'market_mood', 'Neutral')
    
    def _update_credit_rating(self):
        """Update credit rating based on debt-to-equity ratio and financial health."""
        equity = self.market_cap
        if equity <= 0:
            equity = 1  # Prevent division by zero
        
        debt_to_equity = self.debt / equity
        
        # Determine credit rating (STRICTER THRESHOLDS - harder to achieve high ratings)
        # AAA requires very low debt, high cash reserves, and profitability
        if debt_to_equity < 0.05 and self.cash > self.market_cap * 0.15 and self.quarterly_revenue > self.quarterly_costs:
            new_rating = "AAA"
        # AA requires minimal debt and strong cash position
        elif debt_to_equity < 0.15 and self.cash > self.market_cap * 0.10:
            new_rating = "AA"
        # A requires low debt and positive cash
        elif debt_to_equity < 0.30 and self.cash > 0:
            new_rating = "A"
        # BBB requires moderate debt levels
        elif debt_to_equity < 0.55:
            new_rating = "BBB"
        # BB for higher debt
        elif debt_to_equity < 0.90:
            new_rating = "BB"
        # B for very high debt
        elif debt_to_equity < 1.5:
            new_rating = "B"
        else:
            new_rating = "CCC"
        
        # Log rating changes
        if new_rating != self.credit_rating:
            old_rating = self.credit_rating
            self.credit_rating = new_rating
            
            # Rating downgrades hurt stock price
            rating_order = ["AAA", "AA", "A", "BBB", "BB", "B", "CCC"]
            old_index = rating_order.index(old_rating) if old_rating in rating_order else 3
            new_index = rating_order.index(new_rating)
            
            if new_index > old_index:  # Downgrade
                penalty = (new_index - old_index) * 0.05
                self.stock_price *= (1 - penalty)
                self.log.append(f"⚠️ Credit rating DOWNGRADED: {old_rating} → {new_rating} (Stock price -{penalty*100:.0f}%)")
            else:  # Upgrade (REDUCED BONUS - smaller reward for improvements)
                bonus = (old_index - new_index) * 0.02  # Reduced from 0.03
                self.stock_price *= (1 + bonus)
                self.log.append(f"✓ Credit rating UPGRADED: {old_rating} → {new_rating} (Stock price +{bonus*100:.0f}%)")
    
    def _get_interest_rate(self) -> float:
        """Return annual interest rate based on credit rating."""
        rates = {
            "AAA": 0.03,  # 3%
            "AA": 0.04,   # 4%
            "A": 0.05,    # 5%
            "BBB": 0.06,  # 6%
            "BB": 0.08,   # 8%
            "B": 0.14,    # 14% (increased from 11%)
            "CCC": 0.20   # 20% (increased from 15%)
        }
        base_rate = rates.get(self.credit_rating, 0.05)
        # Apply difficulty modifier
        diff_mods = self._get_difficulty_modifiers()
        return base_rate * diff_mods['interest_rate']
    
    def _update_board_satisfaction(self):
        """Update board member satisfaction and trust based on company performance."""
        # Calculate performance score
        stock_change = ((self.stock_price - 10.0) / 10.0) * 100  # % change from initial
        profit_margin = ((self.quarterly_revenue - self.quarterly_costs) / max(self.quarterly_revenue, 1)) * 100 if self.quarterly_revenue > 0 else -50
        morale_score = self.employee_morale - 50
        
        for member in self.board_members:
            # Base satisfaction change on performance
            satisfaction_delta = 0
            trust_delta = 0
            
            # Stock performance affects all board members
            if stock_change > 20:
                satisfaction_delta += 2
                trust_delta += 1
            elif stock_change < -20:
                satisfaction_delta -= 2
                trust_delta -= 1
            
            # Personality-specific updates
            if member.personality == "Conservative":
                # Cares about debt and stability
                if self.debt < self.market_cap * 0.3:
                    satisfaction_delta += 1
                if self.debt > self.market_cap * 0.8:
                    satisfaction_delta -= 2
            
            elif member.personality == "Progressive":
                # Cares about employee morale and innovation
                if self.employee_morale > 60:
                    satisfaction_delta += 2
                if self.employee_morale < 30:
                    satisfaction_delta -= 2
            
            elif member.personality == "Investor-Focused":
                # Only cares about profits and stock price
                if profit_margin > 15:
                    satisfaction_delta += 3
                if profit_margin < 0:
                    satisfaction_delta -= 3
            
            elif member.personality == "Employee-Advocate":
                # Heavily influenced by morale and reputation
                satisfaction_delta += int(morale_score / 20)
                if self.reputation > 60:
                    satisfaction_delta += 1
            
            elif member.personality == "Risk-Taker":
                # Likes growth and bold moves
                if self.customer_base > 50:
                    satisfaction_delta += 2
                if self.technology_level > 50:
                    satisfaction_delta += 1
            
            # Update the member
            member.update_satisfaction(satisfaction_delta)
            member.update_trust(trust_delta)
    
    def get_board_approval(self, decision_type: str) -> tuple[bool, str]:
        """
        Request board approval for major decisions.
        Returns (approved: bool, message: str)
        decision_type: 'acquisitions', 'debt', 'layoffs', 'expansion', 'dividends'
        """
        # Calculate company performance score for voting
        stock_change = ((self.stock_price - 10.0) / 10.0) * 100
        profit_margin = ((self.quarterly_revenue - self.quarterly_costs) / max(self.quarterly_revenue, 1)) * 100 if self.quarterly_revenue > 0 else -50
        performance = (stock_change + profit_margin) / 2
        
        # Get votes from each board member
        votes = []
        details = []
        for member in self.board_members:
            vote = member.vote(decision_type, performance)
            votes.append(vote)
            vote_str = "✓ Approved" if vote else "✗ Rejected"
            details.append(f"{member.name}: {vote_str}")
        
        # Majority vote (3 out of 5)
        approval_count = sum(votes)
        approved = approval_count >= 3
        
        # Build result message
        vote_summary = f"Board Vote: {approval_count}/5 Approved\n\n" + "\n".join(details)
        
        if approved:
            result_msg = f"✓ APPROVED\n\n{vote_summary}\n\nThe board has approved this decision."
            # Slight trust boost for good decisions
            for i, vote in enumerate(votes):
                if vote:
                    self.board_members[i].update_trust(1)
        else:
            result_msg = f"✗ REJECTED\n\n{vote_summary}\n\nThe board has rejected this decision."
            # Trust penalty for rejected proposals
            for member in self.board_members:
                member.update_trust(-2)
        
        return approved, result_msg
    
    def get_leaderboard_position(self):
        """Get player's rank on the Wall Street leaderboard (1 = best)"""
        all_stocks = [(comp.name, comp.stock_price) for comp in self.competitors]
        all_stocks.append((self.corp_name or "Your Company", self.stock_price))
        
        # Sort by stock price descending
        all_stocks.sort(key=lambda x: x[1], reverse=True)
        
        # Find player position
        for i, (name, price) in enumerate(all_stocks):
            if name == (self.corp_name or "Your Company"):
                return i + 1  # 1-indexed position
        return len(all_stocks)
    
    def check_victory_condition(self):
        """Check if player has reached #1 on leaderboard"""
        position = self.get_leaderboard_position()
        if position == 1 and not self.has_won_game:
            self.has_won_game = True
            return True
        return False

    def _update_scenario(self):
        # Only check for new scenario if the current one has expired
        if self.scenario_duration <= 0:
            # Random chance to pick a new one, or return to 'Stable Growth'
            if random.random() < 0.25: 
                new_scenario = random.choice(list(config.SCENARIOS.keys()))
                self.current_scenario = new_scenario
                self.scenario_duration = random.randint(30, 90)
                self.log.append(f"*** MARKET SCENARIO: {new_scenario} - {config.SCENARIOS[new_scenario]['desc']} ***")
            else:
                self.current_scenario = "Stable Growth"
        else:
            self.scenario_duration -= 1

    def _check_quarter_end(self):
        if self.day % 90 == 0:
            self.log.append("*** QUARTER END: Preparing for Earnings Call ***")
            self.previous_quarter_revenue = self.quarterly_revenue # Save for next quarter's comparison
            _set(self, 'quarterly_revenue', 0)
            _set(self, 'quarterly_costs', 0)
            _set(self, 'quarter', self.quarter + 1)
            if self.quarter > 4:
                _set(self, 'quarter', 1)
                _set(self, 'year', self.year + 1)
                # RESET ANNUAL BUDGETS ON NEW YEAR
                self.budget_spent = {"R&D": 0, "Marketing": 0, "Operations": 0, "HR": 0}
                self.log.append("*** NEW YEAR: Annual department budgets reset! ***")
            
            return "Earnings_Call" # Mandatory event trigger


    def _check_game_over(self):
        # Check for victory conditions first
        victory = self._check_victory()
        if victory:
            return victory
        
        # Trigger emergency borrowing if cash is negative
        if self.cash < 0:
            return "EmergencyBorrowing"
        if self.debt > self.max_debt_limit * 10:  # 10x debt limit = bankruptcy
            return "GameOver_Debt"
        if self.board_confidence < 10:
            return "GameOver_Board"
        if self.ceo_health <= 0:
            return "GameOver_Health"
        return "OK"
    
    def _check_victory(self):
        """Check for victory conditions. Returns victory type or None."""
        # Victory 0: Leaderboard Winner - 1st place in stock price
        if self.competitors:
            player_stock = self.stock_price
            highest_competitor_stock = max(comp.stock_price for comp in self.competitors)
            if player_stock > highest_competitor_stock:
                return "Victory_Leaderboard"
        
        # Victory 1: IPO Success - Market cap reaches $500M+
        if self.market_cap >= 500_000_000 and self.stock_price > 50:
            return "Victory_IPO"
        
        # Victory 2: Market Dominance - High customer base + strong revenue
        if self.customer_base >= 80 and self.quarterly_revenue >= 250_000_000:
            return "Victory_Dominance"
        
        # Victory 3: Acquisition Exit - Get acquired by larger company (market cap $750M+, high reputation)
        if self.market_cap >= 750_000_000 and self.reputation >= 80 and self.technology_level >= 75:
            return "Victory_Acquired"
        
        return None

    def _check_executive_point_earnings(self):
        """Award Executive Points for hitting milestones and achievements."""
        points_earned = 0
        
        # Daily earnings for good performance
        if self.quarterly_revenue > self.quarterly_costs:
            points_earned += 1  # 1 point per profitable day
        
        # Stock price milestones (one-time)
        stock_milestones = [15, 25, 50, 100, 200, 500]
        for milestone in stock_milestones:
            milestone_id = f"stock_{milestone}"
            if self.stock_price >= milestone and milestone_id not in self.purchased_upgrades:
                points_earned += 5
                self.purchased_upgrades.append(milestone_id)  # Mark as achieved
                self.log.append(f"🎉 MILESTONE: Stock price hit ${milestone}! Earned 5 Executive Points.")
        
        # Revenue milestones
        if self.day % 30 == 0:  # Monthly check
            monthly_revenue = self.quarterly_revenue / max(1, self.day % 90)
            if monthly_revenue > 5000000:  # $5M+ monthly
                points_earned += 3
        
        # Customer base milestones
        customer_milestones = [40, 60, 80, 100]
        for milestone in customer_milestones:
            milestone_id = f"customer_{milestone}"
            if self.customer_base >= milestone and milestone_id not in self.purchased_upgrades:
                points_earned += 3
                self.purchased_upgrades.append(milestone_id)
                self.log.append(f"🎉 MILESTONE: Customer base hit {milestone}%! Earned 3 Executive Points.")
        
        if points_earned > 0:
            self.executive_points += points_earned
            if points_earned > 1:  # Don't spam for daily 1 point
                self.log.append(f"✨ Earned {points_earned} Executive Points! Total: {self.executive_points}")
    
    def _apply_milestone_stock_boosts(self):
        """Apply major stock price boosts when key milestones are hit."""
        stock_boost = 0
        boost_reason = ""
        
        # First Profitability Achievement
        if self.quarterly_revenue > self.quarterly_costs and "first_profitable" not in self.purchased_upgrades:
            stock_boost = 0.50  # $0.50 boost
            boost_reason = "First Profitable Quarter!"
            self.purchased_upgrades.append("first_profitable")
            self.log.append("🚀 MAJOR EVENT: First profitable quarter! Stock rallies!")
        
        # Revenue thresholds
        revenue_milestones = {"revenue_10m": (10000000, 0.25), "revenue_50m": (50000000, 0.50), 
                             "revenue_100m": (100000000, 1.0), "revenue_250m": (250000000, 2.0)}
        for milestone_id, (threshold, boost) in revenue_milestones.items():
            if self.quarterly_revenue >= threshold and milestone_id not in self.purchased_upgrades:
                stock_boost += boost
                boost_reason = f"Revenue exceeded ${threshold/1000000:.0f}M!"
                self.purchased_upgrades.append(milestone_id)
                self.log.append(f"📈 REVENUE MILESTONE: Quarterly revenue hit ${threshold/1000000:.0f}M! Stock surges!")
                break  # Only trigger one per day
        
        # Customer base thresholds
        if not boost_reason:  # Only if no revenue milestone triggered
            customer_milestones = {"customer_50": (50, 0.30), "customer_75": (75, 0.60), "customer_100": (100, 1.50)}
            for milestone_id, (threshold, boost) in customer_milestones.items():
                if self.customer_base >= threshold and milestone_id not in self.purchased_upgrades:
                    stock_boost += boost
                    boost_reason = f"Customer base reached {threshold}%!"
                    self.purchased_upgrades.append(milestone_id)
                    self.log.append(f"👥 MARKET MILESTONE: Reached {threshold}% customer base! Stock gains!")
                    break  # Only trigger one per day
        
        # Technology milestones
        if not boost_reason:
            tech_milestones = {"tech_50": (50, 0.20), "tech_75": (75, 0.40), "tech_100": (100, 0.80)}
            for milestone_id, (threshold, boost) in tech_milestones.items():
                if self.technology_level >= threshold and milestone_id not in self.purchased_upgrades:
                    stock_boost += boost
                    boost_reason = f"Tech level reached {threshold}!"
                    self.purchased_upgrades.append(milestone_id)
                    self.log.append(f"🔬 TECH MILESTONE: Technology level hit {threshold}! Market excited!")
                    break  # Only trigger one per day
        
        # Project completion boost
        if not boost_reason and len(self.projects) > 0:
            launched_count = sum(1 for p in self.projects if p.lifecycle_stage != "Development")
            project_milestone_id = f"projects_launched_{launched_count}"
            if launched_count >= 3 and project_milestone_id not in self.purchased_upgrades and "first_launched_project" not in self.purchased_upgrades:
                stock_boost = 0.35
                boost_reason = "First project launched!"
                self.purchased_upgrades.append("first_launched_project")
                self.log.append("🎯 MILESTONE: First product launched! Stock rallies on momentum!")
        
        # Apply the boost
        if stock_boost > 0:
            _set(self, 'stock_price', self.stock_price + stock_boost)
            _set(self, 'market_cap', self.stock_price * self.shares_outstanding)
            if hasattr(self, 'recent_changes'):
                self.recent_changes.append(("positive", f"Stock +${stock_boost:.2f} from {boost_reason}"))
    
    def _execute_employee_actions(self):
        """Execute daily auto-actions for each hired employee."""
        for employee in self.employees:
            if not employee.auto_actions:
                continue
            
            # Pick assigned action if set and valid; otherwise random
            if employee.assigned_action and employee.can_perform_action(employee.assigned_action):
                action_name = employee.assigned_action
            else:
                action_name = random.choice(employee.auto_actions)
            
            # Success chance based on employee skill level (90-100% for skilled workers)
            success_chance = 0.85 + (employee.skill_level * 0.10)
            success_chance = min(1.0, success_chance)
            
            if random.random() < success_chance:
                result_msg = self._perform_employee_work(employee, action_name)
                if result_msg:
                    employee.tasks_completed += 1
                    employee.skill_level = min(2.0, employee.skill_level + 0.02)  # Skill improves
                    self.automation_log.append(f"Day {self.day}: {employee.name} ({employee.position}) - {result_msg}")
    
    def _perform_employee_work(self, employee, action_name: str) -> str:
        """Employee performs work and returns detailed description of what they did."""
        try:
            if action_name == "email":
                if self.email_system:
                    # Each employee assigned to email clears 2 emails per day (safe options)
                    emails_cleared = 0
                    for _ in range(2):
                        try:
                            result = getattr(self.email_system, 'auto_clear_one_email', None)
                            if callable(result):
                                msg = self.email_system.auto_clear_one_email()
                                if msg is not None:
                                    emails_cleared += 1
                            else:
                                # Fallback: remove first email conservatively
                                if self.email_system.inbox:
                                    self.email_system.apply_action(0, 0)
                                    emails_cleared += 1
                        except Exception:
                            # Don't break the employee loop on email errors
                            pass
                    if emails_cleared > 0:
                        return f"Cleared {emails_cleared} emails from inbox"
                return None
            
            elif action_name == "marketing":
                budget = min(1500000, self.annual_budget.get('Marketing', 0) - self.budget_spent.get('Marketing', 0))
                if budget > 300000:
                    self.budget_spent['Marketing'] = self.budget_spent.get('Marketing', 0) + budget
                    target = "B2B" if self.market_segments["B2B"] < 50 else "Consumer"
                    growth = random.uniform(0.5, 1.5)
                    self.customer_base = min(100, self.customer_base + growth)
                    # Reset competitor pressure countdown when marketing occurs
                    self.days_without_marketing = 0
                    return f"Ran ${budget/1000000:.1f}M {target} campaign, gained {growth:.1f}% market share"
                return None
            
            elif action_name == "customer_outreach":
                growth = random.uniform(0.3, 0.8) * employee.skill_level
                self.customer_base = min(100, self.customer_base + growth)
                self.reputation = min(100, self.reputation + random.uniform(0.1, 0.3))
                return f"Customer outreach calls: +{growth:.1f}% customer base, +{random.uniform(0.1, 0.3):.1f} reputation"
            
            elif action_name == "rnd":
                budget = min(800000, self.annual_budget.get('R&D', 0) - self.budget_spent.get('R&D', 0))
                if budget > 150000:
                    self.budget_spent['R&D'] = self.budget_spent.get('R&D', 0) + budget
                    available_tracks = [t for t, v in self.technology_tracks.items() if v < 100]
                    if available_tracks:
                        track = random.choice(available_tracks)
                        points = (budget / 100000) * employee.skill_level
                        self.technology_tracks[track] = min(100, self.technology_tracks[track] + points)
                        return f"R&D work on {track}: ${budget/1000:.0f}K spent, +{points:.1f} tech points"
                return None
            
            elif action_name == "innovation":
                tech_boost = random.uniform(0.5, 1.2) * employee.skill_level
                self.technology_level = min(100, self.technology_level + tech_boost)
                return f"Innovation session: developed new tech, +{tech_boost:.1f} tech level"

            elif action_name == "wellness":
                # Host a CEO wellness session funded from HR budget
                available_hr_budget = self.annual_budget.get('HR', 0) - self.budget_spent.get('HR', 0)
                session_cost = 300000  # $300K wellness program
                if available_hr_budget >= session_cost and self.cash >= session_cost:
                    self.budget_spent['HR'] = self.budget_spent.get('HR', 0) + session_cost
                    self.cash -= session_cost
                    health_gain = random.uniform(6, 12) * employee.skill_level
                    morale_gain = random.uniform(1, 2)
                    _set(self, 'ceo_health', min(100, self.ceo_health + health_gain))
                    _set(self, 'employee_morale', min(100, self.employee_morale + morale_gain))
                    return f"Wellness session run: CEO health +{health_gain:.1f}, morale +{morale_gain:.1f}"
                return "Wellness session skipped (insufficient HR budget or cash)"
            
            elif action_name == "budget":
                low_depts = [d for d in self.annual_budget.keys() if self.get_available_budget(d) < 2000000]
                if low_depts and self.cash > 3000000:
                    dept = low_depts[0]
                    boost = 2000000
                    self.annual_budget[dept] += boost
                    self.cash -= boost
                    return f"Budget reallocation: +${boost/1000000:.1f}M to {dept} department"
                return "Reviewed budgets, all departments adequately funded"
            
            elif action_name == "cash_management":
                # Reduce expenses slightly through optimization
                if random.random() < 0.3:  # 30% chance
                    savings = random.uniform(50000, 200000) * employee.skill_level
                    self.cash += savings
                    return f"Optimized expenses: saved ${savings/1000:.0f}K through process improvements"
                return "Reviewed financial reports, monitored cash flow"
            
            elif action_name == "efficiency":
                # Improve operations
                if random.random() < 0.4:  # 40% chance
                    cost_reduction = random.uniform(30000, 100000)
                    self.cash += cost_reduction
                    return f"Streamlined operations: reduced daily costs by ${cost_reduction/1000:.0f}K"
                return "Analyzed workflows, identified optimization opportunities"
            
            elif action_name == "cost_reduction":
                savings = random.uniform(40000, 120000) * employee.skill_level
                self.cash += savings
                return f"Cost audit: eliminated wasteful spending, saved ${savings/1000:.0f}K"
            
            elif action_name == "morale":
                morale_boost = random.uniform(0.8, 2.0) * employee.skill_level
                self.employee_morale = min(100, self.employee_morale + morale_boost)
                return f"Organized team building event: +{morale_boost:.1f} employee morale"
            
            elif action_name == "hiring_support":
                # Small reputation boost from recruitment activities
                rep_gain = random.uniform(0.2, 0.5)
                self.reputation = min(100, self.reputation + rep_gain)
                return f"Screened job candidates, improved employer brand (+{rep_gain:.1f} reputation)"
            
            elif action_name == "launch_project":
                # Project Manager launches a strategic project (carefully - only 30% chance daily)
                if random.random() > 0.30:
                    # Most days, they just review and plan
                    return "Reviewed project pipeline and assessed market opportunities (no launch today)."
                
                if self.projects and len(self.projects) >= 5:
                    # Too many active projects, don't launch more
                    return f"Portfolio full: {len(self.projects)} projects active. Consider retiring mature ones."
                
                # Check if we have sufficient resources (more stringent requirements)
                available_rnd_budget = self.annual_budget.get('R&D', 0) - self.budget_spent.get('R&D', 0)
                if available_rnd_budget < 8000000 or self.cash < 15000000:
                    return "Insufficient R&D budget or cash to launch a new project."
                
                # Propose a project based on employee skill and tech gaps
                project_types = [
                    (1, "AI Integration Engine", 25000000, 50),
                    (1, "Cloud Infrastructure Platform", 20000000, 45),
                    (1, "Advanced Analytics Suite", 18000000, 35),
                    (2, "Customer Engagement Suite", 15000000, 25),
                    (3, "Process Automation Framework", 12000000, 15)
                ]
                proj_type, proj_name, proj_investment, proj_days = random.choice(project_types)
                
                success, msg = self.launch_project(
                    proj_name,
                    proj_investment,
                    base_price=500000,
                    development_days=proj_days,
                    project_type=proj_type
                )
                
                if success:
                    return f"Launched project '{proj_name}': {proj_days}-day dev cycle, ${proj_investment/1000000:.1f}M investment"
                else:
                    return f"Project launch blocked: {msg}"
            
            return None
        
        except Exception as e:
            print(f"Employee work error: {e}")
            return None
    
    def launch_project(self, name, investment, base_price, development_days, project_type):
        """Launch a unified project (development → market lifecycle)."""
        # Calculate risk based on duration (faster = riskier)
        risk = max(0.05, min(0.90, (110 - development_days) / 100))
        
        # 10% upfront, 90% debt
        upfront_cost = investment * 0.1
        debt_amount = investment * 0.9
        
        if self.cash < upfront_cost:
            return False, f"Insufficient cash. Need ${upfront_cost/1000000:.1f}M upfront."
        
        if self.debt + debt_amount > self.max_debt_limit:
            return False, "Project would exceed debt limit."
        
        # Determine budget source
        budget_dept = {1: 'R&D', 2: 'Marketing', 3: 'Operations'}.get(project_type, 'R&D')
        if not self.can_afford_action(budget_dept, upfront_cost):
            return False, f"{budget_dept} budget insufficient."
        
        # Create unified project
        project = Product(name, investment, base_price, development_days, project_type, risk)
        
        # Deduct costs
        self.spend_from_budget(budget_dept, upfront_cost)
        self.cash -= upfront_cost
        self.debt += debt_amount
        
        self.projects.append(project)
        self.log.append(f"🎯 Started project '{name}': ${upfront_cost/1000000:.1f}M cash + ${debt_amount/1000000:.1f}M debt. Dev time: {development_days} days")
        
        return True, f"Project started! {development_days} days development, then market launch."
    
    def retire_product(self, product):
        """Retire a project from the market."""
        product.retire()
        self.log.append(f"Retired project: {product.name}. Total revenue: ${product.total_revenue/1000000:.1f}M")
    
    def update_day(self):
        self.log.append(f"--- Day {self.day} Begins (Q{self.quarter}, Y{self.year}) ---")
        
        # RESET ACTION POINTS FOR NEW DAY (include upgrade bonus)
        self.action_points = self.max_action_points + self.upgrade_bonuses['action_points_bonus']
        self.log.append(f"Daily action points reset to {self.action_points}.")
        
        # EARN EXECUTIVE POINTS from achievements
        self._check_executive_point_earnings()
        
        # APPLY MILESTONE STOCK BOOSTS (NEW)
        self._apply_milestone_stock_boosts()
        
        # EXECUTE EMPLOYEE AUTO-ACTIONS
        self._execute_employee_actions()
        
        # PROCESS ACQUISITION PROFITS (NEW)
        self._process_acquisition_profits()
        
        self._update_scenario()
        self.calculate_efficiency() # Recalculate efficiencies before costs/projects
        self._generate_revenue()
        self._process_projects()  # Handles both development and market phases
        self.process_daily_rnd() # R&D runs after projects/revenue
        self._generate_costs() # Costs run last
        self._update_stock_market()
        self._update_metrics()
        self._update_credit_rating()  # Update credit rating based on debt levels
        self._update_board_satisfaction()  # Update board member trust and satisfaction
        
        self.day += 1
        
        game_over = self._check_game_over()
        if game_over != "OK":
            return game_over
            
        quarter_end = self._check_quarter_end()
        if quarter_end is not None:
            return quarter_end
            
        # Check for daily events/emails
        event_trigger = self.email_system.check_for_events()
        
        if event_trigger is not None:
            return event_trigger # Returns "OK" or a mandatory popup event ID

        return "OK"


    def process_earnings_call(self, final_score):
        # A mock function to simulate Wall Street response after the call
        
        if final_score > 200:
            new_rating = "Strong Buy"
            stock_change = 0.03  # Reduced from 0.10
        elif final_score > 150:
            new_rating = "Buy"
            stock_change = 0.015  # Reduced from 0.05
        elif final_score > 100:
            new_rating = "Hold"
            stock_change = 0.00
        else:
            new_rating = random.choice(["Sell", "Strong Sell"])
            stock_change = -0.02  # Reduced from -0.05
            
        _set(self, 'analyst_rating', new_rating)
        _set(self, 'stock_price', self.stock_price * (1 + stock_change))
        _set(self, 'board_confidence', min(100, self.board_confidence + int(stock_change * 100)))
        
        self.log.append(f"*** EARNINGS CALL COMPLETE. Analyst Rating: {new_rating}. Stock Price: {stock_change:+.0%} ***")
        return f"Analyst rating adjusted to {new_rating}. Stock price changed by {stock_change:+.0%}"


    def use_corp_card(self, action_type):
        """Processes a corporate card expense."""
        cost = 0
        metric = None

        # Map expense names from UI to actions
        if "Executive Retreat" in action_type:
            cost = 5000000
            metric = 'ceo_health'
        elif "Lobbyist Fee" in action_type:
            cost = 2000000
            metric = 'board_confidence'
        elif "Luxury Travel" in action_type:
            cost = 500000
            metric = 'reputation'
        elif "Office Decor" in action_type:
            cost = 100000
            metric = 'employee_morale'
        elif action_type == "PR_Campaign":
            cost = 5000000
            metric = 'reputation'
        elif action_type == "Urgent_Tech_Upgrade":
            cost = 1000000
            metric = 'technology_level'
        elif action_type == "Emergency_Travel":
            cost = 100000
            metric = None
        elif action_type == "CEO_Wellness":
            cost = 750000
            metric = 'ceo_health'
        elif action_type == "Market_Data_Buy":
            cost = 3000000
            metric = 'board_confidence'
        else:
            return "Invalid expense type."

        if self.corp_card_used + cost > self.corp_card_limit:
            return f"Action failed: Exceeds corporate card limit of ${self.corp_card_limit:,.0f}."

        _set(self, 'corp_card_used', self.corp_card_used + cost)
        self.log.append(f"Corp Card Used: ${cost:,.0f} for {action_type}.")

        if metric:
            # Apply a boost to the metric
            boost = random.uniform(5, 15)
            current_value = getattr(self, metric)
            _set(self, metric, min(100, current_value + boost))
            
            # Reset competitor pressure if this was a marketing/PR action
            if action_type == "PR_Campaign":
                self.days_without_marketing = 0
            
            return f"Expense approved! {metric.replace('_', ' ').title()} boosted by {boost:.1f} points."
        
        return "Expense approved. Minor impact."


    def manage_debt_equity(self, action_type, amount):
        """Handles debt borrowing/repaying and equity (shares) management."""
        if action_type == 'Borrow':
            # Calculate dynamic debt limit based on board confidence
            # Higher confidence = higher borrowing capacity
            confidence_multiplier = 0.5 + (self.board_confidence / 100) * 1.5  # 0.5x to 2.0x
            current_limit = self.max_debt_limit * confidence_multiplier
            
            if amount > 500000000: 
                return "Cannot borrow more than $500M in one transaction."
            if self.debt + amount > current_limit:
                return f"Borrowing denied: Would exceed debt limit of ${current_limit:,.0f} (based on board confidence {self.board_confidence:.0f}%). Current debt: ${self.debt:,.0f}"
            
            _set(self, 'debt', self.debt + amount)
            _set(self, 'cash', self.cash + amount)
            _set(self, 'board_confidence', max(0, self.board_confidence - 5))
            self.log.append(f"Borrowed: ${amount:,.0f}. Debt increased. Limit: ${current_limit:,.0f}")
            return f"Successfully borrowed ${amount:,.0f}. Debt is now ${self.debt:,.0f}. Your borrowing limit is ${current_limit:,.0f}."
        elif action_type == 'Repay':
            if amount > self.cash: return "Insufficient cash to repay debt."
            if amount > self.debt: return "Repayment amount exceeds current debt."
            _set(self, 'debt', self.debt - amount)
            _set(self, 'cash', self.cash - amount)
            _set(self, 'board_confidence', min(100, self.board_confidence + 5))
            self.log.append(f"Repaid: ${amount:,.0f}. Debt decreased.")
            return f"Successfully repaid ${amount:,.0f}. Debt is now ${self.debt:,.0f}."
        elif action_type == 'Issue_Shares':
            # Simplified issue shares
            new_shares = amount // int(self.stock_price * 1.1)
            _set(self, 'shares_outstanding', self.shares_outstanding + new_shares)
            _set(self, 'cash', self.cash + amount)
            self.log.append(f"Issued {new_shares:,.0f} shares for ${amount:,.0f}.")
            return f"Issued {new_shares:,.0f} new shares. Cash increased."
        elif action_type == 'Repurchase_Shares':
            # Simplified share buyback
            if amount > self.cash: return "Insufficient cash for share repurchase."
            repurchased_shares = amount // int(self.stock_price * 0.9)
            _set(self, 'shares_outstanding', max(10000, self.shares_outstanding - repurchased_shares))
            _set(self, 'cash', self.cash - amount)
            self.log.append(f"Repurchased {repurchased_shares:,.0f} shares for ${amount:,.0f}.")
            return f"Repurchased {repurchased_shares:,.0f} shares. Shares outstanding decreased."
        return "Invalid action type."

    def manage_manda_actions(self, action_type, amount, **kwargs):
        """Handles mergers/acquisitions, divestitures, and market shifting."""
        if action_type == 'Acquire':
            if amount > self.cash: return "Insufficient cash for acquisition."
            _set(self, 'cash', self.cash - amount)
            _set(self, 'reputation', min(100, self.reputation + 10))
            _set(self, 'customer_base', min(100, self.customer_base + amount * 0.00000001))
            _set(self, 'technology_level', min(100, self.technology_level + amount * 0.00000001))
            _set(self, 'board_confidence', min(100, self.board_confidence + 5))
            self.log.append(f"**M&A:** Acquisition for ${amount:,.0f}. Metrics boosted.")
            return f"Acquisition of ${amount:,.0f} complete. Metrics boosted."
        elif action_type == 'Divest':
            _set(self, 'cash', self.cash + amount)
            _set(self, 'customer_base', max(0, self.customer_base - amount/50000000))
            _set(self, 'technology_level', max(10, self.technology_level - 5))
            self.log.append(f"**M&A:** Divestiture of ${amount:,.0f}.")
            return f"Divestiture complete."
        elif action_type == 'Market_Shift':
            target_segment = kwargs.get('target_segment')
            if target_segment not in self.market_segments: return "Invalid segment."
            if amount > self.cash: return "Insufficient cash."
            
            _set(self, 'cash', self.cash - amount)
            other_segment = [s for s in self.market_segments if s != target_segment][0]
            shift_amount = 10 
            
            if self.market_segments[other_segment] < shift_amount: return "Shift failed. Source segment too small."
            
            self.market_segments[target_segment] = min(100, self.market_segments[target_segment] + shift_amount)
            self.market_segments[other_segment] = max(0, self.market_segments[other_segment] - shift_amount)
            _set(self, 'customer_base', min(100, self.customer_base + 5))
            
            # Reset competitor pressure counter (you're investing in marketing)
            self.days_without_marketing = 0
            
            self.log.append(f"**Action:** Focus shifted to {target_segment}.")
            return f"Market focus shifted to {target_segment}."
        return "Invalid action type."

    def adjust_budget(self, new_budgets):
        # Budget change is immediately reflected
        current_total = sum(self.departments.values())
        new_total = sum(new_budgets.values())
        delta = new_total - current_total
        if delta > 0 and self.cash < delta:
            return "Insufficient cash to increase department budgets."

        self.cash -= delta
        for dept, new_budget in new_budgets.items():
            self.departments[dept] = new_budget

        self.log.append(f"Department budgets adjusted. Cash {'used' if delta>0 else 'returned'}: ${abs(delta):,.0f}.")
        return "Department budgets adjusted successfully."

    # --- EMPLOYEE IMPACT HELPERS ---
    def _employee_dept_bonus(self, dept: str) -> float:
        """Aggregate employee-driven efficiency bonus for a department."""
        bonus = 0.0
        for emp in self.employees:
            if emp.employee_type == "Analyst" and dept == 'Marketing':
                bonus += 2.0 * emp.skill_level
            elif emp.employee_type == "Manager" and dept == 'Operations':
                bonus += 2.0 * emp.skill_level
            elif emp.employee_type == "Specialist" and dept == 'R&D':
                bonus += 2.0 * emp.skill_level
            elif emp.employee_type == "Automation Expert":
                bonus += 1.5 * emp.skill_level  # Broad, smaller lift across all
        return bonus
    
    # --- ACQUISITION SYSTEM HELPERS ---
    def _process_acquisition_profits(self):
        """Calculate and add daily profits from acquired companies (2% daily cut)."""
        if not self.acquired_companies:
            return  # No companies acquired yet
        
        total_profit = 0
        for company in self.acquired_companies:
            daily_profit = company.earn_daily_profit()
            company.total_profit_earned += daily_profit
            total_profit += daily_profit
        
        if total_profit > 0:
            self.cash += total_profit
            self.total_acquisition_profit += total_profit
            self.log.append(f"Acquisition profits: ${total_profit:,.0f} from {len(self.acquired_companies)} companies")
    
    def attempt_acquire_company(self, company_name: str, offer_index: int) -> tuple:
        """
        Attempt to acquire a company with the given offer (0=cheap, 1=medium, 2=expensive).
        Costs 1 action point.
        Returns (success: bool, message: str, price: int)
        """
        # Check action points
        if self.action_points < 1:
            return False, "Not enough action points. Major acquisitions require 1 action point.", 0
        
        # Find the company
        company = None
        for c in self.available_companies:
            if c.name == company_name:
                company = c
                break
        
        if not company:
            return False, "Company not found.", 0
        
        if company.acquired:
            return False, "Company already acquired.", 0
        
        # Get the offer
        offers = company.generate_offers()
        if offer_index < 0 or offer_index >= len(offers):
            return False, "Invalid offer index.", 0
        
        offer = offers[offer_index]
        price = offer['price']
        
        # Check cash and Operations budget
        if self.cash < price:
            return False, f"Insufficient cash. Need ${price:,.0f}M, have ${self.cash:,.0f}.", price
        
        if not self.can_afford_action('Operations', price):
            return False, f"Operations budget insufficient. Need ${price:,.0f}M.", price
        
        # Attempt acquisition (random success based on offer)
        if company.attempt_acquisition(offer_index):
            # Success!
            self.spend_from_budget('Operations', price)
            self.cash -= price
            self.action_points -= 1  # Deduct action point
            company.acquired = True
            company.acquired_day = self.day
            self.acquired_companies.append(company)
            self.available_companies.remove(company)
            self.log.append(f"Acquired {company.name} for ${price:,.0f} ({offer['label']}). -1 action point.")
            return True, f"Acquisition successful! {company.name} now generates 2% daily profits.", price
        else:
            # Failed attempt still costs action point (due diligence was performed)
            self.action_points -= 1
            self.log.append(f"Acquisition attempt for {company.name} rejected ({offer['label']}). -1 action point.")
            return False, f"Board rejected the offer. Try again with a higher bid.", price
    
    def save_game(self, filepath: str) -> bool:
        """Save the current game state to a file."""
        try:
            save_data = {
                'day': self.day,
                'quarter': self.quarter,
                'year': self.year,
                'corp_name': self.corp_name,
                'ceo_name': self.ceo_name,
                'cash': self.cash,
                'debt': self.debt,
                'max_debt_limit': self.max_debt_limit,
                'stock_price': self.stock_price,
                'shares_outstanding': self.shares_outstanding,
                'market_cap': self.market_cap,
                'reputation': self.reputation,
                'employee_morale': self.employee_morale,
                'ceo_health': self.ceo_health,
                'board_confidence': self.board_confidence,
                'customer_base': self.customer_base,
                'technology_level': self.technology_level,
                'market_mood': self.market_mood,
                'current_scenario': self.current_scenario,
                'scenario_duration': self.scenario_duration,
                'analyst_rating': self.analyst_rating,
                'quarterly_revenue': self.quarterly_revenue,
                'quarterly_costs': self.quarterly_costs,
                'previous_quarter_revenue': self.previous_quarter_revenue,
                'corp_card_limit': self.corp_card_limit,
                'corp_card_used': self.corp_card_used,
                'long_timer_multiplier': self.long_timer_multiplier,
                'annual_budget': self.annual_budget.copy(),
                'budget_spent': self.budget_spent.copy(),
                'departments': self.departments.copy(),
                'dept_efficiency': self.dept_efficiency.copy(),
                'permanent_efficiency_boosts': self.permanent_efficiency_boosts.copy(),
                'market_segments': self.market_segments.copy(),
                'daily_rnd_investment': self.daily_rnd_investment.copy(),
                'daily_rnd_cost': self.daily_rnd_cost,
                'rnd_points': self.rnd_points.copy(),
                'days_without_marketing': self.days_without_marketing,
                'action_points': self.action_points,
                'max_action_points': self.max_action_points,
                'technology_tracks': self.technology_tracks.copy(),
                'union_status': self.union_status,
                'union_strength': self.union_strength,
                'union_demands': self.union_demands.copy() if self.union_demands else [],
                'strike_countdown': self.strike_countdown,
                'last_union_check_day': self.last_union_check_day,
                'total_acquisition_profit': self.total_acquisition_profit,
                'log': list(self.log),
                'automation_log': list(self.automation_log),
                # Serialize employees
                'employees': [
                    {
                        'name': e.name,
                        'employee_type': e.employee_type,
                        'signing_bonus': e.signing_bonus,
                        'daily_salary': e.daily_salary,
                        'skill_level': e.skill_level,
                        'hired_day': e.hired_day,
                        'tasks_completed': e.tasks_completed,
                        'assigned_action': e.assigned_action
                    } for e in self.employees
                ],
                # Serialize executives
                'executives': [
                    {
                        'name': ex.name,
                        'role': ex.role,
                        'cost': ex.cost,
                        'personality': ex.personality,
                        'hired_day': ex.hired_day,
                        'satisfaction': ex.satisfaction
                    } for ex in self.executives
                ],
                'cfo': self.cfo.name if self.cfo else None,
                'cto': self.cto.name if self.cto else None,
                'cmo': self.cmo.name if self.cmo else None,
                # Serialize projects
                'projects': [
                    {
                        'name': p.name,
                        'initial_cost': p.initial_cost,
                        'risk': p.risk,
                        'duration_days': p.duration_days,
                        'days_remaining': p.days_remaining,
                        'type': p.type,
                        'daily_cost': p.daily_cost,
                        'potential_revenue': p.potential_revenue
                    } for p in self.projects
                ],
                # Serialize acquired companies
                'acquired_companies': [
                    {
                        'name': c.name,
                        'industry': c.industry,
                        'base_annual_profit': c.base_annual_profit,
                        'difficulty': c.difficulty,
                        'acquired': c.acquired,
                        'acquired_day': c.acquired_day
                    } for c in self.acquired_companies
                ],
                # Serialize available companies
                'available_companies': [
                    {
                        'name': c.name,
                        'industry': c.industry,
                        'base_annual_profit': c.base_annual_profit,
                        'difficulty': c.difficulty
                    } for c in self.available_companies
                ]
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(save_data, f)
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_game(self, filepath: str) -> bool:
        """Load a saved game state from a file."""
        try:
            with open(filepath, 'rb') as f:
                save_data = pickle.load(f)
            
            # Restore basic attributes
            self.day = save_data['day']
            self.quarter = save_data['quarter']
            self.year = save_data['year']
            self.corp_name = save_data['corp_name']
            self.ceo_name = save_data['ceo_name']
            self.cash = save_data['cash']
            self.debt = save_data['debt']
            self.max_debt_limit = save_data['max_debt_limit']
            self.stock_price = save_data['stock_price']
            self.shares_outstanding = save_data['shares_outstanding']
            self.market_cap = save_data['market_cap']
            self.reputation = save_data['reputation']
            self.employee_morale = save_data['employee_morale']
            self.ceo_health = save_data['ceo_health']
            self.board_confidence = save_data['board_confidence']
            self.customer_base = save_data['customer_base']
            self.technology_level = save_data['technology_level']
            self.market_mood = save_data['market_mood']
            self.current_scenario = save_data['current_scenario']
            self.scenario_duration = save_data['scenario_duration']
            self.analyst_rating = save_data['analyst_rating']
            self.quarterly_revenue = save_data['quarterly_revenue']
            self.quarterly_costs = save_data['quarterly_costs']
            self.previous_quarter_revenue = save_data['previous_quarter_revenue']
            self.corp_card_limit = save_data['corp_card_limit']
            self.corp_card_used = save_data['corp_card_used']
            self.long_timer_multiplier = save_data['long_timer_multiplier']
            self.annual_budget = save_data['annual_budget']
            self.budget_spent = save_data['budget_spent']
            self.departments = save_data['departments']
            self.dept_efficiency = save_data['dept_efficiency']
            self.permanent_efficiency_boosts = save_data['permanent_efficiency_boosts']
            self.market_segments = save_data['market_segments']
            self.daily_rnd_investment = save_data['daily_rnd_investment']
            self.daily_rnd_cost = save_data['daily_rnd_cost']
            self.rnd_points = save_data['rnd_points']
            self.days_without_marketing = save_data.get('days_without_marketing', 0)
            self.action_points = save_data['action_points']
            self.max_action_points = save_data['max_action_points']
            self.technology_tracks = save_data['technology_tracks']
            self.union_status = save_data['union_status']
            self.union_strength = save_data['union_strength']
            self.union_demands = save_data['union_demands']
            self.strike_countdown = save_data['strike_countdown']
            self.last_union_check_day = save_data['last_union_check_day']
            self.total_acquisition_profit = save_data['total_acquisition_profit']
            self.log = deque(save_data['log'], maxlen=200)
            self.automation_log = deque(save_data['automation_log'], maxlen=50)
            
            # Restore employees
            from game_core import Employee
            self.employees = []
            for emp_data in save_data['employees']:
                emp = Employee(
                    emp_data['name'],
                    emp_data['employee_type'],
                    emp_data['signing_bonus'],
                    emp_data['daily_salary'],
                    emp_data['skill_level']
                )
                emp.hired_day = emp_data['hired_day']
                emp.tasks_completed = emp_data['tasks_completed']
                emp.assigned_action = emp_data['assigned_action']
                self.employees.append(emp)
            
            # Restore executives
            from game_core import Executive
            self.executives = []
            for ex_data in save_data['executives']:
                ex = Executive(
                    ex_data['name'],
                    ex_data['role'],
                    ex_data['cost'],
                    ex_data['personality']
                )
                ex.hired_day = ex_data['hired_day']
                ex.satisfaction = ex_data['satisfaction']
                self.executives.append(ex)
                
                # Set role references
                if ex.role == 'CFO':
                    self.cfo = ex
                elif ex.role == 'CTO':
                    self.cto = ex
                elif ex.role == 'CMO':
                    self.cmo = ex
            
            # Restore projects
            from game_core import Project
            self.projects = []
            for proj_data in save_data['projects']:
                proj = Project(
                    proj_data['name'],
                    proj_data['initial_cost'],
                    proj_data['risk'],
                    proj_data['duration_days'],
                    proj_data['type']
                )
                proj.days_remaining = proj_data['days_remaining']
                proj.daily_cost = proj_data['daily_cost']
                proj.potential_revenue = proj_data['potential_revenue']
                self.projects.append(proj)
            
            # Restore companies
            from companies import Company
            self.acquired_companies = []
            for comp_data in save_data['acquired_companies']:
                comp = Company(
                    comp_data['name'],
                    comp_data['industry'],
                    comp_data['base_annual_profit'],
                    comp_data['difficulty']
                )
                comp.acquired = comp_data['acquired']
                comp.acquired_day = comp_data['acquired_day']
                self.acquired_companies.append(comp)
            
            self.available_companies = []
            for comp_data in save_data['available_companies']:
                comp = Company(
                    comp_data['name'],
                    comp_data['industry'],
                    comp_data['base_annual_profit'],
                    comp_data['difficulty']
                )
                self.available_companies.append(comp)
            
            return True
        except Exception as e:
            print(f"Error loading game: {e}")
            return False
