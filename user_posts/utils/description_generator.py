import requests
from decouple import config


def generate_description(media_url):
    '''Function to generate description'''
    try:
        # Sets URL for Description generator
        url = config('RAPID_GENERATOR_URL')

        # Validates params for description generation
        params = {
            "imageUrl":media_url,
            "useEmojis":"false",
            "useHashtags":"false",
            "limit":"1"
        }

        # Assigns key and host config in headers before calling the service
        headers = {
            "X-RapidAPI-Key": config('RAPID_GENERATOR_KEY'),
            "X-RapidAPI-Host": config('RAPID_GENERATOR_HOST')
        }

        # Calls the Description generator service
        response = requests.get(url, headers=headers, params=params)

        # Organizes obtained response
        response = response.json()

        # Stores generated description from response -> captions; 
        # if not received, defaults to ""
        generated_description = response['captions'][0] if response.get('captions') else ''
        
        # Returns description to the calling function
        return generated_description
    except Exception as e:
        print(f'An exception occurred in generate_description: {str(e)}')
        return ''