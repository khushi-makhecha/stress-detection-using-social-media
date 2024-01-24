"""
URL configuration for stress_detection project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from user_posts.views import fetch_instagram_posts, check_ocr, fetch_and_process_user_data

urlpatterns = [
    path('admin/', admin.site.urls),
    path('fetch_posts/', fetch_instagram_posts),
    path('perform_ocr/', check_ocr),
    path('process_user_data/', fetch_and_process_user_data)
]
