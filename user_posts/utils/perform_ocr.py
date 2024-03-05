import requests
from decouple import config
import json


def perform_image_ocr(image_url):
    '''Function that returns OCR results of the given image URL.'''
    try:
        # Sets URL of OCR service
        url = config('OCR_SPACE_BASE_URL')

        # Validates params for the service
        params = {
            'apikey': config('OCR_SPACE_API_KEY'),
            'url': image_url
        }

        # Trigger OCR service
        response = requests.request("GET", url, params=params)

        # Formats obtained response for better accessibility
        formatted_response = json.loads(response.text)
        ocr_result = []
        # Excludes extra information and stores parsed results
        parsed_results = formatted_response.get('ParsedResults')

        # Iterates over each and every parsed_result
        for result in parsed_results:
            parsed_text = result.get('ParsedText')
            # Checks if OCR text is obtained
            if parsed_text:
                # Strips new line chars and extra trailing spaces 
                # and stores text in ocr_result
                ocr_result.append(parsed_text.strip())

        # Returns OCR result to the calling function
        return ocr_result
    except Exception as e:
        print(f'An exception occurred in perform_image_ocr: {str(e)}')
        return []
