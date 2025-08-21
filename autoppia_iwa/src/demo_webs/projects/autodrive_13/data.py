from ..operators import CONTAINS, EQUALS, GREATER_EQUAL, GREATER_THAN, IN_LIST, LESS_EQUAL, LESS_THAN, NOT_CONTAINS, NOT_EQUALS, NOT_IN_LIST

LOCATIONS = [
    "1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA",
    "100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA",
    "1000 Chestnut Street Apartments - 1000 Chestnut St, San Francisco, CA 94109, USA",
    "1001 Castro Street - 1001 Castro St, San Francisco, CA 94114, USA",
]

PLACES = [
    {
        "label": "1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA",
        "main": "1 Hotel San Francisco",
        "sub": "8 Mission St, San Francisco, CA 94105, USA",
    },
    {
        "label": "100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA",
        "main": "100 Van Ness",
        "sub": "100 Van Ness Ave, San Francisco, CA 94102, USA",
    },
    {
        "label": "1000 Chestnut Street Apartments - 1000 Chestnut St, San Francisco, CA 94109, USA",
        "main": "1000 Chestnut Street Apartments",
        "sub": "1000 Chestnut St, San Francisco, CA 94109, USA",
    },
    {
        "label": "1030 Post Street Apartments - 1030 Post St #112, San Francisco, CA 94109, USA",
        "main": "1030 Post Street Apartments",
        "sub": "1030 Post St #112, San Francisco, CA 94109, USA",
    },
]
RIDES = [
    {
        "name": "AutoDriverX",
        "icon": "https://ext.same-assets.com/407674263/3757967630.png",
        "image": "/car1.jpg",
        "eta": "1 min away · 1:39 PM",
        "desc": "Affordable rides, all to yourself",
        "seats": 4,
        "price": 26.6,
        "oldPrice": 28.0,
        "recommended": True,
    },
    {
        "name": "Comfort",
        "icon": "https://ext.same-assets.com/407674263/2600779409.svg",
        "image": "/car2.jpg",
        "eta": "2 min away · 1:40 PM",
        "desc": "Newer cars with extra legroom",
        "seats": 4,
        "price": 31.5,
        "oldPrice": 35.0,
        "recommended": False,
    },
    {
        "name": "AutoDriverXL",
        "icon": "https://ext.same-assets.com/407674263/2882408466.svg",
        "image": "/car3.jpg",
        "eta": "3 min away · 1:41 PM",
        "desc": "Affordable rides for groups up to 6",
        "seats": 6,
        "price": 27.37,
        "oldPrice": 32.2,
        "recommended": False,
    },
]

RIDE_TYPES = [
    {
        "name": "AutoDriverX",
        "icon": "/car1.jpg",
        # "icon": "https://ext.same-assets.com/407674263/3757967630.png",
        "price": 26.6,
    },
    {
        "name": "Comfort",
        "icon": "/car2.jpg",
        # "icon": "https://ext.same-assets.com/407674263/2600779409.svg",
        "price": 31.5,
    },
    {
        "name": "AutoDriverXL",
        "icon": "/car3.jpg",
        # "icon": "https://ext.same-assets.com/407674263/2882408466.svg",
        "price": 27.37,
    },
]

TRIPS = [
    {
        "id": "1",
        "status": "upcoming",
        "ride": RIDES[1],
        "pickup": "100 Van Ness - 100 Van Ness Ave, San Francisco, CA 94102, USA",
        "dropoff": "1030 Post Street Apartments - 1030 Post St #112, San Francisco, CA 94109, USA",
        "date": "2025-07-18",
        "time": "13:00",
        "price": 31.5,
        "payment": "Visa ••••1270",
        "driver": {"name": "Alexei Ivanov", "car": "Toyota Camry (Blue)", "plate": "CBA 123", "phone": "+1 416-555-1234", "photo": "https://randomuser.me/api/portraits/men/32.jpg"},
    },
    {
        "id": "2",
        "status": "upcoming",
        "ride": RIDES[0],
        "pickup": "1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA",
        "dropoff": "1000 Chestnut Street Apartments - 1000 Chestnut St, San Francisco, CA 94109, USA",
        "date": "2025-07-18",
        "time": "13:00",
        "price": 26.6,
        "payment": "Visa ••••1270",
        "driver": {"name": "Maria Chen", "car": "Honda Accord (White)", "plate": "XYZ 789", "phone": "+1 647-555-5678", "photo": "https://randomuser.me/api/portraits/women/44.jpg"},
    },
    {
        "id": "3",
        "status": "upcoming",
        "ride": RIDES[0],
        "pickup": "1 Hotel San Francisco - 8 Mission St, San Francisco, CA 94105, USA",
        "dropoff": "1000 Chestnut Street Apartments - 1000 Chestnut St, San Francisco, CA 94109, USA",
        "date": "2025-07-18",
        "time": "13:00",
        "price": 26.6,
        "payment": "Visa ••••1270",
        "driver": {"name": "Samir Patel", "car": "Tesla Model 3 (Red)", "plate": "TES 333", "phone": "+1 416-555-9999", "photo": "https://randomuser.me/api/portraits/men/85.jpg"},
    },
]

STRING_OPERATORS = [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS]
LOGICAL_OPERATORS = [EQUALS, NOT_EQUALS, GREATER_THAN, LESS_THAN, GREATER_EQUAL, LESS_EQUAL]
LIST_OPERATORS = [CONTAINS, NOT_CONTAINS, IN_LIST, NOT_IN_LIST]

FIELD_OPERATORS_MAP_ENTER_LOCATION = {"value": STRING_OPERATORS}
FIELD_OPERATORS_MAP_ENTER_DESTINATION = {
    **FIELD_OPERATORS_MAP_ENTER_LOCATION,
}
FIELD_OPERATORS_MAP_SEE_PRICES = {
    "location": STRING_OPERATORS,
    "destination": STRING_OPERATORS,
}
FIELD_OPERATORS_MAP_SELECT_DATE = {
    "date": LOGICAL_OPERATORS,
}
FIELD_OPERATORS_MAP_SELECT_TIME = {
    "time": LOGICAL_OPERATORS,
}
FIELD_OPERATORS_MAP_NEXT_PICKUP = {
    "date": LOGICAL_OPERATORS,
    "time": LOGICAL_OPERATORS,
}
