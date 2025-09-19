from ..operators import CONTAINS, EQUALS, GREATER_EQUAL, GREATER_THAN, IN_LIST, LESS_EQUAL, LESS_THAN, NOT_CONTAINS, NOT_EQUALS, NOT_IN_LIST

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
    {
        "label": "The Ritz-Carlton - 600 Stockton St, San Francisco, CA 94108, USA",
        "main": "The Ritz-Carlton",
        "sub": "600 Stockton St, San Francisco, CA 94108, USA",
    },
    {
        "label": "Fairmont San Francisco - 950 Mason St, San Francisco, CA 94108, USA",
        "main": "Fairmont San Francisco",
        "sub": "950 Mason St, San Francisco, CA 94108, USA",
    },
    {
        "label": "Hotel Nikko - 222 Mason St, San Francisco, CA 94102, USA",
        "main": "Hotel Nikko",
        "sub": "222 Mason St, San Francisco, CA 94102, USA",
    },
    {
        "label": "Palace Hotel - 2 New Montgomery St, San Francisco, CA 94105, USA",
        "main": "Palace Hotel",
        "sub": "2 New Montgomery St, San Francisco, CA 94105, USA",
    },
    {
        "label": "InterContinental San Francisco - 888 Howard St, San Francisco, CA 94103, USA",
        "main": "InterContinental San Francisco",
        "sub": "888 Howard St, San Francisco, CA 94103, USA",
    },
    {
        "label": "Hotel Zephyr - 250 Beach St, San Francisco, CA 94133, USA",
        "main": "Hotel Zephyr",
        "sub": "250 Beach St, San Francisco, CA 94133, USA",
    },
    {
        "label": "Hotel Zoe Fisherman's Wharf - 425 North Point St, San Francisco, CA 94133, USA",
        "main": "Hotel Zoe Fisherman's Wharf",
        "sub": "425 North Point St, San Francisco, CA 94133, USA",
    },
    {
        "label": "The Clift Royal Sonesta Hotel - 495 Geary St, San Francisco, CA 94102, USA",
        "main": "The Clift Royal Sonesta Hotel",
        "sub": "495 Geary St, San Francisco, CA 94102, USA",
    },
    {
        "label": "The Marker San Francisco - 501 Geary St, San Francisco, CA 94102, USA",
        "main": "The Marker San Francisco",
        "sub": "501 Geary St, San Francisco, CA 94102, USA",
    },
    {
        "label": "Hilton San Francisco Union Square - 333 O'Farrell St, San Francisco, CA 94102, USA",
        "main": "Hilton San Francisco Union Square",
        "sub": "333 O'Farrell St, San Francisco, CA 94102, USA",
    },
    {
        "label": "Parc 55 San Francisco - 55 Cyril Magnin St, San Francisco, CA 94102, USA",
        "main": "Parc 55 San Francisco",
        "sub": "55 Cyril Magnin St, San Francisco, CA 94102, USA",
    },
    {
        "label": "Hotel Kabuki - 1625 Post St, San Francisco, CA 94115, USA",
        "main": "Hotel Kabuki",
        "sub": "1625 Post St, San Francisco, CA 94115, USA",
    },
    {
        "label": "Hotel G San Francisco - 386 Geary St, San Francisco, CA 94102, USA",
        "main": "Hotel G San Francisco",
        "sub": "386 Geary St, San Francisco, CA 94102, USA",
    },
    {
        "label": "The Westin St. Francis - 335 Powell St, San Francisco, CA 94102, USA",
        "main": "The Westin St. Francis",
        "sub": "335 Powell St, San Francisco, CA 94102, USA",
    },
    {
        "label": "Hotel Vitale - 8 Mission St, San Francisco, CA 94105, USA",
        "main": "Hotel Vitale",
        "sub": "8 Mission St, San Francisco, CA 94105, USA",
    },
    {
        "label": "Argonaut Hotel - 495 Jefferson St, San Francisco, CA 94109, USA",
        "main": "Argonaut Hotel",
        "sub": "495 Jefferson St, San Francisco, CA 94109, USA",
    },
    {
        "label": "Hotel Emblem - 562 Sutter St, San Francisco, CA 94102, USA",
        "main": "Hotel Emblem",
        "sub": "562 Sutter St, San Francisco, CA 94102, USA",
    },
    {
        "label": "Hotel Triton - 342 Grant Ave, San Francisco, CA 94108, USA",
        "main": "Hotel Triton",
        "sub": "342 Grant Ave, San Francisco, CA 94108, USA",
    },
    {
        "label": "Hotel North Beach - 935 Kearny St, San Francisco, CA 94133, USA",
        "main": "Hotel North Beach",
        "sub": "935 Kearny St, San Francisco, CA 94133, USA",
    },
    {
        "label": "Hotel Spero - 405 Taylor St, San Francisco, CA 94102, USA",
        "main": "Hotel Spero",
        "sub": "405 Taylor St, San Francisco, CA 94102, USA",
    },
    {
        "label": "Hotel Caza - 1300 Columbus Ave, San Francisco, CA 94133, USA",
        "main": "Hotel Caza",
        "sub": "1300 Columbus Ave, San Francisco, CA 94133, USA",
    },
    {
        "label": "The Donatello - 501 Post St, San Francisco, CA 94102, USA",
        "main": "The Donatello",
        "sub": "501 Post St, San Francisco, CA 94102, USA",
    },
    {
        "label": "Hotel Abri - 127 Ellis St, San Francisco, CA 94102, USA",
        "main": "Hotel Abri",
        "sub": "127 Ellis St, San Francisco, CA 94102, USA",
    },
    {
        "label": "Hotel Fusion - 140 Ellis St, San Francisco, CA 94102, USA",
        "main": "Hotel Fusion",
        "sub": "140 Ellis St, San Francisco, CA 94102, USA",
    },
    {
        "label": "Hotel Whitcomb - 1231 Market St, San Francisco, CA 94103, USA",
        "main": "Hotel Whitcomb",
        "sub": "1231 Market St, San Francisco, CA 94103, USA",
    },
    {
        "label": "Hotel Majestic - 1500 Sutter St, San Francisco, CA 94109, USA",
        "main": "Hotel Majestic",
        "sub": "1500 Sutter St, San Francisco, CA 94109, USA",
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
DISCOUNT_PERCENTAGE_DATA = [
    {"discount_percentage": "5.00"},
    {"discount_percentage": "10.00"},
    {"discount_percentage": "15.00"},
]

STRING_OPERATORS = [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS]
LOGICAL_OPERATORS = [EQUALS, NOT_EQUALS, GREATER_THAN, LESS_THAN, GREATER_EQUAL, LESS_EQUAL]
LIST_OPERATORS = [CONTAINS, NOT_CONTAINS, IN_LIST, NOT_IN_LIST]
BOOL_OPERATORS = [EQUALS, NOT_EQUALS]

FIELD_OPERATORS_MAP_ENTER_LOCATION = {"location": STRING_OPERATORS}
FIELD_OPERATORS_MAP_ENTER_DESTINATION = {
    "destination": [EQUALS, NOT_EQUALS],
    # "destination": STRING_OPERATORS
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
FIELD_OPERATORS_MAP_SEARCH_RIDE = {
    "destination": STRING_OPERATORS,
    "location": STRING_OPERATORS,
    "scheduled": LOGICAL_OPERATORS,
}
FIELD_OPERATORS_MAP_SELECT_CAR = {
    "destination": STRING_OPERATORS,
    "location": STRING_OPERATORS,
    "ride_name": STRING_OPERATORS,
    "scheduled": LOGICAL_OPERATORS,
}
FIELD_OPERATORS_MAP_RESERVE_RIDE = {
    **FIELD_OPERATORS_MAP_SELECT_CAR,
}
