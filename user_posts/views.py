from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from user_posts.fetch_all_posts import extract_post_info


@api_view(["POST"])
def fetch_instagram_posts(request):
    request_data = request.data
    username = request_data.get('username')
    extract_post_info(username)

    return Response('Request submitted successfully')