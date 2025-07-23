from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'news/index.html')

def create_news(request):
    return render(request, 'news/create_news.html')

def news_details(request):
    return render(request, 'news/news_details.html')