from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework import generics, pagination, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from .serializers import TravelStorySerializer
from main.models import TravelStory, TravelImage, TravelCategory, Comment
from main.forms import TravelStoryForm
from main.utils import create_notification
from django.contrib import messages
from django.db.models import Count
# Create your views here.


def tour_wall(request):
    featured = TravelStory.objects.exclude(published=False).prefetch_related('images').order_by('?')[0]
    return render(request, 'main/tour_wall.html', {'featured': featured})

def tour_details(request, slug):
    story = TravelStory.objects.get(slug=slug)
    comments = Comment.objects.filter(travel_story=story).select_related(
        'travel_story__author__userprofile'
        ).prefetch_related(
            'travel_story__images'
        ).order_by('-created_at')
    return render(request, 'main/tour_details.html', {'story': story, 'comments': comments})

def search(request):
    q = request.GET.get('q', None)
    if q:
        results = TravelStory.objects.filter(title__icontains=q)| TravelStory.objects.filter(story__icontains=q)
        results = results.distinct()
        return render(request, 'main/tour_wall.html', {'results': results, 'query': q})
    else:
        return redirect(request.META.get('HTTP_REFFERER'))

class TravelStoryPagination(pagination.PageNumberPagination):
    page_size = 6
    page_query_param = 'page'  # This should be 'page' for page number
    page_size_query_param = 'page_size'  # This allows client to set page size
    max_page_size = 100

class TravelStoryListAPIView(generics.ListAPIView):
    serializer_class = TravelStorySerializer
    pagination_class = TravelStoryPagination

    def get_queryset(self):
        queryset = TravelStory.objects.all().order_by('-created_at')
        q = self.request.GET.get('q', None)
        if q:
            queryset = queryset.filter(title__icontains=q)| queryset.filter(story__icontains=q)
            queryset = queryset.distinct()
        return queryset
    
@login_required
def add_travel_story(request):
    if request.method == 'POST':
        form = TravelStoryForm(request.POST, request.FILES)
        if form.is_valid():
            travel_story = form.save(commit=False)
            travel_story.author = request.user
            travel_story.save()
            
            
            # Handle multiple image uploads
            images = request.FILES.getlist('images')
            if len(images) < 3:
                messages.error(request, 'At least 3 photos are required')
                return render(request, 'main/add_travel_story.html', {'form': form})
                
            for image in images:
                TravelImage.objects.create(travel_story=travel_story, image=image)
            
            if 'publish' in request.POST:
                travel_story.published = True
            travel_story.save()

            messages.success(request, 'Travel story saved successfully!')
            source_template = request.POST.get('source_template')
            if 'content_details' in source_template:
                template, slug = source_template.split(')(')
                return redirect('author:content_details', content_type='tour', slug=slug)
            return redirect('travel:tour_details', slug=travel_story.slug)
    else:
        form = TravelStoryForm()
    
    return render(request, 'main/add_travel_story.html', {'form': form})


# Like/Unlike a travel story
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def like_travel_story(request, pk):
    travel_story = get_object_or_404(TravelStory, id=pk)
    user = request.user
    context = {}
    
    if user in travel_story.likes.all():
        travel_story.likes.remove(user)
        context['status'] = "success"
        context['likes'] = travel_story.likes.count()
        context['action'] = "unlike"
        context['message'] = "Unliked"
    else:
        travel_story.likes.add(user)
        # Remove from dislikes if present
        if user in travel_story.dislikes.all():
            travel_story.dislikes.remove(user)
        context['status'] = "success"
        context['likes'] = travel_story.likes.count()
        context['dislikes'] = travel_story.dislikes.count()
        context['action'] = "like"
        context['message'] = "Liked"
        # Create notification if not the author
        if user != travel_story.author:
            create_notification(travel_story.author, f"{user.userprofile.full_name} liked your travel story {travel_story.title}")
    
    return Response(context)


# Dislike/Undislike a travel story
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def dislike_travel_story(request, pk):
    travel_story = get_object_or_404(TravelStory, id=pk)
    user = request.user
    context = {}
    
    if user in travel_story.dislikes.all():
        travel_story.dislikes.remove(user)
        context['status'] = "success"
        context['dislikes'] = travel_story.dislikes.count()
        context['action'] = "undislike"
        context['message'] = "Undisliked"
    else:
        travel_story.dislikes.add(user)
        # Remove from likes if present
        if user in travel_story.likes.all():
            travel_story.likes.remove(user)
        context['status'] = "success"
        context['likes'] = travel_story.likes.count()
        context['dislikes'] = travel_story.dislikes.count()
        context['action'] = "dislike"
        context['message'] = "Disliked"
    
    return Response(context)


# Toggle like/dislike for travel story (similar to the book toggle_like function)
@login_required(login_url='accounts:login')
def toggle_travel_story_like(request):
    story_id = request.POST.get('story_id')
    op = request.POST.get("op")
    target_story = get_object_or_404(TravelStory, id=story_id)
    user = request.user
    
    if op == "like":
        if user in target_story.dislikes.all():
            target_story.dislikes.remove(user)
        if user in target_story.likes.all():
            target_story.likes.remove(user)
        else:
            target_story.likes.add(user)
            if user != target_story.author: 
                create_notification(target_story.author, f"{user.userprofile.full_name} liked your travel story {target_story.title}")
        return JsonResponse({'status': 'success', 'likes': target_story.likes.count(), 'dislikes': target_story.dislikes.count()})
    elif op == "dislike":
        if user in target_story.likes.all():
            target_story.likes.remove(user)
        if user in target_story.dislikes.all():
            target_story.dislikes.remove(user)
        else:
            target_story.dislikes.add(user)
        return JsonResponse({'status': 'success', 'likes': target_story.likes.count(), 'dislikes': target_story.dislikes.count()})
    else:
        return JsonResponse({'error': 'Invalid request'})
