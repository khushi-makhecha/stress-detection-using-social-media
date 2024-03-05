from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from user_posts.fetch_all_posts import extract_post_info, process_data
from user_posts.utils import perform_ocr, description_generator
from user_posts.model_tester import predict_stress_level


@api_view(["POST"])
def fetch_instagram_posts_view(request):
    request_data = request.data
    username = request_data.get('username')
    extract_post_info(username)

    return Response('Request submitted successfully', status=200)


@api_view(["GET"])
def check_ocr_view(request):
    request_data = request.data
    image_url = request_data.get('image_url')
    perform_ocr.perform_image_ocr(image_url)

    return Response('OCR performed', status=200)


@api_view(["POST"])
def fetch_and_process_user_data_view(request):
    request_data = request.data
    username = request_data.get('username')
    response, response_list = process_data(username)
    if response:
        return Response(f'Stress detected in the user posts.\n{response_list}', status=200)
    return Response('Stress not found in the user posts', status=200)


@api_view(["GET"])
def description_generator_view(request):
    request_data = request.data
    image_url = request_data.get('image_url')
    description_generator.generate_description(image_url)

    return Response('Description generated', status=200)


@api_view(["POST"])
def test_model(request):
    custom_input = request.data.get("text")
    result = predict_stress_level(custom_input)
    
    return Response(f'Stress Result: {result}', status=200)
