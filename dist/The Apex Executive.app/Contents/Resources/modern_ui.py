# modern_ui.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, Text, Scrollbar
import random
import sys
import os 
import config 
from game_core import Corporation, Project
from event_system import EmailSystem
from collections import deque # Added import for MockCorporation

TUTORIAL_STATE_FILE = "tutorial_shown.flag"
THEME_STATE_FILE = "theme_preference.txt"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme(config.COLOR_THEME)

class CEOGameApp:
    def __init__(self, master):
        self.master = master
        master.title("CEO: The Apex Executive Simulator")
        master.geometry("1500x950")
        
        # Load a reusable app icon (PNG/GIF). Place your file at assets/app_icon.png
        self.app_icon = None
        try:
            icon_path = os.path.join(os.path.dirname(__file__), "assets", "app_icon.png")
            if os.path.exists(icon_path):
                self.app_icon = tk.PhotoImage(file=icon_path)
                master.wm_iconphoto(False, self.app_icon)
        except Exception as e:
            print(f"Could not load app icon: {e}")
        
        self.game = Corporation()
        # Initialize email system after game
        self.game.email_system = EmailSystem(self.game) 
        # UI scale (1.0 = default). Settings slider will update this.
        self.ui_scale = 1.0
        
        self._setup_initial_dialog()
        self._setup_main_ui()
        
        # Start news ticker after UI is built
        self._generate_ticker_headlines()
        self._update_ticker()
        
        self._load_saved_theme()
        self._check_and_show_tutorial()
        self._show_priorities_dashboard()
        self._update_status()
        
        # Bind hotkeys
        self._setup_hotkeys()

    def _fmt_pct(self, value):
        try:
            return f"{round(value)}%"
        except Exception:
            return "0%"
    
    def _generate_ticker_headlines(self):
        """Generate rotating news headlines (mix of company-specific and general market news)."""
        corp = self.game
        
        # Company-specific headlines (30% chance)
        company_news = [
            f"🔹 {corp.corp_name} stock ${corp.stock_price:.2f} ({'+' if corp.stock_price > 25 else ''}{((corp.stock_price-25)/25*100):.1f}%)",
            f"🔹 Analysts rate {corp.corp_name} as '{corp.analyst_rating}' - Credit: {corp.credit_rating}",
            f"🔹 {corp.corp_name} holds {corp.customer_base:.0f}% market share in key segments",
            f"🔹 CEO {corp.ceo_name} leads {corp.corp_name} through {corp.current_scenario.lower()} conditions",
            f"🔹 {corp.corp_name} market cap reaches ${corp.market_cap/1e6:.0f}M with {corp.shares_outstanding/1e6:.1f}M shares",
        ]
        
        # General market headlines (70%)
        general_news = [
            "📊 Dow Jones up 0.8% on strong manufacturing data",
            "💹 Tech sector rallies amid AI breakthrough announcements",
            "🏦 Federal Reserve holds rates steady, inflation concerns ease",
            "🌍 Global supply chains normalize after recent disruptions",
            "💼 Corporate earnings beat expectations across sectors",
            "⚡ Energy prices stabilize following OPEC+ production deal",
            "🚀 Space industry sees $5B in new venture capital funding",
            "🏭 Manufacturing PMI hits 18-month high",
            "💻 Cybersecurity spending surges 40% year-over-year",
            "🌱 ESG investments reach record $8.4 trillion globally",
            "📱 Consumer tech sales exceed Q4 projections",
            "🔬 Biotech sector gains on FDA fast-track approvals",
            "🏢 Commercial real estate shows signs of recovery",
            "⚙️ Industrial automation adoption accelerates",
            "🛒 E-commerce growth maintains double-digit pace",
            "🎮 Gaming industry revenue tops $200B milestone",
            "🚗 Electric vehicle sales up 65% this quarter",
            "☁️ Cloud computing market expands to $500B",
            "📡 5G infrastructure rollout ahead of schedule",
            "💊 Healthcare costs stabilize for first time in decade"
        ]
        
        # Mix headlines: 2 company-specific, 6 general
        self.ticker_headlines = random.sample(company_news, 2) + random.sample(general_news, 6)
        random.shuffle(self.ticker_headlines)
        self.ticker_index = 0
    
    def _update_ticker(self):
        """Rotate through headlines every 4 seconds."""
        if self.ticker_headlines:
            headline = self.ticker_headlines[self.ticker_index]
            self.ticker_label.configure(text=headline)
            self.ticker_index = (self.ticker_index + 1) % len(self.ticker_headlines)
            
            # Regenerate headlines every full cycle
            if self.ticker_index == 0:
                self._generate_ticker_headlines()
        
        # Schedule next update
        self.master.after(4000, self._update_ticker)
    
    def _load_saved_theme(self):
        """Load and apply saved theme preference on startup."""
        try:
            if os.path.exists(THEME_STATE_FILE):
                with open(THEME_STATE_FILE, 'r') as f:
                    theme_name = f.read().strip()
                    if theme_name in config.COLOR_THEMES:
                        self._apply_theme_colors(theme_name)
        except Exception as e:
            print(f"Could not load theme preference: {e}")
    
    def _apply_theme_colors(self, theme_name):
        """Apply a color theme to the config module and refresh UI."""
        theme = config.COLOR_THEMES[theme_name]
        config.COLOR_TEXT = theme["TEXT"]
        config.COLOR_HEADER_BG = theme["HEADER_BG"]
        config.COLOR_ACCENT_DANGER = theme["ACCENT_DANGER"]
        config.COLOR_SUCCESS_GREEN = theme["SUCCESS_GREEN"]
        config.COLOR_ACCENT_PRIMARY = theme["ACCENT_PRIMARY"]
        config.COLOR_ACCENT_NEUTRAL = theme["ACCENT_NEUTRAL"]
        config.COLOR_PANEL_BG = theme["PANEL_BG"]
        config.COLOR_MAIN_BG = theme["MAIN_BG"]
        config.COLOR_GOLD = theme["GOLD"]
        
        # Refresh all UI elements with new colors
        self._refresh_ui_colors()
    
    def _refresh_ui_colors(self):
        """Refresh all UI elements with current theme colors."""
        # Main background
        self.master.configure(fg_color=config.COLOR_MAIN_BG)
        
        # Header
        self.header_frame.configure(fg_color=config.COLOR_HEADER_BG)
        self.title_label.configure(text_color=config.COLOR_TEXT)
        self.scenario_label.configure(text_color=config.COLOR_ACCENT_NEUTRAL)
        self.time_label.configure(text_color=config.COLOR_TEXT)
        
        # Panels
        self.status_frame.configure(fg_color=config.COLOR_PANEL_BG)
        self.action_frame.configure(fg_color=config.COLOR_PANEL_BG)
        self.log_frame.configure(fg_color=config.COLOR_PANEL_BG)
        self.project_panel.configure(fg_color=config.COLOR_PANEL_BG)
        
        # Rating label
        self.analyst_label.configure(text_color=config.COLOR_GOLD)
        
        # Refresh status display
        self._update_status()

    def _set_window_icon(self, window):
        """Apply the app icon to any popup window if available."""
        if getattr(self, "app_icon", None):
            try:
                window.wm_iconphoto(False, self.app_icon)
            except Exception:
                pass
    
    def _save_theme_preference(self, theme_name):
        """Save theme preference to file."""
        try:
            with open(THEME_STATE_FILE, 'w') as f:
                f.write(theme_name)
        except Exception as e:
            print(f"Could not save theme preference: {e}")
    
    def _create_tooltip(self, widget, text):
        """Create a simple tooltip that appears on hover."""
        tooltip = None
        
        def on_enter(event):
            nonlocal tooltip
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 25
            
            tooltip = ctk.CTkToplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{x}+{y}")
            self._set_window_icon(tooltip)
            
            label = ctk.CTkLabel(tooltip, text=text, font=config.FONT_BODY, 
                               fg_color=("#34495E"), text_color=config.COLOR_TEXT, 
                               corner_radius=6, wraplength=300, justify='left')
            label.pack(padx=8, pady=6)
        
        def on_leave(event):
            nonlocal tooltip
            if tooltip:
                tooltip.destroy()
                tooltip = None
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    def _setup_hotkeys(self):
        """Setup keyboard shortcuts for faster gameplay"""
        # Number keys 1-9 for CEO actions
        self.master.bind('1', lambda e: self._open_email_dialog())
        self.master.bind('2', lambda e: self._open_debt_equity_dialog())
        self.master.bind('3', lambda e: self._open_market_shift_dialog())
        self.master.bind('4', lambda e: self._open_budget_dialog())
        self.master.bind('5', lambda e: self._open_rnd_dialog())
        self.master.bind('6', lambda e: self._open_expense_dialog())
        self.master.bind('7', lambda e: self._open_ma_dialog())
        self.master.bind('8', lambda e: self._open_exec_team_dialog())
        self.master.bind('9', lambda e: self._open_union_dialog())
        
        # Space or Enter for Advance Day
        self.master.bind('<space>', lambda e: self._advance_day())
        self.master.bind('<Return>', lambda e: self._advance_day())
        
        # L for Leaderboard
        self.master.bind('l', lambda e: self._show_leaderboard())
        self.master.bind('L', lambda e: self._show_leaderboard())
    
    def _show_leaderboard(self):
        """Show stock price leaderboard with all competitors"""
        leaderboard_window = ctk.CTkToplevel(self.master)
        leaderboard_window.title("Stock Price Leaderboard")
        leaderboard_window.geometry("700x600")
        leaderboard_window.attributes('-topmost', True)
        leaderboard_window.grab_set()
        self._set_window_icon(leaderboard_window)
        
        # Header
        header = ctk.CTkFrame(leaderboard_window, fg_color=config.COLOR_ACCENT_PRIMARY, corner_radius=0)
        header.pack(fill='x')
        ctk.CTkLabel(header, text="📊 STOCK PRICE LEADERBOARD", 
                    font=(config.FONT_FAMILY, 22, "bold"),
                    text_color='white').pack(pady=15)
        
        # Instruction
        ctk.CTkLabel(leaderboard_window, text="🏆 Reach 1st place to WIN THE GAME!", 
                    font=config.FONT_HEADER, text_color=config.COLOR_GOLD).pack(pady=10)
        
        # Create leaderboard list (all companies sorted by stock price)
        companies = [(self.game.corp_name, self.game.stock_price, "YOU", config.COLOR_GOLD)]
        for comp in self.game.competitors:
            companies.append((comp.name, comp.stock_price, comp.strategy.upper(), config.COLOR_ACCENT_NEUTRAL))
        
        # Sort by stock price (highest first)
        companies.sort(key=lambda x: x[1], reverse=True)
        
        # Display rankings
        scroll_frame = ctk.CTkScrollableFrame(leaderboard_window, fg_color=config.COLOR_PANEL_BG)
        scroll_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        player_rank = 0
        for i, (name, price, tag, color) in enumerate(companies, 1):
            rank_frame = ctk.CTkFrame(scroll_frame, fg_color=("#2E4053" if tag != "YOU" else "#1C5739"), corner_radius=8)
            rank_frame.pack(fill='x', pady=5, padx=10)
            
            if tag == "YOU":
                player_rank = i
            
            # Rank emoji
            rank_emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            
            # Row layout
            row = ctk.CTkFrame(rank_frame, fg_color="transparent")
            row.pack(fill='x', padx=15, pady=12)
            
            ctk.CTkLabel(row, text=rank_emoji, font=(config.FONT_FAMILY, 18, "bold"),
                        text_color='white', width=50).pack(side=ctk.LEFT)
            
            ctk.CTkLabel(row, text=name, font=config.FONT_HEADER, 
                        text_color=color, anchor='w', width=300).pack(side=ctk.LEFT, padx=(10, 0))
            
            ctk.CTkLabel(row, text=f"${price:.2f}", font=(config.FONT_FAMILY, 16, "bold"),
                        text_color=config.COLOR_SUCCESS_GREEN, anchor='e').pack(side=ctk.RIGHT, padx=(0, 10))
            
            ctk.CTkLabel(row, text=tag, font=(config.FONT_FAMILY, 10),
                        text_color=color, anchor='e', width=100).pack(side=ctk.RIGHT)
        
        # Status message
        status_frame = ctk.CTkFrame(leaderboard_window, fg_color=("#2E4053"), corner_radius=8)
        status_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        if player_rank == 1:
            status_msg = "🎉 YOU'RE IN 1ST PLACE! You've dominated the market!"
            status_color = config.COLOR_SUCCESS_GREEN
        elif player_rank <= 3:
            status_msg = f"💪 You're in {player_rank}{'nd' if player_rank == 2 else 'rd'} place - Keep pushing to reach #1!"
            status_color = config.COLOR_GOLD
        else:
            gap = companies[0][1] - self.game.stock_price
            status_msg = f"📈 You're in {player_rank}th place - ${gap:.2f} behind the leader"
            status_color = config.COLOR_ACCENT_DANGER
        
        ctk.CTkLabel(status_frame, text=status_msg, font=config.FONT_BODY,
                    text_color=status_color).pack(pady=12, padx=15)
        
        # Close button
        ctk.CTkButton(leaderboard_window, text="Close (Press L anytime)",
                     command=leaderboard_window.destroy,
                     fg_color=config.COLOR_ACCENT_NEUTRAL,
                     font=config.FONT_HEADER, height=40).pack(pady=(0, 20))

    def _prompt_dev_password(self) -> bool:
        """Show password dialog for developer mode. Returns True if correct password entered."""
        password_window = ctk.CTkToplevel(self.master)
        password_window.title("Developer Mode")
        password_window.geometry("400x200")
        password_window.attributes('-topmost', True)
        password_window.grab_set()
        password_window.resizable(False, False)
        self._set_window_icon(password_window)
        
        ctk.CTkLabel(password_window, text="🔐 Developer Mode", font=config.FONT_TITLE, text_color=config.COLOR_GOLD).pack(pady=15)
        ctk.CTkLabel(password_window, text="Enter password:", font=config.FONT_HEADER).pack(pady=10)
        
        password_entry = ctk.CTkEntry(password_window, width=250, font=config.FONT_BODY, show="•")
        password_entry.pack(pady=5)
        
        result = {"authenticated": False}
        
        def check_password():
            if password_entry.get() == "wavyarms44":
                result["authenticated"] = True
                password_window.destroy()
            else:
                messagebox.showerror("Access Denied", "Incorrect password.")
                password_entry.delete(0, ctk.END)
        
        ctk.CTkButton(password_window, text="Unlock", command=check_password,
                     fg_color=config.COLOR_SUCCESS_GREEN, font=config.FONT_HEADER,
                     width=200, height=40).pack(pady=15)
        
        password_window.wait_window()
        return result["authenticated"]
    
    def _enable_developer_mode(self):
        """Activate developer mode with unlimited resources."""
        # Grant unlimited resources
        self.game.cash = 999999999999  # Nearly unlimited cash
        self.game.debt = 0
        self.game.stock_price = 1000.0
        self.game.reputation = 100
        self.game.employee_morale = 100
        self.game.ceo_health = 100
        self.game.board_confidence = 100
        self.game.technology_level = 100
        self.game.customer_base = 100
        
        # Max out efficiencies
        for dept in self.game.dept_efficiency.keys():
            self.game.dept_efficiency[dept] = 100
        
        # Unlimited budgets
        for dept in self.game.annual_budget.keys():
            self.game.annual_budget[dept] = 999999999999
        
        self.game.corp_card_limit = 999999999999
        self.game.action_points = 99
        self.game.max_action_points = 99
        
        self.game.log.append("*** DEVELOPER MODE ENABLED: Unlimited resources activated ***")
        messagebox.showinfo("Developer Mode", "✓ Developer Mode activated! Unlimited resources granted.")
        self._update_status()
    
    def _save_game_dialog(self):
        """Open save game dialog."""
        from tkinter import filedialog
        
        default_name = f"{self.game.corp_name.replace(' ', '_')}_Day{self.game.day}.sav"
        filepath = filedialog.asksaveasfilename(
            title="Save Game",
            defaultextension=".sav",
            filetypes=[("Save Files", "*.sav"), ("All Files", "*.*")],
            initialfile=default_name
        )
        
        if filepath:
            success = self.game.save_game(filepath)
            if success:
                messagebox.showinfo("Game Saved", f"Game successfully saved to:\n{filepath}")
            else:
                messagebox.showerror("Save Failed", "Failed to save game. Check console for errors.")
    
    def _load_game_dialog(self):
        """Open load game dialog."""
        from tkinter import filedialog
        
        # Confirm before loading (will replace current game)
        confirm = messagebox.askyesno(
            "Load Game",
            "Loading a save will replace your current game.\n\nContinue?"
        )
        
        if not confirm:
            return
        
        filepath = filedialog.askopenfilename(
            title="Load Game",
            filetypes=[("Save Files", "*.sav"), ("All Files", "*.*")]
        )
        
        if filepath:
            success = self.game.load_game(filepath)
            if success:
                # Reinitialize email system
                self.game.email_system = EmailSystem(self.game)
                self._update_status()
                messagebox.showinfo("Game Loaded", f"Game successfully loaded from:\n{filepath}")
            else:
                messagebox.showerror("Load Failed", "Failed to load game. File may be corrupted or incompatible.")

    def _show_priorities_dashboard(self):
        """Show startup dashboard with top priorities and alerts."""
        # Small delay to ensure UI is ready
        self.master.after(1000, self._show_priorities_window)
    
    def _show_priorities_window(self):
        """Display the priorities/alerts dashboard."""
        dashboard = ctk.CTkToplevel(self.master)
        dashboard.title("📊 Daily Priorities & Alerts")
        dashboard.geometry("600x500")
        dashboard.attributes('-topmost', True)
        dashboard.grab_set()
        self._set_window_icon(dashboard)
        
        # Header
        header_frame = ctk.CTkFrame(dashboard, fg_color=config.COLOR_HEADER_BG, corner_radius=0)
        header_frame.pack(fill=ctk.X)
        ctk.CTkLabel(header_frame, text=f"📊 {self.game.corp_name} - Daily Priorities", 
                     font=config.FONT_TITLE, text_color=config.COLOR_ACCENT_PRIMARY).pack(pady=15, padx=20)
        
        # Scrollable content area
        scroll_frame = ctk.CTkScrollableFrame(dashboard, fg_color=config.COLOR_PANEL_BG, corner_radius=0)
        scroll_frame.pack(fill=ctk.BOTH, expand=True, padx=0, pady=0)
        
        # Get alerts
        alerts = self._generate_priority_alerts()
        
        if alerts:
            for i, alert in enumerate(alerts):
                icon, title, description, color = alert
                
                alert_frame = ctk.CTkFrame(scroll_frame, fg_color=color, corner_radius=10)
                alert_frame.pack(fill=ctk.X, padx=15, pady=10)
                
                content_frame = ctk.CTkFrame(alert_frame, fg_color="transparent")
                content_frame.pack(fill=ctk.X, padx=15, pady=12)
                
                title_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
                title_frame.pack(fill=ctk.X, anchor='w')
                
                ctk.CTkLabel(title_frame, text=f"{icon} {title}", font=(config.FONT_FAMILY, 13, "bold"), 
                            text_color="white").pack(side=ctk.LEFT)
                
                ctk.CTkLabel(content_frame, text=description, font=config.FONT_BODY, 
                            text_color="white", justify='left', wraplength=500).pack(fill=ctk.X, anchor='w', pady=(8, 0))
        else:
            ctk.CTkLabel(scroll_frame, text="✅ No critical alerts - Focus on your strategy!", 
                        font=config.FONT_HEADER, text_color=config.COLOR_SUCCESS_GREEN).pack(pady=30)
        
        # Tips section
        tips_frame = ctk.CTkFrame(scroll_frame, fg_color=("#34495E"), corner_radius=10)
        tips_frame.pack(fill=ctk.X, padx=15, pady=15)
        
        ctk.CTkLabel(tips_frame, text="💡 Tips for Today", font=(config.FONT_FAMILY, 12, "bold"), 
                    text_color=config.COLOR_GOLD).pack(anchor='w', padx=15, pady=(12, 8))
        
        tips = [
            "• You have 3 action points today",
            "• Check your budget before major actions",
            "• Handle urgent emails first",
            "• Acquisitions take ~50 days to break even",
            "• Watch your credit rating"
        ]
        
        for tip in tips:
            ctk.CTkLabel(tips_frame, text=tip, font=config.FONT_BODY, 
                        text_color=config.COLOR_TEXT, justify='left').pack(anchor='w', padx=20, pady=2)
        
        ctk.CTkLabel(tips_frame, text="", font=config.FONT_BODY).pack(pady=6)
        
        # Close button
        button_frame = ctk.CTkFrame(dashboard, fg_color="transparent")
        button_frame.pack(fill=ctk.X, padx=15, pady=15)
        
        ctk.CTkButton(button_frame, text="Got it! Start Playing →", command=dashboard.destroy,
                     fg_color=config.COLOR_SUCCESS_GREEN, hover_color=("#4CAF50"),
                     font=config.FONT_HEADER, width=400, height=40).pack()
    
    def _generate_priority_alerts(self):
        """Generate list of priority alerts based on game state."""
        alerts = []
        
        # Cash warning
        if self.game.cash < 5000000:
            alerts.append(
                ("💰", "Low Cash Reserves", 
                 f"You only have ${self.game.cash:,.0f}. Be careful with expenses!", 
                 ("#E74C3C")  # Red
                )
            )
        
        # Debt warning
        if self.game.debt > self.game.cash * 2:
            alerts.append(
                ("📈", "High Debt Level",
                 f"Debt (${self.game.debt:,.0f}) is over 2x cash. Consider paying down debt.",
                 ("#E67E22")  # Orange
                )
            )
        
        # Credit rating warning
        if self.game.credit_rating and "B" in self.game.credit_rating:
            alerts.append(
                ("⚠️", "Poor Credit Rating",
                 f"Your rating is {self.game.credit_rating} - Interest rates are high. Improve finances!",
                 ("#E74C3C")  # Red
                )
            )
        
        # Morale warning
        if self.game.employee_morale < 50:
            alerts.append(
                ("😞", "Low Employee Morale",
                 f"Morale at {self.game.employee_morale:.0f}% - Risk of unionization if it drops further!",
                 ("#E67E22")  # Orange
                )
            )
        
        # CEO health warning
        if self.game.ceo_health < 40:
            alerts.append(
                ("🏥", "CEO Health Declining",
                 f"Your health is at {self.game.ceo_health:.0f}% - Take time to recover!",
                 ("#E74C3C")  # Red
                )
            )
        
        # Board confidence warning
        if self.game.board_confidence < 50:
            alerts.append(
                ("🎯", "Board Losing Confidence",
                 f"Confidence at {self.game.board_confidence:.0f}% - Deliver results or face consequences!",
                 ("#E67E22")  # Orange
                )
            )
        
        # Stock price warning
        if self.game.stock_price < 10:
            alerts.append(
                ("📉", "Stock Price Tanking",
                 f"Stock at ${self.game.stock_price:.2f} - Market confidence is low. Boost performance!",
                 ("#E74C3C")  # Red
                )
            )
        
        # Budget warnings
        low_budget_depts = []
        for dept, budget in self.game.annual_budget.items():
            if budget < 1000000:  # Less than $1M
                low_budget_depts.append(dept.replace("_", " ").title())
        
        if low_budget_depts:
            alerts.append(
                ("💼", "Low Department Budgets",
                 f"{', '.join(low_budget_depts)} have low budgets - Reallocate funds!",
                 ("#F39C12")  # Yellow
                )
            )
        
        # Positive alerts for good performance
        if self.game.cash > 50000000 and self.game.debt < self.game.cash:
            alerts.append(
                ("🟢", "Strong Financial Position",
                 f"Great cash position! You have flexibility for strategic moves.",
                 ("#27AE60")  # Green
                )
            )
        
        return alerts

    def _setup_initial_dialog(self):
        # Create custom dialog with developer mode button
        dialog = ctk.CTkToplevel(self.master)
        dialog.title("Company Setup")
        dialog.geometry("500x350")
        dialog.attributes('-topmost', True)
        dialog.grab_set()
        self._set_window_icon(dialog)
        
        ctk.CTkLabel(dialog, text="Welcome to CEO Simulator", font=config.FONT_TITLE, text_color=config.COLOR_ACCENT_PRIMARY).pack(pady=20)
        
        # Corporation name input
        ctk.CTkLabel(dialog, text="Corporation Name:", font=config.FONT_HEADER).pack(pady=(10, 5))
        corp_entry = ctk.CTkEntry(dialog, width=300, font=config.FONT_BODY, placeholder_text="Enter your corporation name")
        corp_entry.pack(pady=5)
        
        # CEO name input
        ctk.CTkLabel(dialog, text="CEO Name:", font=config.FONT_HEADER).pack(pady=(10, 5))
        ceo_entry = ctk.CTkEntry(dialog, width=300, font=config.FONT_BODY, placeholder_text="Enter your CEO name")
        ceo_entry.pack(pady=5)
        
        # Start button
        def start_game():
            corp_name = corp_entry.get().strip()
            ceo_name = ceo_entry.get().strip()
            
            if not corp_name or not ceo_name:
                self.game.set_identity("Global Dynamics", "Anonymous CEO", self.game.email_system)
            else:
                self.game.set_identity(corp_name, ceo_name, self.game.email_system)
            dialog.destroy()
        
        # Developer mode button
        def enable_dev_mode():
            # Prompt for password
            if self._prompt_dev_password():
                self.game.set_identity("DevCorp", "Debug CEO", self.game.email_system)
                self._enable_developer_mode()
                dialog.destroy()
        
        ctk.CTkButton(dialog, text="Start Game", command=start_game, 
                      fg_color=config.COLOR_SUCCESS_GREEN, hover_color=("#4CAF50"),
                      font=config.FONT_HEADER, width=200, height=40).pack(pady=20)
        
        # Developer mode button (bottom right corner)
        dev_btn = ctk.CTkButton(dialog, text="🛠️ Developer Mode", command=enable_dev_mode,
                               fg_color=config.COLOR_GOLD, hover_color=("#D4AF37"),
                               font=config.FONT_BODY, width=140, height=30)
        dev_btn.place(relx=1.0, rely=1.0, x=-10, y=-10, anchor='se')
        
        dialog.wait_window()

    def _check_and_show_tutorial(self):
        if not os.path.exists(TUTORIAL_STATE_FILE):
            self._show_tutorial_popup()
            try:
                with open(TUTORIAL_STATE_FILE, 'w') as f:
                    f.write("Tutorial has been shown.")
            except Exception as e:
                print(f"Warning: Could not create tutorial state file: {e}")

    def _show_tutorial_popup(self):
        """Interactive step-by-step tutorial with UI element highlighting."""
        self.tutorial_step = 0
        self.tutorial_overlay = None
        
        tutorial_window = ctk.CTkToplevel(self.master)
        tutorial_window.title("Welcome to CEO Simulator")
        tutorial_window.geometry("700x500")
        tutorial_window.resizable(False, False)
        tutorial_window.attributes('-topmost', True)
        tutorial_window.grab_set()
        self._set_window_icon(tutorial_window)

        ctk.CTkLabel(tutorial_window, text="🎓 Interactive Tutorial", 
                     font=config.FONT_TITLE, text_color=config.COLOR_ACCENT_PRIMARY).pack(pady=15)
        
        # Step content frame
        content_frame = ctk.CTkFrame(tutorial_window, fg_color=config.COLOR_PANEL_BG, corner_radius=12)
        content_frame.pack(fill='both', expand=True, padx=20, pady=(0, 15))
        
        # Tutorial steps with actual UI element references
        tutorial_steps = [
            {
                "title": "Welcome to The Apex Executive!",
                "text": "You're the new CEO. Your job: grow the company, keep the board happy, and survive.\n\n✅ Win by maintaining positive cash, high morale, and hitting growth targets.\n\n❌ Lose if debt spirals, board confidence hits zero, or your health collapses.",
                "highlight": None,
                "pointer": None
            },
            {
                "title": "Step 1: Check Your Status",
                "text": "Look at the TOP LEFT panel. This shows your key metrics:\n\n• Cash & Debt\n• Stock Price & Market Cap\n• Reputation, Morale, CEO Health\n• Board Confidence\n\nKeep these healthy to avoid game over.",
                "highlight": "status_panel",
                "pointer": "←"
            },
            {
                "title": "Step 2: Action Points (Top Center)",
                "text": "You have 3 ACTION POINTS per day. Most strategic decisions cost 1 point.\n\nSee the counter at the top? That's how many moves you have left today.\n\nWhen you hit 0, you'll need to advance the day to get more.",
                "highlight": "action_points_label",
                "pointer": "↑"
            },
            {
                "title": "Step 3: Annual Budgets (Right Panel)",
                "text": "Each department has an ANNUAL BUDGET:\n• R&D, Marketing, Operations, HR\n\nActions draw from these budgets AND your cash. Empty budget = action fails.\n\n🚨 Red = nearly empty\n⚠️ Orange = getting low\n✅ Green = healthy",
                "highlight": "budget_frame",
                "pointer": "→"
            },
            {
                "title": "Step 4: Daily Actions (Center)",
                "text": "These are your CEO powers. Each costs 1 action point:\n\n📧 Executive Inbox - Handle emails (FREE)\n🔬 R&D Lab - Invest in tech\n💰 Budgets - Reallocate funding\n💳 Debt/Equity - Borrow or raise money\n🏢 Acquisitions & HR - Acquire companies and hire employees\n📊 Market Shift - Target B2B or Consumer\n💼 Corporate Card - One-time expenses\n👔 Executive Team - Hire C-suite (CFO/CTO/CMO)\n🪧 Union Relations - Negotiate with unions",
                "highlight": "action_frame",
                "pointer": "↓"
            },
            {
                "title": "Step 5: The Daily Loop",
                "text": "Each day follows this pattern:\n\n1. Click 'ADVANCE DAY >>' (top right)\n2. Revenue & costs process automatically\n3. New emails/events appear\n4. Spend your 3 action points wisely\n5. Check the log (bottom) for what happened\n6. Repeat!\n\nEvery 90 days = Quarterly Earnings Call (answer 3 questions to affect stock price).",
                "highlight": "btn_advance_day",
                "pointer": "→"
            },
            {
                "title": "Step 6: Acquisitions & Growth",
                "text": "ACQUIRE COMPANIES (Acquisitions & HR):\n• Pay 3x, 5x, or 8x annual profit\n• Higher offers = higher success probability\n• Acquired companies pay 2% daily profit\n• Costs 1 action point per attempt\n• ~50 days to break even\n\nLong-term wealth building strategy!",
                "highlight": None,
                "pointer": None
            },
            {
                "title": "Step 7: Employees & Executives",
                "text": "EMPLOYEES (HR):\n• Pay signing bonus + daily salary\n• Automate routine tasks\n• Boost department efficiency\n• Costs 1 action point to hire\n\nEXECUTIVES (Executive Team):\n• CFO: Cash bonuses, debt cost reduction\n• CTO: Tech boosts, R&D efficiency\n• CMO: Customer growth, marketing power\n• Costs 1 action point to hire\n\nHire strategically!",
                "highlight": None,
                "pointer": None
            },
            {
                "title": "Step 8: Credit Rating & Debt",
                "text": "CREDIT RATING (displayed on left panel):\n• AAA/AA/A = Investment Grade (3-5% interest)\n• BBB/BB = Moderate (6-8% interest)\n• B/CCC = Junk (11-15% interest)\n\nRating based on debt-to-equity ratio:\n• High debt = Rating downgrades\n• Downgrades hurt stock price & increase interest\n• Upgrades boost stock price\n\nManage debt carefully!",
                "highlight": None,
                "pointer": None
            },
            {
                "title": "Step 9: Victory Conditions",
                "text": "Three ways to WIN:\n\n🏆 IPO Success - Market cap $500M+, stock $50+\n🏆 Market Dominance - Customer base 80%+, $250M quarterly revenue\n🏆 Acquisition Exit - Market cap $750M+, reputation 80+, tech 75+\n\nPick your path and execute!",
                "highlight": None,
                "pointer": None
            },
            {
                "title": "Step 10: Union Negotiations",
                "text": "If employee morale drops below 40% with 5+ employees, they may UNIONIZE:\n\n⚠️ Forming - Early organizing\n🪧 Active - Demands presented\n🛑 Strike - If you ignore demands\n\nKeep morale high to prevent unions, or negotiate fairly to avoid strikes.",
                "highlight": None,
                "pointer": None
            },
            {
                "title": "Step 11: Pro Tips",
                "text": "✓ Handle URGENT emails (red) first\n✓ Watch credit rating - high debt = expensive interest\n✓ Major decisions (acquisitions, execs) cost action points\n✓ Acquisitions are long-term investments (2% daily = 50 day payback)\n✓ Balance cash flow vs. growth investments\n✓ Hover over action buttons for tooltips\n✓ Check first-day checklist (left panel)\n✓ Use Developer Mode (startup) for testing\n\nReady to lead?",
                "highlight": None,
                "pointer": None
            }
        ]
        
        # Content area
        step_title = ctk.CTkLabel(content_frame, text="", font=config.FONT_TITLE, text_color=config.COLOR_GOLD, wraplength=640)
        step_title.pack(pady=(20, 10), padx=20)
        
        step_text = ctk.CTkLabel(content_frame, text="", font=config.FONT_BODY, text_color=config.COLOR_TEXT, 
                                wraplength=640, justify='left')
        step_text.pack(pady=10, padx=20, fill='both', expand=True)
        
        # Progress indicator
        progress_label = ctk.CTkLabel(content_frame, text="", font=config.FONT_BODY, text_color=config.COLOR_ACCENT_NEUTRAL)
        progress_label.pack(pady=(0, 15))
        
        # Navigation buttons
        btn_frame = ctk.CTkFrame(tutorial_window, fg_color="transparent")
        btn_frame.pack(pady=(0, 15))
        
        def show_step(step_num):
            self.tutorial_step = step_num
            step = tutorial_steps[step_num]
            
            step_title.configure(text=step["title"])
            step_text.configure(text=step["text"])
            progress_label.configure(text=f"Step {step_num + 1} of {len(tutorial_steps)}")
            
            # Highlight UI element if specified
            if step.get("highlight"):
                try:
                    widget = getattr(self, step["highlight"], None)
                    if widget:
                        # Flash the widget with a colored border effect
                        original_fg = widget.cget("fg_color")
                        widget.configure(fg_color=config.COLOR_GOLD)
                        tutorial_window.after(300, lambda: widget.configure(fg_color=config.COLOR_ACCENT_PRIMARY))
                        tutorial_window.after(600, lambda: widget.configure(fg_color=config.COLOR_GOLD))
                        tutorial_window.after(900, lambda: widget.configure(fg_color=original_fg))
                except:
                    pass
            
            # Update button states
            btn_prev.configure(state=ctk.NORMAL if step_num > 0 else ctk.DISABLED)
            if step_num < len(tutorial_steps) - 1:
                btn_next.configure(text="Next →")
            else:
                btn_next.configure(text="Start Playing!")
        
        def next_step():
            if self.tutorial_step < len(tutorial_steps) - 1:
                show_step(self.tutorial_step + 1)
            else:
                tutorial_window.destroy()
        
        def prev_step():
            if self.tutorial_step > 0:
                show_step(self.tutorial_step - 1)
        
        btn_prev = ctk.CTkButton(btn_frame, text="← Previous", command=prev_step,
                                fg_color=config.COLOR_ACCENT_NEUTRAL, width=140, height=40,
                                font=config.FONT_HEADER)
        btn_prev.pack(side=ctk.LEFT, padx=10)
        
        btn_next = ctk.CTkButton(btn_frame, text="Next →", command=next_step,
                                fg_color=config.COLOR_SUCCESS_GREEN, hover_color=("#4CAF50"),
                                width=180, height=40, font=config.FONT_HEADER)
        btn_next.pack(side=ctk.LEFT, padx=10)
        
        btn_skip = ctk.CTkButton(btn_frame, text="Skip Tutorial", command=tutorial_window.destroy,
                                fg_color=config.COLOR_ACCENT_DANGER, width=140, height=40,
                                font=config.FONT_BODY)
        btn_skip.pack(side=ctk.LEFT, padx=10)
        
        # Start with first step
        show_step(0)

    def _apply_ui_scale(self, scale: float):
        """Apply comprehensive UI scaling to all fonts, button sizes, padding, and spacing."""
        try:
            self.ui_scale = scale
            
            # Compute scaled fonts
            title_font = (config.FONT_FAMILY, int(22 * scale), 'bold')
            header_font = (config.FONT_FAMILY, int(16 * scale), 'bold')
            body_font = (config.FONT_FAMILY, int(12 * scale))
            stat_value_font = (config.FONT_FAMILY, int(14 * scale), 'bold')
            mono_font = ('Courier New', int(11 * scale))
            
            # Scaled padding and sizing
            scaled_padx = int(20 * scale)
            scaled_pady = int(10 * scale)
            scaled_button_height = int(48 * scale)
            scaled_button_width = int(220 * scale)
            
            # Header widgets
            self.title_label.configure(font=title_font)
            self.scenario_label.configure(font=header_font)
            self.time_label.configure(font=header_font)
            self.analyst_label.configure(font=header_font)
            self.btn_settings.configure(font=header_font)
            
            # Action frame label and buttons
            try:
                for widget in self.action_frame.winfo_children():
                    if isinstance(widget, ctk.CTkLabel):
                        widget.configure(font=title_font)
                    elif isinstance(widget, ctk.CTkButton):
                        widget.configure(font=header_font, height=scaled_button_height, width=scaled_button_width)
                    elif isinstance(widget, ctk.CTkFrame):
                        # Button frame children (individual buttons)
                        for btn in widget.winfo_children():
                            if isinstance(btn, ctk.CTkButton):
                                btn.configure(font=header_font, height=int(48 * scale), width=int(210 * scale))
            except Exception:
                pass
            
            # Main action buttons
            try:
                self.btn_email.configure(font=header_font, height=scaled_button_height, width=scaled_button_width)
                self.btn_rnd.configure(font=header_font, height=scaled_button_height, width=scaled_button_width)
                self.btn_budget.configure(font=header_font, height=scaled_button_height, width=scaled_button_width)
                self.btn_debt.configure(font=header_font, height=scaled_button_height, width=scaled_button_width)
                self.btn_hr.configure(font=header_font, height=scaled_button_height, width=scaled_button_width)
                self.btn_market.configure(font=header_font, height=scaled_button_height, width=scaled_button_width)
                self.btn_card.configure(font=header_font, height=scaled_button_height, width=scaled_button_width)
            except Exception:
                pass
            
            # Advance button
            self.advance_button.configure(font=title_font, height=int(50 * scale), width=int(250 * scale))
            
            # Log text and project list
            try:
                self.log_text.configure(font=mono_font)
            except Exception:
                pass
            
            # Status frame labels
            try:
                for label_key, label_widget in self.status_labels.items():
                    label_widget.configure(font=stat_value_font)
            except Exception:
                pass
            
            # Section headers in status frame
            try:
                for widget in self.status_frame.winfo_children():
                    if isinstance(widget, ctk.CTkLabel):
                        # Check if it's a section header (short text like "FINANCIALS")
                        text = widget.cget('text')
                        if text and len(text) < 30 and text.isupper():
                            widget.configure(font=header_font)
                    elif isinstance(widget, ctk.CTkFrame):
                        # Frames containing metric rows
                        for child in widget.winfo_children():
                            if isinstance(child, ctk.CTkLabel):
                                child.configure(font=body_font)
            except Exception:
                pass
            
            # Project list header
            try:
                self.project_list_header.configure(font=header_font)
            except Exception:
                pass
            
            # Trigger full refresh to redraw project list and status
            self._update_status()
        except Exception as e:
            print(f"Error in _apply_ui_scale: {e}")


    def _setup_main_ui(self):
        self.master.configure(fg_color=config.COLOR_MAIN_BG)
        
        # ===== TOP HEADER BAR =====
        self.header_frame = ctk.CTkFrame(self.master, fg_color=config.COLOR_HEADER_BG, corner_radius=0, height=60)
        self.header_frame.pack(side=ctk.TOP, fill=ctk.X, pady=(0, 10))
        self.header_frame.pack_propagate(False)
        
        # Left side: Company info
        left_header = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        left_header.pack(side=ctk.LEFT, fill=ctk.X, expand=True, padx=20, pady=10)
        
        self.title_label = ctk.CTkLabel(left_header, text=f"{self.game.corp_name} - {self.game.ceo_name}", 
                                       font=config.FONT_TITLE, text_color=config.COLOR_TEXT)
        self.title_label.pack(side=ctk.LEFT)
        
        self.scenario_label = ctk.CTkLabel(left_header, text="MARKET: STABLE", font=config.FONT_HEADER, 
                                          text_color=config.COLOR_ACCENT_NEUTRAL)
        self.scenario_label.pack(side=ctk.LEFT, padx=(40, 0))
        
        # Right side: Settings and info buttons
        right_header = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        right_header.pack(side=ctk.RIGHT, padx=20, pady=10)
        
        self.btn_settings = ctk.CTkButton(right_header, text="⚙️ Settings", command=self._open_settings_dialog, 
                          fg_color=config.COLOR_ACCENT_NEUTRAL, hover_color=("#555555"), 
                          text_color=config.COLOR_TEXT, font=config.FONT_BODY, width=120)
        self.btn_settings.pack(side=ctk.LEFT, padx=5)
        

        self.btn_load = ctk.CTkButton(self.header_frame, text="📂 Load", command=self._load_game_dialog, 
                          fg_color=config.COLOR_ACCENT_PRIMARY, hover_color=("#4169E1"), 
                          text_color=config.COLOR_TEXT, font=config.FONT_HEADER)
        self.btn_load.pack(side=ctk.RIGHT, padx=10, pady=10)
        
        self.btn_save = ctk.CTkButton(self.header_frame, text="💾 Save", command=self._save_game_dialog, 
                          fg_color=config.COLOR_SUCCESS_GREEN, hover_color=("#228B22"), 
                          text_color=config.COLOR_TEXT, font=config.FONT_HEADER)
        self.btn_save.pack(side=ctk.RIGHT, padx=10, pady=10)

        self.time_label = ctk.CTkLabel(self.header_frame, text="", font=config.FONT_HEADER, text_color=config.COLOR_TEXT)
        self.time_label.pack(side=ctk.RIGHT, padx=20, pady=10)

        # Main Layout Frame
        self.main_frame = ctk.CTkFrame(self.master, fg_color="transparent")
        self.main_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

        # Left Panel (Status/Metrics)
        self.status_frame = ctk.CTkFrame(self.main_frame, fg_color=config.COLOR_PANEL_BG, corner_radius=10)
        self.status_frame.pack(side=ctk.LEFT, fill=ctk.Y, padx=(0, 10))
        
        # Right Panel (Actions and Log)
        self.right_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.right_frame.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True)
        
        # 1. Top Row Container (Action Panel + Budgets/Action Points)
        self.top_row_container = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.top_row_container.pack(side=ctk.TOP, fill=ctk.X, pady=(0, 10))
        
        # 1a. Action Panel Content (LEFT side of top row)
        self.action_frame = ctk.CTkFrame(self.top_row_container, fg_color=config.COLOR_PANEL_BG, corner_radius=10)
        self.action_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=(0, 10))
        ctk.CTkLabel(self.action_frame, text="DAILY CEO ACTIONS", font=config.FONT_TITLE, text_color=config.COLOR_ACCENT_PRIMARY).pack(pady=10)
        
        btn_config = {'fg_color': config.COLOR_ACCENT_PRIMARY, 'hover_color': ("#4A90E2"), 'text_color': config.COLOR_PANEL_BG, 'font': config.FONT_HEADER, 'width': 220, 'height': 48, 'corner_radius': 12}
        
        # Button Group 1
        button_frame_1 = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        button_frame_1.pack(fill=ctk.X, pady=5, padx=10)
        self.btn_email = ctk.CTkButton(button_frame_1, text="1. 📧 Executive Inbox", command=self._open_email_dialog, **btn_config); self.btn_email.pack(side=ctk.LEFT, padx=8)
        self._create_tooltip(self.btn_email, "Handle incoming emails. No action point cost. May require cash/budget.")
        
        self.btn_rnd = ctk.CTkButton(button_frame_1, text="2. R&D Lab & Projects", command=self._open_rnd_dialog, **btn_config); self.btn_rnd.pack(side=ctk.LEFT, padx=8)
        self._create_tooltip(self.btn_rnd, "Invest in R&D tracks or start strategic projects. Costs 1 action point.")
        
        self.btn_budget = ctk.CTkButton(button_frame_1, text="3. Adjust Budgets", command=self._open_budget_dialog, **btn_config); self.btn_budget.pack(side=ctk.LEFT, padx=8)
        self._create_tooltip(self.btn_budget, "Reallocate annual department budgets. Costs 1 action point.")
        
        # Button Group 2
        button_frame_2 = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        button_frame_2.pack(fill=ctk.X, pady=5, padx=10)
        self.btn_debt = ctk.CTkButton(button_frame_2, text="4. Manage Debt/Equity", command=self._open_debt_equity_dialog, **btn_config); self.btn_debt.pack(side=ctk.LEFT, padx=8)
        self._create_tooltip(self.btn_debt, "Borrow or repay debt, issue/repurchase shares. Costs 1 action point + cash.")
        
        self.btn_hr = ctk.CTkButton(button_frame_2, text="5. Acquisitions & HR", command=self._open_hr_dialog, **btn_config); self.btn_hr.pack(side=ctk.LEFT, padx=8)
        self._create_tooltip(self.btn_hr, "Acquire companies and hire employees. Costs 1 action point + budget + cash.")
        
        self.btn_market = ctk.CTkButton(button_frame_2, text="6. Shift Market Focus", command=self._open_market_shift_dialog, **btn_config); self.btn_market.pack(side=ctk.LEFT, padx=8)
        self._create_tooltip(self.btn_market, "Shift focus to B2B or Consumer. Costs 1 action point + campaign budget.")

        # Button Group 3
        button_frame_3 = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        button_frame_3.pack(fill=ctk.X, pady=5, padx=10)
        self.btn_card = ctk.CTkButton(button_frame_3, text="7. Corporate Card", command=self._open_expense_dialog, **btn_config); self.btn_card.pack(side=ctk.LEFT, padx=8)
        self._create_tooltip(self.btn_card, "Charge expenses to corp card (limit $10M/day). Costs 1 action point.")
        
        self.btn_exec_team = ctk.CTkButton(button_frame_3, text="8. 👔 Executive Team", command=self._open_exec_team_dialog, **btn_config); self.btn_exec_team.pack(side=ctk.LEFT, padx=8)
        self._create_tooltip(self.btn_exec_team, "Hire C-suite officers (CFO/CTO/CMO) for strategic bonuses. Costs 1 action point + hiring fee.")
        
        self.btn_union = ctk.CTkButton(button_frame_3, text="9. 🪧 Union Relations", command=self._open_union_dialog, **btn_config); self.btn_union.pack(side=ctk.LEFT, padx=8)
        self._create_tooltip(self.btn_union, "Negotiate with unions if employees organize. No action point cost.")

        # Employee Task Assignment (does not cost an action)
        ctk.CTkButton(self.action_frame, text="Assign Employee Tasks", command=self._open_employee_tasks_dialog,
                  fg_color=config.COLOR_ACCENT_NEUTRAL, hover_color=("#A0A0A0"),
                  text_color=config.COLOR_TEXT, font=config.FONT_HEADER, height=42).pack(fill=ctk.X, padx=12, pady=(6, 6))
        
        # FIRST-DAY CHECKLIST (only shows on Day 1-3)
        self.checklist_frame = ctk.CTkFrame(self.action_frame, fg_color=("#2E4053"), corner_radius=8)
        self.checklist_frame.pack(fill='x', padx=12, pady=(8, 6))
        self.checklist_label = ctk.CTkLabel(self.checklist_frame, text="", font=config.FONT_BODY, text_color=config.COLOR_GOLD, anchor='w', justify='left', wraplength=800)
        self.checklist_label.pack(padx=10, pady=8)
        
        # 1b. Budgets & Action Points Panel (RIGHT side of top row)
        self.info_panel = ctk.CTkFrame(self.top_row_container, fg_color=config.COLOR_PANEL_BG, corner_radius=10, width=340)
        # Let contents determine height so the employee panel is visible
        self.info_panel.pack(side=ctk.RIGHT, fill=ctk.Y, expand=False)
        
        # Action Points Display
        self.action_points_frame = ctk.CTkFrame(self.info_panel, fg_color=("#2E4053"), corner_radius=8)
        self.action_points_frame.pack(fill='x', padx=10, pady=(10, 5))
        ctk.CTkLabel(self.action_points_frame, text="⚡ DAILY ACTIONS", font=config.FONT_HEADER, text_color=config.COLOR_GOLD).pack(pady=(5, 0))
        self.action_points_label = ctk.CTkLabel(self.action_points_frame, text="3 / 3", font=(config.FONT_FAMILY, 28, "bold"), text_color=config.COLOR_SUCCESS_GREEN)
        self.action_points_label.pack(pady=(0, 5))
        
        # Marketing Pressure Display
        self.marketing_frame = ctk.CTkFrame(self.info_panel, fg_color=("#34495E"), corner_radius=8)
        self.marketing_frame.pack(fill='x', padx=10, pady=(5, 5))
        ctk.CTkLabel(self.marketing_frame, text="📊 MARKET DEFENSE", font=(config.FONT_FAMILY, 10, "bold"), text_color=config.COLOR_ACCENT_NEUTRAL).pack(pady=(5, 2))
        self.marketing_counter_label = ctk.CTkLabel(self.marketing_frame, text="Last marketing: 0 days ago", font=config.FONT_BODY, text_color=config.COLOR_SUCCESS_GREEN)
        self.marketing_counter_label.pack(pady=(0, 5))
        
        # Department Budgets Display
        ctk.CTkLabel(self.info_panel, text="DEPT BUDGETS", font=config.FONT_HEADER, text_color='#F39C12').pack(fill='x', pady=(10, 5), padx=10)
        self.budget_labels = {}
        for dept in ['R&D', 'Marketing', 'Operations', 'HR']:
            frame = ctk.CTkFrame(self.info_panel, fg_color=("#34495E"), corner_radius=6)
            frame.pack(fill='x', padx=10, pady=3)
            dept_label = ctk.CTkLabel(frame, text=f"{dept}:", font=config.FONT_BODY, anchor='w', width=80, text_color=config.COLOR_TEXT)
            dept_label.pack(side=ctk.LEFT, padx=(8, 5))
            
            budget_value = ctk.CTkLabel(frame, text="", font=(config.FONT_FAMILY, 11), anchor='w', text_color=config.COLOR_TEXT)
            budget_value.pack(side=ctk.LEFT, fill='x', expand=True, padx=(0, 8))
            self.budget_labels[dept] = budget_value

        # Employees Panel
        emp_panel = ctk.CTkFrame(self.info_panel, fg_color=("#2E4053"), corner_radius=8)
        emp_panel.pack(fill='both', padx=10, pady=(10, 8), expand=True)
        ctk.CTkLabel(emp_panel, text="EMPLOYEES", font=config.FONT_HEADER, text_color=config.COLOR_ACCENT_PRIMARY).pack(pady=(6, 2))
        self.employee_summary_label = ctk.CTkLabel(emp_panel, text="0 employees", font=config.FONT_BODY, text_color=config.COLOR_TEXT)
        self.employee_summary_label.pack()

        self.employee_list_frame = ctk.CTkScrollableFrame(emp_panel, fg_color=("#34495E"), height=140)
        self.employee_list_frame.pack(fill='x', padx=8, pady=(4, 8))

        ctk.CTkLabel(emp_panel, text="Automation Log", font=config.FONT_BODY, text_color=config.COLOR_ACCENT_NEUTRAL).pack()
        self.automation_log_box = ctk.CTkTextbox(emp_panel, height=90, state=ctk.DISABLED, wrap='word',
                                               font=config.FONT_MONO, fg_color=("#3E4E60"), text_color=config.COLOR_TEXT,
                                               border_width=0, corner_radius=6)
        self.automation_log_box.pack(fill='both', expand=False, padx=8, pady=(2, 6))
        
        # News Ticker and Advance Day Container
        ticker_container = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        ticker_container.pack(side=ctk.TOP, fill=ctk.X, pady=(10, 0))
        
        # News Ticker Panel (left side, takes most space)
        self.ticker_frame = ctk.CTkFrame(ticker_container, fg_color=("#1C2833"), corner_radius=10, height=60)
        self.ticker_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=(0, 10))
        self.ticker_frame.pack_propagate(False)
        
        ctk.CTkLabel(self.ticker_frame, text="📰 MARKET NEWS", font=(config.FONT_FAMILY, 10, "bold"), 
                    text_color=config.COLOR_GOLD).pack(side=ctk.LEFT, padx=10)
        
        self.ticker_label = ctk.CTkLabel(self.ticker_frame, text="", font=config.FONT_BODY, 
                                         text_color=config.COLOR_TEXT, anchor='w')
        self.ticker_label.pack(side=ctk.LEFT, fill=ctk.X, expand=True, padx=10)
        
        # Advance Day Button (right side)
        self.advance_button = ctk.CTkButton(ticker_container, text="ADVANCE DAY >>", command=self._advance_day, 
                                            width=200, height=60, 
                                            fg_color=config.COLOR_SUCCESS_GREEN, hover_color=("#4CAF50"), 
                                            text_color=config.COLOR_PANEL_BG, font=config.FONT_TITLE, corner_radius=8)
        self.advance_button.pack(side=ctk.RIGHT)
        
        # Initialize ticker state (will be started after UI setup)
        self.ticker_headlines = []
        self.ticker_index = 0
        
        # 2. Button Footer Frame
        self.footer_frame = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.footer_frame.pack(side=ctk.BOTTOM, fill=ctk.X, pady=(10, 0))
        
        # PRE-EARNINGS BANNER (shows 10 days before earnings call)
        self.earnings_banner = ctk.CTkFrame(self.footer_frame, fg_color=config.COLOR_GOLD, corner_radius=8, height=40)
        self.earnings_banner_label = ctk.CTkLabel(self.earnings_banner, text="", font=config.FONT_HEADER, text_color=config.COLOR_PANEL_BG)
        self.earnings_banner_label.pack(pady=8, padx=12)

        # 3. Log & Projects Container (split horizontally)
        log_projects_container = ctk.CTkFrame(self.action_frame, fg_color="transparent")
        log_projects_container.pack(fill=ctk.BOTH, expand=True, padx=10, pady=(4, 6))
        
        # Log Panel (LEFT half)
        self.log_frame = ctk.CTkFrame(log_projects_container, fg_color=config.COLOR_PANEL_BG, corner_radius=10)
        self.log_frame.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=(0, 5))
        ctk.CTkLabel(self.log_frame, text="EVENT LOG", font=config.FONT_HEADER, text_color=config.COLOR_ACCENT_PRIMARY).pack(pady=5)
        
        self.log_text = ctk.CTkTextbox(self.log_frame, height=260, state="disabled", wrap='word', 
                         font=config.FONT_MONO, fg_color=("#3E4E60"), text_color=config.COLOR_TEXT, 
                         border_width=0, corner_radius=8) 
        self.log_text.pack(fill=ctk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Projects Panel (RIGHT half)
        self.project_panel = ctk.CTkFrame(log_projects_container, fg_color=config.COLOR_PANEL_BG, corner_radius=10)
        self.project_panel.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True, padx=(5, 0))

        self.project_list_header = ctk.CTkLabel(self.project_panel, text="ACTIVE PROJECTS", font=config.FONT_HEADER, text_color=config.COLOR_ACCENT_PRIMARY)
        self.project_list_header.pack(fill='x', pady=(6, 0), padx=10)

        self.project_list_frame = ctk.CTkScrollableFrame(self.project_panel, label_text="Ongoing R&D", label_font=config.FONT_BODY, label_text_color=config.COLOR_TEXT)
        self.project_list_frame.pack(fill='both', padx=10, pady=(0, 10), expand=True)

        # Status Panel Content
        self.status_labels = {}
        
        # NEW: ANALYST & CREDIT RATING WIDGET AT TOP OF LEFT PANEL
        self.rating_frame = ctk.CTkFrame(self.status_frame, fg_color=config.COLOR_PANEL_BG)
        self.rating_frame.pack(fill='x', pady=(10, 0), padx=10)
        ctk.CTkLabel(self.rating_frame, text="WALL ST. RATING", font=config.FONT_HEADER, text_color=config.COLOR_TEXT).pack()
        self.analyst_label = ctk.CTkLabel(self.rating_frame, text="HOLD", font=("Arial", 24, "bold"), text_color=config.COLOR_GOLD)
        self.analyst_label.pack(pady=5)
        
        ctk.CTkLabel(self.rating_frame, text="CREDIT RATING", font=config.FONT_HEADER, text_color=config.COLOR_TEXT).pack(pady=(10, 0))
        self.credit_label = ctk.CTkLabel(self.rating_frame, text="BBB", font=("Arial", 20, "bold"), text_color=config.COLOR_ACCENT_NEUTRAL)
        self.credit_label.pack(pady=5)

        self._add_status_section("FINANCIALS", ["Cash", "Debt", "Stock Price", "Market Cap", "Shares Out"], '#85C1E9')
        self._add_status_section("CEO/BOARD", ["Reputation", "Morale", "CEO Health", "Board Confidence"], '#BB8FCE')
        self._add_status_section("MARKET/TECH", ["Tech Level", "Customer Base", "Market Mood", "Analyst Rating"], '#27AE60') # Added Analyst Rating
        self._add_status_section("OPERATIONS", ["R&D Eff", "Marketing Eff", "Operations Eff", "HR Eff", "B2B Share", "Consumer Share"], '#D35400')
        
        self.email_status_label = ctk.CTkLabel(self.status_frame, text="EMAILS: 0 PENDING", font=config.FONT_HEADER, text_color=config.COLOR_SUCCESS_GREEN)
        self.email_status_label.pack(fill='x', pady=(20, 0))

        # ACTIVE PROJECTS moved to right panel (below event log) for smaller screens


    def _add_status_section(self, title, metrics, color):
        ctk.CTkLabel(self.status_frame, text=title, font=config.FONT_HEADER, text_color=color).pack(fill='x', pady=(10, 0), padx=10)
        for metric in metrics:
            frame = ctk.CTkFrame(self.status_frame, fg_color=config.COLOR_PANEL_BG)
            frame.pack(fill='x', padx=10)
            ctk.CTkLabel(frame, text=f"{metric}:", font=config.FONT_BODY, anchor='w', width=130, text_color=config.COLOR_TEXT).pack(side=ctk.LEFT, padx=(0, 5))
            label_val = ctk.CTkLabel(frame, text="", font=config.FONT_STAT_VALUE, anchor='w', text_color=config.COLOR_TEXT)
            label_val.pack(side=ctk.LEFT, fill='x', expand=True)
            self.status_labels[metric] = label_val

    

    def _update_status(self):
        corp = self.game
        
        # Update Time/Header
        self.time_label.configure(text=f"Q{corp.quarter} | Y{corp.year} | Day {corp.day}")
        self.scenario_label.configure(text=f"MARKET: {corp.current_scenario.upper()}")
        
        # Update Analyst Rating Widget Separately
        self.analyst_label.configure(text=corp.analyst_rating.upper())
        if corp.analyst_rating in ["Strong Buy", "Buy"]:
            self.analyst_label.configure(text_color=config.COLOR_SUCCESS_GREEN)
        elif corp.analyst_rating in ["Strong Sell", "Sell"]:
            self.analyst_label.configure(text_color=config.COLOR_ACCENT_DANGER)
        else:
            self.analyst_label.configure(text_color=config.COLOR_GOLD)

        # Update Credit Rating Widget
        self.credit_label.configure(text=corp.credit_rating)
        # Color code credit rating
        if corp.credit_rating in ["AAA", "AA", "A"]:
            self.credit_label.configure(text_color=config.COLOR_SUCCESS_GREEN)
        elif corp.credit_rating in ["BBB", "BB"]:
            self.credit_label.configure(text_color=config.COLOR_GOLD)
        else:
            self.credit_label.configure(text_color=config.COLOR_ACCENT_DANGER)
        
        # Update Metrics
        self.status_labels["Cash"].configure(text=f"${corp.cash:,.0f}")
        self.status_labels["Debt"].configure(text=f"${corp.debt:,.0f} ({corp._get_interest_rate()*100:.1f}% APR)")
        self.status_labels["Stock Price"].configure(text=f"${corp.stock_price:.2f}")
        self.status_labels["Market Cap"].configure(text=f"${corp.market_cap:,.0f}")
        self.status_labels["Shares Out"].configure(text=f"{corp.shares_outstanding:,.0f}")
        
        self.status_labels["Reputation"].configure(text=self._fmt_pct(corp.reputation))
        self.status_labels["Morale"].configure(text=self._fmt_pct(corp.employee_morale))
        self.status_labels["CEO Health"].configure(text=self._fmt_pct(corp.ceo_health))
        self.status_labels["Board Confidence"].configure(text=self._fmt_pct(corp.board_confidence))
        
        self.status_labels["Tech Level"].configure(text=self._fmt_pct(corp.technology_level))
        self.status_labels["Customer Base"].configure(text=self._fmt_pct(corp.customer_base))
        self.status_labels["Market Mood"].configure(text=f"{corp.market_mood}")
        
        self.status_labels["R&D Eff"].configure(text=self._fmt_pct(corp.dept_efficiency['R&D']))
        self.status_labels["Marketing Eff"].configure(text=self._fmt_pct(corp.dept_efficiency['Marketing']))
        self.status_labels["Operations Eff"].configure(text=self._fmt_pct(corp.dept_efficiency['Operations']))
        self.status_labels["HR Eff"].configure(text=self._fmt_pct(corp.dept_efficiency['HR']))
        self.status_labels["B2B Share"].configure(text=self._fmt_pct(corp.market_segments['B2B']))
        self.status_labels["Consumer Share"].configure(text=self._fmt_pct(corp.market_segments['Consumer']))
        
        # Update Action Points Display
        self.action_points_label.configure(text=f"{corp.action_points} / {corp.max_action_points}")
        if corp.action_points == 0:
            self.action_points_label.configure(text_color=config.COLOR_ACCENT_DANGER)
        elif corp.action_points <= 1:
            self.action_points_label.configure(text_color='#F39C12')  # Orange warning
        else:
            self.action_points_label.configure(text_color=config.COLOR_SUCCESS_GREEN)
        
        # Update Marketing Pressure Counter
        days_without = corp.days_without_marketing
        if days_without >= 15:
            counter_color = config.COLOR_ACCENT_DANGER
            status_text = f"⚠️ DANGER: {days_without} days"
        elif days_without >= 5:
            counter_color = '#F39C12'  # Orange
            status_text = f"⚠️ Warning: {days_without} days"
        else:
            counter_color = config.COLOR_SUCCESS_GREEN
            status_text = f"✓ Safe: {days_without} days ago"
        
        self.marketing_counter_label.configure(text=status_text, text_color=counter_color)
        
        # Update Annual Department Budgets with color-coded warnings and alert icons
        for dept in ['R&D', 'Marketing', 'Operations', 'HR']:
            remaining = corp.get_budget_remaining(dept)
            total = corp.annual_budget[dept]
            pct_remaining = (remaining / total * 100) if total > 0 else 0
            
            # Color code based on budget health
            if pct_remaining > 50:
                dept_color = config.COLOR_SUCCESS_GREEN
                icon = ""
            elif pct_remaining > 20:
                dept_color = '#F39C12'  # Orange warning
                icon = "⚠️ "
            else:
                dept_color = config.COLOR_ACCENT_DANGER
                icon = "🚨 "
            
            # More compact format with warning icon
            text = f"{icon}${remaining/1000000:.0f}M / ${total/1000000:.0f}M"
            self.budget_labels[dept].configure(text=text, text_color=dept_color)

        # Update Employees Panel with color-coded labels and bonus info
        employees = corp.employees
        total_skill = sum(getattr(e, 'skill_level', 1) for e in employees)
        total_bonus = sum(corp._employee_dept_bonus(d) for d in ['R&D', 'Marketing', 'Operations', 'HR'])
        self.employee_summary_label.configure(text=f"{len(employees)} employees | Total skill {total_skill:.1f} | Bonus +{total_bonus:.1f}%")
        for widget in self.employee_list_frame.winfo_children():
            widget.destroy()
        if not employees:
            ctk.CTkLabel(self.employee_list_frame, text="No hires yet.", font=config.FONT_BODY, text_color=config.COLOR_ACCENT_NEUTRAL).pack(pady=4, padx=6)
        else:
            for e in employees:
                row = ctk.CTkFrame(self.employee_list_frame, fg_color="transparent")
                row.pack(fill='x', padx=4, pady=2)
                
                # Color-code by employee type
                if e.employee_type == "Analyst":
                    badge_color = config.COLOR_ACCENT_NEUTRAL
                elif e.employee_type == "Manager":
                    badge_color = config.COLOR_ACCENT_PRIMARY
                elif e.employee_type == "Specialist":
                    badge_color = ("#9B59B6")
                else:  # Automation Expert
                    badge_color = config.COLOR_GOLD
                
                badge = ctk.CTkLabel(row, text=e.employee_type[0], font=(config.FONT_FAMILY, 9, 'bold'), 
                                   text_color=config.COLOR_PANEL_BG, fg_color=badge_color, 
                                   corner_radius=4, width=20, height=20)
                badge.pack(side=ctk.LEFT, padx=(2, 6))
                
                assigned = f" → {e.assigned_action}" if getattr(e, 'assigned_action', None) else ""
                ctk.CTkLabel(row, text=f"{e.name}{assigned}", font=config.FONT_BODY, text_color=config.COLOR_TEXT, anchor='w').pack(side=ctk.LEFT, padx=2)
                ctk.CTkLabel(row, text=f"Lvl{e.skill_level:.1f} T{e.tasks_completed}", font=config.FONT_BODY, text_color=config.COLOR_ACCENT_NEUTRAL, anchor='e').pack(side=ctk.RIGHT, padx=4)

        # Automation log
        self.automation_log_box.configure(state=ctk.NORMAL)
        self.automation_log_box.delete("1.0", ctk.END)
        for entry in reversed(list(corp.automation_log)):
            self.automation_log_box.insert(ctk.END, entry + '\n')
        self.automation_log_box.configure(state=ctk.DISABLED)
        
        # Update Log
        self.log_text.configure(state=ctk.NORMAL)
        self.log_text.delete("1.0", ctk.END)
        for entry in reversed(self.game.log):
            self.log_text.insert(ctk.END, entry + '\n')
        self.log_text.configure(state=ctk.DISABLED)
        
        # Update Project List
        for widget in self.project_list_frame.winfo_children():
            widget.destroy()
            
        if not corp.projects:
            ctk.CTkLabel(self.project_list_frame, text="No Active Projects", font=config.FONT_BODY, text_color=config.COLOR_ACCENT_NEUTRAL).pack(pady=10)
        else:
            for i, p in enumerate(corp.projects):
                # Card container for each project (matches panel color scheme)
                p_frame = ctk.CTkFrame(self.project_list_frame, fg_color=config.COLOR_PANEL_BG, corner_radius=8)
                p_frame.pack(fill='x', pady=8, padx=6)

                # Header: type badge and project name
                header = ctk.CTkFrame(p_frame, fg_color="transparent")
                header.pack(fill='x', padx=10, pady=(8, 0))
                p_type = {1: 'R&D', 2: 'Marketing', 3: 'Operations'}.get(p.type, 'Misc')
                badge = ctk.CTkLabel(header, text=f"{p_type}", font=(config.FONT_FAMILY, 10, 'bold'), text_color=config.COLOR_PANEL_BG, fg_color=config.COLOR_ACCENT_PRIMARY, corner_radius=6)
                badge.pack(side=ctk.LEFT, padx=(0,8))
                ctk.CTkLabel(header, text=p.name, font=config.FONT_HEADER, text_color=config.COLOR_TEXT).pack(side=ctk.LEFT, anchor='w')

                # Body: progress and days remaining
                body = ctk.CTkFrame(p_frame, fg_color="transparent")
                body.pack(fill='x', padx=10, pady=(6, 8))
                days_label = ctk.CTkLabel(body, text=f"Days Left: {p.days_remaining} / {p.duration_days}", font=config.FONT_BODY, text_color=config.COLOR_ACCENT_NEUTRAL)
                days_label.pack(anchor='w')

                progress = (p.duration_days - p.days_remaining) / max(1, p.duration_days)
                progress_bar = ctk.CTkProgressBar(body, width=320)
                progress_bar.set(max(0.0, min(1.0, progress)))
                progress_bar.pack(fill='x', pady=6)

                # Footer: cancel button and quick info
                footer = ctk.CTkFrame(p_frame, fg_color="transparent")
                footer.pack(fill='x', padx=10, pady=(0, 8))

                def cancel_project(proj_idx, proj_name=p.name):
                    if messagebox.askyesno("Confirm Cancellation", f"Are you sure you want to cancel the project '{proj_name}'? You will lose all investment."):
                        try:
                            corp.projects.pop(proj_idx)
                        except Exception:
                            pass
                        corp.log.append(f"Project '{proj_name}' cancelled.")
                        self._update_status()

                ctk.CTkButton(footer, text="Cancel", command=lambda idx=i: cancel_project(idx), 
                              fg_color=config.COLOR_ACCENT_DANGER, hover_color=("#C0392B"), 
                              font=config.FONT_BODY, width=120).pack(side=ctk.RIGHT)


        # Email Status Update
        email_count = len(self.game.email_system.inbox)
        color = config.COLOR_ACCENT_DANGER if email_count > 0 else config.COLOR_SUCCESS_GREEN
        status_text = f"EMAILS: {email_count} PENDING"
        self.email_status_label.configure(text=status_text, text_color=color)
        self.title_label.configure(text=f"{self.game.corp_name} - {self.game.ceo_name}")
        
        # Update First-Day Checklist (Day 1-3 only)
        if corp.day <= 3:
            checklist_items = []
            if email_count > 0:
                checklist_items.append("☐ Clear Executive Inbox")
            if corp.action_points > 0:
                checklist_items.append(f"☐ Spend action points ({corp.action_points} left)")
            if all(corp.get_budget_remaining(d) > corp.annual_budget[d] * 0.8 for d in ['R&D', 'Marketing', 'Operations', 'HR']):
                checklist_items.append("☐ Consider allocating budgets (none spent yet)")
            
            if not checklist_items:
                self.checklist_label.configure(text="✓ Day 1 checklist complete! You're ready to advance.")
            else:
                checklist_text = "Day 1-3 Checklist:\n" + "\n".join(checklist_items)
                self.checklist_label.configure(text=checklist_text)
            self.checklist_frame.pack(fill='x', padx=12, pady=(8, 6))
        else:
            self.checklist_frame.pack_forget()
        
        # Update Pre-Earnings Banner (10 days before earnings call)
        days_in_quarter = (corp.day - 1) % 90
        days_until_earnings = 90 - days_in_quarter
        if days_until_earnings <= 10:
            self.earnings_banner_label.configure(text=f"⚠️ EARNINGS CALL IN {days_until_earnings} DAYS ⚠️")
            self.earnings_banner.pack(side=ctk.LEFT, fill='x', expand=True, padx=(10, 10), pady=5)
        else:
            self.earnings_banner.pack_forget()

    def _open_settings_dialog(self):
        settings_window = ctk.CTkToplevel(self.master)
        settings_window.title("Game Settings")
        settings_window.geometry("550x700")  # Increased size to show all settings
        self._set_window_icon(settings_window)
        settings_window.attributes('-topmost', True)
        settings_window.grab_set()

        ctk.CTkLabel(settings_window, text="Application Settings", font=config.FONT_TITLE, text_color=config.COLOR_ACCENT_PRIMARY).pack(pady=20)

        # Scrollable frame for all settings
        scroll_frame = ctk.CTkScrollableFrame(settings_window, fg_color="transparent")
        scroll_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        # 1. Theme Selector
        ctk.CTkLabel(scroll_frame, text="Appearance Mode:", font=config.FONT_HEADER).pack(pady=(10, 5))
        def change_theme(new_mode):
            ctk.set_appearance_mode(new_mode)
        
        theme_selector = ctk.CTkSegmentedButton(scroll_frame, values=["Light", "Dark", "System"], 
                                                command=change_theme)
        theme_selector.set(ctk.get_appearance_mode())
        theme_selector.pack(pady=5)
        
        # 2. Tutorial Button
        def show_tutorial():
            settings_window.destroy()
            self._show_tutorial_popup()
            
        ctk.CTkButton(scroll_frame, text="Show Tutorial Again", command=show_tutorial, 
                      fg_color=config.COLOR_ACCENT_NEUTRAL, font=config.FONT_HEADER).pack(pady=10)

        # 3. Quit Button
        ctk.CTkButton(scroll_frame, text="Quit Game", command=sys.exit, 
                      fg_color=config.COLOR_ACCENT_DANGER, font=config.FONT_HEADER).pack(pady=10)

        # --- NEW SETTINGS ---
        # Coaching Emails Toggle
        coaching_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        coaching_frame.pack(fill='x', pady=(6, 6), padx=20)
        ctk.CTkLabel(coaching_frame, text="Enable Coaching Emails:", font=config.FONT_BODY).pack(side=ctk.LEFT)
        def toggle_coaching(state):
            try:
                self.game.email_system.coaching_enabled = state
                self.game.log.append(f"Settings: Coaching emails {'enabled' if state else 'disabled'}.")
            except Exception as e:
                print(f"Could not toggle coaching: {e}")

        coaching_var = ctk.BooleanVar(value=self.game.email_system.coaching_enabled)
        coaching_switch = ctk.CTkSwitch(coaching_frame, variable=coaching_var, command=lambda: toggle_coaching(coaching_var.get()), progress_color=config.COLOR_ACCENT_PRIMARY)
        coaching_switch.pack(side=ctk.RIGHT)

        # UI Scale Slider
        scale_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        scale_frame.pack(fill='x', pady=(6, 6), padx=20)
        ctk.CTkLabel(scale_frame, text="UI Scale:", font=config.FONT_BODY).pack(side=ctk.LEFT)
        def on_scale(val):
            try:
                self.ui_scale = float(val)
                self._apply_ui_scale(self.ui_scale)
            except Exception:
                pass

        scale_slider = ctk.CTkSlider(scale_frame, from_=0.8, to=1.4, number_of_steps=6, command=on_scale)
        scale_slider.set(self.ui_scale)
        scale_slider.pack(side=ctk.RIGHT, fill='x', expand=True, padx=(10,0))

        # Color Theme selector (dropdown)
        theme_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        theme_frame.pack(fill='x', pady=(6, 6), padx=20)
        ctk.CTkLabel(theme_frame, text="Color Theme:", font=config.FONT_BODY).pack(side=ctk.LEFT)
        
        def apply_color_theme(theme_name):
            try:
                if theme_name not in config.COLOR_THEMES:
                    return
                
                # Save the preference
                self._save_theme_preference(theme_name)
                self._apply_theme_colors(theme_name)
                
                self.game.log.append(f"Settings: Color theme changed to {theme_name}.")
                messagebox.showinfo("Theme Changed", f"Theme '{theme_name}' applied successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Theme change failed: {e}")

        # Detect current theme
        current_theme = "Executive Dark"
        try:
            if os.path.exists(THEME_STATE_FILE):
                with open(THEME_STATE_FILE, 'r') as f:
                    saved = f.read().strip()
                    if saved in config.COLOR_THEMES:
                        current_theme = saved
        except:
            pass

        theme_options = list(config.COLOR_THEMES.keys())
        theme_menu = ctk.CTkOptionMenu(theme_frame, values=theme_options, command=apply_color_theme, width=200)
        theme_menu.set(current_theme)
        theme_menu.pack(side=ctk.RIGHT)

        # Reset tutorial flag
        def reset_tutorial():
            try:
                if os.path.exists(TUTORIAL_STATE_FILE):
                    os.remove(TUTORIAL_STATE_FILE)
                    messagebox.showinfo("Tutorial Reset", "Tutorial will show again on next startup.")
                else:
                    messagebox.showinfo("Tutorial Reset", "Tutorial file not present; will show on next start.")
            except Exception as e:
                messagebox.showerror("Error", f"Could not reset tutorial: {e}")

        ctk.CTkButton(scroll_frame, text="Reset Tutorial", command=reset_tutorial, fg_color=config.COLOR_ACCENT_NEUTRAL, font=config.FONT_BODY).pack(pady=10)

        # Developer Mode Toggle (with password protection)
        ctk.CTkLabel(scroll_frame, text="🔐 Developer Mode", font=config.FONT_HEADER, text_color=config.COLOR_GOLD).pack(pady=(15, 5))
        ctk.CTkLabel(scroll_frame, text="Grant yourself unlimited resources for testing.", font=config.FONT_BODY, text_color=config.COLOR_ACCENT_NEUTRAL).pack(pady=(0, 10))
        
        def activate_dev_mode_from_settings():
            # Prompt for password
            if self._prompt_dev_password():
                self._enable_developer_mode()
                settings_window.destroy()
        
        ctk.CTkButton(scroll_frame, text="Activate Developer Mode", command=activate_dev_mode_from_settings,
                     fg_color=config.COLOR_GOLD, hover_color=("#D4AF37"), font=config.FONT_HEADER).pack(pady=10)

        # Long-Timer Multiplier Slider
        long_timer_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        long_timer_frame.pack(fill='x', pady=(6, 6), padx=20)
        ctk.CTkLabel(long_timer_frame, text="Long-Project Reward Multiplier:", font=config.FONT_BODY).pack(side=ctk.LEFT)

        def on_long_timer(val):
            try:
                m = float(val)
                self.game.long_timer_multiplier = m
                self.game.log.append(f"Settings: Long-timer multiplier set to {m:.2f}x")
            except Exception:
                pass

        long_timer_slider = ctk.CTkSlider(long_timer_frame, from_=1.0, to=3.0, number_of_steps=20, command=on_long_timer)
        long_timer_slider.set(self.game.long_timer_multiplier)
        long_timer_slider.pack(side=ctk.RIGHT, fill='x', expand=True, padx=(10,0))


    def _handle_mandatory_popup(self, event_id):
        corp = self.game
        
        try:
            # Check if the event is a pre-defined mandatory popup or an Earnings Call
            if event_id == "Earnings_Call":
                self._show_earnings_call_dialog()
                return

            # Show crisis decision popup for events
            event_data = corp.email_system.POPUP_EVENTS.get(event_id)
            if not event_data:
                messagebox.showerror("Error", f"Could not find event data for ID: {event_id}")
                return

            # Show crisis decision popup for all events
            self._show_crisis_decision_popup(event_id, event_data)
        except Exception as e:
            print(f"Error in _handle_mandatory_popup: {e}")
            messagebox.showerror("Error", f"Failed to handle event popup: {e}")

    def _show_crisis_decision_popup(self, event_id, event_data):
        corp = self.game

        try:
            popup = ctk.CTkToplevel(self.master)
            popup.title(event_data.get('title', "Critical Decision"))
            popup.geometry("600x400")
            popup.transient(self.master)
            popup.attributes('-topmost', True)
            popup.grab_set()
            popup.focus_force()
            popup.after(50, popup.focus_force)  # Nudge focus once the window is fully drawn
            self._set_window_icon(popup)

            ctk.CTkLabel(popup, text=event_data.get('title', "CRITICAL DECISION"),
                         font=config.FONT_TITLE, text_color=event_data.get('color', config.COLOR_ACCENT_DANGER)).pack(pady=10)

            # Prefer rich story text if provided
            dialogue = event_data.get('body') or event_data.get('dialogue') or "A major crisis requires your immediate attention."
            ctk.CTkLabel(popup, text=dialogue, font=config.FONT_BODY, wraplength=550, justify=ctk.LEFT).pack(pady=10, padx=20)

            choices = event_data.get('choices', [])
            if not choices:
                # Log the problematic event for debugging
                print(f"DEBUG: Event {event_id} has no choices. Event data: {event_data}")
                corp.log.append(f"EVENT ERROR: {event_id} was skipped (no options available)")
                messagebox.showinfo("Event Skipped", "This event had no available options and has been skipped.")
                if popup.winfo_exists():
                    popup.destroy()
                self.advance_button.configure(state=ctk.NORMAL)
                return

            choice_buttons = []

            def handle_choice(choice):
                try:
                    # Disable buttons immediately to avoid double-click glitches
                    for btn in choice_buttons:
                        btn.configure(state=ctk.DISABLED)

                    text, action_func, risk = choice

                    # Check for conditional action (Condition, Success_Action, Failure_Action)
                    if isinstance(action_func, tuple) and len(action_func) == 3:
                        condition, success_action, failure_action = action_func
                        if condition:
                            result_msg = success_action(self.game.email_system)
                            messagebox.showinfo("Decision Result", f"Action executed successfully. {result_msg}")
                        else:
                            result_msg = failure_action(self.game.email_system)
                            messagebox.showerror("Decision Failed", f"Action failed due to insufficient funds/condition. {result_msg}")

                    # Check for simple action (Impact_Function)
                    else:
                        result_msg = action_func(self.game.email_system)
                        messagebox.showinfo("Decision Result", result_msg)

                    # Clean up and continue
                    if popup.winfo_exists():
                        popup.destroy()
                    self.advance_button.configure(state=ctk.NORMAL)
                    self._update_status()
                except Exception as e:
                    print(f"Error handling choice: {e}")
                    if popup.winfo_exists():
                        popup.destroy()
                    self.advance_button.configure(state=ctk.NORMAL)
                    messagebox.showerror("Error", f"An error occurred: {e}")

            choice_frame = ctk.CTkFrame(popup, fg_color="transparent")
            choice_frame.pack(fill='x', pady=10, padx=20)

            for i, choice in enumerate(choices):
                try:
                    text, action_func, risk = choice
                except Exception:
                    print(f"Invalid choice payload for event {event_id}: {choice}")
                    messagebox.showerror("Event Error", "Invalid event choice detected. Please close and continue.")
                    continue

                if risk == 'RISK_HIGH':
                    btn_color = config.COLOR_ACCENT_DANGER
                    btn_hover = ("#C0392B")
                elif risk == 'RISK_LOW':
                    btn_color = config.COLOR_SUCCESS_GREEN
                    btn_hover = ("#4CAF50")
                else:
                    btn_color = config.COLOR_ACCENT_PRIMARY
                    btn_hover = ("#4A90E2")

                btn = ctk.CTkButton(choice_frame, text=f"{i+1}. {text}", command=lambda c=choice: handle_choice(c),
                                     width=500, height=40, fg_color=btn_color, hover_color=btn_hover,
                                     text_color="white", font=config.FONT_HEADER)
                btn.pack(pady=8)
                choice_buttons.append(btn)

            # Emergency close button (bottom of popup)
            def emergency_close():
                if popup.winfo_exists():
                    popup.destroy()
                self.advance_button.configure(state=ctk.NORMAL)

            ctk.CTkButton(popup, text="⚠️ Force Close Event", command=emergency_close,
                         fg_color=("#555555"), hover_color=("#333333"), font=config.FONT_BODY, height=32).pack(pady=(10, 5), padx=20, fill='x')

            # Also handle window-manager close to re-enable controls
            popup.protocol("WM_DELETE_WINDOW", emergency_close)

            # Remove event from POPUP_EVENTS so it doesn't trigger again
            if event_id in corp.email_system.POPUP_EVENTS:
                del corp.email_system.POPUP_EVENTS[event_id]

        except Exception as e:
            print(f"Error creating crisis popup: {e}")
            self.advance_button.configure(state=ctk.NORMAL)
            messagebox.showerror("Error", f"Failed to show event popup: {e}")




    def _show_earnings_call_dialog(self):
        corp = self.game
        self.advance_button.configure(state=ctk.DISABLED)

        earnings_window = ctk.CTkToplevel(self.master)
        earnings_window.title(f"Quarter {corp.quarter} Earnings Call - Y{corp.year}")
        earnings_window.geometry("800x650")
        earnings_window.attributes('-topmost', True)
        earnings_window.grab_set()
        self._set_window_icon(earnings_window)

        ctk.CTkLabel(earnings_window, text="QUARTERLY EARNINGS CALL", font=config.FONT_TITLE, text_color=config.COLOR_GOLD).pack(pady=10)
        
        # Financial Summary
        summary_frame = ctk.CTkFrame(earnings_window)
        summary_frame.pack(pady=10, padx=20, fill='x')
        
        rev_change = ((corp.quarterly_revenue - corp.previous_quarter_revenue) / corp.previous_quarter_revenue) * 100 if corp.previous_quarter_revenue else 0
        
        ctk.CTkLabel(summary_frame, text=f"Revenue: ${corp.quarterly_revenue:,.0f} (Change: {rev_change:+.0f}%)", font=config.FONT_HEADER, text_color=config.COLOR_TEXT).pack(anchor='w', padx=10, pady=2)
        ctk.CTkLabel(summary_frame, text=f"Costs: ${corp.quarterly_costs:,.0f}", font=config.FONT_HEADER, text_color=config.COLOR_TEXT).pack(anchor='w', padx=10, pady=2)
        ctk.CTkLabel(summary_frame, text=f"Cash Reserves: ${corp.cash:,.0f}", font=config.FONT_HEADER, text_color=config.COLOR_TEXT).pack(anchor='w', padx=10, pady=2)

        # Question & Answer Section
        qa_frame = ctk.CTkFrame(earnings_window, fg_color=config.COLOR_PANEL_BG)
        qa_frame.pack(pady=10, padx=20, fill='x', expand=True)
        
        questions = random.sample(config.EARNINGS_QUESTIONS, 3) 
        current_q_index = 0
        answer_score = 0
        
        question_label = ctk.CTkLabel(qa_frame, text="", font=config.FONT_HEADER, wraplength=700)
        question_label.pack(pady=10, padx=10)
        
        option_buttons = []
        
        def update_qa_display():
            nonlocal current_q_index
            if current_q_index < len(questions):
                q_data = questions[current_q_index]
                question_label.configure(text=f"Analyst Question {current_q_index + 1}: {q_data['q']}")
                
                # Clear old buttons
                for btn in option_buttons:
                    btn.destroy()
                option_buttons.clear()
                
                # Create new buttons
                for i, (text, impact_type) in enumerate(q_data['options']):
                    btn = ctk.CTkButton(qa_frame, text=text, 
                                        command=lambda idx=i: handle_answer(idx),
                                        width=600, height=40, font=config.FONT_BODY,
                                        fg_color=config.COLOR_ACCENT_NEUTRAL)
                    btn.pack(pady=5)
                    option_buttons.append(btn)
                
                submit_btn.pack_forget()
            else:
                question_label.configure(text="All questions answered. Preparing final summary...")
                for btn in option_buttons:
                    btn.destroy()
                submit_btn.pack(pady=20)
                
        def handle_answer(option_index):
            nonlocal current_q_index, answer_score
            impact_type = questions[current_q_index]['options'][option_index][1]
            
            # Simple scoring logic based on impact type
            if impact_type == "safest":
                score_change = random.choice([0, 1])
            elif impact_type == "tech_focused":
                score_change = 2 if corp.technology_level > 60 else -1
            elif impact_type == "profit_focused":
                score_change = 2 if corp.quarterly_revenue > corp.quarterly_costs * 1.5 else -1
            elif impact_type == "growth_focused":
                score_change = 2 if corp.customer_base > 50 else -1
            elif impact_type == "risky":
                score_change = random.choice([3, -3])
            else:
                score_change = 0

            answer_score += score_change
            current_q_index += 1
            update_qa_display()

        def submit_call():
            result_msg = corp.process_earnings_call(answer_score)
            messagebox.showinfo("Earnings Call Result", result_msg)
            earnings_window.destroy()
            self.advance_button.configure(state=ctk.NORMAL)
            self._update_status()

        submit_btn = ctk.CTkButton(earnings_window, text="End Call & Face Wall Street", command=submit_call, fg_color=config.COLOR_GOLD, hover_color=("#D4AF37"), font=config.FONT_TITLE)
        
        # Initial display
        update_qa_display()

    def _advance_day(self):
        try:
            # 1. Disable button to prevent spam
            self.advance_button.configure(state=ctk.DISABLED)
            
            # 2. Process the game logic for the day
            event_trigger = self.game.update_day()
            
            # 2b. Check for union activity (with error handling)
            try:
                if hasattr(self.game, 'check_unionization_threat') and self.game.check_unionization_threat():
                    # Union event occurred - show notification
                    if self.game.union_status == "Active":
                        messagebox.showwarning("Union Formed!", 
                            "Employees have formed a union and are presenting demands.\n\n" + 
                            "Check '🪧 Union Relations' to negotiate before they strike.")
            except Exception as e:
                print(f"Union check error (non-critical): {e}")

            # 3. Check for Emergency Borrowing
            if event_trigger == "EmergencyBorrowing":
                self._handle_emergency_borrowing()
                return
            
            # 4. Check for Game Over condition
            if event_trigger.startswith("GameOver"):
                self._check_game_over(event_trigger)
                return

            # 5. Handle Popup Event
            if event_trigger and event_trigger != "OK":
                self._update_status()
                self._handle_mandatory_popup(event_trigger)
                return

            # 6. Normal day advance complete
            self._update_status()
            self.advance_button.configure(state=ctk.NORMAL) # Re-enable if no blocking event
        
        except Exception as e:
            print(f"Advance day error: {e}")
            self.advance_button.configure(state=ctk.NORMAL)  # Always re-enable button on error
            messagebox.showerror("Error", f"An error occurred while advancing the day: {e}")
    
    def _handle_emergency_borrowing(self):
        """Handle negative cash emergency - force player to borrow or go bankrupt."""
        corp = self.game
        
        emergency_window = ctk.CTkToplevel(self.master)
        emergency_window.title("⚠️ CASH CRISIS")
        emergency_window.geometry("700x650")
        emergency_window.attributes('-topmost', True)
        emergency_window.grab_set()
        self._set_window_icon(emergency_window)
        
        # Title
        ctk.CTkLabel(emergency_window, text="⚠️ CASH CRISIS", 
                    font=config.FONT_TITLE, text_color=config.COLOR_ACCENT_DANGER).pack(pady=(20, 10))
        
        ctk.CTkLabel(emergency_window, text="NEGATIVE CASH BALANCE - IMMEDIATE ACTION REQUIRED", 
                    font=config.FONT_HEADER, text_color=config.COLOR_ACCENT_DANGER).pack(pady=(0, 20))
        
        # Crisis info
        crisis_frame = ctk.CTkFrame(emergency_window, fg_color=config.COLOR_ACCENT_DANGER, corner_radius=10)
        crisis_frame.pack(fill='x', padx=30, pady=10)
        
        ctk.CTkLabel(crisis_frame, text=f"Current Cash: ${corp.cash:,.0f}", 
                    font=config.FONT_HEADER, text_color="white").pack(pady=8)
        ctk.CTkLabel(crisis_frame, text=f"Current Debt: ${corp.debt:,.0f}", 
                    font=config.FONT_BODY, text_color="white").pack(pady=4)
        ctk.CTkLabel(crisis_frame, text=f"Debt Limit: ${corp.max_debt_limit:,.0f}", 
                    font=config.FONT_BODY, text_color="white").pack(pady=(4, 8))
        
        # Warning message
        warning_frame = ctk.CTkFrame(emergency_window, fg_color="transparent")
        warning_frame.pack(fill='x', padx=30, pady=15)
        ctk.CTkLabel(warning_frame, text="⚠️ You must borrow money immediately or declare bankruptcy!", 
                    font=config.FONT_BODY, wraplength=600, justify='center').pack()
        
        # Calculate how much needed to get back to positive
        amount_needed = abs(corp.cash) + 1000000  # Cover deficit + $1M buffer
        max_borrowable = corp.max_debt_limit - corp.debt
        
        # Borrowing info
        borrow_frame = ctk.CTkFrame(emergency_window, fg_color=config.COLOR_PANEL_BG, corner_radius=10)
        borrow_frame.pack(fill='x', padx=30, pady=15)
        
        ctk.CTkLabel(borrow_frame, text=f"Amount needed to cover deficit: ${amount_needed:,.0f}", 
                    font=config.FONT_HEADER, text_color=config.COLOR_GOLD).pack(pady=8)
        ctk.CTkLabel(borrow_frame, text=f"Available credit remaining: ${max_borrowable:,.0f}", 
                    font=config.FONT_BODY, text_color=config.COLOR_ACCENT_NEUTRAL).pack(pady=(0, 8))
        
        def emergency_borrow():
            if max_borrowable < amount_needed:
                emergency_window.destroy()
                messagebox.showerror("Credit Exhausted", 
                    "You've exceeded your borrowing capacity.\nThe company is insolvent.\n\nGAME OVER")
                self._check_game_over("GameOver_Debt")
                return
            
            # Force borrow the minimum amount
            borrow_amount = min(amount_needed, max_borrowable)
            corp.cash += borrow_amount
            corp.debt += borrow_amount
            corp.log.append(f"EMERGENCY BORROWING: ${borrow_amount:,.0f}")
            
            emergency_window.destroy()
            messagebox.showinfo("Emergency Loan Secured", 
                f"Borrowed ${borrow_amount:,.0f} at 5% annual interest.\n\n" +
                f"Remember: 1% minimum debt payment is required daily!")
            
            self._update_status()
            self.advance_button.configure(state=ctk.NORMAL)
        
        def declare_bankruptcy():
            emergency_window.destroy()
            messagebox.showinfo("Bankruptcy Filed", "The company has declared bankruptcy.\n\nGAME OVER")
            self._check_game_over("GameOver_Debt")
        
        # Action buttons
        btn_frame = ctk.CTkFrame(emergency_window, fg_color="transparent")
        btn_frame.pack(pady=30)
        
        ctk.CTkButton(btn_frame, text=f"💰 Emergency Loan: ${amount_needed:,.0f}", 
                     command=emergency_borrow,
                     fg_color=config.COLOR_SUCCESS_GREEN, 
                     hover_color="#228B22",
                     font=config.FONT_HEADER, 
                     width=280, 
                     height=50).pack(pady=8)
        
        ctk.CTkButton(btn_frame, text="⚠️ Declare Bankruptcy (Game Over)", 
                     command=declare_bankruptcy,
                     fg_color=config.COLOR_ACCENT_DANGER, 
                     hover_color="#8B0000",
                     font=config.FONT_HEADER, 
                     width=280, 
                     height=50).pack(pady=8)
        
        # Prevent closing without action
        emergency_window.protocol("WM_DELETE_WINDOW", lambda: None)

    def _check_game_over(self, reason):
        # ... (Game Over logic remains the same, using CTkinter dialogs)
        self.advance_button.configure(state=ctk.DISABLED)
        
        # Check for victory conditions
        if reason == "Victory_Leaderboard":
            msg = f"🎉 VICTORY! You've reached #1 in the stock market!\n\nYour Stock: ${self.game.stock_price:.2f}\nYou've outperformed all competitors and dominated the market!\n\nCongratulations, you're the ultimate CEO!"
            messagebox.showinfo("🏆 VICTORY - MARKET LEADER!", msg)
        elif reason == "Victory_IPO":
            msg = f"🎉 VICTORY! Your company went public with a market cap of ${self.game.market_cap/1_000_000:.0f}M!\n\nYou've achieved the dream of every CEO: a successful IPO!"
            messagebox.showinfo("🏆 VICTORY - IPO SUCCESS!", msg)
        elif reason == "Victory_Dominance":
            msg = f"🎉 VICTORY! You've achieved market dominance!\n\nCustomer Base: {self.game.customer_base:.0f}%\nQuarterly Revenue: ${self.game.quarterly_revenue/1_000_000:.0f}M\n\nYour company is now an industry titan!"
            messagebox.showinfo("🏆 VICTORY - MARKET DOMINANCE!", msg)
        elif reason == "Victory_Acquired":
            msg = f"🎉 VICTORY! Your company was acquired for ${self.game.market_cap/1_000_000:.0f}M!\n\nYou've built something so valuable that a tech giant wanted to buy it. Congratulations on your lucrative exit!"
            messagebox.showinfo("🏆 VICTORY - ACQUISITION EXIT!", msg)
        elif reason == "GameOver_Debt":
            msg = "Your corporation was declared insolvent due to crippling debt and market failure!"
            messagebox.showerror("GAME OVER", msg)
        elif reason == "GameOver_Board":
            msg = "The Board of Directors lost confidence and executed a vote of no confidence. You have been removed as CEO!"
            messagebox.showerror("GAME OVER", msg)
        elif reason == "GameOver_Health":
            msg = "Your health reached a critical level. Stress has forced you into early retirement. Game Over."
            messagebox.showerror("GAME OVER", msg)
        else:
            msg = "The game has ended."
            messagebox.showerror("GAME OVER", msg)
        
        # Disable all action buttons
        for btn in [self.btn_email, self.btn_rnd, self.btn_budget, self.btn_debt, self.btn_hr, self.btn_market, self.btn_card]:
            btn.configure(state=ctk.DISABLED)

