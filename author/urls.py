from django.urls import path
from . import views

app_name = 'author'

urlpatterns = [
    path('dashboard', views.author_dashboard, name="author_dashboard"),
    path('content/<str:content_type>', views.author_content, name="author_content"),
    path('analytics', views.author_analytics, name="author_analytics"),
    path('community', views.author_community, name="author_community"),
    path('copyright', views.author_copyright, name="author_copyright"),
    path('earn', views.author_earn, name="author_earn"),
    path('content-details/<str:content_type>/<str:slug>', views.content_details, name="content_details"),
    path('content-analytics/<str:content_type>/<str:slug>', views.content_analytics, name="content_analytics"),
    path('content-comments/<str:content_type>/<str:slug>', views.content_comments, name="content_comments"),
    path('book-translate/<str:slug>', views.content_translate, name="content_translate"),
    path('book-audio/<str:slug>', views.content_audio, name="content_audio"),
    path('content-copyright/<str:content_type>/<str:slug>', views.content_copyright, name="content_copyright"),
    path('write-book', views.write_book, name="write_book"),
    path('create-news', views.create_news, name="create_news"),
    path('get-translation/<int:book_id>/<int:translation_id>', views.get_translation, name='get_translation'),
    path('change-visibility/<int:book_id>/<str:status>', views.change_visibility, name="change_visibilty"),
    path('delete-book/<int:book_id>', views.delete_book, name="delete_book"),
    path('update-session-key/', views.update_session_key, name='update_session_key'),

]