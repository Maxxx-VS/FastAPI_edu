from urllib.request import AbstractBasicAuthHandler
from fastapi import FastAPI, HTTPException, Path, Query, Body
from typing import Optional, List, Dict, Annotated
from fastapi.params import Query
from pydantic import BaseModel, Field

app = FastAPI()

# @app.get("/")
# async def home() -> dict[str, str]:
#     return {'data': "message"}

# @app.get("/contacts")
# async def contacts() -> int:
#     return 34

class User(BaseModel):
    id: int
    name: str
    age: int

class Post(BaseModel):
    id: int
    title: str
    body: str
    author: User

class PostCreate(BaseModel):
    title: str
    body: str
    author_id: int


class UserCreate(BaseModel):
    name: Annotated[
        str, Field(..., title='Имя пользователя', min_length=2, max_length=20)
    ]
    age: Annotated[
        int, Field(..., title='Возраст пользователя', ge=1, le=120)
    ]

users = [
    {'id': 1, 'name': 'John', 'age': 35},
    {'id': 2, 'name': 'Alex', 'age': 12},
    {'id': 3, 'name': 'Bob', 'age': 45},
]

posts = [
    {'id': 1, 'title': 'News 1', 'body': 'text 1', 'author': users[1]},
    {'id': 2, 'title': 'News 2', 'body': 'text 2', 'author': users[0]},
    {'id': 3, 'title': 'News 3', 'body': 'text 3', 'author': users[2]},
]

@app.post("/user/add")
async def user_add(user: Annotated[
    UserCreate,
    Body(..., example={
        "name": "UserName",
        "age": 1
    })
]) -> User:
    new_user_id = len(users) + 1

    new_user= {'id': new_user_id, 'name': user.name, 'age': user.age}
    users.append(new_user)

    return User(**new_user)


@app.get("/items")
async def items() -> List[Post]:
    return [Post(**post)for post in posts]


@app.post("/items/add")
async def add_item(post: PostCreate) -> Post:
    author = next((user for user in users if user['id'] == post.author_id), None)
    if not author:
        raise HTTPException(status_code=404, detail="User Not Faind")

    new_post_id = len(posts) + 1

    new_post = {'id': new_post_id, 'title': post.title, 'body': post.body, 'author': author}
    posts.append(new_post)
    return Post(**new_post)


@app.get("/items/{id}")
async def items(id: Annotated[int, Path(...,
                                        title='Здесь указывается id поста',
                                        ge=1,
                                        lt=100)]) -> Post:
    for post in posts:
        if post['id'] == id:
            return Post(**post)

    raise HTTPException(status_code=404, detail='Post not found')


@app.get("/search")
async def search(post_id: Annotated[
    Optional[int],
    Query(title="id of post",
          ge=1,
          le=50)
]) -> Dict[str, Optional[Post]]:
    if post_id:
        for post in posts:
            if post['id'] == post_id:
                return {'data': Post(**post)}
        raise HTTPException(status_code=404, detail='Post not found')
    else:
        return {'data': None}