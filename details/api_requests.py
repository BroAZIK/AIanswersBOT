import requests
from settings import *
import os
from openai import OpenAI

ocr_key = "K83430220988957"
endpoint = "https://models.github.ai/inference"
model = "openai/gpt-4.1"
token = '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'
client = OpenAI(
    base_url=endpoint,
    api_key=token,
)




def OCRres(file_url):
    api_key = ocr_key
    ocr_url = "https://api.ocr.space/parse/image"

    print("Rasmni yuklab olish")
    r = requests.get(file_url)
    with open("temp.jpg", "wb") as f:
        f.write(r.content)

    print("Apiga rasmni jo'natish")
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
    
    




def ai_request(text):
    response = client.chat.completions.create(
        messages=[
        {
            "role": "system",
            "content": gpt_tasks
        },
        {
            "role": "user",
            "content": text,
        }
        ],
        temperature=1.0,
        top_p=1.0,
        model=model
    )

    # print(response.choices[0].message.content)
    return response.choices[0].message.content