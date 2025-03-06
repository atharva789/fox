from fastapi import FastAPI, HTTPException, Body, Depends, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from routers import courses
import os
import json
import requests
from dotenv import load_dotenv
from client import prisma
from typing import List, Optional
from pydantic import parse_obj_as

from datetime import datetime, timedelta
from jose import JWTError, jwt
from keycove import hash
from models.canvas_models import Courses, Course
from models.parsing_models import Module, File, Directory, DirectoryPage
from models.parsing_models import parse_files
from prisma import errors

load_dotenv()

app = FastAPI()

app.include_router(courses.router)

@app.on_event("startup")
async def startup():
  await prisma.connect()

@app.on_event("shutdown")
async def shutdown():
  await prisma.disconnect()

origins = [
  "http://localhost",
  "http://localhost:3000",
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

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

async def authenticate_user(canvas_api_key: str):
  #check if api_key belongs in database
  hashed_key = hash(value_to_hash=canvas_api_key)
  user = await prisma.student.find_unique(where={'apiKey' : f'{hashed_key}'})
  if user is None:
    return None
  else:
    return user
  

async def parse_data(int: course_id, dict: header) -> bool:
  #parses and stores modules and files from Canvas as Module, Resource, Assignment, AssignmentAttachment objects
  
  #if folders are not authorized, then files are not authorized
    #then, either check modules or check pages
    
  #else if folders exist but is of length 0,
    #check files/
    
#we will have:
  #1. folder_root, folders_url, files_url are pretty useless mostly
  #4. modules_url: lists all module_id (s), titles, and module context (each containing a path to a file) 
  #5. #pages_url: lists the pages directory, which is where some instructors store their files
    
  #we will parse all the above URLs with PyDantic Models
  
  #if a course has no modules, it will always be empty
  #course files can be retrieved 2 ways:
    #1. fetching /files by course_id: this is generally open for very few courses
    #2. getting the specific files endpoint via course_id with the course_id/folders endpoint: this is almost always the case, and is more annoying
  
  try:
    modules_response = requests.get(f"https://canvas.case.edu/api/v1/courses/{course_id}/modules?per_page=100", headers=header)
    #if modules is empty, we only parse files/folders from pages
    
    #getting files from modules
      #1. course_id/modules has the modules objects with the items_url 
      #2. items_url contains 1 or more files endpoints
      #3. each item in the items_url has a new 'url' endpoint
      #4. each 'url' endpoint contains a new object of type File with attribute url (this is the actual downloadable link)
    
    #summary of the obtaining files from modules:
    # Module(s) -> item(s) -> item -> file
    
    modules_data = modules_response.json()
    if len(modules_data) == 0:
      #check files/folders
      try:
        pages_response = requests.get(f"https://canvas.case.edu/api/v1/courses/{course_id}/pages?per_page=100", headers=header)
        pages_response.raise_for_status()
        pages_data = pages_response.json()
        for item in pages_data: #each page is a folder: one page can contain several files in the 'body'
          html_url = item["html_url"]
          files_directory = requests.get(html_url, headers=header)
          files_data = files_directory.json()
          files_arr: List[Files] = parse_files(files_data["body"])
          #store in prisma
          count: int = await prisma.resource.create_many(data=files_arr)
          #logging
        return True
      except requests.exceptions.HTTPError as e:
        if response.status_code == 403: #means that /pages endpoint is not enabled for that course
          print("Forbidden (403) error:", e)
        else:
          print(f"HTTP error: {e}, status code: {response.status_code}")
      except requests.exceptions.RequestException as e:
        print(f"Request exception: {e}")
      except KeyError:
        print("cannot parse object")
        return False
      except errors.PrismaClientKnownRequestError as e:
        print("Prisma couldn't create 'File' object: some constraint violated")
        return False
      except Exception as e:
        print(e)
        return False
    elif len(modules_data) == 0  and 1 > 0: #case where modules & pages doesn't work
      print()
    else:
      for module in modules_data:
        #parse each module
        module: Module = module
        context: str = module.name #we will add this context field to every resource
        items_url = module.items_url
        items_response = requests.get(items_url, header)
        items_json = items.json()
        files_arr: list[Files] = []
        for item in items_json:
          item_endpoint = item["url"]
          files_response = requests.get(item_endpoint, headers=header)
          file: File = item
          files_arr.append(file)
        files_len = len(files_arr)
        count: int = await prisma.resource.create_many(data=files_arr)
        if files_len != count:
          print("Not all files from canvas could be loaded")
          return False
      return True
        #prisma create to store each file with the same context (module name)
  except requests.exceptions.HTTPError as e:
    if e.status_code == 403:
      print("Idk what happened")
      return False
  return False
  
  

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), response: Response = None):
  api_key = form_data.username
  user = await authenticate_user(api_key)
  if not user:
    #create user
    #check if api key works
    try:
      hashed_key = hash(value_to_hash=api_key)
      user = await prisma.student.create(
        data={
          "apiKey": hashed_key,
          "Course": []
        }
      )
      user_id = user.id
      #pull all assignments, create all courses if not already created
      headers = {'Authorization': f"Bearer {api_key}"}
      course_response = requests.get("https://canvas.case.edu/api/v1/courses/?enrollment_state=active&include[]=term", headers=headers)
      for item in course_response.json():
        #create course object for user
        #if course exists, add student_id to course, vice_versa
        existing_courses: Courses = await prisma.course.find_unique(
          where={
            'code': item["id"]
          }
        )
        #do the same for assignments
        #only assignmentAttachments (the student's homework submissions that is) will differ for each student
        if len(existing_courses) !=0:
          #first list all student courses and check whether they already exist in the database: if yes, then we just add them to this student
          for course in existing_courses:
            result = await prisma.course.update(
              where={'code': course.code},
              data={
                'students': {
                  'connect': {'id': user_id}
                }
              }
            )
        else:
          course = await prisma.course.create(
            data={
              "name": item["name"], 
              "code": item["id"],
              "StudentID": user_id, 
              "Course": [],
              "Module": [], 
              "Assignments": [], 
              "StudyGuide": []
            }
          )
          course_id = course.id
          
          files_parsed: bool = parse_data(course.id, headers)
          if not files_parsed:
            raise HTTPException(status_code=400, detail={'could not parse canvas modules/files'})
        
    except Exception as e:
      raise HTTPException(status_code=400, detail=str(e))
  access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRES")))
  access_token = create_access_token(
    data={"sub": api_key}, expires_delta=access_token_expires
  )
  
  response.set_cookie(
    key="token",
    value=access_token,
    httponly=True,                   # Prevents JavaScript from reading the cookie
    max_age=int(access_token_expires.total_seconds()),
    path="/",
    samesite="lax",
    secure=(os.getenv("ENV", "development") == "production")
  )
  print({"token": access_token, "token_type": "bearer"})
  return {"token": access_token, "token_type": "bearer"}

