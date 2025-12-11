# event_system.py
import random
import config # Requires config.py to be in the same directory

# --- Email System Class ---
class EmailSystem:
    def __init__(self, corp):
        self.corp = corp
        self.inbox = []
        self.POPUP_EVENTS = {}
        # Coaching emails can be toggled from UI settings
        self.coaching_enabled = True
        self._initialize_starting_email()

    def _initialize_starting_email(self):
        """Add a welcome email on day 1."""
        welcome_email = {
            'from': 'Board Chairman',
            'subject': 'Welcome, CEO!',
            'body': "Welcome to your first day. Please review the company status and begin daily operations. We expect proactive leadership.",
            'options': [
                {'text': 'Acknowledge (Low Risk/Neutral)', 'impact': self.action_acknowledge}
            ],
            'type': 'welcome'
        }
        self.inbox.append(welcome_email)

    def action_acknowledge(self, *args):
        """Simple action that removes the email and provides a log entry."""
        self.corp.log.append("Acknowledged welcome message from Board Chairman.")
        return "Message acknowledged. Board confidence slightly up."

    def action_approve_marketing(self, *args):
        """Action for an email to approve a marketing campaign."""
        cost = random.randint(200_000, 1_000_000)
        if not self.corp.can_afford_action('Marketing', cost):
            remaining = self.corp.get_budget_remaining('Marketing')
            return f"Action failed: Insufficient Marketing budget. Need ${cost:,.0f}, but only ${remaining:,.0f} remaining this year."
        
        self.corp.spend_from_budget('Marketing', cost)
        self.corp.cash -= cost
        self.corp.customer_base = min(100, self.corp.customer_base + random.randint(3, 8))
        self.corp.employee_morale = min(100, self.corp.employee_morale + 5)
        self.corp.log.append(f"Approved a marketing campaign costing ${cost:,.0f}.")
        return "Campaign approved and launched. Customer Base increased."

    def action_reject_marketing(self, *args):
        """Action for an email to reject a marketing campaign."""
        self.corp.employee_morale = max(20, self.corp.employee_morale - 10)
        self.corp.reputation = max(20, self.corp.reputation - 5)
        self.corp.log.append("Rejected marketing campaign. Morale and Reputation took a hit.")
        return "Campaign rejected. Employee morale and reputation slightly decreased."

    def action_take_a_break(self, *args):
        """Action to improve CEO health."""
        self.corp.ceo_health = min(100, self.corp.ceo_health + 15)
        self.corp.board_confidence = max(10, self.corp.board_confidence - 10)
        self.corp.log.append("Took a 3-day break to recover.")
        return "Took a much-needed break. Health is up, but the Board is slightly impatient."

    def action_settle_lawsuit(self, email_system):
        cost = 4_000_000
        if email_system.corp.cash < cost:
            email_system.corp.log.append("Action failed: Insufficient Cash for settlement.")
            return "Action failed: Insufficient Cash. The lawsuit drags on."
        
        email_system.corp.cash -= cost
        email_system.corp.reputation = max(20, email_system.corp.reputation - 5)
        email_system.corp.log.append(f"Settled the lawsuit for ${cost:,.0f}.")
        return "Lawsuit settled. Reputations takes a minor hit."

    def action_fight_lawsuit(self, email_system):
        if random.random() < 0.6: # 60% chance to lose
            email_system.corp.reputation = max(10, email_system.corp.reputation - 20)
            email_system.corp.stock_price *= 0.85
            email_system.corp.log.append("CATASTROPHIC FAILURE: Lost the case and massive reputation hit.")
            return "CATASTROPHIC FAILURE: Lost the case and massive reputation hit."
        else:
            email_system.corp.reputation = min(100, email_system.corp.reputation + 10)
            email_system.corp.log.append("SUCCESS: Won the case. Reputation increased.")
            return "SUCCESS: Won the case. Reputation increased."

    def action_investor_meeting(self, *args):
        """Action for accepting an investor meeting."""
        self.corp.board_confidence = min(100, self.corp.board_confidence + 8)
        self.corp.ceo_health = max(0, self.corp.ceo_health - 5)
        self.corp.log.append("Held meeting with major investor. Board confidence increased, but CEO health took a hit.")
        return "Meeting held successfully. Board confidence increased."

    def action_decline_investor(self, *args):
        """Action for declining an investor meeting."""
        self.corp.board_confidence = max(0, self.corp.board_confidence - 10)
        self.corp.reputation = max(20, self.corp.reputation - 5)
        self.corp.log.append("Declined investor meeting. Board and investor relations suffered.")
        return "Meeting declined. Board confidence and reputation decreased."

    def action_increase_hr_budget(self, *args):
        """Action to increase HR budget."""
        budget_increase = 2_000_000
        if not self.corp.can_afford_action('HR', budget_increase):
            remaining = self.corp.get_budget_remaining('HR')
            return f"Action failed: Insufficient HR budget. Need ${budget_increase:,.0f}, but only ${remaining:,.0f} remaining this year."
        self.corp.spend_from_budget('HR', budget_increase)
        self.corp.cash -= budget_increase
        self.corp.departments['HR'] += budget_increase
        self.corp.employee_morale = min(100, self.corp.employee_morale + 15)
        self.corp.log.append(f"Increased HR budget by ${budget_increase:,.0f}. Employee morale improved.")
        return "HR budget increased. Employee morale significantly improved."

    def action_implement_benefits(self, *args):
        """Action to implement non-financial benefits."""
        cost = 600_000
        if self.corp.cash < cost:
            return "Action failed: Insufficient cash for benefits implementation."
        self.corp.cash -= cost
        self.corp.employee_morale = min(100, self.corp.employee_morale + 10)
        self.corp.reputation = min(100, self.corp.reputation + 5)
        self.corp.log.append(f"Implemented non-financial benefits costing ${cost:,.0f}. Morale and reputation improved.")
        return "Benefits implemented successfully. Morale and reputation improved."

    def action_ignore_survey(self, *args):
        """Action to ignore the employee satisfaction survey."""
        self.corp.employee_morale = max(0, self.corp.employee_morale - 20)
        self.corp.reputation = max(20, self.corp.reputation - 10)
        self.corp.log.append("Ignored employee survey. Major morale and reputation hit.")
        return "Survey ignored. Employee morale and reputation significantly decreased."

    def action_counter_product(self, *args):
        """Action to fast-track a counter product."""
        cost = 5_000_000
        if not self.corp.can_afford_action('R&D', cost):
            remaining = self.corp.get_budget_remaining('R&D')
            return f"Action failed: Insufficient R&D budget. Need ${cost:,.0f}, but only ${remaining:,.0f} remaining this year."
        self.corp.spend_from_budget('R&D', cost)
        self.corp.cash -= cost
        self.corp.technology_level = min(100, self.corp.technology_level + 10)
        self.corp.customer_base = min(100, self.corp.customer_base + 8)
        self.corp.log.append(f"Fast-tracked counter product costing ${cost:,.0f}. Technology and market position improved.")
        return "Counter product approved. Technology level and market position improved."

    def action_defensive_pr(self, *args):
        """Action to launch defensive PR campaign."""
        cost = 1_000_000
        if self.corp.cash < cost:
            return "Action failed: Insufficient cash for PR campaign."
        self.corp.cash -= cost
        self.corp.reputation = min(100, self.corp.reputation + 8)
        self.corp.customer_base = min(100, self.corp.customer_base + 5)
        self.corp.log.append(f"Launched defensive PR campaign costing ${cost:,.0f}.")
        return "PR campaign launched. Reputation and customer base improved."

    def action_wait_observe(self, *args):
        """Action to wait and observe competitor."""
        self.corp.log.append("Monitoring competitor activity. Market position remains stable.")
        return "Competitive position monitored. No immediate action taken."

    def action_full_tech_upgrade(self, *args):
        """Action for full tech infrastructure upgrade."""
        cost = 3_000_000
        if not self.corp.can_afford_action('Operations', cost):
            remaining = self.corp.get_budget_remaining('Operations')
            return f"Action failed: Insufficient Operations budget. Need ${cost:,.0f}, but only ${remaining:,.0f} remaining this year."
        self.corp.spend_from_budget('Operations', cost)
        self.corp.cash -= cost
        self.corp.technology_level = min(100, self.corp.technology_level + 15)
        self.corp.dept_efficiency['Operations'] = min(100, self.corp.dept_efficiency['Operations'] + 10)
        self.corp.log.append(f"Completed full technology upgrade costing ${cost:,.0f}. Efficiency significantly improved.")
        return "Technology infrastructure fully upgraded. Efficiency increased by 10%."

    def action_partial_tech_upgrade(self, *args):
        """Action for partial tech infrastructure upgrade."""
        cost = 1_400_000
        if self.corp.cash < cost:
            return "Action failed: Insufficient cash for upgrade."
        self.corp.cash -= cost
        self.corp.technology_level = min(100, self.corp.technology_level + 8)
        self.corp.dept_efficiency['Operations'] = min(100, self.corp.dept_efficiency['Operations'] + 5)
        self.corp.log.append(f"Completed partial technology upgrade costing ${cost:,.0f}.")
        return "Partial technology upgrade completed. Efficiency moderately improved."

    def action_delay_upgrade(self, *args):
        """Action to delay tech upgrade."""
        self.corp.log.append("Delayed technology upgrade. System risk continues to grow.")
        return "Upgrade delayed. Technology debt continues to accumulate."

    def action_hire_consultants(self, *args):
        """Action to hire external compliance consultants."""
        cost = 1_600_000
        if self.corp.cash < cost:
            return "Action failed: Insufficient cash for consultants."
        self.corp.cash -= cost
        self.corp.reputation = min(100, self.corp.reputation + 5)
        self.corp.log.append(f"Hired external compliance consultants costing ${cost:,.0f}.")
        return "External consultants hired. Regulatory compliance quickly achieved."

    def action_build_compliance_team(self, *args):
        """Action to build in-house compliance team."""
        cost = 600_000
        if self.corp.cash < cost:
            return "Action failed: Insufficient cash for compliance team."
        self.corp.cash -= cost
        self.corp.departments['HR'] += cost
        self.corp.log.append(f"Built in-house compliance team costing ${cost:,.0f}.")
        return "In-house compliance team established. Compliance achieved gradually."

    def action_risk_compliance(self, *args):
        """Action to risk non-compliance."""
        self.corp.log.append("Took regulatory risk. Company faces potential fines and legal issues.")
        return "Regulatory risk taken. Legal exposure increased."

    def action_accept_interview(self, *args):
        """Action to accept media interview."""
        self.corp.reputation = min(100, self.corp.reputation + 15)
        self.corp.ceo_health = max(0, self.corp.ceo_health - 8)
        self.corp.log.append("Forbes cover interview accepted. Reputation greatly improved, but CEO health suffered.")
        return "Interview accepted and featured. Major reputation boost."

    def action_decline_interview(self, *args):
        """Action to decline media interview."""
        self.corp.log.append("Declined media interview opportunity.")
        return "Interview declined. Opportunity missed, but no costs incurred."

    def action_hire_vp(self, *args):
        """Action to hire former Google VP."""
        salary_cost = 400_000
        self.corp.cash -= salary_cost
        self.corp.dept_efficiency['R&D'] = min(100, self.corp.dept_efficiency['R&D'] + 20)
        self.corp.technology_level = min(100, self.corp.technology_level + 12)
        self.corp.log.append(f"Hired former Google VP for ${salary_cost:,.0f}/year. R&D significantly boosted.")
        return "VP hired. R&D productivity dramatically increased."

    def action_pass_vp(self, *args):
        """Action to pass on VP candidate."""
        self.corp.log.append("Passed on senior talent opportunity.")
        return "Candidate passed. Opportunity lost, but no costs incurred."

    def action_immediate_recall(self, *args):
        """Action to immediately recall defective product."""
        cost = 6_000_000
        if self.corp.cash < cost:
            return "Action failed: Insufficient cash for recall."
        self.corp.cash -= cost
        self.corp.reputation = min(100, self.corp.reputation + 10)
        self.corp.log.append(f"Immediately recalled defective product costing ${cost:,.0f}. Reputation protected.")
        return "Product recalled immediately. Reputation protected, liability minimized."

    def action_investigate_recall(self, *args):
        """Action to investigate before recalling."""
        self.corp.log.append("Initiated further investigation into product safety issue.")
        return "Investigation underway. Risk exposure remains."

    def action_quiet_fix(self, *args):
        """Action to quietly fix issue in next version."""
        self.corp.log.append("Planned quiet fix for next product version. High legal and reputation risk.")
        self.corp.reputation = max(10, self.corp.reputation - 15)
        return "Quiet fix planned. Company faces massive reputation risk if exposed."

    def action_accept_partnership(self, *args):
        """Action to accept strategic partnership."""
        cost = 2_000_000
        if self.corp.cash < cost:
            return "Action failed: Insufficient cash for partnership."
        self.corp.cash -= cost
        self.corp.customer_base = min(100, self.corp.customer_base + 20)
        self.corp.log.append(f"Accepted strategic partnership costing ${cost:,.0f}. Market expansion initiated.")
        return "Partnership accepted. Massive new market opportunities opened."

    def action_negotiate_partnership(self, *args):
        """Action to negotiate partnership terms."""
        if random.random() < 0.6:  # 60% chance of success
            self.corp.customer_base = min(100, self.corp.customer_base + 15)
            self.corp.log.append("Negotiated better partnership terms. Deal improved.")
            return "Negotiation successful. Better terms achieved."
        else:
            self.corp.log.append("Partnership negotiation failed. Deal fell through.")
            return "Negotiation failed. Deal fell through."

    def action_decline_partnership(self, *args):
        """Action to decline partnership."""
        self.corp.log.append("Declined strategic partnership. Opportunity missed.")
        return "Partnership declined. Opportunity lost but no commitment made."

    def action_negotiate_activist(self, *args):
        """Action to negotiate with activist shareholder."""
        self.corp.board_confidence = max(0, self.corp.board_confidence - 5)
        self.corp.log.append("Negotiated compromise with activist shareholder.")
        return "Compromise negotiated. Board confidence slightly affected."

    def action_resist_activist(self, *args):
        """Action to resist activist shareholder demands."""
        cost = 400_000
        self.corp.cash -= cost
        self.corp.reputation = max(20, self.corp.reputation - 8)
        self.corp.log.append(f"Resisted activist demands with legal costs of ${cost:,.0f}. Reputation affected.")
        return "Activist demands resisted. Legal and PR costs incurred."

    def action_offer_board_seat(self, *args):
        """Action to offer board seat to activist."""
        self.corp.board_confidence = min(100, self.corp.board_confidence + 5)
        self.corp.log.append("Offered board seat to activist shareholder. Control risk accepted.")
        return "Board seat offered. Activist support secured, but control risk increased."

    def action_emergency_shutdown(self, *args):
        """Action for emergency system shutdown."""
        revenue_loss = 1_000_000
        self.corp.cash -= revenue_loss
        self.corp.reputation = min(100, self.corp.reputation + 10)
        self.corp.log.append(f"Emergency shutdown initiated. Revenue loss: ${revenue_loss:,.0f}, but security threat contained.")
        return "Systems shut down. Security threat contained, reputation protected."

    def action_silent_monitor(self, *args):
        """Action to silently monitor security threat."""
        if random.random() < 0.4:  # 40% chance breach becomes public
            self.corp.reputation = max(10, self.corp.reputation - 25)
            self.corp.stock_price *= 0.8
            self.corp.log.append("CATASTROPHIC: Security breach exposed publicly. Massive reputation and stock damage.")
            return "CATASTROPHIC: Breach exposed publicly. Massive damage to reputation and stock price."
        else:
            self.corp.log.append("Silent monitoring successful. Threat contained.")
            return "Threat successfully contained. Crisis averted."

    def action_hire_security(self, *args):
        """Action to hire external security firm."""
        cost = 600_000
        if self.corp.cash < cost:
            return "Action failed: Insufficient cash for security firm."
        self.corp.cash -= cost
        self.corp.log.append(f"Hired external security firm costing ${cost:,.0f}. Threat investigated.")
        return "Security firm engaged. Threat professionally contained."

    def action_full_expansion(self, *args):
        """Action for full Asian market expansion."""
        cost = 10_000_000
        if self.corp.cash < cost:
            return "Action failed: Insufficient cash for expansion."
        self.corp.cash -= cost
        self.corp.customer_base = min(100, self.corp.customer_base + 30)
        self.corp.log.append(f"Launched full Asian expansion costing ${cost:,.0f}. Customer base massively expanded.")
        return "Asian expansion launched. Customer base significantly increased."

    def action_pilot_expansion(self, *args):
        """Action for pilot Asian market expansion."""
        cost = 2_000_000
        if self.corp.cash < cost:
            return "Action failed: Insufficient cash for pilot."
        self.corp.cash -= cost
        self.corp.customer_base = min(100, self.corp.customer_base + 10)
        self.corp.log.append(f"Launched pilot Asian expansion costing ${cost:,.0f}.")
        return "Pilot expansion launched. Customer base moderately increased."

    def action_delay_expansion(self, *args):
        """Action to delay Asian market expansion."""
        self.corp.log.append("Delayed Asian market expansion. Competitors may move first.")
        return "Expansion delayed. Competitive risk increases."

    def _generate_email(self):
        """Generates 2-3 new emails per day based on the current game state."""
        # Generate 2-3 emails per day (70% chance for 2, 30% chance for 3)
        num_emails = 2 if random.random() < 0.7 else 3
        
        for _ in range(num_emails):
            # 70% chance to generate an email each iteration
            if random.random() > 0.7:
                continue

            email_type = random.choice([
                'marketing_request', 'reputation_crisis', 'ceo_health_warning',
                'investor_meeting', 'employee_complaint', 'competitor_threat',
                'tech_upgrade', 'regulatory_issue', 'media_interview',
                'talent_acquisition', 'product_recall', 'partnership_offer',
                'shareholder_activist', 'cybersecurity_breach', 'expansion_opportunity'
            ])

            if email_type == 'marketing_request':
                email = {
                    'from': 'CMO',
                    'subject': 'URGENT: Approve Q3 Marketing Campaign',
                    'body': "Our competitor is gaining ground. We must launch this aggressive $1M-$5M marketing campaign immediately to maintain market share.",
                    'options': [
                        {'text': 'Approve Campaign (High Risk/High Cost)', 'impact': self.action_approve_marketing},
                        {'text': 'Reject Campaign (Low Risk/Morale Hit)', 'impact': self.action_reject_marketing}
                    ],
                    'type': 'marketing_request'
                }
            elif email_type == 'ceo_health_warning' and self.corp.ceo_health < 50:
                email = {
                    'from': 'Self-reflection System',
                    'subject': 'STATUS ALERT: CEO Health Warning',
                    'body': "The system detects signs of burnout. A break may be necessary to maintain peak performance.",
                    'options': [
                        {'text': 'Take a mandatory 3-day break (Reputation/Health)', 'impact': self.action_take_a_break},
                        {'text': 'Ignore Alert (Risk Health/Board Confidence)', 'impact': lambda *args: "Ignored alert. Health risks persist."}
                    ],
                    'type': 'ceo_health_warning'
                }
            elif email_type == 'reputation_crisis' and self.corp.reputation < 50:
                email = {
                    'from': 'Legal Department',
                    'subject': 'LAWSUIT THREAT: Patent Infringement Claim',
                    'body': "We have been hit with a major patent infringement claim. We must decide whether to settle or fight in court.",
                    'options': [
                        {'text': 'Settle Immediately (Cost $20M)', 'impact': self.action_settle_lawsuit},
                        {'text': 'Fight in Court (High Risk)', 'impact': self.action_fight_lawsuit}
                    ],
                    'type': 'lawsuit_threat'
                }
            elif email_type == 'investor_meeting':
                email = {
                    'from': 'Investor Relations',
                    'subject': 'Major Investor Requesting Private Meeting',
                    'body': "BlackRock Investment Group wants a private meeting to discuss our long-term strategy. They control 8% of our shares.",
                    'options': [
                        {'text': 'Accept Meeting (Time Investment, Board Confidence)', 'impact': self.action_investor_meeting},
                        {'text': 'Decline Politely (Risk: Investor Relations)', 'impact': self.action_decline_investor}
                    ],
                    'type': 'investor_meeting'
                }
            elif email_type == 'employee_complaint':
                email = {
                    'from': 'HR Director',
                    'subject': 'Employee Satisfaction Survey Results - URGENT',
                    'body': "The latest survey shows 60% of employees are dissatisfied with compensation and work-life balance. We're at risk of mass exodus.",
                    'options': [
                        {'text': 'Increase HR Budget by $10M', 'impact': self.action_increase_hr_budget},
                        {'text': 'Implement Non-Financial Benefits', 'impact': self.action_implement_benefits},
                        {'text': 'Ignore Survey (High Risk)', 'impact': self.action_ignore_survey}
                    ],
                    'type': 'employee_complaint'
                }
            elif email_type == 'competitor_threat':
                email = {
                    'from': 'Market Intelligence',
                    'subject': 'ALERT: Competitor Launching Disruptive Product',
                    'body': "Our main competitor is launching a product next month that could make our flagship offering obsolete. We need to respond.",
                    'options': [
                        {'text': 'Fast-Track Counter Product ($25M)', 'impact': self.action_counter_product},
                        {'text': 'Launch Aggressive PR Campaign ($5M)', 'impact': self.action_defensive_pr},
                        {'text': 'Wait and Observe (Low Cost, High Risk)', 'impact': self.action_wait_observe}
                    ],
                    'type': 'competitor_threat'
                }
            elif email_type == 'tech_upgrade':
                email = {
                    'from': 'CTO',
                    'subject': 'Critical Infrastructure Upgrade Required',
                    'body': "Our current tech stack is 3 years old. Upgrading now will cost $15M but improve efficiency by 10%. Delaying risks system failures.",
                    'options': [
                        {'text': 'Approve Full Upgrade ($15M)', 'impact': self.action_full_tech_upgrade},
                        {'text': 'Partial Upgrade ($7M)', 'impact': self.action_partial_tech_upgrade},
                        {'text': 'Delay Until Next Quarter', 'impact': self.action_delay_upgrade}
                    ],
                    'type': 'tech_upgrade'
                }
            elif email_type == 'regulatory_issue':
                email = {
                    'from': 'Legal & Compliance',
                    'subject': 'New Government Regulation Impacts Our Operations',
                    'body': "New data privacy laws require immediate compliance. We can hire consultants ($8M) or build in-house capability (slower, cheaper).",
                    'options': [
                        {'text': 'Hire External Consultants ($8M, Fast)', 'impact': self.action_hire_consultants},
                        {'text': 'Build In-House Team ($3M, Slow)', 'impact': self.action_build_compliance_team},
                        {'text': 'Risk Non-Compliance (High Legal Risk)', 'impact': self.action_risk_compliance}
                    ],
                    'type': 'regulatory_issue'
                }
            elif email_type == 'media_interview':
                email = {
                    'from': 'Communications Director',
                    'subject': 'Forbes Interview Request - Cover Story',
                    'body': "Forbes wants to feature you on their cover for a story about innovative CEOs. Great PR opportunity but requires 2 days of your time.",
                    'options': [
                        {'text': 'Accept Interview (Reputation Boost, Health Cost)', 'impact': self.action_accept_interview},
                        {'text': 'Decline (Safe, Missed Opportunity)', 'impact': self.action_decline_interview}
                    ],
                    'type': 'media_interview'
                }
            elif email_type == 'talent_acquisition':
                email = {
                    'from': 'Head of Talent',
                    'subject': 'Opportunity: Hire Former Google VP of Engineering',
                    'body': "A former Google VP is available and interested in joining us. Compensation: $2M/year + equity. Could accelerate our R&D significantly.",
                    'options': [
                        {'text': 'Make Offer ($2M/year, R&D Boost)', 'impact': self.action_hire_vp},
                        {'text': 'Pass on Candidate (No Cost)', 'impact': self.action_pass_vp}
                    ],
                    'type': 'talent_acquisition'
                }
            elif email_type == 'product_recall':
                email = {
                    'from': 'Quality Assurance',
                    'subject': 'CRITICAL: Safety Issue Detected in Product Line',
                    'body': "QA has found a safety flaw affecting 50,000 units. We can recall immediately ($30M) or investigate further (risk exposure).",
                    'options': [
                        {'text': 'Immediate Recall ($30M, Reputation Protected)', 'impact': self.action_immediate_recall},
                        {'text': 'Further Investigation (Delay Risk)', 'impact': self.action_investigate_recall},
                        {'text': 'Quietly Fix in Next Version (High Risk)', 'impact': self.action_quiet_fix}
                    ],
                    'type': 'product_recall'
                }
            elif email_type == 'partnership_offer':
                email = {
                    'from': 'Business Development',
                    'subject': 'Strategic Partnership Offer from Fortune 500 Company',
                    'body': "A Fortune 500 company wants to partner with us on a new venture. Requires $10M investment but could open massive markets.",
                    'options': [
                        {'text': 'Accept Partnership ($10M Investment)', 'impact': self.action_accept_partnership},
                        {'text': 'Negotiate Better Terms (Risk Deal)', 'impact': self.action_negotiate_partnership},
                        {'text': 'Decline Partnership', 'impact': self.action_decline_partnership}
                    ],
                    'type': 'partnership_offer'
                }
            elif email_type == 'shareholder_activist':
                email = {
                    'from': 'Investor Relations',
                    'subject': 'URGENT: Activist Shareholder Demanding Board Seat',
                    'body': "An activist investor with 5% stake is demanding a board seat and pushing for aggressive cost-cutting. We must respond.",
                    'options': [
                        {'text': 'Negotiate Compromise (Board Confidence Risk)', 'impact': self.action_negotiate_activist},
                        {'text': 'Resist Demands (Legal Costs, PR Risk)', 'impact': self.action_resist_activist},
                        {'text': 'Offer Board Seat (Control Risk)', 'impact': self.action_offer_board_seat}
                    ],
                    'type': 'shareholder_activist'
                }
            elif email_type == 'cybersecurity_breach':
                email = {
                    'from': 'Chief Information Security Officer',
                    'subject': 'URGENT: Potential Security Breach Detected',
                    'body': "Our systems detected unusual activity. We can shut down systems for investigation (operations halt) or monitor silently (risk exposure).",
                    'options': [
                        {'text': 'Emergency Shutdown ($5M Lost Revenue)', 'impact': self.action_emergency_shutdown},
                        {'text': 'Silent Monitoring (High Risk)', 'impact': self.action_silent_monitor},
                        {'text': 'Hire External Security Firm ($3M)', 'impact': self.action_hire_security}
                    ],
                    'type': 'cybersecurity_breach'
                }
            elif email_type == 'expansion_opportunity':
                email = {
                    'from': 'VP of Strategy',
                    'subject': 'Market Expansion: Enter Asian Markets Now?',
                    'body': "Asian markets are booming. Entering now requires $50M investment but could triple our customer base in 2 years.",
                    'options': [
                        {'text': 'Full Expansion ($50M Investment)', 'impact': self.action_full_expansion},
                        {'text': 'Pilot Program ($10M Test)', 'impact': self.action_pilot_expansion},
                        {'text': 'Delay Expansion (Safe)', 'impact': self.action_delay_expansion}
                    ],
                    'type': 'expansion_opportunity'
                }
            else:
                continue # No relevant email generated for this iteration

            self.inbox.append(email)

    def _generate_mandatory_event(self):
        """Checks for events that stop the day advance (excluding earnings call)."""
        event_id = None
        
        # Board Confidence Drop
        if self.corp.board_confidence < 30 and self.corp.day % 10 == 0:
            dialogue = "The Board of Directors is losing patience. You must take an action that demonstrates leadership."
            self.POPUP_EVENTS['MANDATORY_BOARD'] = {
                'category': 'MANDATORY_ACTION',
                'dialogue': dialogue,
                'action_type': 'M&A', # Must open the M&A dialog
                'title': "BOARD CONFIDENCE CRITICAL"
            }
            event_id = 'MANDATORY_BOARD'
            
        # Cash Low
        elif self.corp.cash < 50_000_000 and self.corp.day % 5 == 0:
            dialogue = "Cash reserves are dangerously low. You must find a way to raise capital or cut costs immediately."
            self.POPUP_EVENTS['MANDATORY_CASH'] = {
                'category': 'MANDATORY_ACTION',
                'dialogue': dialogue,
                'action_type': 'Debt/Equity', # Must open Debt/Equity dialog
                'title': "CASH RESERVE CRITICAL"
            }
            event_id = 'MANDATORY_CASH'
        
        # Critical Reputation Crisis (This acts like a mandatory crisis decision)
        elif self.corp.reputation < 20 and self.corp.day % 7 == 0:
            event_id = 'CRISIS_REPUTATION'
            dialogue = "An external disaster has completely shattered public trust. You must make a public statement."
            
            def choice_apologize_donate(email_system):
                cost = 2_000_000
                if email_system.corp.cash < cost:
                    email_system.corp.log.append("Action failed: Cannot afford the donation.")
                    return "Action failed: Cannot afford the public action. Reputation suffers more."
                email_system.corp.cash -= cost
                email_system.corp.reputation = min(100, email_system.corp.reputation + 15)
                email_system.corp.board_confidence = max(0, email_system.corp.board_confidence - 5)
                email_system.corp.log.append("CRISIS ACTION: Apology and donation made. Reputation slowly recovers.")
                return "Apology and donation made. Reputation slowly recovers."

            def choice_deny_everything(email_system):
                email_system.corp.reputation = max(0, email_system.corp.reputation - 25)
                email_system.corp.board_confidence = max(0, email_system.corp.board_confidence - 10)
                email_system.corp.log.append("CRISIS ACTION: Denied everything. Massive further reputation loss.")
                return "Denial issued. Total collapse of public trust."

            self.POPUP_EVENTS[event_id] = {
                'category': 'BAD_DECISION', # Type that triggers the decision popup
                'dialogue': dialogue,
                'choices': [
                    (f"Public Apology & Donate $2M (High Cost, Rep. Gain)", choice_apologize_donate, "RISK_LOW"),
                    ("Deny All Responsibility (No Cost, Huge Rep. Loss)", choice_deny_everything, "RISK_HIGH")
                ],
                'title': 'GLOBAL REPUTATION CRISIS'
            }
        
        return event_id

    # --- NEW: Random Event Logic ---
    def _generate_random_event(self):
        """
        Generates a random event based on the specified probabilities:
        50% chance overall. If occurs: 10% Good, 10% Bad, 80% Neutral.
        
        Returns the event_id if an event is generated, otherwise None.
        """
        # 50% chance of an event happening
        if random.random() > 0.50: 
            return None 
        
        event_roll = random.random()
        event_id = f"RANDOM_DAY_{self.corp.day}_{random.randint(1000, 9999)}"

        # --- 10% GOOD EVENT: The Viral Campaign (0.0 to 0.10) ---
        if event_roll < 0.10: 
            dialogue = (
                "Overnight, a demo clip from our R&D showcase hit the front page of every major tech blog. "
                "Analysts are speculating we’re the next platform leader, and inbound partnership emails are piling up. "
                "We can either pour fuel on the fire or ride the wave more conservatively."
            )
            
            def choice_invest_more(email_system):
                cost = 400_000
                if email_system.corp.cash < cost:
                    email_system.corp.log.append("Action failed: Insufficient cash for follow-up investment.")
                    return "Action failed: Insufficient cash. Missed opportunity."
                
                email_system.corp.cash -= cost
                email_system.corp.technology_level = min(100, email_system.corp.technology_level + 5)
                email_system.corp.reputation = min(100, email_system.corp.reputation + 5)
                email_system.corp.log.append("**EVENT:** Viral R&D capitalized. Technology and Reputation boosted.")
                return "SUCCESS: Invested to amplify the buzz. Massive Technology boost achieved."

            def choice_stay_course(email_system):
                email_system.corp.technology_level = min(100, email_system.corp.technology_level + 1)
                email_system.corp.reputation = min(100, email_system.corp.reputation + 2)
                email_system.corp.log.append("**EVENT:** Viral recognition noted, minimal action taken.")
                return "NEUTRAL: The wave passes, but we gained a small tech advantage."
            
            choices = [
                ("Invest $400K to Amplify (High Gain)", choice_invest_more, "GAIN_HIGH"),
                ("Stay the Course (Low Gain)", choice_stay_course, "GAIN_LOW")
            ]
            
            category = 'GOOD'

        # --- 10% BAD EVENT: Executive Resignation (0.10 to 0.20) ---
        elif event_roll < 0.20:
            dialogue = (
                "Late last night, our star CMO abruptly resigned and surfaced at a rival—taking two senior managers with them. "
                "Campaigns are mid-flight, agency contracts are unsettled, and the marketing floor is rattled. "
                "We need to decide whether to buy stability fast or lean on internal talent and accept turbulence."
            )
            
            def choice_hire_pricy_replacement(email_system):
                cost = 10_000_000
                if email_system.corp.cash < cost:
                    email_system.corp.log.append("Action failed: Insufficient cash for top-tier replacement.")
                    return "Action failed: Insufficient cash. Marketing efficiency drops further."
                    
                email_system.corp.cash -= cost
                email_system.corp.dept_efficiency['Marketing'] = max(20, email_system.corp.dept_efficiency['Marketing'] - 5) 
                email_system.corp.log.append(f"**EVENT:** Hired expensive replacement. Marketing efficiency stabilized at a small cost.")
                return "RISK MITIGATED: Replacement hired. Marketing efficiency stabilized but at a huge cost."

            def choice_promote_from_within(email_system):
                email_system.corp.employee_morale = min(100, email_system.corp.employee_morale + 10) 
                email_system.corp.dept_efficiency['Marketing'] = max(0, email_system.corp.dept_efficiency['Marketing'] - 15) 
                email_system.corp.log.append("**EVENT:** Promoted internally. Morale up, but Marketing efficiency tanks.")
                return "RISK HIGH: Internal promotion done. Major drop in Marketing Efficiency, but Morale is high."

            choices = [
                (f"Hire Expensive Replacement (Cost: $10M, Minor Eff. Loss)", choice_hire_pricy_replacement, "RISK_LOW"),
                ("Promote Internally (Morale Gain, Major Eff. Loss)", choice_promote_from_within, "RISK_HIGH")
            ]
            
            category = 'BAD'

        # --- 80% NEUTRAL EVENT: Software Licensing Conflict (0.20 to 1.00) ---
        else:
            dialogue = (
                "Our core operations software vendor just invoked a surprise 30% price hike, effective next billing cycle. "
                "Legal says the contract’s loophole makes it enforceable, but IT claims we could migrate in a quarter—with painful downtime. "
                "Do we absorb the hit to keep systems stable, or rip the band-aid and migrate at the cost of efficiency?"
            )
            cost_increase = 2_000_000
            
            def choice_accept_fee(email_system):
                if email_system.corp.cash < cost_increase:
                    email_system.corp.log.append("Action failed: Cannot afford the new fee.")
                    return "Action failed: Cannot afford. Operations Efficiency drops significantly."
                
                email_system.corp.cash -= cost_increase
                email_system.corp.log.append(f"**EVENT:** Accepted the new licensing fee of ${cost_increase:,.0f}.")
                return "NEUTRAL: Fee accepted. Operations are stable, but Cash is reduced."

            def choice_migrate_systems(email_system):
                # Temporary hit to efficiency for the migration process
                email_system.corp.dept_efficiency['Operations'] = max(0, email_system.corp.dept_efficiency['Operations'] - 20)
                email_system.corp.log.append("**EVENT:** Initiated system migration. Operations efficiency severely reduced for now.")
                return "RISK: Initiated a system migration. Massive temporary Operations Efficiency hit, but no immediate cash cost."
                
            choices = [
                (f"Accept New Fee (Cost: ${cost_increase:,.0f}, No Efficiency Change)", choice_accept_fee, "COST_HIGH"),
                ("Initiate System Migration (No Immediate Cost, High Eff. Loss)", choice_migrate_systems, "EFFICIENCY_LOSS")
            ]
            
            category = 'NEUTRAL'
        
        self.POPUP_EVENTS[event_id] = {
            'category': category,
            'dialogue': dialogue,
            'choices': choices,
            'title': f'{category.upper()} RANDOM EVENT'
        }
        
        return event_id

    def _generate_coaching_email(self):
        """Generate a single coaching email daily to guide the player (CEO).
        The email suggests a recommended action based on the corporation's weakest metric.
        """
        # Determine priority area
        corp = self.corp
        # Simple priority checks (ordered)
        if corp.cash < 200_000_000:
            title = "COACH: Cash Reserves Low"
            body = "Your cash reserves are low. Consider raising capital or cutting costs to avoid insolvency."
            def apply_action(es):
                # Try issuing debt / raise funds (game_core.manage_debt_equity handles details)
                try:
                    es.corp.manage_debt_equity('Issue_Debt', 200_000_000)
                    es.corp.log.append("Coach Action: Issued debt to raise capital.")
                    return "Issued debt to raise capital."
                except Exception as e:
                    return f"Coach action failed: {e}"
            explain = (
                "Issuing debt provides liquidity now but increases interest expense; use cautiously.\n"
                "Short-term: +Cash, higher interest costs.\n"
                "Long-term: preserves runway but may pressure earnings. Consider combining with cost cuts."
            )
        elif corp.reputation < 50:
            title = "COACH: Reputation Weakening"
            body = "Your public reputation is slipping. A PR campaign or settling minor issues can stabilize public trust."
            def apply_action(es):
                return es.action_defensive_pr()
            explain = (
                "Reputation affects customer retention and stock performance.\n"
                "Short-term: PR boosts public sentiment and customer base.\n"
                "Long-term: sustained reputation reduces churn and improves analyst perception."
            )
        elif corp.ceo_health < 60:
            title = "COACH: CEO Burnout Risk"
            body = "Your health is declining. Take a short break to recover — the board may be impatient but a healthy CEO performs better long-term."
            def apply_action(es):
                return es.action_take_a_break()
            explain = (
                "Rest improves cognitive function and long-term decision quality.\n"
                "Short-term: health +, but board confidence dips slightly.\n"
                "Long-term: fewer costly mistakes and better strategic choices."
            )
        elif corp.employee_morale < 55:
            title = "COACH: Employee Morale Low"
            body = "Employee morale is slipping. Consider increasing HR spending or non-financial benefits to avoid productivity loss."
            def apply_action(es):
                # Prefer benefits if cash constrained
                if es.corp.cash > 5_000_000:
                    return es.action_implement_benefits()
                else:
                    return es.action_increase_hr_budget()
            explain = (
                "Employee morale impacts productivity, retention, and quality.\n"
                "Short-term: morale + productivity lift.\n"
                "Long-term: lower hiring costs and higher innovation throughput."
            )
        elif corp.technology_level < 45:
            title = "COACH: Technology Lagging"
            body = "Technology level is below industry expectations. Invest in upgrades or R&D to stay competitive."
            def apply_action(es):
                return es.action_partial_tech_upgrade()
            explain = (
                "Technology investments raise efficiency and enable new products.\n"
                "Short-term: cash spent, possible efficiency gains.\n"
                "Long-term: higher margins and new revenue opportunities."
            )
        elif corp.board_confidence < 55:
            title = "COACH: Board Confidence Low"
            body = "Board confidence is slipping. Consider a small PR move or targeted financial action to reassure stakeholders."
            def apply_action(es):
                try:
                    es.corp.manage_debt_equity('Repurchase_Shares', 10_000_000)
                    es.corp.log.append('Coach Action: Small share repurchase executed to support board confidence.')
                    return 'Executed small share repurchase.'
                except Exception as e:
                    return f"Coach action failed: {e}"
            explain = (
                "Board confidence impacts strategic freedom and investor perception.\n"
                "Short-term: small repurchases or PR restore confidence.\n"
                "Long-term: sustained board support enables bolder initiatives."
            )
        else:
            title = "COACH: Growth Suggestion"
            body = "Your company is in generally good shape. Consider investing in R&D or growth experiments to accelerate progress."
            def apply_action(es):
                # gentle nudge: partial tech upgrade as growth nudge
                return es.action_partial_tech_upgrade()
            explain = (
                "Regular, modest investments compound into significant capability over time.\n"
                "Short-term: small efficiency gains.\n"
                "Long-term: opens new product/market opportunities and improves valuation."
            )

        # Build email
        coaching_email = {
            'from': 'Advisor Bot',
            'subject': title,
            'body': body + "\n\n(Advisor Tip: choose 'Explain why' to learn more or 'Auto-apply' to enact.)",
            'options': [
                {'text': 'Auto-apply recommended action', 'impact': lambda es, _apply=apply_action: _apply(es)},
                {'text': 'Explain why', 'impact': lambda es, _msg=explain: (es.corp.log.append(f"Advisor Explanation: {_msg}"), _msg)[1]},
                {'text': 'Detailed Rationale', 'impact': lambda es, _title=title, _body=body, _exp=explain: (es.corp.log.append(f"Advisor Detailed Rationale - {_title}: {_body}\n{_exp}"), f"Detailed rationale logged.")},
                {'text': 'Ignore advice', 'impact': lambda es: "Ignored advisor guidance."}
            ],
            'type': 'coaching'
        }

        # Don't spam if same coaching email already at top of inbox
        if not self.inbox or self.inbox[0].get('type') != 'coaching' or self.inbox[0].get('subject') != coaching_email['subject']:
            self.inbox.insert(0, coaching_email)

    # The check_for_events method is the public interface used by game_core.py
    def check_for_events(self):
        """Called daily to check for new emails, mandatory popups, and random events."""
        self._generate_email()
        # Generate one coaching email per day (non-duplicating) if coaching is enabled
        try:
            if getattr(self, 'coaching_enabled', True):
                self._generate_coaching_email()
        except Exception:
            # Never let coaching generation block the day advance
            pass
        
        # 1. Check for a mandatory event (highest priority, must stop day advance)
        mandatory_event_id = self._generate_mandatory_event()
        if mandatory_event_id:
            return mandatory_event_id
        
        # 2. Check for a new random event (lower priority, just pop up)
        random_event_id = self._generate_random_event()
        if random_event_id:
            return random_event_id
            
        return None

    def apply_action(self, email_index, option_index):
        """Executes the chosen action for an email and removes it."""
        try:
            email = self.inbox.pop(email_index)
            option = email['options'][option_index]
            
            # Execute the function associated with the impact
            result_msg = option['impact'](self)
            
            return result_msg
        except IndexError:
            return "Error: Email or option index was invalid."
        except Exception as e:
            return f"Action failed due to an error: {e}"