from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, AnyUrl, field_validator
from faker import Faker


class Genre(BaseModel):
    id: Optional[int] = None
    name: str = Field(max_length=100)

    model_config = {
        "from_attributes": True
    }


class Comment(BaseModel):
    id: Optional[int] = None
    movie_id: int
    name: str = Field(max_length=100)
    content: str
    created_at: Optional[datetime] = None
    avatar: Optional[str] = None

    model_config = {
        "from_attributes": True
    }


class Movie(BaseModel):
    id: Optional[int] = None
    name: str = Field(max_length=250)
    desc: str
    year: int = Field(ge=1900, le=2100)
    img: str
    director: Optional[str] = Field(None, max_length=250)
    cast: Optional[str] = None
    duration: Optional[int] = Field(None, description="Duration in minutes")
    trailer_url: Optional[AnyUrl] = None
    rating: float = Field(0.0, ge=0.0, le=5.0, description="Rating between 0 and 5")
    genres: List[Genre] = []
    comments: List[Comment] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

    @field_validator('cast', mode='before')
    @classmethod
    def cast_to_list(cls, v):
        if not v:
            return []
        return [actor.strip() for actor in v.split(',') if actor.strip()]

    def get_genre_list(self) -> str:
        return ", ".join([g.name for g in self.genres])

    def get_cast_list(self) -> List[str]:
        if not self.cast:
            return []
        return [actor.strip() for actor in self.cast.split(',') if actor.strip()]


class UserProfile(BaseModel):
    id: Optional[int] = None
    user_id: int
    bio: Optional[str] = Field(None, max_length=500)
    profile_pic: Optional[str] = None
    favorite_genres: List[Genre] = []
    website: Optional[AnyUrl] = None
    location: Optional[str] = Field(None, max_length=100)

    model_config = {
        "from_attributes": True
    }


class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    profile: Optional[UserProfile] = None

    model_config = {
        "from_attributes": True
    }


class ContactMessage(BaseModel):
    id: Optional[int] = None
    name: str = Field(max_length=100)
    email: str
    subject: str = Field(max_length=200)
    message: str
    created_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }


MODELS = [Genre,Comment,Movie,UserProfile,User,ContactMessage]

# ================ Data Generation Functions ================
# Initialize Faker
faker = Faker()


def generate_fake_genre() -> Genre:
    return Genre(
        id=faker.random_int(min=1, max=100),
        name=faker.word().capitalize()
    )


def generate_fake_movie() -> Movie:
    return Movie(
        id=faker.random_int(min=1, max=1000),
        name=faker.catch_phrase(),
        desc=faker.text(),
        year=faker.random_int(min=1950, max=2023),
        img=f"gallery/{faker.file_name(extension='jpg')}",
        director=faker.name(),
        cast=", ".join([faker.name() for _ in range(3)]),
        duration=faker.random_int(min=60, max=180),
        trailer_url=faker.url(),
        rating=round(faker.random.uniform(1.0, 5.0), 1),
        created_at=faker.date_time_this_year(),
        updated_at=faker.date_time_this_month(),
        genres=[generate_fake_genre() for _ in range(faker.random_int(min=1, max=3))]
    )


def generate_fake_comment(movie_id: Optional[int] = None) -> Comment:
    return Comment(
        id=faker.random_int(min=1, max=1000),
        movie_id=movie_id or faker.random_int(min=1, max=100),
        name=faker.name(),
        content=faker.text(),
        created_at=faker.date_time_this_year(),
        avatar=f"gallery/avatars/{faker.file_name(extension='jpg')}" if faker.boolean() else None
    )


def generate_fake_user_profile(user_id: Optional[int] = None) -> UserProfile:
    return UserProfile(
        id=faker.random_int(min=1, max=1000),
        user_id=user_id or faker.random_int(min=1, max=100),
        bio=faker.text(max_nb_chars=200) if faker.boolean() else None,
        profile_pic=f"gallery/profiles/{faker.file_name(extension='jpg')}" if faker.boolean() else None,
        favorite_genres=[generate_fake_genre() for _ in range(faker.random_int(min=0, max=3))],
        website=faker.url() if faker.boolean() else None,
        location=faker.city() if faker.boolean() else None
    )


def generate_fake_user() -> User:
    user_id = faker.random_int(min=1, max=100)
    return User(
        id=user_id,
        username=faker.user_name(),
        email=faker.email(),
        first_name=faker.first_name(),
        last_name=faker.last_name(),
        profile=generate_fake_user_profile(user_id)
    )


def generate_fake_contact_message() -> ContactMessage:
    return ContactMessage(
        id=faker.random_int(min=1, max=1000),
        name=faker.name(),
        email=faker.email(),
        subject=faker.sentence(),
        message=faker.text(max_nb_chars=200),
        created_at=faker.date_time_this_year()
    )


def generate_fake_data(count: int = 5) -> Dict[str, List[Any]]:
    """Generate fake data for all models"""
    movies = [generate_fake_movie() for _ in range(count)]

    # Add comments to movies
    for movie in movies:
        movie.comments = [generate_fake_comment(movie.id) for _ in range(faker.random_int(min=0, max=5))]

    return {
        "genres": [generate_fake_genre() for _ in range(count)],
        "movies": movies,
        "comments": [c for m in movies for c in m.comments],
        "users": [generate_fake_user() for _ in range(count)],
        "contact_messages": [generate_fake_contact_message() for _ in range(count)]
    }