# --- ACTION DIALOGS (CTKTOPLEVEL) ---

    def _open_email_dialog(self):
        corp = self.game
        
        # Emails don't cost action points (they're part of daily routine)
        # No action point check needed
        
        email_window = ctk.CTkToplevel(self.master)
        email_window.title("Executive Inbox")
        email_window.geometry("800x600")
        email_window.attributes('-topmost', True)
        email_window.grab_set()
        self._set_window_icon(email_window)
        
        header_label = ctk.CTkLabel(email_window, text=f"INBOX - {len(corp.email_system.inbox)} New Emails", font=config.FONT_TITLE, text_color=config.COLOR_ACCENT_PRIMARY)
        header_label.pack(pady=10)

        # Scrollable frame for emails
        scroll_frame = ctk.CTkScrollableFrame(email_window, label_text="Unread Communications", label_font=config.FONT_HEADER)
        scroll_frame.pack(fill='both', expand=True, padx=20, pady=10)

        # Function to process the action
        def process_action(email_index, option_index):
            result_msg = corp.email_system.apply_action(email_index, option_index)
            messagebox.showinfo("Action Result", result_msg)
            self._update_status() # Refresh main UI metrics and email count
            if not corp.email_system.inbox:
                email_window.destroy()
                return
            render_emails()

        def render_emails():
            header_label.configure(text=f"INBOX - {len(corp.email_system.inbox)} New Emails")
            for child in scroll_frame.winfo_children():
                child.destroy()
            if not corp.email_system.inbox:
                ctk.CTkLabel(scroll_frame, text="✓ Your inbox is empty. Excellent job!", font=config.FONT_BODY, text_color=config.COLOR_SUCCESS_GREEN).pack(pady=20)
                return
            
            # Sort emails: URGENT first, then normal
            sorted_emails = sorted(enumerate(corp.email_system.inbox), 
                                  key=lambda x: (0 if 'URGENT' in x[1].get('subject', '') else 1))
            
            # Inline cue at top if there are urgent emails
            urgent_count = sum(1 for _, e in sorted_emails if 'URGENT' in e.get('subject', ''))
            if urgent_count > 0:
                cue_frame = ctk.CTkFrame(scroll_frame, fg_color=config.COLOR_ACCENT_DANGER, corner_radius=8)
                cue_frame.pack(fill='x', padx=5, pady=(5, 10))
                ctk.CTkLabel(cue_frame, text=f"⚠️ {urgent_count} URGENT email(s) require immediate attention. Handle red subjects first.", 
                           font=config.FONT_HEADER, text_color="white", wraplength=750).pack(padx=12, pady=8)
            
            # Display sorted emails
            for original_idx, email in sorted_emails:
                is_urgent = 'URGENT' in email.get('subject', '')
                border_color = config.COLOR_ACCENT_DANGER if is_urgent else config.COLOR_ACCENT_NEUTRAL
                e_frame = ctk.CTkFrame(scroll_frame, fg_color=("#3E4E60"), corner_radius=8, border_width=2, border_color=border_color)
                e_frame.pack(fill='x', pady=8, padx=5)

                # Urgency badge + From
                header_row = ctk.CTkFrame(e_frame, fg_color="transparent")
                header_row.pack(fill='x', padx=10, pady=(8, 0))
                
                if is_urgent:
                    badge = ctk.CTkLabel(header_row, text="URGENT", font=(config.FONT_FAMILY, 9, 'bold'), 
                                       text_color="white", fg_color=config.COLOR_ACCENT_DANGER, 
                                       corner_radius=4, width=60, height=20)
                    badge.pack(side=ctk.LEFT, padx=(0, 8))
                
                ctk.CTkLabel(header_row, text=f"From: {email['from']}", font=config.FONT_BODY, anchor='w', 
                           text_color=config.COLOR_ACCENT_NEUTRAL).pack(side=ctk.LEFT)
                
                # Subject
                ctk.CTkLabel(e_frame, text=f"{email['subject']}", font=config.FONT_HEADER, anchor='w', 
                            text_color=config.COLOR_ACCENT_DANGER if is_urgent else config.COLOR_ACCENT_PRIMARY, 
                            justify=ctk.LEFT, wraplength=750).pack(fill='x', padx=10, pady=(4, 6))
                
                # Body
                ctk.CTkLabel(e_frame, text=email['body'], font=config.FONT_BODY, justify=ctk.LEFT, wraplength=750, 
                           text_color=config.COLOR_TEXT).pack(fill='x', padx=10, pady=5)
                
                # Options with inline hints
                option_frame = ctk.CTkFrame(e_frame, fg_color="transparent")
                option_frame.pack(fill='x', pady=8, padx=10)
                ctk.CTkLabel(option_frame, text="💡 Choose your response (each may cost cash/budget):", 
                           font=config.FONT_BODY, text_color=config.COLOR_GOLD).pack(anchor='w', pady=(0, 4))
                
                for j, option in enumerate(email['options']):
                    # Color-code option buttons by implied risk
                    opt_text = option['text'].lower()
                    if 'high risk' in opt_text or 'reject' in opt_text or 'ignore' in opt_text:
                        btn_color = config.COLOR_ACCENT_DANGER
                    elif 'low risk' in opt_text or 'approve' in opt_text:
                        btn_color = config.COLOR_SUCCESS_GREEN
                    else:
                        btn_color = config.COLOR_ACCENT_NEUTRAL
                    
                    ctk.CTkButton(option_frame, text=option['text'], command=lambda ei=original_idx, oi=j: process_action(ei, oi), 
                                  fg_color=btn_color, font=config.FONT_BODY, width=600, height=36).pack(pady=4, anchor='w')

        render_emails()

        ctk.CTkButton(email_window, text="Close Inbox", command=email_window.destroy, fg_color=config.COLOR_ACCENT_NEUTRAL, font=config.FONT_HEADER).pack(pady=10)

    def _open_hr_dialog(self):
        """HR & Automation hiring dialog"""
        corp = self.game
        
        # Check action points
        if corp.action_points <= 0:
            messagebox.showwarning("No Actions Remaining", "You have no daily actions left. Advance to the next day or hire employees to automate tasks.")
            return
        
        # Deduct action point
        corp.action_points -= 1
        self._update_status()
        
        hr_window = ctk.CTkToplevel(self.master)
        hr_window.title("HR & M&A Center")
        hr_window.geometry("950x680")
        hr_window.attributes('-topmost', True)
        hr_window.grab_set()
        self._set_window_icon(hr_window)

        # Header with toggle
        header = ctk.CTkFrame(hr_window, fg_color="transparent")
        header.pack(fill='x', padx=12, pady=10)
        ctk.CTkLabel(header, text="HR & M&A Center", font=config.FONT_TITLE, text_color=config.COLOR_ACCENT_PRIMARY).pack(side=ctk.LEFT)

        # View toggle buttons
        view_state = {"current": "employees"}
        toggle_frame = ctk.CTkFrame(header, fg_color="transparent")
        toggle_frame.pack(side=ctk.RIGHT)

        # ========== EMPLOYEES TAB ==========
        employees_frame = ctk.CTkFrame(hr_window, fg_color="transparent")

        info_banner = ctk.CTkFrame(employees_frame, fg_color=config.COLOR_ACCENT_PRIMARY, corner_radius=8)
        info_banner.pack(fill='x', padx=12, pady=(0, 12))
        ctk.CTkLabel(info_banner, text="💡 Hire employees to automate actions when you run out of daily action points.", 
                    font=config.FONT_BODY, text_color="white").pack(padx=10, pady=8)

        emp_scroll = ctk.CTkScrollableFrame(employees_frame, fg_color="transparent")
        emp_scroll.pack(fill=ctk.BOTH, expand=True, padx=12, pady=12)

        # Current employees
        emp_list = ctk.CTkFrame(emp_scroll, fg_color="transparent")
        emp_list.pack(fill='x', pady=(0, 16))

        def refresh_emp_list():
            for w in emp_list.winfo_children():
                w.destroy()
            ctk.CTkLabel(emp_list, text="👥 Current Employees", font=config.FONT_HEADER, text_color=config.COLOR_ACCENT_NEUTRAL).pack(anchor='w', pady=(0, 8))
            if not corp.employees:
                ctk.CTkLabel(emp_list, text="No employees hired yet.", font=config.FONT_BODY, text_color=config.COLOR_ACCENT_NEUTRAL).pack(pady=8)
                return
            for e in corp.employees:
                row = ctk.CTkFrame(emp_list, fg_color=config.COLOR_PANEL_BG, corner_radius=6)
                row.pack(fill='x', pady=3)
                ctk.CTkLabel(row, text=f"{e.name} ({e.employee_type})", font=config.FONT_BODY, text_color=config.COLOR_GOLD).pack(side=ctk.LEFT, padx=10, pady=6)
                ctk.CTkLabel(row, text=f"${e.daily_salary:,.0f}/day | Tasks: {e.tasks_completed}", font=config.FONT_BODY, text_color=config.COLOR_ACCENT_NEUTRAL).pack(side=ctk.RIGHT, padx=10)

        refresh_emp_list()

        # Hiring options
        ctk.CTkLabel(emp_scroll, text="🎯 Available Hires", font=config.FONT_HEADER, text_color=config.COLOR_ACCENT_NEUTRAL).pack(anchor='w', pady=(12, 8))

        options = [
            {"type": "Analyst", "signing_bonus": 1000000, "daily_salary": 15000, "skill": 1.0, "desc": "Can automate simple inbox and PR tasks."},
            {"type": "Manager", "signing_bonus": 3000000, "daily_salary": 35000, "skill": 1.25, "desc": "Handles investor meetings and legal issues."},
            {"type": "Specialist", "signing_bonus": 6000000, "daily_salary": 70000, "skill": 1.5, "desc": "Assists with tech upgrades and benefits."},
            {"type": "Automation Expert", "signing_bonus": 12000000, "daily_salary": 150000, "skill": 1.75, "desc": "Handles nearly all action types reliably."},
        ]

        for opt in options:
            card = ctk.CTkFrame(emp_scroll, fg_color=config.COLOR_PANEL_BG, corner_radius=8)
            card.pack(fill='x', pady=4)
            
            left = ctk.CTkFrame(card, fg_color="transparent")
            left.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True, padx=10, pady=8)
            
            ctk.CTkLabel(left, text=opt['type'], font=config.FONT_HEADER, text_color=config.COLOR_TEXT).pack(anchor='w')
            ctk.CTkLabel(left, text=opt['desc'], font=config.FONT_BODY, text_color=config.COLOR_ACCENT_NEUTRAL).pack(anchor='w')
            
            right = ctk.CTkFrame(card, fg_color="transparent")
            right.pack(side=ctk.RIGHT, padx=10, pady=8)
            
            ctk.CTkLabel(right, text=f"Signing Bonus: ${opt['signing_bonus']:,.0f}", font=config.FONT_BODY, text_color=config.COLOR_GOLD).pack(anchor='e')
            ctk.CTkLabel(right, text=f"Daily Salary: ${opt['daily_salary']:,.0f}", font=config.FONT_BODY, text_color=config.COLOR_ACCENT_NEUTRAL).pack(anchor='e', pady=(0, 4))
            
            def make_hire(opt_data):
                def _hire():
                    if not corp.can_afford_action('HR', opt_data['signing_bonus']):
                        messagebox.showwarning("Budget Shortfall", f"HR cannot afford this hire.")
                        return
                    if corp.cash < opt_data['signing_bonus']:
                        messagebox.showwarning("Insufficient Cash", "Not enough corporate cash.")
                        return
                    
                    corp.spend_from_budget('HR', opt_data['signing_bonus'])
                    corp.cash -= opt_data['signing_bonus']
                    name = f"{opt_data['type']}_{len(corp.employees)+1}"
                    emp = config.EMPLOYEE_FACTORY(name, opt_data['type'], opt_data['signing_bonus'], opt_data['daily_salary'], opt_data['skill'])
                    emp.hired_day = corp.day
                    corp.employees.append(emp)
                    corp.log.append(f"Hired {emp.name}.")
                    self._update_status()
                    refresh_emp_list()
                return _hire
            
            ctk.CTkButton(right, text="Hire", command=make_hire(opt), fg_color=config.COLOR_SUCCESS_GREEN, width=80, height=32).pack()

        employees_frame.pack(fill=ctk.BOTH, expand=True, padx=0, pady=0)

        # ========== ACQUISITIONS TAB ==========
        acq_frame = ctk.CTkFrame(hr_window, fg_color="transparent")

        def refresh_acquisitions():
            for w in acq_frame.winfo_children():
                w.destroy()
            
            acq_scroll = ctk.CTkScrollableFrame(acq_frame, fg_color="transparent")
            acq_scroll.pack(fill=ctk.BOTH, expand=True, padx=12, pady=12)

            # Acquired companies
            if corp.acquired_companies:
                acq_label = ctk.CTkLabel(acq_scroll, text="💰 Owned Companies (30% profit share)", font=config.FONT_HEADER, text_color=config.COLOR_SUCCESS_GREEN)
                acq_label.pack(anchor='w', pady=(0, 8))
                
                for comp in corp.acquired_companies:
                    card = ctk.CTkFrame(acq_scroll, fg_color=config.COLOR_PANEL_BG, corner_radius=8)
                    card.pack(fill='x', pady=4)
                    
                    ctk.CTkLabel(card, text=f"{comp.name} ({comp.industry})", font=config.FONT_HEADER, text_color=config.COLOR_GOLD).pack(anchor='w', padx=10, pady=(8, 2))
                    ctk.CTkLabel(card, text=f"Daily Profit: ${comp.daily_profit * 0.3:,.0f} | Total Earned: ${comp.total_profit_earned:,.0f}", 
                               font=config.FONT_BODY, text_color=config.COLOR_ACCENT_NEUTRAL).pack(anchor='w', padx=10, pady=(0, 8))

            # Available companies
            if corp.available_companies:
                avail_label = ctk.CTkLabel(acq_scroll, text="📊 Available Targets", font=config.FONT_HEADER, text_color=config.COLOR_ACCENT_PRIMARY)
                avail_label.pack(anchor='w', pady=(12, 8))
                
                for company in corp.available_companies:
                    card = ctk.CTkFrame(acq_scroll, fg_color=config.COLOR_PANEL_BG, corner_radius=8)
                    card.pack(fill='x', pady=4)
                    
                    hdr = ctk.CTkFrame(card, fg_color="transparent")
                    hdr.pack(fill='x', padx=10, pady=(8, 4))
                    ctk.CTkLabel(hdr, text=f"{company.name} ({company.industry})", font=config.FONT_HEADER, text_color=config.COLOR_TEXT).pack(anchor='w', side=ctk.LEFT)
                    ctk.CTkLabel(hdr, text=f"Difficulty: {company.difficulty.upper()}", font=config.FONT_BODY, text_color=config.COLOR_GOLD).pack(anchor='e', side=ctk.RIGHT)
                    
                    info = ctk.CTkFrame(card, fg_color="transparent")
                    info.pack(fill='x', padx=10, pady=(0, 4))
                    ctk.CTkLabel(info, text=f"Annual Profit: ${company.base_annual_profit}M | Your Cut: ${company.base_annual_profit * 0.3:.0f}M/year", 
                               font=config.FONT_BODY, text_color=config.COLOR_ACCENT_NEUTRAL).pack(anchor='w')
                    
                    offers = company.generate_offers()
                    for i, offer in enumerate(offers):
                        offer_text = f"{offer['label']}: ${offer['price']:.0f}M ({int(offer['acceptance_chance']*100)}% success)"
                        
                        def make_acquire(comp, idx):
                            def _acquire():
                                success, msg, price = corp.attempt_acquire_company(comp.name, idx)
                                if success:
                                    messagebox.showinfo("Success", msg)
                                else:
                                    messagebox.showwarning("Failed", msg)
                                self._update_status()
                                refresh_acquisitions()
                            return _acquire
                        
                        colors = [config.COLOR_ACCENT_DANGER, config.COLOR_ACCENT_PRIMARY, config.COLOR_SUCCESS_GREEN]
                        ctk.CTkButton(card, text=offer_text, command=make_acquire(company, i), 
                                    fg_color=colors[i], font=config.FONT_BODY, height=28).pack(fill='x', padx=10, pady=2)
                    
                    ctk.CTkLabel(card, text="", font=config.FONT_BODY).pack(pady=(0, 4))

        def switch_to_employees():
            view_state["current"] = "employees"
            acq_frame.pack_forget()
            employees_frame.pack(fill=ctk.BOTH, expand=True, padx=0, pady=0)
            emp_btn.configure(fg_color=config.COLOR_ACCENT_PRIMARY)
            acq_btn.configure(fg_color=config.COLOR_ACCENT_NEUTRAL)
        
        def switch_to_acquisitions():
            view_state["current"] = "acquisitions"
            employees_frame.pack_forget()
            refresh_acquisitions()
            acq_frame.pack(fill=ctk.BOTH, expand=True, padx=0, pady=0)
            emp_btn.configure(fg_color=config.COLOR_ACCENT_NEUTRAL)
            acq_btn.configure(fg_color=config.COLOR_ACCENT_PRIMARY)
        
        emp_btn = ctk.CTkButton(toggle_frame, text="👥 Employees", command=switch_to_employees, 
                               fg_color=config.COLOR_ACCENT_PRIMARY, height=32, width=100, font=config.FONT_BODY)
        emp_btn.pack(side=ctk.LEFT, padx=4)
        
        acq_btn = ctk.CTkButton(toggle_frame, text="🏢 Acquisitions", command=switch_to_acquisitions, 
                               fg_color=config.COLOR_ACCENT_NEUTRAL, height=32, width=120, font=config.FONT_BODY)
        acq_btn.pack(side=ctk.LEFT, padx=4)

    def _open_employee_tasks_dialog(self):
        """Assign specific actions to hired employees (no action point cost)."""
        corp = self.game
        if not corp.employees:
            messagebox.showinfo("No Employees", "Hire employees first in HR & Automation to assign tasks.")
            return

        assign_window = ctk.CTkToplevel(self.master)
        assign_window.title("Assign Employee Tasks")
        assign_window.geometry("720x520")
        assign_window.attributes('-topmost', True)
        assign_window.grab_set()
        self._set_window_icon(assign_window)

        ctk.CTkLabel(assign_window, text="Assign Actions to Employees", font=config.FONT_TITLE, text_color=config.COLOR_ACCENT_PRIMARY).pack(pady=10)
        ctk.CTkLabel(assign_window, text="Pick a specific task for each employee. Leave 'No Assignment' to let them choose automatically.",
                     font=config.FONT_BODY, text_color=config.COLOR_ACCENT_NEUTRAL, wraplength=680).pack(pady=(0,10))

        # Map actions to friendly labels
        action_labels = {
            "email": "Handle Emails",
            "marketing": "Run Marketing",
            "rnd": "Invest in R&D",
            "budget": "Rebalance Budgets",
            "hr": "Boost Morale"
        }

        scroll = ctk.CTkScrollableFrame(assign_window, fg_color="transparent")
        scroll.pack(fill='both', expand=True, padx=12, pady=6)

        selections = {}

        for e in corp.employees:
            card = ctk.CTkFrame(scroll, fg_color=config.COLOR_PANEL_BG, corner_radius=10)
            card.pack(fill='x', padx=6, pady=6)
            ctk.CTkLabel(card, text=f"{e.name} ({e.employee_type})", font=config.FONT_HEADER, text_color=config.COLOR_TEXT).pack(anchor='w', padx=10, pady=(8,2))
            ctk.CTkLabel(card, text=f"Skill {e.skill_level:.2f} | Tasks {e.tasks_completed}", font=config.FONT_BODY, text_color=config.COLOR_ACCENT_NEUTRAL).pack(anchor='w', padx=10, pady=(0,6))

            values = ["No Assignment"] + [action_labels[a] for a in e.auto_actions if a in action_labels]
            var = ctk.StringVar(value="No Assignment" if not e.assigned_action else action_labels.get(e.assigned_action, "No Assignment"))
            selections[e] = var
            ctk.CTkOptionMenu(card, variable=var, values=values, width=260).pack(anchor='w', padx=10, pady=(0,10))

        def save_assignments():
            try:
                for e, var in selections.items():
                    chosen_label = var.get()
                    if chosen_label == "No Assignment":
                        e.set_assignment(None)
                    else:
                        # Reverse lookup
                        for key, label in action_labels.items():
                            if label == chosen_label:
                                e.set_assignment(key)
                                break
                corp.log.append("Employee assignments updated.")
                self._update_status()
                messagebox.showinfo("Saved", "Employee task assignments updated.")
                assign_window.destroy()
            except Exception as ex:
                messagebox.showerror("Error", f"Could not save assignments: {ex}")

        ctk.CTkButton(assign_window, text="Save Assignments", command=save_assignments,
                      fg_color=config.COLOR_SUCCESS_GREEN, font=config.FONT_HEADER, width=220).pack(pady=12)
        ctk.CTkButton(assign_window, text="Close", command=assign_window.destroy, fg_color=config.COLOR_ACCENT_NEUTRAL).pack(pady=(0,12))

    def _open_rnd_dialog(self):
        corp = self.game
        
        # Check action points
        if corp.action_points <= 0:
            messagebox.showwarning("No Actions Remaining", "You have no daily actions left. Advance to the next day or hire employees to automate tasks.")
            return
        
        # Deduct action point
        corp.action_points -= 1
        self._update_status()
        
        rnd_window = ctk.CTkToplevel(self.master)
        rnd_window.title("R&D Lab and Projects")
        rnd_window.geometry("1000x800")
        rnd_window.attributes('-topmost', True)
        rnd_window.grab_set()
        self._set_window_icon(rnd_window)

        ctk.CTkLabel(rnd_window, text="R&D Lab & Strategic Projects", font=config.FONT_TITLE, text_color=config.COLOR_ACCENT_PRIMARY).pack(pady=10)
        
        # Inline cue
        cue_frame = ctk.CTkFrame(rnd_window, fg_color=("#2E4053"), corner_radius=8)
        cue_frame.pack(fill='x', padx=12, pady=(0, 8))
        ctk.CTkLabel(cue_frame, text="💡 Daily R&D investment drains cash each day until track is complete. Projects have upfront + daily costs.", 
                   font=config.FONT_BODY, text_color=config.COLOR_GOLD, wraplength=960, justify='left').pack(padx=10, pady=8)

        tabview = ctk.CTkTabview(rnd_window, width=950, height=700)
        tabview.pack(padx=20, pady=20, fill='both', expand=True)

        # --- R&D INVESTMENT TAB ---
        rnd_tab = tabview.add("R&D Investment")
        
        def update_rnd_status():
            # Function to re-render R&D section (called after an action)
            for widget in rnd_tab.winfo_children(): 
                # Re-render only the investment frames
                if widget.winfo_class() == 'CTkFrame': 
                    widget.destroy()

            ctk.CTkLabel(rnd_tab, text="Daily R&D Investment", font=config.FONT_HEADER, text_color=config.COLOR_GOLD).pack(pady=10)
            ctk.CTkLabel(rnd_tab, text=f"Current Daily Cost: ${corp.calculate_daily_rnd_cost():,.0f}", font=config.FONT_BODY, text_color=config.COLOR_TEXT).pack(pady=5)

            for track_name, track_data in config.RND_TRACKS.items():
                
                investment_frame = ctk.CTkFrame(rnd_tab, fg_color=config.COLOR_PANEL_BG)
                investment_frame.pack(fill='x', padx=20, pady=5)
                
                # Display current status
                current_investment = corp.daily_rnd_investment.get(track_name, 0)
                track_info = corp.technology_tracks.get(track_name, {'progress': 0, 'completed': False})
                current_points = track_info['progress']
                is_complete = track_info['completed']
                
                status_text = "✓ COMPLETE" if is_complete else f"{current_points:.0f}/{track_data['max_points']} pts"
                status_color = config.COLOR_SUCCESS_GREEN if is_complete else config.COLOR_GOLD
                
                header_row = ctk.CTkFrame(investment_frame, fg_color="transparent")
                header_row.pack(fill='x', padx=10, pady=(5, 0))
                ctk.CTkLabel(header_row, text=f"{track_name}", 
                            font=config.FONT_HEADER, anchor='w').pack(side=ctk.LEFT)
                ctk.CTkLabel(header_row, text=status_text, font=config.FONT_BODY, text_color=status_color, anchor='e').pack(side=ctk.RIGHT)
                
                # Input for new daily investment
                ctk.CTkLabel(investment_frame, text=f"Daily Investment: ${current_investment:,.0f} | Cost/Point: ${track_data['daily_cost_per_point']}", 
                            font=config.FONT_BODY, anchor='w', text_color=config.COLOR_ACCENT_NEUTRAL).pack(fill='x', padx=10, pady=(2, 4))
                
                if not is_complete:
                    new_investment_var = ctk.StringVar(value=f"{current_investment:,}")
                    
                    def make_setter(track, var):
                        def set_investment():
                            try:
                                amount = int(var.get().replace(',', ''))
                                if amount < 0: raise ValueError
                                
                                corp.daily_rnd_investment[track] = amount
                                messagebox.showinfo("R&D Update", f"Daily investment for {track} set to ${amount:,.0f}.")
                                update_rnd_status()
                                self._update_status()
                            except ValueError:
                                messagebox.showerror("Input Error", "Investment must be a non-negative whole number.")
                        return set_investment
                    
                    entry_row = ctk.CTkFrame(investment_frame, fg_color="transparent")
                    entry_row.pack(fill='x', padx=10, pady=(0, 10))
                    entry = ctk.CTkEntry(entry_row, textvariable=new_investment_var, width=200, justify=ctk.RIGHT)
                    entry.pack(side=ctk.LEFT, padx=(0, 10))
                    
                    ctk.CTkButton(entry_row, text="Set Investment", command=make_setter(track_name, new_investment_var), 
                                  fg_color=config.COLOR_ACCENT_NEUTRAL, font=config.FONT_BODY, width=140).pack(side=ctk.LEFT)
                else:
                    ctk.CTkLabel(investment_frame, text="Track completed. Investment stopped.", 
                               font=config.FONT_BODY, text_color=config.COLOR_SUCCESS_GREEN).pack(padx=10, pady=(0, 8))

        # --- NEW PROJECT TAB ---
        project_tab = tabview.add("New Strategic Project")
        
        if len(corp.projects) >= config.PROJECT_LIMIT:
            ctk.CTkLabel(project_tab, text=f"Project Limit Reached: {config.PROJECT_LIMIT}", font=config.FONT_TITLE, text_color=config.COLOR_ACCENT_DANGER).pack(pady=20)
        else:
            new_proj_frame = ctk.CTkFrame(project_tab, fg_color="transparent")
            new_proj_frame.pack(pady=10, padx=20, anchor='n')

            ctk.CTkLabel(new_proj_frame, text="Start a New Strategic Project", font=config.FONT_HEADER, text_color=config.COLOR_GOLD).pack(pady=10)
            
            # Name
            ctk.CTkLabel(new_proj_frame, text="Project Name:", font=config.FONT_BODY, text_color=config.COLOR_TEXT).pack(pady=(5, 0))
            name_entry = ctk.CTkEntry(new_proj_frame, width=300, font=config.FONT_BODY)
            name_entry.pack()

            # Total Cost
            ctk.CTkLabel(new_proj_frame, text="Total Project Investment:", font=config.FONT_BODY, text_color=config.COLOR_TEXT).pack(pady=(5, 0))
            cost_entry = ctk.CTkEntry(new_proj_frame, width=150, font=config.FONT_BODY, placeholder_text="10,000,000")
            cost_entry.pack()
            ctk.CTkLabel(new_proj_frame, text="💰 10% upfront cash + 90% added to debt", font=config.FONT_BODY, text_color=config.COLOR_GOLD).pack()
            ctk.CTkLabel(new_proj_frame, text="⚠️ Pick your timeline carefully - speed vs. safety trade-off", font=config.FONT_BODY, text_color=config.COLOR_ACCENT_DANGER).pack(pady=(0, 5))

            # Project Type
            type_options = {"R&D (Tech/Innovation)": 1, "Marketing (Customer/Rep)": 2, "Operations (Efficiency)": 3}
            type_var = ctk.StringVar(value=list(type_options.keys())[0])
            ctk.CTkLabel(new_proj_frame, text="Project Type:", font=config.FONT_BODY, text_color=config.COLOR_TEXT).pack(pady=(5, 0))
            type_menu = ctk.CTkOptionMenu(new_proj_frame, variable=type_var, values=list(type_options.keys()), width=300, font=config.FONT_BODY)
            type_menu.pack()

            # Duration (dropdown with fixed options)
            duration_options = ["10 days (90% risk)", "20 days (80% risk)", "30 days (70% risk)", 
                              "40 days (60% risk)", "50 days (50% risk)", "60 days (40% risk)",
                              "70 days (30% risk)", "80 days (20% risk)", "90 days (10% risk)", "100 days (5% risk)"]
            duration_var = ctk.StringVar(value=duration_options[4])  # Default to 50 days
            ctk.CTkLabel(new_proj_frame, text="Project Timeline:", font=config.FONT_BODY, text_color=config.COLOR_TEXT).pack(pady=(5, 0))
            duration_menu = ctk.CTkOptionMenu(new_proj_frame, variable=duration_var, values=duration_options, width=300, font=config.FONT_BODY)
            duration_menu.pack()
            ctk.CTkLabel(new_proj_frame, text="⏱️ Longer timelines = Lower risk, better success chance", 
                        font=(config.FONT_FAMILY, 9), text_color=config.COLOR_SUCCESS_GREEN).pack(pady=2)
            
            def start_project():
                if len(corp.projects) >= config.PROJECT_LIMIT:
                    messagebox.showerror("Limit Reached", f"Cannot start a new project. Max limit is {config.PROJECT_LIMIT}.")
                    return
                try:
                    name = name_entry.get()
                    cost = int(cost_entry.get().replace(',', ''))
                    p_type = type_options[type_var.get()]
                    
                    # Parse duration from selected option (e.g., "50 days (50% risk)" -> 50)
                    duration_text = duration_var.get()
                    duration = int(duration_text.split()[0])
                    
                    # Calculate risk: 10 days = 90%, 20 days = 80%, ..., 100 days = 5%
                    # Formula: risk = (110 - duration) / 100
                    risk = (110 - duration) / 100
                    # Clamp between 0.05 and 0.90
                    risk = max(0.05, min(0.90, risk))

                    if not name or cost <= 0:
                        raise ValueError
                        
                    upfront_cost = cost * 0.1
                    debt_amount = cost * 0.9  # 90% goes to debt

                    if corp.cash < upfront_cost:
                        messagebox.showerror("Error", f"Insufficient Cash. Upfront cost is ${upfront_cost:,.0f}.")
                        return
                    
                    if corp.debt + debt_amount > corp.max_debt_limit:
                        messagebox.showerror("Error", f"Project would exceed debt limit. Need ${debt_amount:,.0f} in available credit.")
                        return

                    new_project = Project(name, cost, risk, duration, p_type)
                    corp.cash -= upfront_cost
                    corp.debt += debt_amount  # Add 90% to debt
                    corp.log.append(f"Project '{name}' started: ${upfront_cost:,.0f} cash + ${debt_amount:,.0f} debt ({duration} days, {risk:.0%} risk)")
                    corp.projects.append(new_project)
                    messagebox.showinfo("Project Started", 
                        f"Strategic Project '{name}' initiated.\n\n" +
                        f"Upfront: ${upfront_cost:,.0f}\n" +
                        f"Financed: ${debt_amount:,.0f} (added to debt)\n" +
                        f"Duration: {duration} days\n" +
                        f"Risk Level: {risk:.0%}")
                    name_entry.delete(0, ctk.END)
                    cost_entry.delete(0, ctk.END)
                    self._update_status()
                    rnd_window.grab_set()
                except ValueError:
                    messagebox.showerror("Input Error", "Please ensure all fields are valid: Name is set and Cost is a positive integer.")

            ctk.CTkButton(new_proj_frame, text="Start Project", command=start_project, 
                          fg_color=config.COLOR_SUCCESS_GREEN, hover_color=("#4CAF50"), 
                          font=config.FONT_HEADER, width=250).pack(pady=20)


        # Initial call to set up the investment section
        update_rnd_status()
        
        ctk.CTkButton(rnd_window, text="Close", command=rnd_window.destroy, fg_color=config.COLOR_ACCENT_NEUTRAL, font=config.FONT_HEADER).pack(pady=10)


    def _open_budget_dialog(self):
        corp = self.game
        
        # Check action points
        if corp.action_points <= 0:
            messagebox.showwarning("No Actions Remaining", "You have no daily actions left. Advance to the next day or hire employees to automate tasks.")
            return
        
        # Deduct action point
        corp.action_points -= 1
        self._update_status()
        
        budget_window = ctk.CTkToplevel(self.master)
        budget_window.title("Annual Department Budget Allocation")
        budget_window.geometry("700x600")
        budget_window.attributes('-topmost', True)
        budget_window.grab_set()
        self._set_window_icon(budget_window)

        ctk.CTkLabel(budget_window, text="ANNUAL DEPARTMENT BUDGET ALLOCATION", font=config.FONT_TITLE, text_color=config.COLOR_ACCENT_PRIMARY).pack(pady=15)
        
        info_frame = ctk.CTkFrame(budget_window, fg_color=config.COLOR_ACCENT_DANGER, corner_radius=8)
        info_frame.pack(fill='x', padx=20, pady=(0, 10))
        
        ctk.CTkLabel(info_frame, text="⚠️ CRITICAL: Each department's annual budget controls what actions you can take. Email actions, projects, and initiatives deduct from the relevant department's budget. When a budget is depleted, actions for that department will fail. Budgets reset on the new year.", font=config.FONT_BODY, text_color="white", wraplength=650, justify=ctk.LEFT).pack(padx=15, pady=15)

        # Scrollable budget allocation frame
        scroll_frame = ctk.CTkScrollableFrame(budget_window, fg_color="transparent")
        scroll_frame.pack(fill='both', expand=True, padx=20, pady=10)

        budget_entries = {}
        remaining_labels = {}
        
        for dept in ['R&D', 'Marketing', 'Operations', 'HR']:
            dept_frame = ctk.CTkFrame(scroll_frame, fg_color=config.COLOR_PANEL_BG, corner_radius=10)
            dept_frame.pack(fill='x', pady=10)
            
            # Department header with color
            header_frame = ctk.CTkFrame(dept_frame, fg_color="transparent")
            header_frame.pack(fill='x', padx=15, pady=(10, 5))
            
            ctk.CTkLabel(header_frame, text=dept, font=config.FONT_HEADER, text_color=config.COLOR_ACCENT_PRIMARY).pack(side=ctk.LEFT)
            ctk.CTkLabel(header_frame, text=f"Annual Limit: ${corp.annual_budget[dept]:,.0f}", font=config.FONT_BODY, text_color=config.COLOR_ACCENT_NEUTRAL).pack(side=ctk.RIGHT)
            
            # Budget entry
            entry_frame = ctk.CTkFrame(dept_frame, fg_color="transparent")
            entry_frame.pack(fill='x', padx=15, pady=(0, 10))
            
            entry_var = ctk.StringVar(value=f"{corp.annual_budget[dept]:,}")
            entry = ctk.CTkEntry(entry_frame, textvariable=entry_var, width=250, font=config.FONT_BODY, justify=ctk.RIGHT)
            entry.pack(side=ctk.LEFT, padx=(0, 10))
            budget_entries[dept] = entry_var
            
            # Show spent + remaining
            spent = corp.budget_spent.get(dept, 0)
            remaining = corp.get_budget_remaining(dept)
            remaining_label = ctk.CTkLabel(entry_frame, text=f"Spent: ${spent:,.0f} | Remaining: ${remaining:,.0f}", font=config.FONT_BODY, text_color=config.COLOR_TEXT)
            remaining_label.pack(side=ctk.LEFT)
            remaining_labels[dept] = remaining_label

        # Action buttons
        button_frame = ctk.CTkFrame(budget_window, fg_color="transparent")
        button_frame.pack(fill='x', padx=20, pady=15)
        
        def apply_budgets():
            try:
                new_budgets = {}
                for dept, var in budget_entries.items():
                    amount = int(var.get().replace(',', ''))
                    if amount < corp.annual_budget[dept] * 0.5:  # Warn if cutting budget < 50%
                        if not messagebox.askyesno("Warning", f"{dept} budget is below 50% of annual allocation. Continue?"):
                            return
                    new_budgets[dept] = amount

                # Enforce cash backing: increasing total budget must be covered by available cash.
                current_total = sum(corp.annual_budget.values())
                new_total = sum(new_budgets.values())
                delta = new_total - current_total
                if delta > 0 and corp.cash < delta:
                    messagebox.showerror("Insufficient Cash", f"Need ${delta:,.0f} cash to raise budgets, but only ${corp.cash:,.0f} available.")
                    return

                # Apply cash movement (delta>0 consumes cash, delta<0 refunds cash)
                corp.cash -= delta
                corp.annual_budget.update(new_budgets)
                corp.log.append(f"Department annual budgets reallocated. Cash {'used' if delta>0 else 'returned'}: ${abs(delta):,.0f}.")
                messagebox.showinfo("Budget Update", "Annual department budgets updated and backed by cash.")
                budget_window.destroy()
                self._update_status()
            except ValueError:
                messagebox.showerror("Input Error", "All budgets must be positive whole numbers.")
        
        def reset_budgets():
            for dept in ['R&D', 'Marketing', 'Operations', 'HR']:
                budget_entries[dept].delete(0, ctk.END)
                budget_entries[dept].insert(0, f"{corp.annual_budget[dept]:,}")
        
        ctk.CTkButton(button_frame, text="Apply Budgets", command=apply_budgets, 
                      fg_color=config.COLOR_SUCCESS_GREEN, hover_color=("#4CAF50"), 
                      font=config.FONT_HEADER, width=150).pack(side=ctk.LEFT, padx=5)
        
        ctk.CTkButton(button_frame, text="Reset to Current", command=reset_budgets, 
                      fg_color=config.COLOR_ACCENT_NEUTRAL, font=config.FONT_HEADER, width=150).pack(side=ctk.LEFT, padx=5)
        
        ctk.CTkButton(button_frame, text="Close", command=budget_window.destroy, 
                      fg_color=config.COLOR_ACCENT_DANGER, font=config.FONT_HEADER, width=100).pack(side=ctk.RIGHT, padx=5)


    def _open_debt_equity_dialog(self):
        corp = self.game
        
        # Check action points
        if corp.action_points <= 0:
            messagebox.showwarning("No Actions Remaining", "You have no daily actions left. Advance to the next day or hire employees to automate tasks.")
            return
        
        # Deduct action point
        corp.action_points -= 1
        self._update_status()
        
        debt_window = ctk.CTkToplevel(self.master)
        debt_window.title("Debt and Equity Management")
        debt_window.geometry("600x500")
        debt_window.attributes('-topmost', True)
        debt_window.grab_set()
        self._set_window_icon(debt_window)

        ctk.CTkLabel(debt_window, text="Debt and Equity Management", font=config.FONT_TITLE, text_color=config.COLOR_ACCENT_PRIMARY).pack(pady=10)
        
        # Calculate and display debt limit
        confidence_multiplier = 0.5 + (corp.board_confidence / 100) * 1.5
        debt_limit = corp.max_debt_limit * confidence_multiplier
        debt_utilization = (corp.debt / debt_limit * 100) if debt_limit > 0 else 0
        limit_color = config.COLOR_SUCCESS_GREEN if debt_utilization < 50 else (config.COLOR_GOLD if debt_utilization < 80 else config.COLOR_ACCENT_DANGER)
        
        ctk.CTkLabel(debt_window, text=f"Current Debt: ${corp.debt:,.0f} | Cash: ${corp.cash:,.0f}", font=config.FONT_HEADER).pack(pady=(0, 5))
        ctk.CTkLabel(debt_window, text=f"Borrowing Limit: ${debt_limit:,.0f} ({debt_utilization:.0f}% used) | Board Confidence: {corp.board_confidence:.0f}%", 
                   font=config.FONT_BODY, text_color=limit_color).pack(pady=(0, 10))

        # --- BORROW DEBT ---
        borrow_frame = ctk.CTkFrame(debt_window, fg_color=config.COLOR_PANEL_BG)
        borrow_frame.pack(fill='x', padx=20, pady=5)
        ctk.CTkLabel(borrow_frame, text="Borrow Funds (Increases Debt):", font=config.FONT_HEADER, text_color=config.COLOR_ACCENT_PRIMARY).pack(anchor='w', padx=10, pady=5)
        
        borrow_amount_var = ctk.StringVar(value="10,000,000")
        borrow_entry = ctk.CTkEntry(borrow_frame, textvariable=borrow_amount_var, width=200, font=config.FONT_BODY, justify=ctk.RIGHT)
        borrow_entry.pack(side=ctk.LEFT, padx=10, pady=10)
        
        def borrow():
            try:
                amount = int(borrow_amount_var.get().replace(',', ''))
                if amount <= 0: raise ValueError
                result = corp.manage_debt_equity('Borrow', amount)
                messagebox.showinfo("Borrow Result", result)
                self._update_status()
                debt_window.destroy()
            except ValueError:
                messagebox.showerror("Input Error", "Invalid borrowing amount.")

        ctk.CTkButton(borrow_frame, text="Borrow Funds", command=borrow, fg_color=config.COLOR_SUCCESS_GREEN, hover_color=("#4CAF50"), font=config.FONT_HEADER).pack(side=ctk.LEFT, padx=10, pady=10)

        # --- REPAY DEBT ---
        repay_frame = ctk.CTkFrame(debt_window, fg_color=config.COLOR_PANEL_BG)
        repay_frame.pack(fill='x', padx=20, pady=5)
        ctk.CTkLabel(repay_frame, text="Repay Debt (Decreases Cash):", font=config.FONT_HEADER, text_color=config.COLOR_ACCENT_DANGER).pack(anchor='w', padx=10, pady=5)

        repay_amount_var = ctk.StringVar(value="1,000,000")
        repay_entry = ctk.CTkEntry(repay_frame, textvariable=repay_amount_var, width=200, font=config.FONT_BODY, justify=ctk.RIGHT)
        repay_entry.pack(side=ctk.LEFT, padx=10, pady=10)

        def repay():
            try:
                amount = int(repay_amount_var.get().replace(',', ''))
                if amount <= 0: raise ValueError
                result = corp.manage_debt_equity('Repay', amount)
                messagebox.showinfo("Repay Result", result)
                self._update_status()
                debt_window.destroy()
            except ValueError:
                messagebox.showerror("Input Error", "Invalid repayment amount.")

        ctk.CTkButton(repay_frame, text="Repay Debt", command=repay, fg_color=config.COLOR_ACCENT_DANGER, hover_color=("#C0392B"), font=config.FONT_HEADER).pack(side=ctk.LEFT, padx=10, pady=10)
        
        ctk.CTkButton(debt_window, text="Close", command=debt_window.destroy, fg_color=config.COLOR_ACCENT_NEUTRAL, font=config.FONT_HEADER).pack(pady=10)


    def _open_ma_dialog(self):
        corp = self.game
        
        # Check action points
        if corp.action_points <= 0:
            messagebox.showwarning("No Actions Remaining", "You have no daily actions left. Advance to the next day or hire employees to automate tasks.")
            return
        
        # Deduct action point
        corp.action_points -= 1
        self._update_status()
        
        ma_window = ctk.CTkToplevel(self.master)
        ma_window.title("Mergers & Acquisitions")
        ma_window.geometry("600x450")
        ma_window.attributes('-topmost', True)
        ma_window.grab_set()
        self._set_window_icon(ma_window)

        ctk.CTkLabel(ma_window, text="Mergers & Acquisitions / Divestiture", font=config.FONT_TITLE, text_color=config.COLOR_ACCENT_PRIMARY).pack(pady=10)
        ctk.CTkLabel(ma_window, text=f"Cash: ${corp.cash:,.0f} | Market Cap: ${corp.market_cap:,.0f}", font=config.FONT_HEADER).pack(pady=(0, 10))

        # --- ACQUIRE (BUY) ---
        acquire_frame = ctk.CTkFrame(ma_window, fg_color=config.COLOR_PANEL_BG)
        acquire_frame.pack(fill='x', padx=20, pady=5)
        ctk.CTkLabel(acquire_frame, text="Acquire Competitor (Costly, High Risk)", font=config.FONT_HEADER, text_color=config.COLOR_ACCENT_PRIMARY).pack(anchor='w', padx=10, pady=5)
        
        acquire_amount_var = ctk.StringVar(value="500,000,000")
        acquire_entry = ctk.CTkEntry(acquire_frame, textvariable=acquire_amount_var, width=200, font=config.FONT_BODY, justify=ctk.RIGHT)
        acquire_entry.pack(side=ctk.LEFT, padx=10, pady=10)
        
        def acquire():
            try:
                amount = int(acquire_amount_var.get().replace(',', ''))
                if amount <= 0: raise ValueError
                result = corp.manage_manda_actions('Acquire', amount)
                messagebox.showinfo("Acquisition Result", result)
                self._update_status()
                ma_window.destroy()
            except ValueError:
                messagebox.showerror("Input Error", "Invalid amount. Must be a positive whole number.")

        ctk.CTkButton(acquire_frame, text="Acquire", command=acquire, fg_color=config.COLOR_SUCCESS_GREEN, hover_color=("#4CAF50"), font=config.FONT_HEADER).pack(side=ctk.LEFT, padx=10, pady=10)

        # --- DIVEST (SELL) ---
        divest_frame = ctk.CTkFrame(ma_window, fg_color=config.COLOR_PANEL_BG)
        divest_frame.pack(fill='x', padx=20, pady=5)
        ctk.CTkLabel(divest_frame, text="Divest Non-Core Assets (Gains Cash, Lowers Tech)", font=config.FONT_HEADER, text_color=config.COLOR_ACCENT_DANGER).pack(anchor='w', padx=10, pady=5)

        divest_amount_var = ctk.StringVar(value="50,000,000")
        divest_entry = ctk.CTkEntry(divest_frame, textvariable=divest_amount_var, width=200, font=config.FONT_BODY, justify=ctk.RIGHT)
        divest_entry.pack(side=ctk.LEFT, padx=10, pady=10)

        def divest():
            try:
                amount = int(divest_amount_var.get().replace(',', ''))
                if amount <= 0: raise ValueError
                result = corp.manage_manda_actions('Divest', amount)
                messagebox.showinfo("Divestiture Result", result)
                self._update_status()
                ma_window.destroy()
            except ValueError:
                messagebox.showerror("Input Error", "Invalid amount. Must be a positive whole number.")

        ctk.CTkButton(divest_frame, text="Divest", command=divest, fg_color=config.COLOR_ACCENT_DANGER, hover_color=("#C0392B"), font=config.FONT_HEADER).pack(side=ctk.LEFT, padx=10, pady=10)
        
        ctk.CTkButton(ma_window, text="Close", command=ma_window.destroy, fg_color=config.COLOR_ACCENT_NEUTRAL, font=config.FONT_HEADER).pack(pady=10)


    def _open_market_shift_dialog(self):
        corp = self.game
        
        # Check action points
        if corp.action_points <= 0:
            messagebox.showwarning("No Actions Remaining", "You have no daily actions left. Advance to the next day or hire employees to automate tasks.")
            return
        
        # Deduct action point
        corp.action_points -= 1
        self._update_status()
        
        shift_window = ctk.CTkToplevel(self.master)
        shift_window.title("Shift Market Focus")
        shift_window.geometry("500x350")
        shift_window.attributes('-topmost', True)
        shift_window.grab_set()
        self._set_window_icon(shift_window)

        ctk.CTkLabel(shift_window, text="Shift Market Focus", font=config.FONT_TITLE, text_color=config.COLOR_ACCENT_PRIMARY).pack(pady=10)
        ctk.CTkLabel(shift_window, text="Shifting focus costs cash but permanently changes market segment focus.", font=config.FONT_BODY).pack(pady=(0, 10))

        # Cost
        cost_frame = ctk.CTkFrame(shift_window, fg_color=config.COLOR_PANEL_BG)
        cost_frame.pack(fill='x', padx=20, pady=5)
        ctk.CTkLabel(cost_frame, text="Cost of Campaign ($):", font=config.FONT_BODY, width=150, anchor='w').pack(side=ctk.LEFT, padx=10)
        cost_var = ctk.StringVar(value="10,000,000")
        cost_entry = ctk.CTkEntry(cost_frame, textvariable=cost_var, width=200, font=config.FONT_BODY, justify=ctk.RIGHT)
        cost_entry.pack(side=ctk.RIGHT, padx=10)

        # Target Segment
        segment_frame = ctk.CTkFrame(shift_window, fg_color=config.COLOR_PANEL_BG)
        segment_frame.pack(fill='x', padx=20, pady=5)
        ctk.CTkLabel(segment_frame, text="Target Market Segment:", font=config.FONT_BODY, width=150, anchor='w').pack(side=ctk.LEFT, padx=10)
        
        segment_options = list(corp.market_segments.keys())
        segment_var = ctk.StringVar(value=segment_options[0])
        segment_menu = ctk.CTkOptionMenu(segment_frame, variable=segment_var, values=segment_options, width=200)
        segment_menu.pack(side=ctk.RIGHT, padx=10)
        
        def submit():
            try:
                cost = int(cost_var.get().replace(',', ''))
                segment = segment_var.get()

                if cost <= 0: raise ValueError("Cost must be positive.")

                result = corp.manage_manda_actions('Market_Shift', cost, target_segment=segment)
                messagebox.showinfo("Market Shift Result", result)
                self._update_status()
                shift_window.destroy()
            except ValueError:
                messagebox.showerror("Input Error", "Invalid cost. Must be a positive whole number.")
            except Exception as e:
                messagebox.showerror("Error", f"Action failed: {e}")

        ctk.CTkButton(shift_window, text="Execute Market Shift", command=submit, fg_color=config.COLOR_ACCENT_PRIMARY, font=config.FONT_HEADER, width=250).pack(pady=15)
        ctk.CTkButton(shift_window, text="Close", command=shift_window.destroy, fg_color=config.COLOR_ACCENT_NEUTRAL, font=config.FONT_HEADER).pack(pady=5)


    def _open_expense_dialog(self):
        corp = self.game
        
        # Check action points
        if corp.action_points <= 0:
            messagebox.showwarning("No Actions Remaining", "You have no daily actions left. Advance to the next day or hire employees to automate tasks.")
            return
        
        # Deduct action point
        corp.action_points -= 1
        self._update_status()
        
        expense_window = ctk.CTkToplevel(self.master)
        expense_window.title("Corporate Card Expenses")
        expense_window.geometry("500x400")
        expense_window.attributes('-topmost', True)
        expense_window.grab_set()
        self._set_window_icon(expense_window)

        ctk.CTkLabel(expense_window, text="Corporate Card Expenses", font=config.FONT_TITLE, text_color=config.COLOR_ACCENT_PRIMARY).pack(pady=10)
        ctk.CTkLabel(expense_window, text=f"Limit: ${corp.corp_card_limit:,.0f} | Used Today: ${corp.corp_card_used:,.0f}", font=config.FONT_HEADER, text_color=config.COLOR_GOLD).pack(pady=(0, 10))

        # Expense Type Selection
        expense_options = {
            "Executive Retreat ($5,000,000)": 5_000_000, 
            "Lobbyist Fee ($2,000,000)": 2_000_000, 
            "Luxury Travel ($500,000)": 500_000,
            "Office Decor Upgrade ($100,000)": 100_000
        }
        
        ctk.CTkLabel(expense_window, text="Select Expense:", font=config.FONT_BODY).pack(pady=(5, 0))
        expense_keys = list(expense_options.keys())
        selected_key = ctk.StringVar(value=expense_keys[0])
        expense_menu = ctk.CTkOptionMenu(expense_window, variable=selected_key, values=expense_keys, width=350)
        expense_menu.pack(pady=10)

        def submit_expense():
            try:
                expense_type = selected_key.get()
                expense_cost = expense_options[expense_type]
                
                if corp.corp_card_used + expense_cost > corp.corp_card_limit:
                    messagebox.showerror("Limit Exceeded", f"This expense of ${expense_cost:,.0f} would exceed your Corporate Card limit of ${corp.corp_card_limit:,.0f}.")
                    return
                
                result = corp.use_corp_card(expense_type)
                messagebox.showinfo("Expense Result", result)
                expense_window.destroy()
                self._update_status()
            except Exception as e:
                messagebox.showerror("Error", f"Action failed: {e}")

        ctk.CTkButton(expense_window, text="Charge to Corporate Card", command=submit_expense, fg_color=config.COLOR_ACCENT_PRIMARY, font=config.FONT_HEADER, width=250).pack(pady=15)
        ctk.CTkButton(expense_window, text="Close", command=expense_window.destroy, fg_color=config.COLOR_ACCENT_NEUTRAL, font=config.FONT_HEADER).pack(pady=5)


    def _open_exec_team_dialog(self):
        """Executive Team hiring dialog for C-suite officers."""
        corp = self.game
        
        # Check action points
        if corp.action_points <= 0:
            messagebox.showwarning("No Actions Remaining", "You have no daily actions left.")
            return
        
        # Deduct action point
        corp.action_points -= 1
        self._update_status()
        
        exec_window = ctk.CTkToplevel(self.master)
        exec_window.title("Executive Team")
        exec_window.geometry("1000x700")
        exec_window.attributes('-topmost', True)
        exec_window.grab_set()
        self._set_window_icon(exec_window)

        ctk.CTkLabel(exec_window, text="👔 Executive Team (C-Suite)", font=config.FONT_TITLE, text_color=config.COLOR_ACCENT_PRIMARY).pack(pady=10)
        
        # Show current executives
        current_frame = ctk.CTkFrame(exec_window, fg_color=config.COLOR_PANEL_BG)
        current_frame.pack(fill='x', padx=15, pady=10)
        ctk.CTkLabel(current_frame, text="Current C-Suite:", font=config.FONT_HEADER, text_color=config.COLOR_GOLD).pack(anchor='w', padx=10, pady=5)
        
        if not corp.executives:
            ctk.CTkLabel(current_frame, text="No executives hired yet.", font=config.FONT_BODY, text_color=config.COLOR_ACCENT_NEUTRAL).pack(padx=10, pady=5)
        else:
            for exec in corp.executives:
                row = ctk.CTkFrame(current_frame, fg_color="transparent")
                row.pack(fill='x', padx=10, pady=3)
                ctk.CTkLabel(row, text=f"{exec.role}: {exec.name} ({exec.personality})", font=config.FONT_HEADER, anchor='w').pack(side=ctk.LEFT, padx=5)
                ctk.CTkLabel(row, text=f"Satisfaction: {exec.satisfaction}%", font=config.FONT_BODY, text_color=config.COLOR_SUCCESS_GREEN if exec.satisfaction > 70 else config.COLOR_ACCENT_DANGER).pack(side=ctk.RIGHT, padx=5)
        
        # Scrollable candidates area
        ctk.CTkLabel(exec_window, text="Available Candidates:", font=config.FONT_HEADER).pack(pady=(10, 5))
        scroll_frame = ctk.CTkScrollableFrame(exec_window, fg_color="transparent", height=450)
        scroll_frame.pack(fill='both', expand=True, padx=15, pady=5)
        
        def hire_exec(role, candidate):
            # Check if role already filled
            if role == "CFO" and corp.cfo:
                messagebox.showwarning("Position Filled", "CFO position already filled.")
                return
            if role == "CTO" and corp.cto:
                messagebox.showwarning("Position Filled", "CTO position already filled.")
                return
            if role == "CMO" and corp.cmo:
                messagebox.showwarning("Position Filled", "CMO position already filled.")
                return
            
            # Check action points
            if corp.action_points < 1:
                messagebox.showwarning("No Action Points", "Hiring executives requires 1 action point.")
                return
            
            cost = candidate['cost']
            if corp.cash < cost:
                messagebox.showwarning("Insufficient Cash", f"Need ${cost:,.0f} to hire this executive.")
                return
            
            corp.cash -= cost
            corp.action_points -= 1
            from game_core import Executive
            exec_obj = Executive(candidate['name'], role, cost, candidate['personality'])
            exec_obj.hired_day = corp.day
            corp.executives.append(exec_obj)
            
            if role == "CFO":
                corp.cfo = exec_obj
            elif role == "CTO":
                corp.cto = exec_obj
            elif role == "CMO":
                corp.cmo = exec_obj
            
            corp.log.append(f"Hired {exec_obj.name} as {role}. Personality: {exec_obj.personality}. -1 action point.")
            messagebox.showinfo("Hire Success", f"{exec_obj.name} hired as {role}!")
            exec_window.destroy()
            self._update_status()
        
        # Display candidates by role
        for role in ["CFO", "CTO", "CMO"]:
            role_frame = ctk.CTkFrame(scroll_frame, fg_color=config.COLOR_PANEL_BG, corner_radius=10)
            role_frame.pack(fill='x', pady=10)
            
            ctk.CTkLabel(role_frame, text=f"{role} Candidates", font=config.FONT_HEADER, text_color=config.COLOR_GOLD).pack(anchor='w', padx=10, pady=8)
            
            for candidate in config.EXECUTIVE_CANDIDATES[role]:
                card = ctk.CTkFrame(role_frame, fg_color=config.COLOR_MAIN_BG, corner_radius=8)
                card.pack(fill='x', padx=10, pady=5)
                
                top_row = ctk.CTkFrame(card, fg_color="transparent")
                top_row.pack(fill='x', padx=10, pady=8)
                
                ctk.CTkLabel(top_row, text=candidate['name'], font=config.FONT_HEADER, text_color=config.COLOR_TEXT).pack(side=ctk.LEFT)
                ctk.CTkLabel(top_row, text=f"${candidate['cost']/1000000:.0f}M", font=config.FONT_HEADER, text_color=config.COLOR_GOLD).pack(side=ctk.RIGHT)
                
                ctk.CTkLabel(card, text=f"Personality: {candidate['personality']}", font=config.FONT_BODY, text_color=config.COLOR_ACCENT_PRIMARY).pack(anchor='w', padx=10)
                ctk.CTkLabel(card, text=candidate['description'], font=config.FONT_BODY, text_color=config.COLOR_ACCENT_NEUTRAL, wraplength=900, justify='left').pack(anchor='w', padx=10, pady=(0, 5))
                
                ctk.CTkButton(card, text="Hire", command=lambda r=role, c=candidate: hire_exec(r, c),
                            fg_color=config.COLOR_SUCCESS_GREEN, hover_color=("#4CAF50"), width=100, height=32).pack(padx=10, pady=(0, 8))
        
        ctk.CTkButton(exec_window, text="Close", command=exec_window.destroy, fg_color=config.COLOR_ACCENT_NEUTRAL, font=config.FONT_HEADER).pack(pady=10)
    
    def _open_union_dialog(self):
        """Union negotiation dialog."""
        corp = self.game
        
        union_window = ctk.CTkToplevel(self.master)
        union_window.title("Union Relations")
        union_window.geometry("800x600")
        union_window.attributes('-topmost', True)
        union_window.grab_set()
        self._set_window_icon(union_window)

        ctk.CTkLabel(union_window, text="🪧 Union Relations", font=config.FONT_TITLE, text_color=config.COLOR_ACCENT_PRIMARY).pack(pady=10)
        
        # Union status
        status_frame = ctk.CTkFrame(union_window, fg_color=config.COLOR_PANEL_BG)
        status_frame.pack(fill='x', padx=15, pady=10)
        
        if corp.union_status is None:
            ctk.CTkLabel(status_frame, text="✅ No Union Activity", font=config.FONT_HEADER, text_color=config.COLOR_SUCCESS_GREEN).pack(padx=10, pady=10)
            ctk.CTkLabel(status_frame, text="Employees are not currently organizing. Keep morale above 40% to prevent unionization.", 
                       font=config.FONT_BODY, text_color=config.COLOR_TEXT, wraplength=750).pack(padx=10, pady=5)
        elif corp.union_status == "Forming":
            ctk.CTkLabel(status_frame, text="⚠️ Union Forming", font=config.FONT_HEADER, text_color=config.COLOR_GOLD).pack(padx=10, pady=10)
            ctk.CTkLabel(status_frame, text=f"Union Strength: {corp.union_strength}% | Improve morale to stop organizing efforts.", 
                       font=config.FONT_BODY, text_color=config.COLOR_TEXT).pack(padx=10, pady=5)
        elif corp.union_status == "Active":
            ctk.CTkLabel(status_frame, text="🪧 Union Active - Demands Pending", font=config.FONT_HEADER, text_color=config.COLOR_ACCENT_DANGER).pack(padx=10, pady=10)
            ctk.CTkLabel(status_frame, text=f"Strike Countdown: {corp.strike_countdown} days | You must respond to union demands.", 
                       font=config.FONT_BODY, text_color=config.COLOR_ACCENT_DANGER).pack(padx=10, pady=5)
        
        # Display demands if active
        if corp.union_status == "Active" and corp.union_demands:
            ctk.CTkLabel(union_window, text="Union Demands:", font=config.FONT_HEADER).pack(pady=(10, 5))
            
            demands_frame = ctk.CTkScrollableFrame(union_window, fg_color="transparent", height=300)
            demands_frame.pack(fill='both', expand=True, padx=15, pady=5)
            
            for i, demand in enumerate(corp.union_demands):
                card = ctk.CTkFrame(demands_frame, fg_color=config.COLOR_PANEL_BG, corner_radius=10)
                card.pack(fill='x', pady=8)
                
                ctk.CTkLabel(card, text=f"Demand #{i+1}: {demand['description']}", font=config.FONT_HEADER, text_color=config.COLOR_TEXT).pack(anchor='w', padx=10, pady=8)
                
                if demand.get('cost', 0) > 0:
                    ctk.CTkLabel(card, text=f"Cost: ${demand['cost']:,.0f}", font=config.FONT_BODY, text_color=config.COLOR_GOLD).pack(anchor='w', padx=10)
                
                btn_frame = ctk.CTkFrame(card, fg_color="transparent")
                btn_frame.pack(fill='x', padx=10, pady=8)
                
                def resolve(idx, act):
                    result = corp.resolve_union_demand(idx, act)
                    messagebox.showinfo("Union Response", result)
                    union_window.destroy()
                    self._update_status()
                
                ctk.CTkButton(btn_frame, text="Accept", command=lambda idx=i: resolve(idx, "Accept"),
                            fg_color=config.COLOR_SUCCESS_GREEN, width=120).pack(side=ctk.LEFT, padx=5)
                ctk.CTkButton(btn_frame, text="Counter-Offer", command=lambda idx=i: resolve(idx, "Counter"),
                            fg_color=config.COLOR_GOLD, width=120).pack(side=ctk.LEFT, padx=5)
                ctk.CTkButton(btn_frame, text="Ignore", command=lambda idx=i: resolve(idx, "Ignore"),
                            fg_color=config.COLOR_ACCENT_DANGER, width=120).pack(side=ctk.LEFT, padx=5)
        
        ctk.CTkButton(union_window, text="Close", command=union_window.destroy, fg_color=config.COLOR_ACCENT_NEUTRAL, font=config.FONT_HEADER).pack(pady=10)
    



