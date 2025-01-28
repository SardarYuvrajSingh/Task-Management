# from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
# from fastapi import APIRouter, Depends, HTTPException
# from pydantic import BaseModel
# from streamlit import status
# from src.connection import get_db
# from sqlalchemy.orm import Session

# router = APIRouter()
# oa2=OAuth2PasswordBearer(tokenUrl="token")

# class User(BaseModel):
#     username: str
#     email: str | None = None
#     full_name: str | None = None
#     disabled: bool | None = None

# class UserInDB(User):
#     hashed_password: str

# fake_users_db = {
#     "johndoe": dict(
#         username="johndoe",
#         full_name="John Doe",
#         email="johndoe@example.com",
#         hashed_password="fakehashedsecret",
#         disabled=False,
#     ),
#     "alice": dict(
#         username="alice",
#         full_name="Alice Wonderson",
#         email="alice@example.com",
#         hashed_password="fakehashedsecret2",
#         disabled=True,
#     ),
# }


# def fake_hash_password(password: str):
#     return f"fakehashed{password}"


# class User(BaseModel):
#     username: str
#     email: str | None = None
#     full_name: str | None = None
#     disabled: bool | None = None


# class UserInDB(User):
#     hashed_password: str


# def get_user(db, username: str):
#     if username in db:
#         user_dict = db[username]
#         return UserInDB(**user_dict)


# def fake_decode_token(token):
#     return get_user(fake_users_db, token)


# async def get_current_user(token: str = Depends(oa2)):
#     user = fake_decode_token(token)
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid authentication credentials",
#             headers={"WWW-Authenticate": "Bearer"},
#         )
#     return user


# async def get_current_active_user(current_user: User = Depends(get_current_user)):
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user


# @router.post("/token")
# async def login(form_data: OAuth2PasswordRequestForm = Depends()):
#     user_dict = fake_users_db.get(form_data.username)
#     if not user_dict:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")
#     user = UserInDB(**user_dict)
#     hashed_password = fake_hash_password(form_data.password)
#     if not hashed_password == user.hashed_password:
#         raise HTTPException(status_code=400, detail="Incorrect username or password")

#     return {"access_token": user.username, "token_type": "bearer"}


# @router.get("/users/me")
# async def get_me(current_user: User = Depends(get_current_active_user)):
#     return current_user


# @router.get("/items/")
# async def read_items(token: str = Depends(oa2)):
#     return {"token": token}


from datetime import datetime,timedelta
from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from dotenv import load_dotenv
import os
from fastapi import Depends,HTTPException
from jose import JWSError, jwt
# import jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import sessionmaker, Session
from src.schemas import UserCreate
from src.connection import get_db
from model.sql import User
from model import sql
 
load_dotenv()
 
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "mySecret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
 
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
 
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)
 
def get_password_hash(password: str):
    return pwd_context.hash(password)
 
def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None
   
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
   
    db_user = db.query(User).filter(User.username == payload.get("sub")).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
   
    return db_user


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
 

from fastapi import HTTPException

# Token endpoint with try-except block
@router.post("/token/")
async def token(user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> dict:
    try:
        print("db_user")
        db_user = db.query(sql.User).filter(sql.User.username == user.username).first()
        print(db_user)
        if db_user is None or not verify_password(user.password, db_user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        access_token = create_access_token(data={"sub": db_user.username})
        return {"access_token": access_token, "token_type": "bearer"}
    
    except Exception as e:
        # You can log the exception here for debugging
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}" ) from e


 
 
 
@router.post("/register/")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(sql.User).filter(sql.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")
   
    hashed_password = get_password_hash(user.password)
 
    new_user = sql.User(username=user.username, hashed_password=hashed_password)
   
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
   
    return {"message": "User created successfully"}