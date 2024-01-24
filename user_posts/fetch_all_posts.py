import requests
from decouple import config
from user_posts.utils.mongo_connection import MongoDBConnection
from user_posts.utils.perform_ocr import perform_image_ocr
from user_posts.utils.description_generator import generate_description

def get_user_posts(username):
    try:
        params = {
            'start_cursor': 0,
            'depth': 10,
            'token': config('ENSEMBLE_TOKEN'),
            'chunk_size': 33,
            'alternative_method': True,
            'username': username
        }
        
        posts_url = config('ENSEMBLE_BASE_URL') + config('ENSEMBLE_ENDPOINT_2')
        response = requests.get(url=posts_url, params=params)
        if response.status_code == 472:
            print(f'{username} has a private account.')
            return
        response = response.json().get('data').get('posts')

        return response
    except Exception as e:
        print(f'An exception occurred in get_user_posts: {str(e)}')
        return []


def extract_post_info(username):
    try:
        user_posts = get_user_posts(username)
        if not user_posts:
            print(f'{username} has no public posts')
            return
        
        all_posts_processed = []
        for post in user_posts:
            thumbnail_url = None
            instagram_post_url = f'https://www.instagram.com/p/{post.get("code")}/'
            caption = post['caption']['text'] if post.get('caption') and post['caption'].get('text') else ""
            
            post.update({"username": username})
            post.update({'instagram_post_url': instagram_post_url})
            save_data_to_mongo(post, config('MONGO_RAW_COLLECTION_NAME'))

            if post.get('image_versions2') and post.get('carousel_media'):
                for carousel in post.get('carousel_media'):
                    if carousel.get('video_versions'):
                        media_url = carousel.get('video_versions')[0].get('url')
                        media_type = 'video'
                        thumbnail_url = post.get('image_versions2').get('candidates')[0].get('url')
                    else:
                        media_url = (
                            carousel.get('image_versions2').get('candidates')[0].get('url')
                        )
                        media_type = 'image'
            else:
                if post.get('video_versions'):
                    media_url = post.get('video_versions')[0].get('url')
                    media_type = 'video'
                    thumbnail_url = post.get('image_versions2').get('candidates')[0].get('url')
                else:
                    media_url = (post.get('image_versions2').get('candidates')[0].get('url'))
                    media_type = 'image'

            processed_data = {
                'instagram_post_url': instagram_post_url,
                'caption': caption,
                'thumbnail_url': thumbnail_url,
                'media_url': media_url,
                'media_type': media_type,
                'username': username
            }

            save_data_to_mongo(processed_data, config('MONGO_COLLECTION_NAME'))
            all_posts_processed.append(processed_data)
        
        return all_posts_processed
    except Exception as e:
        print(f'An exception occurred in extract_post_info: {str(e)}')
        return {}
    
def save_data_to_mongo(data, collection_name):
    try:
        with MongoDBConnection(
            config('MONGO_CONNECTION_STRING'),
            config('MONGO_DB_NAME')
        ) as mongo_connection:
            db = mongo_connection.get_collection(collection_name)
            db.update_many(
                {'username': data.get('username'),
                 'instagram_post_url': data.get('instagram_post_url')
                },
                {'$set': data},
                upsert=True
            )

            return True
    except Exception as e:
        print(f'An exception occurred in save_data_to_mongo: {str(e)}')
        return False
            

def process_data(username):
    try:
        processed_data = extract_post_info(username)
        if not processed_data:
            print('Data not processed')
            return False
        
        for data in processed_data:
            image_input = data['media_url'] if data['media_type'] == 'image' else data['thumbnail_url']
            ocr_result = perform_image_ocr(image_input)
            data['ocr_result'] = ocr_result
            if not data.get('caption'):
                description_result = generate_description(image_input)
                data['text_data'] = description_result
            else:
                data['text_data'] = data.get('caption')
            save_data_to_mongo(data, config('MONGO_COLLECTION_NAME'))
            
            return True
    except Exception as e:
        print(f'An exception occurred in process_data: {str(e)}')
        return False