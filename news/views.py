from django.shortcuts import render, redirect
from author.forms import NewsForm, NewsImageFormSet
# Create your views here.
def home(request):
    return render(request, 'news/index.html')

def create_news(request):
    if request.method == 'POST':
        form = NewsForm(request.POST)
        formset = NewsImageFormSet(request.POST, request.FILES, instance=form.instance)
        
        if form.is_valid() and formset.is_valid():
            news = form.save()
            formset.instance = news
            formset.save()
            return redirect('news:news_feed')
    else:
        form = NewsForm()
        formset = NewsImageFormSet()
    
    return render(request, 'news/create_news.html', {
        'form': form,
        'formset': formset
    })

def news_details(request):
    return render(request, 'news/news_details.html')