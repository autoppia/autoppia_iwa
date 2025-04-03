MOVIES_DATA = [
    {
        "id": 1,
        "name": "The Shawshank Redemption",
        "desc": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
        "year": 1994,
        "director": "Frank Darabont",
        "cast": "Tim Robbins, Morgan Freeman, Bob Gunton",
        "duration": 142,
        "trailer_url": "https://www.youtube.com/watch?v=6hB3S9bIaco",
        "rating": 4.8,
        "img_file": "the-shawshank-redemption.jpg",
        "genres": ["Drama"],
    },
    {
        "id": 2,
        "name": "The Godfather",
        "desc": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
        "year": 1972,
        "director": "Francis Ford Coppola",
        "cast": "Marlon Brando, Al Pacino, James Caan",
        "duration": 175,
        "trailer_url": "https://www.youtube.com/watch?v=sY1S34973zA",
        "rating": 4.7,
        "img_file": "the-godfather.jpg",
        "genres": ["Crime", "Drama"],
    },
    {
        "id": 3,
        "name": "The Dark Knight",
        "desc": "When the menace known as the Joker wreaks havoc and chaos on the people of Gotham, Batman must accept one of the greatest psychological and physical tests of his ability to fight injustice.",
        "year": 2008,
        "director": "Christopher Nolan",
        "cast": "Christian Bale, Heath Ledger, Aaron Eckhart",
        "duration": 152,
        "trailer_url": "https://www.youtube.com/watch?v=EXeTwQWrcwY",
        "rating": 4.7,
        "img_file": "the-dark-knight.jpg",
        "genres": ["Action", "Crime", "Drama", "Thriller"],
    },
    {
        "id": 4,
        "name": "Pulp Fiction",
        "desc": "The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.",
        "year": 1994,
        "director": "Quentin Tarantino",
        "cast": "John Travolta, Uma Thurman, Samuel L. Jackson",
        "duration": 154,
        "trailer_url": "https://www.youtube.com/watch?v=s7EdQ4FqbhY",
        "rating": 4.6,
        "img_file": "pulp-fiction.jpg",
        "genres": ["Crime", "Drama"],
    },
    {
        "id": 5,
        "name": "Inception",
        "desc": "A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
        "year": 2010,
        "director": "Christopher Nolan",
        "cast": "Leonardo DiCaprio, Joseph Gordon-Levitt, Ellen Page",
        "duration": 148,
        "trailer_url": "https://www.youtube.com/watch?v=YoHD9XEInc0",
        "rating": 4.5,
        "img_file": "inception.jpg",
        "genres": ["Action", "Adventure", "Sci-Fi", "Thriller"],
    },
    {
        "id": 6,
        "name": "The Lord of the Rings: The Fellowship of the Ring",
        "desc": "A meek Hobbit from the Shire and eight companions set out on a journey to destroy the powerful One Ring and save Middle-earth from the Dark Lord Sauron.",
        "year": 2001,
        "director": "Peter Jackson",
        "cast": "Elijah Wood, Ian McKellen, Orlando Bloom",
        "duration": 178,
        "trailer_url": "https://www.youtube.com/watch?v=V75dMMIW2B4",
        "rating": 4.6,
        "img_file": "the-lord-of-the-rings-the-fellowship-of-the-ring.jpg",
        "genres": ["Action", "Adventure", "Drama", "Fantasy"],
    },
    {
        "id": 7,
        "name": "Forrest Gump",
        "desc": "The presidencies of Kennedy and Johnson, the events of Vietnam, Watergate, and other historical events unfold through the perspective of an Alabama man with an IQ of 75, whose only desire is to be reunited with his childhood sweetheart.",
        "year": 1994,
        "director": "Robert Zemeckis",
        "cast": "Tom Hanks, Robin Wright, Gary Sinise",
        "duration": 142,
        "trailer_url": "https://www.youtube.com/watch?v=bLvqoHBptjg",
        "rating": 4.6,
        "img_file": "forrest-gump.jpg",
        "genres": ["Drama", "Romance"],
    },
    {
        "id": 8,
        "name": "The Matrix",
        "desc": "A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
        "year": 1999,
        "director": "Lana Wachowski, Lilly Wachowski",
        "cast": "Keanu Reeves, Laurence Fishburne, Carrie-Anne Moss",
        "duration": 136,
        "trailer_url": "https://www.youtube.com/watch?v=vKQi3bBA1y8",
        "rating": 4.5,
        "img_file": "the-matrix.jpg",
        "genres": ["Action", "Sci-Fi"],
    },
    {
        "id": 9,
        "name": "Goodfellas",
        "desc": "The story of Henry Hill and his life in the mob, covering his relationship with his wife Karen Hill and his mob partners Jimmy Conway and Tommy DeVito in the Italian-American crime syndicate.",
        "year": 1990,
        "director": "Martin Scorsese",
        "cast": "Robert De Niro, Ray Liotta, Joe Pesci",
        "duration": 146,
        "trailer_url": "https://www.youtube.com/watch?v=qo5jJpHtI1Y",
        "rating": 4.6,
        "img_file": "goodfellas.jpg",
        "genres": ["Biography", "Crime", "Drama"],
    },
    {
        "id": 10,
        "name": "Interestellar",
        "desc": "A team of explorers travel through a wormhole in space in an attempt to ensure humanity's survival.",
        "year": 2014,
        "director": "Christopher Nolan",
        "cast": "Matthew McConaughey, Anne Hathaway, Jessica Chastain",
        "duration": 169,
        "trailer_url": "https://www.youtube.com/watch?v=zSWdZVtXT7E",
        "rating": 4.5,
        "img_file": "interstellar.jpg",
        "genres": ["Adventure", "Drama", "Sci-Fi"],
    },
]

