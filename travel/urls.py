from django.urls import path
from . import views

app_name = "travel"

urlpatterns = [
    path('', views.TravelStoryListAPIView.as_view(), name="travel"),
    path('tour_wall', views.tour_wall, name="tour_wall"),
    path('tour_details/<str:slug>', views.tour_details, name="tour_details"),
    path('add_travel_story', views.add_travel_story, name='add_travel_story'),
]
