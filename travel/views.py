from django.shortcuts import render, redirect
from rest_framework import generics, pagination
from .serializers import TravelStorySerializer
from main.models import TravelStory, TravelImage, TravelCategory
from main.forms import TravelStoryForm
from django.contrib import messages
# Create your views here.


def tour_wall(request):
    featured = TravelStory.objects.exclude(published=False).prefetch_related('images').order_by('?')[0]
    return render(request, 'main/tour_wall.html', {'featured': featured})

def tour_details(request, slug):
    story = TravelStory.objects.get(slug=slug)
    return render(request, 'main/tour_details.html', {'story': story})

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
