from pydantic import BaseModel

class Module(BaseModel):
  id: int
  name: str
  items_url: str 
  
  class Config:
    extra = "ignore"

# class Folder_root(BaseModel):
#   context_id: int
#   parent_folder_id: str
  
#   class Config:
#     extra = "ignore"


class File(BaseModel):
  id: int| None
  folder_id: int | None
  display_name: str
  file_name: str | None
  url: str
  
  class Config:
    extra = "ignore"

class Files(BaseModel):
  files: list[Files]

  
#every Pages object contains
# class Page(BaseModel):
#   #this is a the main page in pages which contained titled folders with all files relevant to a section. 
#   #this can be a singular folder
#   pages: list[Directory]


class Directory(BaseModel): #this is generally a link to a folder conatining all the files
  html_url: str
  
  class Config:
    extra = "ignore"

class DirectoryPage(BaseModel):
  title: str #name of the folder
  body: str #this contains the html we need to parse to actually get all the files
  
  class Config:
    extra = "ignore"
    
    

def parse_files(html: str) -> list[File]:
  soup = BeautifulSoup(html, 'html.parser')
  files = []

  # Extract files from <link> tags (e.g., CSS files)
  for link in soup.find_all('link', href=True):
    url = link['href']
    # Get the file name from the URL (decode percent-encoded parts)
    file_name = unquote(url.split('/')[-1])
    files.append(File(display_name=file_name, url=url, file_name=file_name, folder_id=None, id=None))

  # Extract files from <a> tags that contain file links
  for a in soup.find_all('a', href=True):
    # Check if the anchor has a file-specific class
    if 'instructure_file_link' in a.get('class', []):
      url = a['href']
      # Prefer the title attribute for the file name if available, otherwise use the link text
      file_name = a.get('title') or a.text.strip()
      files.append(File(display_name=file_name, url=url, file_name=file_name, folder_id=None, id=None))

  files_obj = Files(files=files)
  return files_obj