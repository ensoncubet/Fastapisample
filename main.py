from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated
import models
from database import engine, sessionLocal
from sqlalchemy.orm import Session
# import schemas
from typing import List

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class PostBase(BaseModel):
    title: str
    content:str
    user_id:int
   
class UserBase(BaseModel):
    username: str

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# @app.post("/register")
# def register_user(user: schemas.UserCreate, session: Session = Depends(get_session)):
#     existing_user = session.query(models.User).filter_by(email=user.email).first()
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Email already registered")

#     encrypted_password =get_hashed_password(user.password)

#     new_user = models.User(username=user.username, email=user.email, password=encrypted_password )

#     session.add(new_user)
#     session.commit()
#     session.refresh(new_user)

#     return {"message":"user created successfully"}

@app.post("/posts/", status_code=status.HTTP_201_CREATED)
async def create_post(post: PostBase, db: db_dependency):
    db_post = models.Post(**post.dict())
    db.add(db_post)
    db.commit()

@app.get("/posts/{posts_id}", status_code=status.HTTP_200_OK)
async def get_post(posts_id: int, db: db_dependency):
    user = db.query(models.Post).filter(models.Post.id == posts_id).first()
    if user is None:
        raise Exception(status.HTTP_404_NOT_FOUND, detail='post not found')
    return user

@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserBase, db: db_dependency):
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()

@app.get("/users/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(user_id: int, db: db_dependency):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        raise Exception(status.HTTP_404_NOT_FOUND, detail='user not found')
    return user
