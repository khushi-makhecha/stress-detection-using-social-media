import requests
from decouple import config
from user_posts.mongo_connection import MongoDBConnection

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
            # "user_id": 18428658,
            # "oldest_timestamp": 1666262030,
        
        posts_url = config('ENSEMBLE_BASE_URL') + config('ENSEMBLE_ENDPOINT_2')
        response = requests.get(url=posts_url, params=params)
        if response.status_code == 472:
            print(f'{username} has a private account.')
            return
        response = response.json().get('data').get('posts')

        return response
    except Exception as e:
        print(f'An exception occurred in get_user_posts: {str(e)}')


def extract_post_info(username):
    try:
        user_posts = get_user_posts(username)
        if not user_posts:
            print(f'{username} has no public posts')
            return

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
        
        return True
    except Exception as e:
        print(f'An exception occurred in extract_post_info: {str(e)}')
        return False
    
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
            