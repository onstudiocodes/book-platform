from django.shortcuts import render, redirect, get_object_or_404
from author.forms import NewsForm, NewsImageFormSet
from main.models import News, NewsImage, NewsCategory, Comment
from django.db.models import Count
from .serializers import NewsImageSerializer, NewsSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework import permissions, generics, serializers
from main.utils import log_news_view
from main.serializers import CommentSerializer

# Create your views here.
def home(request):
    categories = NewsCategory.objects.annotate(news_count=Count('news')).order_by('-news_count')
    recent_news = News.objects.order_by('-published_date')[:2]
    trending_news = News.objects.annotate(views_count=Count('news_views')).order_by('-views_count')[:3]
    context = {
        'categories': categories,
        'recent_news': recent_news,
        "trending_news": trending_news
    }
    return render(request, 'news/index.html', context)

def create_news(request):
    if request.method == 'POST':
        form = NewsForm(request.POST)
        formset = NewsImageFormSet(request.POST, request.FILES, instance=form.instance)

        if form.is_valid() and formset.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news.save()
            
            # Save the formset with the news instance
            instances = formset.save(commit=False)
            for instance in instances:
                instance.news = news
                instance.save()
            
            # Save many-to-many data if needed
            form.save_m2m()
            
            return redirect('news:news_feed')
    else:
        form = NewsForm()
        formset = NewsImageFormSet(queryset=NewsImage.objects.none())  # Empty queryset for new instances
    
    return render(request, 'news/create_news.html', {
        'form': form,
        'formset': formset
    })
def news_details(request, slug):
    news = News.objects.select_related('author__userprofile').prefetch_related(
        'images'
    ).get(slug=slug)
    user = request.user if request.user.is_authenticated else None
    if user:
        log_news_view(news=news, user=user)
    else:
        log_news_view(news=news)
    news.views = news.news_views.count()
    news.save()
    comments = Comment.objects.filter(news=news).select_related(
        'news__author__userprofile'
        ).annotate(
            likes_count=Count('likes'),
            dislikes_count=Count('dislikes')
        ).order_by('-created_at')

    related_news = News.objects.order_by('?').prefetch_related(
            'images'
        ).exclude(id__in=[news.id])[:3]

    return render(request, 'news/news_details.html', {'news': news, 'comments': comments, 'related_news': related_news})

class NewsPagination(PageNumberPagination):
    page_size = 2  # Number of items per page
    page_size_query_param = 'page_size'
    max_page_size = 100

class NewsListCreateView(generics.ListCreateAPIView):
    queryset = News.objects.select_related('author', 'author__userprofile').prefetch_related('likes', 'dislikes', 'images', 'comments').order_by('-published_date')
    serializer_class = NewsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = NewsPagination 
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def get_queryset(self):
        queryset = News.objects.select_related(
            'author', 'author__userprofile'
        ).prefetch_related(
            'likes', 'dislikes', 'images', 'comments'
        ).annotate(
            likes_count=Count('likes', distinct=True),
            dislikes_count=Count('dislikes', distinct=True),
            comments_count=Count('comments', distinct=True),
            views_count=Count('news_views', distinct=True)
        ).order_by('-published_date')

        exclude_id = self.request.query_params.get('exclude')
        if exclude_id and exclude_id.isdigit():
            queryset = queryset.exclude(id=int(exclude_id))

        category_name = self.request.query_params.get('category')
        if category_name:
            queryset = queryset.filter(category__name=category_name)

        return queryset

# Retrieve, update, or delete a specific news item
class NewsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class CommentListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all().order_by('created_at')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        content_type = self.request.query_params.get('type')
        object_id = self.request.query_params.get('id')
        queryset = Comment.objects.all().order_by('created_at')
        if content_type and object_id and object_id.isdigit():
            if content_type == 'news':
                queryset = queryset.filter(news_id=object_id)
            elif content_type == 'book':
                queryset = queryset.filter(book_id=object_id)
            elif content_type == 'travelstory':
                queryset = queryset.filter(travelstory_id=object_id)
        return queryset

    def perform_create(self, serializer):
        content_type = self.request.data.get('type')
        object_id = self.request.data.get('id')

        if content_type == 'news':
            serializer.save(user=self.request.user, news_id=object_id)
        elif content_type == 'book':
            serializer.save(user=self.request.user, book_id=object_id)
        elif content_type == 'travelstory':
            serializer.save(user=self.request.user, travel_story_id=object_id)
        else:
            raise serializers.ValidationError({"error": "Invalid content type"})


    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        response.data = {'success': True, 'comment': response.data}
        return response