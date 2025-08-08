from autoppia_iwa.src.demo_webs.projects.operators import CONTAINS, EQUALS, GREATER_EQUAL, GREATER_THAN, LESS_EQUAL, LESS_THAN, NOT_CONTAINS, NOT_EQUALS

mockUsers = [
    {
        "username": "johndoe",
        "name": "John Doe",
        "avatar": "https://randomuser.me/api/portraits/men/32.jpg",
        "bio": "Software Engineer passionate about building products.",
        "title": "Software Engineer",
        "about": "Hello, I'm John! I specialize in frontend engineering and building delightful web experiences for users. I love JavaScript, React, and solving interesting UI problems. Always looking for new tech to learn!\n\nBS in Computer Science from MIT, 2017.",
        "experience": [
            {
                "title": "Software Engineer",
                "company": "Google",
                "logo": "https://logo.clearbit.com/google.com",
                "duration": "Sep 2018 - Present • 5 yrs 9 mos",
                "location": "Mountain View, California",
                "description": "Working on scalable dashboards for Google Cloud platform. Building performant UIs in React, collaborating with cross-functional teams.",
            },
            {
                "title": "Frontend Engineer (Intern)",
                "company": "Dropbox",
                "logo": "https://logo.clearbit.com/dropbox.com",
                "duration": "May 2018 - Aug 2018 • 4 mos",
                "location": "San Francisco, California",
                "description": "Created new onboarding flows and improved user activation in the Dropbox web app as an intern.",
            },
        ],
    },
    {
        "username": "janedoe",
        "name": "Jane Doe",
        "avatar": "https://randomuser.me/api/portraits/women/68.jpg",
        "bio": "Product Manager & startup enthusiast.",
        "title": "Product Manager",
        "about": "Hello, I'm Jane! I am passionate about software engineering and have a strong background in developing innovative solutions. I enjoy working in collaborative environments and am always eager to learn new technologies and improve my skills.\n\nI graduated from Stanford University in 2018 with a B.S. in Computer Science. During my time at Stanford, I had the opportunity to intern at several top companies, gaining valuable experience and insights into the tech industry.",
        "experience": [
            {
                "title": "Product Manager",
                "company": "Innovate Ltd",
                "logo": "https://logo.clearbit.com/microsoft.com",
                "duration": "Jul 2018 - Present • 5 yrs 11 mos",
                "location": "Redmond, Washington",
                "description": "As a Product Manager at Innovate, I coordinate cross-functional teams to launch new features, lead product demos and deliver high-quality user experiences.",
            },
            {
                "title": "Software Development Intern",
                "company": "Amazon",
                "logo": "https://logo.clearbit.com/amazon.com",
                "duration": "Jun 2017 - Aug 2017 • 3 mos",
                "location": "Seattle, Washington",
                "description": "During my internship at Amazon, I worked on projects to improve internal tools, gaining hands-on experience in agile development, API design, and project management.",
            },
        ],
    },
    {
        "username": "alexsmith",
        "name": "Alex Smith",
        "avatar": "https://randomuser.me/api/portraits/men/76.jpg",
        "bio": "Designer focused on usability and delight.",
        "title": "UI/UX Designer",
        "about": "Hello, I'm Alex! I design thoughtful and accessible interfaces for modern web products. I believe great design is both beautiful and invisible.\n\nBA in Digital Design from NYU, 2016.",
        "experience": [
            {
                "title": "Senior Designer",
                "company": "Pixel Perfect",
                "logo": "https://logo.clearbit.com/behance.net",
                "duration": "Jan 2020 - Present • 4 yrs 5 mos",
                "location": "Los Angeles, CA",
                "description": "Leading design for web and mobile apps for clients in e-commerce and tech. I drive design systems and user-centered workflows.",
            },
            {
                "title": "Design Intern",
                "company": "Adobe",
                "logo": "https://logo.clearbit.com/adobe.com",
                "duration": "Jun 2015 - Aug 2015 • 3 mos",
                "location": "San Jose, CA",
                "description": "Contributed to Adobe XD prototyping library and participated in usability research for UI patterns.",
            },
        ],
    },
    {
        "username": "sarahlee",
        "name": "Sarah Lee",
        "avatar": "https://randomuser.me/api/portraits/women/45.jpg",
        "bio": "Marketing strategist with a love for branding and storytelling.",
        "title": "Marketing Lead",
        "about": "Hi, I'm Sarah! I help startups and enterprises build strong brand presence through creative strategy and digital marketing.\n\nMBA from Wharton School, 2016.",
        "experience": [
            {
                "title": "Head of Marketing",
                "company": "BrandSphere",
                "logo": "https://logo.clearbit.com/brandsphere.com",
                "duration": "Feb 2019 - Present • 5 yrs 4 mos",
                "location": "New York, NY",
                "description": "Lead digital marketing efforts, overseeing brand campaigns, social media and content strategy. Managed a team of 10.",
            }
        ],
    },
    {
        "username": "michaelchan",
        "name": "Michael Chan",
        "avatar": "https://randomuser.me/api/portraits/men/83.jpg",
        "bio": "DevOps engineer passionate about cloud infra & CI/CD pipelines.",
        "title": "DevOps Engineer",
        "about": "I'm Michael, and I architect scalable DevOps solutions to accelerate product delivery. Love automating everything.\n\nAWS Certified DevOps Engineer, Kubernetes enthusiast.",
        "experience": [
            {
                "title": "DevOps Engineer",
                "company": "CloudNetics",
                "logo": "https://logo.clearbit.com/cloudnetics.com",
                "duration": "Mar 2020 - Present • 4 yrs 3 mos",
                "location": "Remote",
                "description": "Implemented CI/CD workflows, infrastructure-as-code with Terraform, and monitoring with Prometheus and Grafana.",
            }
        ],
    },
    {
        "username": "ninapatel",
        "name": "Nina Patel",
        "avatar": "https://randomuser.me/api/portraits/women/34.jpg",
        "bio": "HR professional helping build great cultures and teams.",
        "title": "HR Manager",
        "about": "Hi there! I'm Nina. I thrive on connecting people, fostering inclusive workplace environments, and scaling teams.\n\nCertified SHRM-CP.",
        "experience": [
            {
                "title": "HR Manager",
                "company": "PeopleFirst",
                "logo": "https://logo.clearbit.com/peoplefirst.com",
                "duration": "Jan 2021 - Present • 3 yrs 5 mos",
                "location": "Austin, TX",
                "description": "Manage recruitment, employee relations, and performance management for a fast-growing tech company.",
            }
        ],
    },
    {
        "username": "davidbrown",
        "name": "David Brown",
        "avatar": "https://randomuser.me/api/portraits/men/41.jpg",
        "bio": "AI/ML researcher turning theory into products.",
        "title": "Machine Learning Scientist",
        "about": "I'm David, currently working on foundation models, LLMs, and graph neural networks. I publish regularly and enjoy prototyping AI solutions.\n\nPhD, Computer Science - Carnegie Mellon University.",
        "experience": [
            {
                "title": "ML Scientist",
                "company": "NeuroTech AI",
                "logo": "https://logo.clearbit.com/neurotech.ai",
                "duration": "Aug 2020 - Present • 3 yrs 10 mos",
                "location": "Palo Alto, CA",
                "description": "Design and train deep learning models for NLP and CV use cases. Co-authored 5 research papers.",
            }
        ],
    },
    {
        "username": "emilynguyen",
        "name": "Emily Nguyen",
        "avatar": "https://randomuser.me/api/portraits/women/52.jpg",
        "bio": "Entrepreneur. Speaker. Creative mind.",
        "title": "Startup Founder",
        "about": "Founder of a VC-backed SaaS startup focused on productivity tools for remote teams. Previously built and sold a design consultancy.\n\nPassionate about tech, design, and empowering women in entrepreneurship.",
        "experience": [
            {
                "title": "Founder & CEO",
                "company": "RemoteWorks",
                "logo": "https://logo.clearbit.com/remoteworks.com",
                "duration": "May 2019 - Present • 5 yrs 1 mo",
                "location": "San Francisco, CA",
                "description": "Leading product, growth and team operations at a remote-first startup. Raised $2.5M seed funding.",
            }
        ],
    },
]