# --- Mock Classes for Testing/Debugging ---
# This is used for quick UI testing without running full game logic.
class MockCorporation:
    def __init__(self):
        # Game State
        self.day = 1
        self.quarter = 1
        self.year = 1
        self.log = deque(["Welcome to the game log..."], maxlen=20)
        self.corp_name = "MockCorp"
        self.ceo_name = "MockCEO"
        
        # Financials
        self.cash = 50000000  # Scaled 50%
        self.debt = 25000000
        self.stock_price = 12.50
        self.market_cap = 125000000
        self.shares_outstanding = 5000000
        self.quarterly_revenue = 200000000
        self.previous_quarter_revenue = 190000000
        self.quarterly_costs = 100000000
        self.analyst_rating = "Hold"
        
        # Core Metrics
        self.reputation = 25  # Scaled 50%
        self.employee_morale = 38
        self.ceo_health = 50
        self.board_confidence = 35
        self.technology_level = 25
        self.customer_base = 25
        self.market_mood = "Stable"
        self.current_scenario = "Stable"

        # Departments
        self.dept_efficiency = {'R&D': 25, 'Marketing': 25, 'Operations': 25, 'HR': 25}  # Scaled 50%
        self.market_segments = {'B2B': 25, 'Consumer': 25}
        self.departments = {'R&D': 20000000, 'Marketing': 20000000, 'Operations': 20000000, 'HR': 20000000}
        
        # Projects/R&D
        self.projects = []
        
        # Corporate Card (Used in expense dialog)
        self.corp_card_limit = 10000000
        self.corp_card_used = 10000
        
        self.department_budgets = {'R&D': 20000000, 'Marketing': 20000000, 'Operations': 20000000, 'HR': 20000000}
        self.POPUP_EVENTS = {}
        self.ACTION_PROMPT = None

        # --- FIX START ---
        self.daily_rnd_investment = {} # Added missing attribute to fix AttributeError in calculate_daily_rnd_cost
        # --- FIX END ---
        

    def update_day(self): return "OK"
    def calculate_efficiency(self): pass
    def calculate_daily_rnd_cost(self): self.daily_rnd_cost = sum(self.daily_rnd_investment.values())
    def set_identity(self, corp_name, ceo_name, email_system): 
        self.corp_name = corp_name
        self.ceo_name = ceo_name
    def process_earnings_call(self, score): return f"Call processed with score {score}."
    def manage_debt_equity(self, action, amount): return f"{action} of ${amount:,.0f} executed."
    def manage_manda_actions(self, action, amount, **kwargs): return f"{action} of ${amount:,.0f} executed."
    def adjust_budget(self, new_budgets): return "Budgets adjusted."
    def use_corp_card(self, expense_type): 
        # Mock usage to allow the dialog to work
        self.corp_card_used += 100000 
        return f"Expense '{expense_type}' charged to card."


