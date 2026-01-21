from dotenv import load_dotenv
import os 
load_dotenv()  
openai_key = os.getenv("OPENAI_API_KEY")

from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small",
    openai_api_key=openai_key
)