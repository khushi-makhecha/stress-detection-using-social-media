import requests
from decouple import config
from user_posts.utils.mongo_connection import MongoDBConnection
from user_posts.utils.perform_ocr import perform_image_ocr
from user_posts.utils.description_generator import generate_description
from user_posts.model_tester import predict_stress_level

def get_user_posts(username):
    '''Function that calls the API service for fetching Instagram posts of public accounts.'''
    try:
        # Required parameters for the API call
        params = {
            'start_cursor': 0,
            'depth': 10,
            'token': config('ENSEMBLE_TOKEN'),
            'chunk_size': 33,
            'alternative_method': True,
            'username': username
        }
        
        # Setting the URL with appropriate endpoint for fetching posts
        posts_url = config('ENSEMBLE_BASE_URL') + config('ENSEMBLE_ENDPOINT_2')

        # Triggering the API
        response = requests.get(url=posts_url, params=params)

        # Handling the condition of private account
        if response.status_code == 472:
            print(f'{username} has a private account.')
            return
        
        # Modifying API response for efficient handling
        response = response.json().get('data').get('posts')

        # Returning all user posts
        return response
    except Exception as e:
        print(f'An exception occurred in get_user_posts: {str(e)}')
        return []


def extract_post_info(username):
    '''Function to fetch user posts and process the collected data for better efficiency.'''
    try:
        # Calls the function to collect user posts.
        user_posts = get_user_posts(username)

        # Returns a message if no data is obtained.
        if not user_posts:
            print(f'{username} has no public posts')
            return
        
        all_posts_processed = []

        # Iterates over each and every collected post
        for post in user_posts:
            thumbnail_url = None

            # Link to actual instagram post
            instagram_post_url = f'https://www.instagram.com/p/{post.get("code")}/'
            # Caption of post; sets as "" if caption is not found
            caption = post['caption']['text'] if post.get('caption') and post['caption'].get('text') else ""
            post.update({"username": username})
            post.update({'instagram_post_url': instagram_post_url})

            # Stores raw data to MongoDB
            save_data_to_mongo(post, config('MONGO_RAW_COLLECTION_NAME'))

            # Checks if the post is of carousel type
            if post.get('image_versions2') and post.get('carousel_media'):
                for carousel in post.get('carousel_media'):
                    # If carousel contains video
                    if carousel.get('video_versions'):
                        # For each and every carousel post, sets media_url as video URL, 
                        # media_type as "video" and thumbnail_url as the image in first frame 
                        media_url = carousel.get('video_versions')[0].get('url')
                        media_type = 'video'
                        thumbnail_url = post.get('image_versions2').get('candidates')[0].get('url')
                    
                    # If carousel contains image
                    else:
                        # Sets media_url as image URL and media_type as "image"; thumbnail_url N/A
                        media_url = (
                            carousel.get('image_versions2').get('candidates')[0].get('url')
                        )
                        media_type = 'image'
            else:
                # Checks if the post is of video type
                if post.get('video_versions'):
                    # Sets media_url as video URL, media_type as "video" 
                    # and thumbnail_url as the image in first frame 
                    media_url = post.get('video_versions')[0].get('url')
                    media_type = 'video'
                    thumbnail_url = post.get('image_versions2').get('candidates')[0].get('url')
                else:
                    # Checks if the post is of image type; sets media_url as image URL 
                    # and media_type as "image"; thumbnail_url N/A
                    media_url = (post.get('image_versions2').get('candidates')[0].get('url'))
                    media_type = 'image'

            # Accumulates all necessary fields in the form of dictionary
            processed_data = {
                'instagram_post_url': instagram_post_url,
                'caption': caption,
                'thumbnail_url': thumbnail_url,
                'media_url': media_url,
                'media_type': media_type,
                'username': username
            }

            # Stores processed data in MongoDB
            save_data_to_mongo(processed_data, config('MONGO_COLLECTION_NAME'))
            all_posts_processed.append(processed_data)
        
        # Returns processed data from all the posts of given user
        return all_posts_processed
    except Exception as e:
        print(f'An exception occurred in extract_post_info: {str(e)}')
        return {}
    
def save_data_to_mongo(data, collection_name):
    '''Function to save data in MongoDB'''
    try:
        # Takes connection string and database name from config
        with MongoDBConnection(
            config('MONGO_CONNECTION_STRING'),
            config('MONGO_DB_NAME')
        ) as mongo_connection:
            # Accepts collection name from params
            db = mongo_connection.get_collection(collection_name)

            # Updates objects based on username and post URL
            db.update_many(
                {'username': data.get('username'),
                 'instagram_post_url': data.get('instagram_post_url')
                },
                {'$set': data},
                upsert=True
            )

            # Returns True if the update query is successful; otherwise False
            return True
    except Exception as e:
        print(f'An exception occurred in save_data_to_mongo: {str(e)}')
        return False
    

def fetch_posts_by_username(username, collection_name):
    '''Function to fetch all saved posts by username from MongoDB'''
    try:
        # Takes connection string and database name from config
        with MongoDBConnection(
            config('MONGO_CONNECTION_STRING'),
            config('MONGO_DB_NAME')
        ) as mongo_connection:
            # Accepts collection name from params
            db = mongo_connection.get_collection(collection_name)

            # Finds all documents matching the given username
            results = db.find({'username': username})

            # Converts the results to a list (assuming you want to return a list of dictionaries)
            posts = list(results)

            # Check if posts exist for the user
            if posts:
                return posts
            else:
                print("No posts found for the specified username.")
                return []
    except Exception as e:
        print(f'An exception occurred in fetch_posts_by_username: {str(e)}')
        return []
            

def process_data(username):
    '''Function to update user data with OCR and description generator results '''
    try:
        # Fetches and processes user posts
        # processed_data = extract_post_info(username)
        processed_data = fetch_posts_by_username(username, config('MONGO_COLLECTION_NAME'))

        # Returns message and stops execution if processed data is not obtained
        if not processed_data:
            print('Data not processed')
            return False, []
        
        total_posts_with_stress = {}
        
        # Iterates over each and every post
        for data in processed_data:
            # Sets image input as image URL if post has an image; 
            # uses thumbnail URL if it has video
            image_input = data['media_url'] if data['media_type'] == 'image' else data['thumbnail_url']

            # Performs OCR
            ocr_result = perform_image_ocr(image_input)
            data['ocr_result'] = ocr_result

            # Calls Description generator if post lacks caption
            if not data.get('caption'):
                description_result = generate_description(image_input)
                data['text_data'] = description_result
            else:
                data['text_data'] = data.get('caption')

            # Stores OCR and description results to MongoDB
            save_data_to_mongo(data, config('MONGO_COLLECTION_NAME'))

            # Checks whether the given post displays stress based on text data and OCR result
            is_stressful_post = predict_stress_level(data['text_data'])
            if not is_stressful_post and ocr_result:
                is_stressful_post = predict_stress_level(ocr_result[0])
            if is_stressful_post:
                total_posts_with_stress[data['text_data']] = data['instagram_post_url']

        # Fetches threshold percentage from config to predict if the user has stress
        if len(total_posts_with_stress) / len(processed_data) >= int(config('STRESS_THRESHOLD'))/100:
            return True, total_posts_with_stress
        else:
            return False, {}
    except Exception as e:
        print(f'An exception occurred in process_data: {str(e)}')
        return False, []