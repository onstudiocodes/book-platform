from django.shortcuts import render, redirect, get_object_or_404
from author.forms import NewsForm, NewsImageFormSet
from main.models import News, NewsImage, NewsCategory
# Create your views here.
def home(request):
    return render(request, 'news/index.html')

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