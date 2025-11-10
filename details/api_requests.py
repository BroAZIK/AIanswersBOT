import requests
from settings import *
import os
from openai import OpenAI
from google import genai
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.messages import HumanMessage, SystemMessage
load_dotenv()

endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1"

llm = ChatGoogleGenerativeAI(model='gemini-2.5-flash', temperature=0, google_api_key=os.getenv("OPENAI_API_KEY"))


client = OpenAI(
    base_url=endpoint,
    api_key=token,
)




def OCRres(file_url):
    ocr_url = "https://api.ocr.space/parse/image"

    r = requests.get(file_url)
    with open("temp.jpg", "wb") as f:
        f.write(r.content)

    with open("temp.jpg", "rb") as f:
        response = requests.post(
            ocr_url,
            data={"apikey": api_key, "language": "eng"},
            files={"file": f}
        )

    result = response.json()

    os.remove("temp.jpg")

    if "ParsedResults" in result:
        return result["ParsedResults"][0].get("ParsedText", "").strip()
    else:
        return f"❌ OCR xato: {result.get('ErrorMessage')}"
    
    




# def ai_request(text):
#     response = client.chat.completions.create(
#         messages=[
#         {
#             "role": "system",
#             "content": gpt_tasks
#         },
#         {
#             "role": "user",
#             "content": text,
#         }
#         ],
#         temperature=1.0,
#         top_p=1.0,
#         model=model
#     )

#     # print(response.choices[0].message.content)
#     return response.choices[0].message.content

def ai_request(text):
    response = llm.invoke([
    SystemMessage(content=gpt_tasks),
    HumanMessage(content=text)
    ])
    # print(response.content)
    return response.content
