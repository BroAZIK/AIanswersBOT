import requests
from dotenv import load_dotenv, dotenv_values
import os
load_dotenv()

ocr_key = os.getenv('ocr_token')

def OCRres(file_url):
    api_key = ocr_key
    ocr_url = "https://api.ocr.space/parse/image"

    response = requests.post(
        ocr_url,
        data={
            "apikey": api_key,
            "url": file_url,  # Telegramdagi rasm URL manzili
            "language": "eng"
        }
    )

    result = response.json()
    print(result["ParsedResults"][0]["ParsedText"])
    
    return result["ParsedResults"][0]["ParsedText"]