class MockEmailSystem:
    def __init__(self, corp): 
        self.inbox = [{'from': 'CMO', 'subject': 'URGENT: New Product Launch', 'body': 'Competitor just undercut us.', 'options': [{'text': 'Acknowledge', 'impact': lambda self: "OK"}]}]
        self.POPUP_EVENTS = {}
        self.ACTION_PROMPT = None
    def check_for_events(self): return None 
    def apply_action(self, email_index, option_index): return "Mock action executed." 


# If the code is running in a development/test environment, replace the real Corporation with the MockCorporation
# To activate, set environment variable MOCK_MODE=True (e.g., in a Windows command prompt: set MOCK_MODE=True)
if os.environ.get('MOCK_MODE') == 'True':
    print("MOCK MODE ACTIVE: Using MockCorporation and MockEmailSystem for UI development.")
    from game_core import Corporation as RealCorporation # Preserve original
    from event_system import EmailSystem as RealEmailSystem # Preserve original
    Corporation = MockCorporation
    EmailSystem = MockEmailSystem
    
if __name__ == "__main__":
    try:
        root = ctk.CTk()
        app = CEOGameApp(root)
        root.mainloop()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        # In modern_ui.py, inside the CEOGameApp class:

    def _show_popup_event(self, event_id):
        """Displays a custom popup window for mandatory or random events."""
        event_data = self.game.email_system.POPUP_EVENTS.get(event_id)
        
        if not event_data:
            self.advance_button.configure(state="normal")
            return

        is_mandatory = (event_id == self.game.email_system.ACTION_PROMPT)
        
        # Disable main UI while popup is active
        self.advance_button.configure(state="disabled") 

        popup = ctk.CTkToplevel(self.master)
        popup.title(f"{event_data['category']} Event")
        popup.grab_set() # Modal window
        popup.attributes('-topmost', True)
        popup.geometry("600x400")
        self._set_window_icon(popup)
        
        # Title
        title_text = "MANDATORY ACTION" if is_mandatory else "CRITICAL DECISION"
        ctk.CTkLabel(popup, text=title_text, font=config.FONT_HEADER).pack(pady=10)
        
        # Dialogue Text
        dialogue_frame = ctk.CTkFrame(popup)
        dialogue_frame.pack(padx=20, pady=5, fill="x")
        ctk.CTkLabel(dialogue_frame, 
                     text=event_data['dialogue'], 
                     font=config.FONT_BODY, 
                     wraplength=550, 
                     justify="left").pack(padx=10, pady=10)

        # Choice Buttons Frame
        choices_frame = ctk.CTkFrame(popup, fg_color="transparent")
        choices_frame.pack(pady=10, padx=20)
        
        def process_choice(choice_index):
            # 1. Execute the function stored in the event data
            choice_func = event_data['choices'][choice_index][1]
            result_message = choice_func(self.game.email_system)
            
            # 2. Cleanup and unlock
            if event_id in self.game.email_system.POPUP_EVENTS:
                del self.game.email_system.POPUP_EVENTS[event_id]
            
            if is_mandatory:
                self.game.email_system.ACTION_PROMPT = None
            
            # 3. Update UI and show result
            self._update_status()
            messagebox.showinfo("Event Result", result_message)
            popup.destroy()
            
            # 4. Re-enable the main button
            self.advance_button.configure(state="normal") 

        # Create buttons for each choice
        for i, (text, func, impact_type) in enumerate(event_data['choices']):
            color = config.COLOR_ACCENT_PRIMARY
            # Apply color coding for better UX
            if 'BAD' in event_data['category'] and 'RISK_HIGH' in impact_type:
                 color = config.COLOR_ACCENT_DANGER
            elif 'GOOD' in event_data['category'] and 'GAIN_HIGH' in impact_type:
                 color = config.COLOR_SUCCESS_GREEN
                 
            ctk.CTkButton(choices_frame, 
                          text=f"[{i+1}] {text}", 
                          command=lambda i=i: process_choice(i),
                          fg_color=color,
                          hover_color=color).pack(pady=5, fill="x")