def get_current_user_from_cookie(request: Request):
  token = request.cookies.get("token")
  if not token:
    raise HTTPException(
      status_code=status.HTTP_401_UNAUTHORIZED,
      detail="Not authenticated: token missing in cookie",
    )
  try:
    payload = jwt.decode(token, os.getenv("FASTAPI_SECRET_KEY", "your_secret_key"), algorithms=[os.getenv("ALGORITHM", "HS256")])
    canvas_api_key: str = payload.get("sub")
    if canvas_api_key is None:
      raise HTTPException(status_code=401, detail="Invalid token")
  except jwt.PyJWTError:
    raise HTTPException(status_code=401, detail="Invalid token")
  return canvas_api_key

@app.get("/api/validate")
async def validate(apiKey: str = Depends(get_current_user_from_cookie)):
  return {"authenticated": True, "apiKey": hash(value_to_hash=apiKey)}

@app.get("/get-courses")
async def get_home(canvas_api_key: str = Depends(get_current_user_from_cookie)):
  headers = {'Authorization': f"Bearer {canvas_api_key}"}
  response = requests.get("https://canvas.case.edu/api/v1/courses/?enrollment_state=active&include[]=term", headers=headers)
  data = response.json()
  try:
    courseData = Courses(**data) #parses data into desired pydantic model
    return courseData
  except TypeError:
    # return HTTPException(
    #   status_code=status.HTTP_401_UNAUTHORIZED, 
    #   detail="canvas api request not successful or error retrieving canvas api key from jwt token", 
    #   headers={"WWW-Authenticate": "Bearer"}
    # )
    return data