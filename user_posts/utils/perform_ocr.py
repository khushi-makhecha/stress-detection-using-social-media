import requests
from decouple import config
import json


def perform_image_ocr(image_url):
    try:
        url = config('OCR_SPACE_BASE_URL')

        params = {
            'apikey': config('OCR_SPACE_API_KEY'),
            'url': image_url
        }
        response = requests.request("GET", url, params=params)
        formatted_response = json.loads(response.text)
        ocr_result = []
        parsed_results = formatted_response.get('ParsedResults')

        for result in parsed_results:
            parsed_text = result.get('ParsedText')
            if parsed_text:
                ocr_result.append(parsed_text.strip())

        return ocr_result
    except Exception as e:
        print(f'An exception occurred in perform_image_ocr: {str(e)}')
        return []
