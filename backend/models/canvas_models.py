from pydantic import BaseModel

class Course(BaseModel):
  id: int
  name: str
  account_id: int
  
  class Config:
    extra = "ignore"
  
class Courses(BaseModel):
  courses: list[Course]
  
  class Config:
    extra = "ignore"
