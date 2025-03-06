from fastapi import APIRouter, Depends, FastAPI, HTTPException
from client import prisma
import requests
import io
import httpx
import fitz  # PyMuPDF
import openai


prompt = """
<|system|>
You are a student in a course and you need to create a study guide for the course. The study guide should include all the important information from the course materials. You can use the course materials to help you answer the question.
The study guide should include all the important information from the course materials. All information should be explained with at least two detailed examples, and at the end of each major concept you should include some practice questions. The study guide should be well-organized and easy to read, and should be formatted in markdown. You can use the course materials to help you answer the question. Here is the question you need to answer.

'Context' stores context vector/vectors for your reference
Context: {}

<|user|>
---
Here is the question you need to answer.

Question: {}
<|assistant|>
"""

router = APIRouter()



@router.post("/courses/{course_id}/study_guides/create/")
async def create_study_guide(course_id: int, query: str):
    #find top k=5 vectors
    query_embedding = generate_embedding(query)
    
    results = await prisma.fetch_raw(
      '''
      SELECT id, file, embedding
      FROM "Resource"
      ORDER BY embedding <=> $1::vector
      LIMIT 5
      ''',
      query_embedding
    )
    # Step 3: Format results for prompt
    formatted_results = "\n".join([f"ID: {row['id']}, File: {row['file']}" for row in results])

    # Step 4: Generate completion
    prompt = prompt.format(formatted_results, query)
    
    response = openai.Completion.create(
        model="o1",
        prompt=prompt,
    )

    # Step 5: Store new StudyGuide row
    return await prisma.study_guide.create(
        data={"course_id": course_id, "content": response.choices[0].text.strip()}
    )


async def extract_text_from_pdf(pdf_url: str) -> str:
  try:
    async with httpx.AsyncClient() as client:
      response = await client.get(pdf_url)
      response.raise_for_status()
      pdf_bytes = response.content

    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

    extracted_text = ""
    for page_num in range(pdf_document.page_count):
      page = pdf_document.load_page(page_num)
      extracted_text += page.get_text()

    return extracted_text

  except httpx.HTTPStatusError as http_err:
    raise HTTPException(status_code=http_err.response.status_code, detail=str(http_err))
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
