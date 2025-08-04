from django.urls import path
from . import views 

app_name = 'news'

urlpatterns = [
    path('', views.home, name="news_feed"),
    path('create', views.create_news, name="create_news"),
    path('details/<str:slug>', views.news_details, name="news_details"),
    path('news-api/', views.NewsListCreateView.as_view(), name='news-list-create'),
    path('comments/', views.CommentListCreateAPIView.as_view(), name='comments' )

]