mockPosts = [
    {
        "id": "1",
        "user": mockUsers[1],
        "content": "Excited to join LinkedIn Lite!",
        # "timestamp": new Date(Date.now() - 1000 * 60 * 30).toISOString(),
        "likes": 3,
        "liked": False,
        "comments": [
            {
                "id": "c1",
                "user": mockUsers[0],
                "text": "Welcome aboard, Jane!",
                # "timestamp": new Date(Date.now() - 1000 * 60 * 20).toISOString()
            }
        ],
        "image": "https://images.unsplash.com/photo-1515378791036-0648a3ef77b2?fit=crop&w=720&q=80",  # // board room
    },
    {
        "id": "2",
        "user": mockUsers[0],
        "content": "Just released a minimal LinkedIn clone with Next.js and Tailwind CSS! 🚀",
        # "timestamp": new Date(Date.now() - 1000 * 60 * 100).toISOString(),
        "likes": 2,
        "liked": False,
        "comments": [],
        "image": "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?fit=crop&w=720&q=80",
        # // laptop and notepad
    },
    {
        # // Post 7
        "id": "7",
        "user": mockUsers[1],
        "content": "Attended a fantastic webinar on remote team collaboration today! Highly recommend it.",
        # "timestamp": new Date(Date.now() - 1000 * 60 * 60 * 8).toISOString(),
        "likes": 5,
        "liked": False,
        "comments": [
            {
                "id": "c6",
                "user": mockUsers[2],
                "text": "Thanks for sharing, Jane!",
                # "timestamp": new Date(Date.now() - 1000 * 60 * 60 * 7.8).toISOString()
            }
        ],
        "image": "https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?fit=crop&w=720&q=80",
        # // people collaborating
    },
    {
        # // Post 8
        "id": "8",
        "user": mockUsers[0],
        "content": "Started learning TypeScript this week. Any tips for a React dev?",
        # "timestamp": new Date(Date.now() - 1000 * 60 * 60 * 15).toISOString(),
        "likes": 3,
        "liked": False,
        "comments": [
            {
                "id": "c7",
                "user": mockUsers[1],
                "text": "You'll love the type safety!",
                # "timestamp": new Date(Date.now() - 1000 * 60 * 60 * 14.5).toISOString()
            }
        ],
        "image": "https://images.unsplash.com/photo-1503676382389-4809596d5290?fit=crop&w=720&q=80",
        # // coffee and code
    },
    {
        # // Post 9
        "id": "9",
        "user": mockUsers[2],
        "content": "Just finished a 10k run for charity. Feeling accomplished!",
        # "timestamp": new Date(Date.now() - 1000 * 60 * 60 * 36).toISOString(),
        "likes": 6,
        "liked": False,
        "comments": [
            {
                "id": "c8",
                "user": mockUsers[0],
                "text": "Congrats Alex!",
                # "timestamp": new Date(Date.now() - 1000 * 60 * 60 * 35.5).toISOString()
            }
        ],
        "image": "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?fit=crop&w=720&q=80",  # // running event
    },
    {
        # // Post 10
        "id": "10",
        "user": mockUsers[1],
        "content": "Reading 'Inspired' by Marty Cagan. Game changer for product managers!",
        # "timestamp": new Date(Date.now() - 1000 * 60 * 60 * 72).toISOString(),
        "likes": 2,
        "liked": False,
        "comments": [],
    },
    {
        "id": "11",
        "user": mockUsers[3],  # // Sarah Lee
        "content": "Just launched our summer brand campaign. Feeling proud of the team! 🌞📣",
        # "timestamp": new Date(Date.now() - 1000 * 60 * 10).toISOString(),
        "likes": 7,
        "liked": False,
        "comments": [
            {
                "id": "c11",
                "user": mockUsers[0],
                "text": "Congrats Sarah! 🔥",
                # "timestamp": new Date(Date.now() - 1000 * 60 * 7).toISOString()
            }
        ],
        "image": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?fit=crop&w=720&q=80",
        # // team celebration
    },
    {
        "id": "12",
        "user": mockUsers[4],  # // Michael Chan
        "content": "Migrated 20+ services to Kubernetes today. DevOps win! ⚙️🐳",
        # "timestamp": new Date(Date.now() - 1000 * 60 * 60 * 5).toISOString(),
        "likes": 4,
        "liked": False,
        "comments": [],
    },
    {
        "id": "13",
        "user": mockUsers[5],  # // Nina Patel
        "content": "Hosting our first DEI panel at PeopleFirst. Let's build inclusive cultures. 🌈",
        # "timestamp": new Date(Date.now() - 1000 * 60 * 60 * 9).toISOString(),
        "likes": 8,
        "liked": False,
        "comments": [
            {
                "id": "c13",
                "user": mockUsers[2],
                "text": "This is so important 👏",
                # "timestamp": new Date(Date.now() - 1000 * 60 * 60 * 8.8).toISOString()
            }
        ],
    },
    {
        "id": "14",
        "user": mockUsers[6],  # // David Brown
        "content": "Experimenting with fine-tuning LLMs on small domain datasets. Results look promising.",
        # "timestamp": new Date(Date.now() - 1000 * 60 * 60 * 20).toISOString(),
        "likes": 12,
        "liked": False,
        "comments": [],
    },
    {
        "id": "15",
        "user": mockUsers[7],  # // Emily Nguyen
        "content": "We just hit 10K users on RemoteWorks! 💪 Thank you for believing in us.",
        # "timestamp": new Date(Date.now() - 1000 * 60 * 60 * 48).toISOString(),
        "likes": 14,
        "liked": False,
        "comments": [
            {
                "id": "c15",
                "user": mockUsers[1],
                "text": "Huge milestone, Emily!",
                # "timestamp": new Date(Date.now() - 1000 * 60 * 60 * 47.5).toISOString()
            }
        ],
        "image": "https://images.unsplash.com/photo-1556761175-4b46a572b786?fit=crop&w=720&q=80",
        # // startup celebration
    },
    {
        "id": "16",
        "user": mockUsers[6],  # // David Brown
        "content": "Published a new research paper on GNNs and edge inference. DM for collab. 📄📊",
        # "timestamp": new Date(Date.now() - 1000 * 60 * 60 * 80).toISOString(),
        "likes": 6,
        "liked": False,
        "comments": [],
    },
]

