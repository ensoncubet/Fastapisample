from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine, sessionLocal
from sqlalchemy.orm import Session
from dep import get_current_user
from utils import get_hashed_password
from uuid import uuid4
from fastapi import FastAPI, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import RedirectResponse
from schemas import UserOut, UserAuth, TokenSchema
from utils import (
    get_hashed_password,
    create_access_token,
    create_refresh_token,
    verify_password
)
from uuid import uuid4

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class PostBase(BaseModel):
    title: str
    content:str
    user_id:int
   
class UserBase(BaseModel):
    email: str

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.post('/signup', summary="Create new user", response_model=UserOut)
async def create_user(data: UserAuth, db: db_dependency):
    # querying database to check if user already exist
    user = db.get(data.email, None)
    if user is not None:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exist"
        )
    user = {
        'email': data.email,
        'password': get_hashed_password(data.password),
        'id': str(uuid4())
    }
    db[data.email] = user    # saving user to database
    return user


@app.post('/login', summary="Create access and refresh tokens for user", response_model=TokenSchema)
async def login(db:db_dependency, form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.get(form_data.username, None)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )

    hashed_pass = user['password']
    if not verify_password(form_data.password, hashed_pass):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    return {
        "access_token": create_access_token(user['email']),
        "refresh_token": create_refresh_token(user['email']),
    }

@app.get('/me', summary='Get details of currently logged in user', response_model=UserOut)
async def get_me(user: UserBase = Depends(get_current_user)):
    return user

@app.post("/posts/", status_code=status.HTTP_201_CREATED)
async def create_post(post: PostBase, db: db_dependency, user: UserBase = Depends(get_current_user)):
    db_post = models.Post(**post.dict())
    db.add(db_post)
    db.commit()

@app.get("/posts/{posts_id}", status_code=status.HTTP_200_OK)
async def get_post(posts_id: int, db: db_dependency, user: UserBase = Depends(get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == posts_id).first()
    if post is None:
        raise Exception(status.HTTP_404_NOT_FOUND, detail='post not found')
    return post