from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from user_posts.fetch_all_posts import extract_post_info, process_data
from user_posts.utils import perform_ocr


@api_view(["POST"])
def fetch_instagram_posts(request):
    request_data = request.data
    username = request_data.get('username')
    extract_post_info(username)

    return Response('Request submitted successfully')


@api_view(["GET"])
def check_ocr(request):
    request_data = request.data
    image_url = request_data.get('image_url')
    perform_ocr.perform_image_ocr(image_url)

    return Response('OCR performed')


@api_view(["POST"])
def fetch_and_process_user_data(request):
    request_data = request.data
    username = request_data.get('username')
    process_data(username)

    return Response('Request submitted successfully')