# constants.py

EQUALS = "equals"
NOT_EQUALS = "not_equals"
CONTAINS = "contains"
NOT_CONTAINS = "not_contains"
GREATER_THAN = "greater_than"
LESS_THAN = "less_than"
GREATER_EQUAL = "greater_equal"
LESS_EQUAL = "less_equal"
IN_LIST = "in_list"
NOT_IN_LIST = "not_in_list"

# Sugerencia de mapeo campo -> lista de operadores válidos
FIELD_OPERATORS_MAP_FILM = {
    "name": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "director": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "year": [EQUALS, NOT_EQUALS, GREATER_THAN, LESS_THAN, GREATER_EQUAL, LESS_EQUAL, IN_LIST, NOT_IN_LIST],
    "rating": [EQUALS, NOT_EQUALS, GREATER_THAN, LESS_THAN, GREATER_EQUAL, LESS_EQUAL],
    "duration": [EQUALS, NOT_EQUALS, GREATER_THAN, LESS_THAN, GREATER_EQUAL, LESS_EQUAL],
    "genres": [CONTAINS, NOT_CONTAINS, IN_LIST, NOT_IN_LIST],
}

FIELD_OPERATORS_MAP_CONTACT = {
    "name": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "email": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "subject": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "message": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
}

FIELD_OPERATORS_MAP_ADD_COMMENT = {
    "movie_name": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "commenter_name": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
    "content": [EQUALS, NOT_EQUALS, CONTAINS, NOT_CONTAINS],
}

FIELD_OPERATORS_MAP_EDIT_USER = {
    "first_name": [EQUALS, CONTAINS, NOT_CONTAINS],
    "last_name": [EQUALS, CONTAINS, NOT_CONTAINS],
    "bio": [EQUALS, CONTAINS, NOT_CONTAINS],
    "location": [EQUALS, CONTAINS, NOT_CONTAINS],
    "website": [EQUALS, CONTAINS, NOT_CONTAINS],
    "favorite_genres": [IN_LIST, NOT_IN_LIST],
}
