import calendar
import random
import re
from datetime import date

from .data import ALLOWED_EVENT_COLORS, CLIENT_DATA, DOCUMENT_DATA, MATTERS_DATA


def replace_placeholders(text: str) -> str:
    if not isinstance(text, str):
        return text

    def get_random_event_date():
        today = date.today()
        year, month = today.year, today.month

        # Get number of days in the current month
        days_in_month = calendar.monthrange(year, month)[1]

        # Generate a random day
        random_day = random.randint(1, days_in_month)

        return date(year, month, random_day).isoformat()  # format as 'YYYY-MM-DD'

    def get_random_event_time():
        return random.choice(["9:00am", "10:00am", "11:30am", "1:00pm", "2:30pm", "3:15pm", "4:45pm", "5:00pm"])

    def get_random_event_label():
        return random.choice(
            ["Team Sync", "Court Filing", "Internal Review", "Strategy Meeting", "Budget Review", "Staff Meeting", "Weekly Standup", "Doc Submission", "Partner Call", "Client Check-in"]
        )

    def get_random_log_hours():
        return str(random.choice([0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 4.0]))

    def get_random_log_status():
        return random.choice(["Billable", "Billed", "Non-billable", "Pending", "Approved", "Rejected"])

    extended_user_names = [
        "Aisha Khan",
        "Muhammad Ali",
        "Usman Riaz",
        "Zainab Shah",
        "Hassan Tariq",
        "Mehak Noor",
        "John Smith",
        "Emily Rose",
        "David Johnson",
        "Sophia Williams",
        "James Anderson",
        "Anna Thompson",
        "Michael Brown",
        "Grace Miller",
        "Daniel Wilson",
        "Emma Davis",
        "Alex Kim",
        "Liam Chen",
        "Isabella Garcia",
        "Noah Patel",
        "Olivia Martin",
        "Lucas Novak",
        "Chloe Tan",
        "Ethan Wang",
        "Nora Suzuki",
        "Leo Jensen",
        "Aria Silva",
    ]

    forbidden_names = ["Guest User", "Anonymous", "Default User", "Unknown", "Demo User", "Temp Account", "Test User", "No Name", "Placeholder", "UserX"]

    placeholder_value_sources = {
        # Matter
        # "<matter_name>": list({m["name"] for m in MATTERS_DATA}),
        # "<matter_status>": list({m["status"] for m in MATTERS_DATA}),
        # "<updated_at>": list({m["updated"] for m in MATTERS_DATA}),
        # "<client_name>": list({m["client"] for m in MATTERS_DATA}),
        # Client
        "<client_email>": list({c["email"] for c in CLIENT_DATA}),
        "<client_status>": list({c["status"] for c in CLIENT_DATA}),
        "<client_matter>": [str(c["matters"]) for c in CLIENT_DATA],
        # Document
        "<document_name>": list({d["name"] for d in DOCUMENT_DATA}),
        "<document_status>": list({d["status"] for d in DOCUMENT_DATA}),
        "<document_updated>": list({d["updated"] for d in DOCUMENT_DATA}),
        "<document_version>": list({d["version"] for d in DOCUMENT_DATA}),
        "<document_size>": list({d["size"] for d in DOCUMENT_DATA}),
        # Calendar
        "<event_date>": [get_random_event_date() for _ in range(10)],
        "<event_time>": [get_random_event_time() for _ in range(10)],
        "<event_label>": [get_random_event_label() for _ in range(10)],
        "<event_type>": [random.choice(ALLOWED_EVENT_COLORS) for _ in range(10)],
        # Logs
        "<log_hours>": [get_random_log_hours() for _ in range(10)],
        "<log_status>": [get_random_log_status() for _ in range(10)],
        "<log_client>": list({m["client"] for m in MATTERS_DATA}),
        # Search
        "<query>": list({c["name"].split()[0] for c in CLIENT_DATA}),
        "<query_part>": list({c["name"].split()[-1] for c in CLIENT_DATA}),
        # User name
        "<new_name>": random.sample(extended_user_names, k=min(10, len(extended_user_names))),
        "<forbidden_name>": random.sample(forbidden_names, k=min(10, len(forbidden_names))),
    }

    found_placeholders = re.findall(r"<[^<>]+?>", text)
    modified_text = text

    for placeholder in set(found_placeholders):
        count = found_placeholders.count(placeholder)
        values = placeholder_value_sources.get(placeholder, [])

        if not values:
            replacements = ["<missing>"] * count
        else:
            random.shuffle(values)
            replacements = (values * ((count // len(values)) + 1))[:count]

        for replacement in replacements:
            modified_text = modified_text.replace(placeholder, replacement, 1)

    return modified_text
