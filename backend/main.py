from fastapi import FastAPI, HTTPException, Body, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from routers import courses
import os
from dotenv import load_dotenv
from client import prisma
from pydantic import BaseModel
from typing import List, Optional

from datetime import datetime, timedelta
from jose import JWTError, jwt
from keycove import hash

load_dotenv()

app = FastAPI()

app.include_router(courses.router)

@app.on_event("startup")
async def startup():
  await prisma.connect()

@app.on_event("shutdown")
async def shutdown():
  await prisma.disconnect()

@app.get("/")
def read_root():
  return {"Hello": "World"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#if issues access token for user credentials
def create_access_token(data: dict, expires_delta: timedelta = None):
  to_encode = data.copy()
  if expires_delta:
    expire = datetime.utcnow() + expires_delta
  else:
    expire = datetime.utcnow() + timedelta(minutes=os.getevn("ACCESS_TOKEN_EXPIRES"))
  to_encode.update({"exp": expire})
  encoded_jwt = jwt.encode(to_encode, os.getenv("FASTAPI_SECRET_KEY"), algorithm=os.getenv("ALGORITHM"))
  return encoded_jwt

def authenticate_user(canvas_api_key: str):
  #check if api_key belongs in database
  hashed_key = hash(value_to_hash=canvas_api_key)
  user = prisma.student.find_unique(where={'apiKey' : f'{hashed_key}'})
  if user is None:
    return None
  else:
    return user
  
@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
  user = authenticate_user(form_data.apiKey)
  if not user:
    #create user
    #check if api key works
    try:
      # Create a new student record in the database
      #frontend makes an API request with existing key and fetches your name to validate 
      #if provided API key is yours
      hashed_key = hash(value_to_hash=api_key)
      user = await prisma.student.create(
        data={
          "apiKey": hashed_key,
        }
      )
    except Exception as e:
      raise HTTPException(status_code=400, detail=str(e))
  access_token_expires = timedelta(minutes=os.getenv("ACCESS_TOKEN_EXPIRES"))
  access_token = create_access_token(
    data={"sub": user["apiKey"]}, expires_delta=access_token_expires
  )
  return {"access_token": access_token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
  credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
  )
  try:
    payload = jwt.decode(token, os.getenv("FASTAPI_SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
    canvas_api_key : str = payload.get("sub")
    if canvas_api_key is None:
      raise credentials_exception
  except JWTError:
    raise credentials_exception
  return canvas_api_key

@app.get("/home")
async def get_home(canvas_api_key: str = Depends(get_current_user)):
  return {"home": "content"}
    