mockJobs = [
    {
        "id": "j1",
        "title": "Senior Frontend Developer",
        "company": "Tech Innovations",
        "location": "Remote",
        "logo": "https://logo.clearbit.com/techinnovations.com",
        "salary": "$120,000 - $150,000",
        "type": "Full-time",
        "experience": "5+ years",
        "description": "We're looking for a Senior Frontend Developer to join our growing team. You'll be responsible for building scalable, performant web applications using React, TypeScript, and modern frontend technologies. You'll work closely with designers and backend engineers to deliver exceptional user experiences.",
        "requirements": [
            "5+ years of experience with React, TypeScript, and modern JavaScript",
            "Strong understanding of CSS, HTML, and responsive design",
            "Experience with state management (Redux, Zustand, or similar)",
            "Knowledge of testing frameworks (Jest, React Testing Library)",
            "Experience with build tools (Webpack, Vite, or similar)",
            "Strong problem-solving skills and attention to detail",
        ],
        "benefits": [
            "Competitive salary and equity package",
            "Flexible remote work policy",
            "Health, dental, and vision insurance",
            "401(k) with company match",
            "Unlimited PTO",
            "Professional development budget",
        ],
        "postedDate": "2024-01-15",
        "applicationCount": 47,
        "companySize": "50-100 employees",
        "industry": "Technology",
        "remote": True,
    },
    {
        "id": "j2",
        "title": "Product Designer",
        "company": "Creative Studio",
        "location": "New York, NY",
        "logo": "https://logo.clearbit.com/creativestudio.com",
        "salary": "$90,000 - $120,000",
        "type": "Full-time",
        "experience": "3+ years",
        "description": "Join our design team to create beautiful, intuitive user experiences. You'll work on products that impact millions of users, from concept to final implementation. We value creativity, collaboration, and user-centered design thinking.",
        "requirements": [
            "3+ years of product design experience",
            "Proficiency in Figma, Sketch, or similar design tools",
            "Strong portfolio showcasing user-centered design work",
            "Experience with design systems and component libraries",
            "Knowledge of user research and usability testing",
            "Excellent communication and presentation skills",
        ],
        "benefits": [
            "Competitive salary",
            "Health and wellness benefits",
            "Flexible work arrangements",
            "Creative workspace in Manhattan",
            "Professional development opportunities",
            "Team events and activities",
        ],
        "postedDate": "2024-01-12",
        "applicationCount": 89,
        "companySize": "25-50 employees",
        "industry": "Design",
        "remote": False,
    },
    {
        "id": "j3",
        "title": "Marketing Specialist",
        "company": "Startup Hub",
        "location": "San Francisco, CA",
        "logo": "https://logo.clearbit.com/startuphub.com",
        "salary": "$70,000 - $90,000",
        "type": "Full-time",
        "experience": "2+ years",
        "description": "Help us grow our brand and reach new customers through innovative marketing strategies. You'll work on digital marketing campaigns, content creation, and social media management. Perfect role for someone passionate about startups and growth marketing.",
        "requirements": [
            "2+ years of digital marketing experience",
            "Experience with social media platforms and advertising",
            "Knowledge of Google Analytics and marketing tools",
            "Strong writing and content creation skills",
            "Experience with email marketing campaigns",
            "Analytical mindset and data-driven approach",
        ],
        "benefits": ["Competitive salary with performance bonuses", "Health insurance", "Flexible PTO", "Professional development budget", "Stock options", "Modern office in SF"],
        "postedDate": "2024-01-10",
        "applicationCount": 156,
        "companySize": "10-25 employees",
        "industry": "Technology",
        "remote": False,
    },
    {
        "id": "j4",
        "title": "UI/UX Designer",
        "company": "Pixel Perfect",
        "location": "Los Angeles, CA",
        "logo": "https://logo.clearbit.com/pixelperfect.com",
        "salary": "$85,000 - $110,000",
        "type": "Full-time",
        "experience": "4+ years",
        "description": "Create stunning user interfaces and seamless user experiences for our digital products. You'll collaborate with cross-functional teams to design solutions that delight users and drive business goals.",
        "requirements": [
            "4+ years of UI/UX design experience",
            "Expertise in Figma, Adobe Creative Suite",
            "Strong understanding of user-centered design principles",
            "Experience with design systems and component libraries",
            "Knowledge of accessibility standards",
            "Portfolio demonstrating web and mobile design work",
        ],
        "benefits": [
            "Competitive salary",
            "Health, dental, and vision insurance",
            "Flexible work schedule",
            "Beautiful office in LA",
            "Professional development opportunities",
            "Team building activities",
        ],
        "postedDate": "2024-01-08",
        "applicationCount": 67,
        "companySize": "50-100 employees",
        "industry": "Design",
        "remote": False,
    },
    {
        "id": "j5",
        "title": "Backend Engineer",
        "company": "DataStream Inc.",
        "location": "Boston, MA",
        "logo": "https://logo.clearbit.com/datastream.com",
        "salary": "$130,000 - $160,000",
        "type": "Full-time",
        "experience": "6+ years",
        "description": "Build scalable backend systems that process millions of data points daily. You'll work with cutting-edge technologies to develop APIs, databases, and microservices that power our data platform.",
        "requirements": [
            "6+ years of backend development experience",
            "Expertise in Python, Java, or Go",
            "Experience with cloud platforms (AWS, GCP, Azure)",
            "Knowledge of database design and optimization",
            "Experience with microservices architecture",
            "Strong understanding of system design and scalability",
        ],
        "benefits": [
            "Competitive salary and equity",
            "Comprehensive health benefits",
            "Flexible remote work options",
            "401(k) with company match",
            "Professional development budget",
            "Modern office in Boston",
        ],
        "postedDate": "2024-01-05",
        "applicationCount": 34,
        "companySize": "100-250 employees",
        "industry": "Technology",
        "remote": True,
    },
    {
        "id": "j6",
        "title": "Content Strategist",
        "company": "MediaWorks",
        "location": "Seattle, WA",
        "logo": "https://logo.clearbit.com/mediaworks.com",
        "salary": "$75,000 - $95,000",
        "type": "Full-time",
        "experience": "3+ years",
        "description": "Develop and execute content strategies that engage our audience and drive business objectives. You'll create compelling content across multiple channels and work with creative teams to maintain brand voice and quality.",
        "requirements": [
            "3+ years of content strategy experience",
            "Excellent writing and editing skills",
            "Experience with content management systems",
            "Knowledge of SEO and content marketing",
            "Experience with social media content creation",
            "Strong analytical and project management skills",
        ],
        "benefits": [
            "Competitive salary",
            "Health and wellness benefits",
            "Flexible work arrangements",
            "Professional development opportunities",
            "Creative and collaborative environment",
            "Beautiful office in Seattle",
        ],
        "postedDate": "2024-01-03",
        "applicationCount": 78,
        "companySize": "50-100 employees",
        "industry": "Media",
        "remote": False,
    },
    {
        "id": "j7",
        "title": "QA Engineer",
        "company": "QualityFirst",
        "location": "Remote (US)",
        "logo": "https://logo.clearbit.com/qualityfirst.com",
        "salary": "$80,000 - $100,000",
        "type": "Full-time",
        "experience": "4+ years",
        "description": "Ensure the quality and reliability of our software products through comprehensive testing strategies. You'll work with development teams to implement automated testing, manual testing processes, and quality assurance best practices.",
        "requirements": [
            "4+ years of QA engineering experience",
            "Experience with automated testing frameworks",
            "Knowledge of testing methodologies and best practices",
            "Experience with CI/CD pipelines",
            "Strong analytical and problem-solving skills",
            "Experience with bug tracking and test management tools",
        ],
        "benefits": ["Competitive salary", "Health, dental, and vision insurance", "Fully remote work environment", "Flexible PTO", "Professional development budget", "Home office setup allowance"],
        "postedDate": "2024-01-01",
        "applicationCount": 92,
        "companySize": "100-250 employees",
        "industry": "Technology",
        "remote": True,
    },
    {
        "id": "j8",
        "title": "DevOps Engineer",
        "company": "CloudTech Solutions",
        "location": "Austin, TX",
        "logo": "https://logo.clearbit.com/cloudtech.com",
        "salary": "$110,000 - $140,000",
        "type": "Full-time",
        "experience": "5+ years",
        "description": "Build and maintain our cloud infrastructure and deployment pipelines. You'll work with cutting-edge technologies to ensure our systems are scalable, secure, and highly available.",
        "requirements": [
            "5+ years of DevOps experience",
            "Expertise in AWS, Docker, and Kubernetes",
            "Experience with infrastructure as code (Terraform, CloudFormation)",
            "Knowledge of CI/CD pipelines and automation",
            "Experience with monitoring and logging tools",
            "Strong scripting skills (Python, Bash, etc.)",
        ],
        "benefits": [
            "Competitive salary and equity",
            "Comprehensive health benefits",
            "Flexible work arrangements",
            "401(k) with company match",
            "Professional development budget",
            "Modern office in Austin",
        ],
        "postedDate": "2023-12-28",
        "applicationCount": 45,
        "companySize": "50-100 employees",
        "industry": "Technology",
        "remote": True,
    },
    {
        "id": "j9",
        "title": "Data Scientist",
        "company": "Analytics Pro",
        "location": "Chicago, IL",
        "logo": "https://logo.clearbit.com/analyticspro.com",
        "salary": "$120,000 - $150,000",
        "type": "Full-time",
        "experience": "4+ years",
        "description": "Transform data into actionable insights that drive business decisions. You'll work with large datasets, develop machine learning models, and create data-driven solutions for complex business problems.",
        "requirements": [
            "4+ years of data science experience",
            "Expertise in Python, R, or similar languages",
            "Experience with machine learning frameworks",
            "Knowledge of statistical analysis and modeling",
            "Experience with big data technologies",
            "Strong communication and presentation skills",
        ],
        "benefits": [
            "Competitive salary and equity",
            "Health, dental, and vision insurance",
            "Flexible work arrangements",
            "401(k) with company match",
            "Professional development budget",
            "Modern office in Chicago",
        ],
        "postedDate": "2023-12-25",
        "applicationCount": 38,
        "companySize": "100-250 employees",
        "industry": "Technology",
        "remote": False,
    },
    {
        "id": "j10",
        "title": "Product Manager",
        "company": "InnovateCorp",
        "location": "Denver, CO",
        "logo": "https://logo.clearbit.com/innovatecorp.com",
        "salary": "$100,000 - $130,000",
        "type": "Full-time",
        "experience": "5+ years",
        "description": "Lead product strategy and execution for our flagship products. You'll work with cross-functional teams to define product vision, prioritize features, and deliver exceptional user experiences.",
        "requirements": [
            "5+ years of product management experience",
            "Experience with agile development methodologies",
            "Strong analytical and strategic thinking skills",
            "Experience with user research and data analysis",
            "Excellent communication and leadership skills",
            "Technical background or understanding preferred",
        ],
        "benefits": [
            "Competitive salary and equity",
            "Comprehensive health benefits",
            "Flexible work arrangements",
            "401(k) with company match",
            "Professional development budget",
            "Beautiful office in Denver",
        ],
        "postedDate": "2023-12-20",
        "applicationCount": 112,
        "companySize": "250-500 employees",
        "industry": "Technology",
        "remote": False,
    },
]

