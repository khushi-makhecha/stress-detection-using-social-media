import requests
from decouple import config


def generate_description(media_url):
    try:
        url = config('RAPID_GENERATOR_URL')

        params = {
            "imageUrl":media_url,
            "useEmojis":"false",
            "useHashtags":"false",
            "limit":"1"
        }

        headers = {
            "X-RapidAPI-Key": config('RAPID_GENERATOR_KEY'),
            "X-RapidAPI-Host": config('RAPID_GENERATOR_HOST')
        }

        response = requests.get(url, headers=headers, params=params)
        response = response.json()
        generated_description = response['captions'][0] if response.get('captions') else ''
        
        return generated_description
    except Exception as e:
        print(f'An exception occurred in generate_description: {str(e)}')
        return ''