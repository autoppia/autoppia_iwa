from ...projects.operators import CONTAINS, EQUALS, GREATER_EQUAL, GREATER_THAN, IN_LIST, LESS_EQUAL, LESS_THAN, NOT_CONTAINS, NOT_EQUALS, NOT_IN_LIST

TASKS = [
    {"name": "Implement user authentication", "description": "Set up backend and frontend for user registration and login using JWT."},
    {"name": "Design new homepage mockup", "description": "Create a high-fidelity mockup in Figma for the new company homepage."},
    {"name": "Draft Q3 marketing report", "description": "Analyze Q2 performance data and draft a comprehensive report for the Q3 planning meeting."},
    {"name": "Onboard new software engineer", "description": "Prepare and execute the onboarding plan for the new hire joining the engineering team."},
    {"name": "Fix login page CSS bug", "description": "Resolve the alignment issue with the login button on Safari browsers."},
    {"name": "Update API documentation", "description": "Update Swagger/OpenAPI documentation for all public-facing endpoints."},
    {"name": "Create social media content calendar", "description": "Plan and schedule posts for LinkedIn, Twitter, and Facebook for the upcoming month."},
    {"name": "Research competitor pricing", "description": "Gather and analyze pricing information from our top 5 competitors."},
    {"name": "Develop user profile page", "description": "Build the frontend and backend for the user's editable profile page."},
    {"name": "Test payment gateway integration", "description": "Perform thorough testing of the Stripe integration to ensure reliability."},
    {"name": "Write blog post on new feature", "description": "Draft, edit, and publish a blog post announcing the launch of our new AI feature."},
    {"name": "Organize team offsite event", "description": "Coordinate logistics, travel, and activities for the annual team offsite."},
    {"name": "Refactor database schema", "description": "Update the database schema to support multi-tenancy."},
    {"name": "Build CI/CD pipeline", "description": "Implement a complete CI/CD pipeline using GitHub Actions for automated testing and deployment."},
    {"name": "Design email newsletter template", "description": "Design a responsive and reusable email template in Mailchimp."},
    {"name": "Analyze customer feedback survey", "description": "Synthesize results from the latest customer survey and present key findings."},
    {"name": "Create onboarding tutorial video", "description": "Produce a short video that walks new users through the main features of the app."},
    {"name": "Optimize application performance", "description": "Identify and resolve performance bottlenecks in the main application."},
    {"name": "Resolve production server outage", "description": "Investigate and fix the root cause of the recent production outage."},
    {"name": "Plan Q4 product roadmap", "description": "Collaborate with stakeholders to define the product roadmap for the next quarter."},
    {"name": "Localize app for German market", "description": "Translate and adapt the user interface and content for the German-speaking market."},
    {"name": "Conduct user acceptance testing (UAT)", "description": "Coordinate with QA and product managers to conduct final UAT before release."},
    {"name": "Update terms of service", "description": "Update the legal terms of service and privacy policy."},
    {"name": "Prepare investor presentation", "description": "Create a compelling slide deck for the upcoming seed funding round."},
    {"name": "Migrate legacy data to new system", "description": "Execute the migration of user data from the old monolithic system to the new microservices architecture."},
    {"name": "Set up A/B test for landing page", "description": "Configure and run an A/B test on the main landing page to improve conversion rates."},
    {"name": "Design mobile app icon", "description": "Create a new, modern icon for our iOS and Android applications."},
    {"name": "Review and merge pull requests", "description": "Review open pull requests on GitHub, provide feedback, and merge approved changes."},
    {"name": "Create financial model for new project", "description": "Build a detailed financial projection for the proposed 'Project Titan'."},
    {"name": "Secure new office space", "description": "Research, visit, and negotiate a lease for a new, larger office."},
    {"name": "Develop internal knowledge base", "description": "Establish and populate a Confluence space for internal documentation."},
    {"name": "Fix memory leak in backend service", "description": "Diagnose and patch the memory leak identified in the user-service."},
    {"name": "Design promotional banners for ad campaign", "description": "Create a set of visually appealing banners for the upcoming Google Ads campaign."},
    {"name": "Interview candidates for frontend role", "description": "Conduct technical interviews for the Senior Frontend Engineer position."},
    {"name": "Write end-to-end tests for checkout flow", "description": "Write automated end-to-end tests using Cypress for the entire user checkout process."},
    {"name": "Update company website's 'About Us' page", "description": "Refresh the content and team photos on the company's 'About Us' page."},
    {"name": "Plan and execute a webinar", "description": "Plan the content, find speakers, and manage the execution of a public-facing webinar."},
    {"name": "Perform security audit", "description": "Engage a third-party firm to perform a full penetration test of our platform."},
    {"name": "Create a style guide for branding", "description": "Develop a comprehensive brand style guide covering logos, colors, and typography."},
    {"name": "Develop a data dashboard for KPIs", "description": "Build a real-time dashboard in Grafana to monitor key performance indicators."},
    {"name": "Negotiate contract with a new vendor", "description": "Finalize the terms and sign a contract with the new cloud services provider."},
    {"name": "Fix accessibility issues on the dashboard", "description": "Ensure the main dashboard is compliant with WCAG 2.1 AA standards."},
    {"name": "Create a content strategy for the next 6 months", "description": "Outline the themes, topics, and formats for blog and video content for H2."},
    {"name": "Set up monitoring and alerting for services", "description": "Configure Datadog to monitor all critical services and set up on-call alerts."},
    {"name": "Design a new feature for the mobile app", "description": "Design the user flow and UI for a new 'collaboration' feature in the mobile app."},
    {"name": "Write technical specifications for Project X", "description": "Write a detailed technical specification document for the upcoming 'Project X'."},
    {"name": "Organize a company-wide hackathon", "description": "Plan and manage all aspects of an internal hackathon to foster innovation."},
    {"name": "Update dependencies for all microservices", "description": "Update all outdated libraries and dependencies across our microservices."},
    {"name": "Create a user persona document", "description": "Research and document detailed user personas for our target audience."},
    {"name": "Develop a script for data migration", "description": "Write and test a Python script to safely migrate customer data."},
]

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
    {"value": "li@example.com", "label": "Li Wei"},
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
    "member_count": LOGICAL_OPERATORS,
}
FIELD_OPERATORS_TEAM_ROLE_ASSIGNED_MAP = {
    "member": STRING_OPERATORS,
    "role": STRING_OPERATORS,
}
FIELD_OPERATORS_TEAM_CREATED_MAP = {
    "team_name": STRING_OPERATORS,
    "team_description": STRING_OPERATORS,
    "member_name": STRING_OPERATORS,
    "member_email": STRING_OPERATORS,
}