# B. Modify your existing _advance_day method (or whatever is bound to your button):

# This is an assumed structure. Integrate the bold lines into your actual function.

    def _advance_day(self):
        # Prevent double-clicking
        self.advance_button.configure(state="disabled") 
        
        # 1. Process the day
        self.game.process_day()
        self._update_status()
        
        # 2. Check for pop-up events (Mandatory or Random)
        event_id = self.game.email_system.check_for_events()
        
        if event_id:
            # All popups are now handled by this function
            self._show_popup_event(event_id) 
            # The button will be re-enabled inside _show_popup_event after the choice.
        else:
            # Re-enable the button if no popup is shown
            self.advance_button.configure(state="normal") 

        # Check for game over condition
        if self.game.game_over_check():
            messagebox.showinfo("Game Over", self.game.game_over_reason)
            self.master.destroy()
    
    def _generate_ticker_headlines(self):
        """Generate rotating news headlines (mix of company-specific and general market news)."""
        corp = self.game
        
        # Company-specific headlines (30% chance)
        company_news = [
            f"🔹 {corp.corp_name} stock ${corp.stock_price:.2f} ({'+' if corp.stock_price > 25 else ''}{((corp.stock_price-25)/25*100):.1f}%)",
            f"🔹 Analysts rate {corp.corp_name} as '{corp.analyst_rating}' - Credit: {corp.credit_rating}",
            f"🔹 {corp.corp_name} holds {corp.customer_base:.0f}% market share in key segments",
            f"🔹 CEO {corp.ceo_name} leads {corp.corp_name} through {corp.current_scenario.lower()} conditions",
            f"🔹 {corp.corp_name} market cap reaches ${corp.market_cap/1e6:.0f}M with {corp.shares_outstanding/1e6:.1f}M shares",
        ]
        
        # General market headlines (70%)
        general_news = [
            "📊 Dow Jones up 0.8% on strong manufacturing data",
            "💹 Tech sector rallies amid AI breakthrough announcements",
            "🏦 Federal Reserve holds rates steady, inflation concerns ease",
            "🌍 Global supply chains normalize after recent disruptions",
            "💼 Corporate earnings beat expectations across sectors",
            "⚡ Energy prices stabilize following OPEC+ production deal",
            "🚀 Space industry sees $5B in new venture capital funding",
            "🏭 Manufacturing PMI hits 18-month high",
            "💻 Cybersecurity spending surges 40% year-over-year",
            "🌱 ESG investments reach record $8.4 trillion globally",
            "📱 Consumer tech sales exceed Q4 projections",
            "🔬 Biotech sector gains on FDA fast-track approvals",
            "🏢 Commercial real estate shows signs of recovery",
            "⚙️ Industrial automation adoption accelerates",
            "🛒 E-commerce growth maintains double-digit pace",
            "🎮 Gaming industry revenue tops $200B milestone",
            "🚗 Electric vehicle sales up 65% this quarter",
            "☁️ Cloud computing market expands to $500B",
            "📡 5G infrastructure rollout ahead of schedule",
            "💊 Healthcare costs stabilize for first time in decade"
        ]
        
        # Mix headlines: 2 company-specific, 6 general
        self.ticker_headlines = random.sample(company_news, 2) + random.sample(general_news, 6)
        random.shuffle(self.ticker_headlines)
        self.ticker_index = 0
    
    def _update_ticker(self):
        """Rotate through headlines every 4 seconds."""
        if self.ticker_headlines:
            headline = self.ticker_headlines[self.ticker_index]
            self.ticker_label.configure(text=headline)
            self.ticker_index = (self.ticker_index + 1) % len(self.ticker_headlines)
            
            # Regenerate headlines every full cycle
            if self.ticker_index == 0:
                self._generate_ticker_headlines()
        
        # Schedule next update
        self.master.after(4000, self._update_ticker)

if __name__ == "__main__":
    root = ctk.CTk()
    app = CEOGameApp(root)
    root.mainloop()