COMPANIES = [
    {"name": "Adobe", "desc": "Company • Design tools", "logo": "https://logo.clearbit.com/adobe.com"},
    {"name": "Y Combinator", "desc": "Company • Start up accelerator", "logo": "https://logo.clearbit.com/ycombinator.com"},
    {"name": "TED", "desc": "TEDTalks • TEDConferences", "logo": "https://logo.clearbit.com/ted.com"},
    {"name": "Figma", "desc": "Company • Design systems", "logo": "https://logo.clearbit.com/figma.com"},
    {"name": "Notion", "desc": "Company • Productivity", "logo": "https://logo.clearbit.com/notion.so"},
    {"name": "Stripe", "desc": "Company • Fintech", "logo": "https://logo.clearbit.com/stripe.com"},
]

POSTS_DATA_MODIFIED = []
for post in mockPosts:
    modified_post = post.copy()
    modified_post["name"] = post["user"]["name"]
    modified_post["username"] = post["user"]["username"]
    POSTS_DATA_MODIFIED.append(modified_post)

STRING_OPERATORS = [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS]
LOGICAL_OPERATORS = [EQUALS, NOT_EQUALS, GREATER_EQUAL, GREATER_THAN, LESS_EQUAL, LESS_THAN]

FIELD_OPERATORS_VIEW_USER_PROFILE_MAP = {
    "username": STRING_OPERATORS,
    "name": STRING_OPERATORS,
}

