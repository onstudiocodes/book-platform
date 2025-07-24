from django.urls import path
from . import views 

app_name = 'news'

urlpatterns = [
    path('', views.home, name="news_feed"),
    path('create', views.create_news, name="create_news"),
    path('details', views.news_details, name="news_details")
]
