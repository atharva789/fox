import weaviate
from weaviate.classes.config import Configure, Property, DataType, Multi2VecField
import os
from dotenv import load_dotenv

load_dotenv()

weaviate_client = weaviate.Client(
    url = "http://localhost:8080",  # with v4, you can keep “url” if you prefer
    additional_headers={"X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")}
)

material_class = {
    "class": "Material",
    "vectorizer": "text2vec-openai",
    "moduleConfig": {
       "text2vec-openai": {
         "model": "text-embedding-ada-002",   # or your chosen model
         "modelVersion": "002",
         "type": "text"
       }
    },
    "properties": [
        {
            "name": "moduleName",
            "dataType": ["text"]
        },
        {
            "name": "fileName",
            "dataType": ["text"]
        },
        {
            "name": "text",
            "dataType": ["text"]
        }
    ]
}

def init_weaviate_schema():
    existing_classes = weaviate_client.schema.get()["classes"]
    existing_class_names = [c["class"] for c in existing_classes]

    if "Material" not in existing_class_names:
        weaviate_client.schema.create_class(material_class)

# Create the class
weaviate_client.schema.create_class(schema)
print("Class 'Material' created!")

weaviate_client.close()