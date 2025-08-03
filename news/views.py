from django.shortcuts import render, redirect, get_object_or_404
from author.forms import NewsForm, NewsImageFormSet
from main.models import News, NewsImage, NewsCategory
from django.db.models import Count
from .serializers import NewsImageSerializer, NewsSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework import permissions, generics


# Create your views here.
def home(request):
    categories = NewsCategory.objects.annotate(news_count=Count('news')).order_by('-news_count')
    recent_news = News.objects.order_by('-published_date')[:2]
    context = {
        'categories': categories,
        'recent_news': recent_news
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
    news = get_object_or_404(News, slug=slug)
    return render(request, 'news/news_details.html', {'news': news})

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
        ).order_by('-published_date')

        exclude_id = self.request.query_params.get('exclude')
        if exclude_id and exclude_id.isdigit():
            queryset = queryset.exclude(id=int(exclude_id))
        return queryset


# Retrieve, update, or delete a specific news item
class NewsDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]