FIELD_OPERATORS_CONNECT_WITH_USER_MAP = {
    "target_username": STRING_OPERATORS,
    "target_name": STRING_OPERATORS,
}

FIELD_OPERATORS_LIKE_POST_MAP = {
    "poster_name": STRING_OPERATORS,
    "poster_content": STRING_OPERATORS,
}

FIELD_OPERATORS_COMMENT_ON_POST_MAP = {
    "comment_text": STRING_OPERATORS,
    "poster_name": STRING_OPERATORS,
    "poster_content": STRING_OPERATORS,
}
FIELD_OPERATORS_POST_STATUS_MAP = {
    "content": STRING_OPERATORS,
}

FIELD_OPERATORS_SEARCH_USERS_MAP = {
    "query": STRING_OPERATORS,
}

FIELD_OPERATORS_FOLLOW_PAGE_MAP = {
    "company": STRING_OPERATORS,
}

FIELD_OPERATORS_VIEW_JOB_MAP = {
    "job_title": STRING_OPERATORS,
    "company": STRING_OPERATORS,
    "location": STRING_OPERATORS,
}

FIELD_OPERATORS_APPLY_FOR_JOB_MAP = {
    "job_title": STRING_OPERATORS,
    "company": STRING_OPERATORS,
    "location": STRING_OPERATORS,
}

FIELD_OPERATORS_SEARCH_JOBS_MAP = {
    "query": STRING_OPERATORS,
    # 'result_count': LOGICAL_OPERATORS,
    # "experience": [EQUALS, NOT_EQUALS],
    # "location": STRING_OPERATORS,
    # "remote": [EQUALS],
    # "salary": [EQUALS, NOT_EQUALS],
    # "search": STRING_OPERATORS
}
