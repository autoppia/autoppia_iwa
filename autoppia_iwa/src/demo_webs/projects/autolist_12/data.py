from ...projects.operators import CONTAINS, EQUALS, GREATER_EQUAL, GREATER_THAN, IN_LIST, LESS_EQUAL, LESS_THAN, NOT_CONTAINS, NOT_EQUALS, NOT_IN_LIST

TEAMS = [
    {"name": "Core Platform", "description": "Manages the core backend services, APIs, and infrastructure."},
    {"name": "Frontend Warriors", "description": "Builds and maintains the user-facing web application."},
    {"name": "Marketing Mavericks", "description": "Drives all marketing campaigns, lead generation, and brand awareness."},
    {"name": "UX/UI Guild", "description": "Focuses on user research, user experience, and interface design."},
    {"name": "Data Science", "description": "Analyzes data, builds models, and provides business intelligence."},
    {"name": "Project Phoenix", "description": "A cross-functional team dedicated to launching the new Phoenix product line."},
    {"name": "Mobile (iOS)", "description": "Develops and maintains the native iOS application."},
    {"name": "Mobile (Android)", "description": "Develops and maintains the native Android application."},
    {"name": "SRE & DevOps", "description": "Ensures site reliability, manages CI/CD, and oversees cloud infrastructure."},
    {"name": "QA Titans", "description": "Responsible for quality assurance, test planning, and automated testing."},
    {"name": "Growth Hackers", "description": "Focuses on innovative strategies to rapidly grow the user base."},
    {"name": "Customer Success", "description": "Assists customers with onboarding, support, and ensuring their success."},
    {"name": "Sales & Business Development", "description": "Manages new sales opportunities and strategic business partnerships."},
    {"name": "Finance & Accounting", "description": "Handles all financial operations, reporting, and budgeting."},
    {"name": "Human Resources", "description": "Manages recruitment, employee relations, and company culture."},
    {"name": "Legal & Compliance", "description": "Oversees all legal matters, contracts, and regulatory compliance."},
    {"name": "Project Chimera", "description": "A secret project team working on a next-generation hardware device."},
    {"name": "The Innovators", "description": "A special projects team focused on rapid prototyping and innovation."},
    {"name": "API Team", "description": "Develops and maintains the public and private APIs."},
    {"name": "Security Champions", "description": "Leads security initiatives, code reviews, and vulnerability management."},
    {"name": "Design System Crew", "description": "Maintains and evolves the company-wide design system and component library."},
    {"name": "Content Creators", "description": "Produces all written and video content for marketing and product."},
    {"name": "Infrastructure Squad", "description": "Manages the underlying cloud infrastructure on AWS and Google Cloud."},
    {"name": "Product Management", "description": "Defines the product vision, strategy, and feature roadmap."},
    {"name": "Executive Leadership", "description": "The senior leadership team responsible for overall company strategy."},
    {"name": "Intern Program", "description": "A group of summer interns working on special projects."},
    {"name": "Research & Development", "description": "Explores new technologies and long-term strategic initiatives."},
    {"name": "The Vanguard", "description": "A forward-deployed team that tackles the most challenging technical problems."},
    {"name": "Data Engineering", "description": "Builds and maintains the data pipelines and data warehouse."},
    {"name": "Machine Learning Ops", "description": "Manages the deployment and scaling of machine learning models."},
    {"name": "Partner Integrations", "description": "Builds and maintains integrations with third-party partners."},
    {"name": "Community Support", "description": "Engages with and supports our user community on forums and social media."},
    {"name": "Brand Studio", "description": "Manages the company's brand identity, voice, and visual assets."},
    {"name": "Internal Tools", "description": "Develops and maintains tools for internal use by other teams."},
    {"name": "Alpha Launch Team", "description": "The cross-functional team responsible for the initial 'Alpha' product launch."},
    {"name": "Beta Testers Group", "description": "A volunteer group of users who test new features before public release."},
    {"name": "European Expansion", "description": "Leads the company's market entry and growth in Europe."},
    {"name": "APAC Expansion", "description": "Leads the company's market entry and growth in the Asia-Pacific region."},
    {"name": "North America Sales", "description": "The sales team focused on the North American market."},
    {"name": "Enterprise Accounts", "description": "The sales team dedicated to large enterprise customers."},
    {"name": "SMB Accounts", "description": "The sales team focused on small and medium-sized businesses."},
    {"name": "Developer Relations", "description": "Engages with the developer community through content, events, and support."},
    {"name": "The Fixers (Bug Triage)", "description": "A dedicated team focused on triaging and fixing incoming bugs."},
    {"name": "Automation Allies", "description": "Focuses on automating manual processes across the company."},
    {"name": "Cloud Operations", "description": "Manages day-to-day operations of our cloud environments."},
    {"name": "Analytics & Insights", "description": "Provides data-driven insights and reporting to the entire organization."},
    {"name": "Talent Acquisition", "description": "Responsible for sourcing and hiring new talent for the company."},
    {"name": "Learning & Development", "description": "Creates and manages training and professional development programs."},
    {"name": "The Architects", "description": "A senior group of engineers responsible for high-level system architecture."},
    {"name": "Project Cerberus", "description": "A cross-functional team working on the top-secret Project Cerberus."},
]
ROLES = [
    {"value": "admin", "label": "Admin"},
    {"value": "member", "label": "Member"},
    {"value": "viewer", "label": "Viewer"},
    {"value": "developer", "label": "Developer"},
    {"value": "designer", "label": "Designer"},
    {"value": "tester", "label": "Tester"},
    {"value": "product_manager", "label": "Product Manager"},
]
TEAM_MEMBERS_OPTIONS = [
    {"value": "john@example.com", "label": "John Doe"},
    {"value": "jane@example.com", "label": "Jane Smith"},
    {"value": "bob@example.com", "label": "Bob Johnson"},
    {"value": "alice@example.com", "label": "Alice Williams"},
    {"value": "michael@example.com", "label": "Michael Brown"},
    {"value": "emily@example.com", "label": "Emily Davis"},
    {"value": "david@example.com", "label": "David Wilson"},
    {"value": "sophia@example.com", "label": "Sophia Martinez"},
    {"value": "lie@example.com", "label": "Lie Wei"},
    {"value": "fatima@example.com", "label": "Fatima Al-Farsi"},
]
DATES_QUICK_OPTIONS = ["today", "tomorrow", "nextweek", "weekend"]
PRIORITIES = ["Highest", "High", "Medium", "Low"]
LOGICAL_OPERATORS = [EQUALS, NOT_EQUALS, GREATER_EQUAL, GREATER_THAN, LESS_EQUAL, LESS_THAN]
STRING_OPERATORS = [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS]
ARRAY_OPERATORS = [CONTAINS, NOT_CONTAINS, IN_LIST, NOT_IN_LIST]
EQUALITY_OPERATORS = [EQUALS, NOT_EQUALS]


# --- Field Operator Mappings ---
FIELD_OPERATORS_SELECT_DATE_MAP = {
    "date": LOGICAL_OPERATORS,
    "quick_option": EQUALITY_OPERATORS,
}
FIELD_OPERATORS_SELECT_PRIORITY_MAP = {
    "priority": EQUALITY_OPERATORS,
}
FIELD_OPERATORS_TASK_MAP = {
    "name": STRING_OPERATORS,
    "description": STRING_OPERATORS,
    "priority": EQUALITY_OPERATORS,
    "date": LOGICAL_OPERATORS,
}
FIELD_OPERATORS_TEAM_MEMBERS_ADDED_MAP = {
    "members": ARRAY_OPERATORS,
    "member_count": [EQUALS, GREATER_EQUAL, LESS_EQUAL],
}
FIELD_OPERATORS_TEAM_ROLE_ASSIGNED_MAP = {
    "member": STRING_OPERATORS,
    "role": STRING_OPERATORS,
}
FIELD_OPERATORS_TEAM_CREATED_MAP = {
    "name": STRING_OPERATORS,
    "description": STRING_OPERATORS,
    "member": STRING_OPERATORS,
    "role": STRING_OPERATORS,
}
