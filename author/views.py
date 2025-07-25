from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from main.models import Book, User, Comment, BookView, Booktranslation, News
from django.contrib import messages
from .forms import BookUploadForm, NewsForm, NewsImageFormSet, AudioForm, TranslationForm
import base64
from django.core.files.base import ContentFile
from main.utils import get_last_n_days_data, year_specific_data
import json, datetime
from django.utils import timezone
from django.core.paginator import Paginator
from accounts.models import UserFollow
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
@login_required(login_url='accounts:login')
def author_dashboard(request):
    followers_in_28 = get_last_n_days_data(UserFollow, user=request.user, n=28)
    context = {
        'followers_in_28': followers_in_28
    }
    return render(request, 'author/admin_dashboard.html', context)

@login_required(login_url='accounts:login')
def author_content(request, content_type):
    if content_type == 'books':
        items = Book.objects.filter(author=request.user)
    elif content_type == 'news':
        items = News.objects.filter(author=request.user)
    rows_per_page = request.session.get('rows_per_page')
    if not rows_per_page:
        request.session['rows_per_page'] = 10
        rows_per_page = 10
    
    paginator = Paginator(items, rows_per_page)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    context = {
        'books': page_obj,
        'content_type': content_type
    }
    return render(request, 'author/admin_content.html', context)

@csrf_exempt
def update_session_key(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        new_value = data.get('key')
        request.session['rows_per_page'] = int(new_value)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'})

@login_required(login_url='accounts:login',)
def author_analytics(request):
    days = request.GET.get('days', 28)
        
    days = int(days)
    entries = get_last_n_days_data(BookView, days, user=request.user, formatted=True)
    follower_entries = get_last_n_days_data(UserFollow, days, user=request.user, formatted=True)

    start_date = (timezone.now() - datetime.timedelta(days=days)).date()
    end_date = timezone.now()
    views = BookView.objects.filter(book__author=request.user, created_at__gte=start_date)

    labels = [item['date'] for item in entries]
    data = [item['count'] for item in entries]
    follower_entries_labels = [item['date'] for item in follower_entries]
    follower_entries_data = [item['count'] for item in follower_entries]


    context = {
        'views': views,
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'start_date': start_date,
        'end_date': end_date,
        'days': days,
        'follower_entries_labels': json.dumps(follower_entries_labels),
        'follower_entries_data': json.dumps(follower_entries_data)
    }
    return render(request, 'author/admin_analytics.html', context)

@login_required(login_url='accounts:login')
def author_community(request):
    comments = Comment.objects.filter(book__author=request.user)
    context = {
        'comments': comments
    }
    return render(request, 'author/admin_community.html', context)

@login_required(login_url='accounts:login')
def author_earn(request):
    follower_progress = request.user.followers_users.count() / 1000 * 100
    reader_progress = request.user.userprofile.get_total_views() / 100000 * 100
    context = {
        'follower_progress': follower_progress,
        'reader_progress': reader_progress
    }
    return render(request, 'author/admin_earn.html', context)

@login_required(login_url='accounts:login')
def author_copyright(request):
    return render(request, 'author/admin_copyright.html')

@login_required(login_url='accounts:login')
def content_details(request, slug):
    if 'book-details' in request.META.get('PATH_INFO'):
        book = Book.objects.get(slug=slug)  # Fetch the existing book

    else:
        book = News.objects.get(slug=slug)
    if request.method == "POST":
        form = BookUploadForm(request.POST, request.FILES, instance=book)  # Bind the form with the book instance
        print(request.FILES)
        if form.is_valid():
            book = form.save(commit=False)  # Get the book instance with updated data
            book.author = request.user  # Ensure the author is set to the current user
            # Check if a new thumbnail is provided
            if 'thumbnail' in request.FILES:
                book.thumbnail = request.FILES['thumbnail']
            book.save()  # Save the updated book object to the database
            return redirect(request.META.get('HTTP_REFERER', '/fallback-url/'))  # Redirect after saving

    else:
        form = BookUploadForm(instance=book)  # Prefill the form with the existing book data

    context = {
        'book': book,
        'form': form
    }
    return render(request, 'author/content_details.html', context)


@login_required(login_url='accounts:login')
def content_analytics(request, slug):
    book = Book.objects.get(slug=slug)
    days = request.GET.get('days', 90)
        
    days = int(days)
    views = get_last_n_days_data(BookView, days, book=book)
    entries = get_last_n_days_data(BookView, days, user=request.user, book=book, formatted=True)
    follower_entries = get_last_n_days_data(UserFollow, days, user=request.user, formatted=True, book=book)

    start_date = (timezone.now() - datetime.timedelta(days=days)).date()
    end_date = timezone.now()
    labels = [item['date'] for item in entries]
    data = [item['count'] for item in entries]
    follower_entries_labels = [item['date'] for item in follower_entries]
    follower_entries_data = [item['count'] for item in follower_entries]

    followers = get_last_n_days_data(UserFollow, days, user=request.user, book=book).count()

    context = {
        'views': views,
        'followers': followers,
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'start_date': start_date,
        'end_date': end_date,
        'days': days,
        'book': book,
        'follower_entries_labels': json.dumps(follower_entries_labels),
        'follower_entries_data': json.dumps(follower_entries_data)
    }
    
    return render(request, 'author/content_analytics.html', context)

@login_required(login_url='accounts:login')
def content_comments(request, slug):
    book = Book.objects.get(slug=slug)
    context = {
        'book': book
    }
    return render(request, 'author/content_comments.html', context)

@login_required(login_url='accounts:login')
def content_copyright(request, slug):
    book = Book.objects.get(slug=slug)
    context = {
        'book': book
    }
    return render(request, 'author/content_copyright.html', context)

@login_required(login_url='accounts:login')
def content_translate(request, slug):
    book = Book.objects.get(slug=slug)
    if request.method == "POST":
        form = TranslationForm(request.POST)
        if form.is_valid():
            translation = form.save(commit=False)
            translation.book = book
            translation.save()
            messages.success(request, 'Translation added to book')
        else:
            print(form.errors)
            messages.error(request, 'Invalid response')
    form = TranslationForm()
    context = {
        'book': book,
        'form': form
    }
    return render(request, 'author/content_translate.html', context)


def get_translation(request, book_id, translation_id):
    if translation_id == 0:
        book = Book.objects.get(id=book_id)
        context = {
            'translated_title': book.title,
            'translated_description': book.description,
            'translated_content': book.content
        }
    else:
        translation = Booktranslation.objects.get(id=translation_id)
        context = {
            'translated_title': translation.translated_title,
            'translated_description': translation.translated_description,
            'translated_content': translation.translated_content
        }
    return JsonResponse(context)


@login_required(login_url='accounts:login')
def content_audio(request, slug):
    book = Book.objects.get(slug=slug)
    if request.method == "POST":
        form = AudioForm(request.POST, request.FILES)
        if form.is_valid():
            audio = form.save(commit=False)
            audio.book = book
            audio.save()
            messages.success(request, "Audio added to book.")
        else:
            messages.error(request, 'Invalid files')
    form = AudioForm()
    context = {
        'book': book,
        'form': form
    }
    return render(request, 'author/content_audio.html', context)

@login_required(login_url='accounts:login')
def write_book(request):
    if request.method == "POST":
        form = BookUploadForm(request.POST, request.FILES)

        # Handle cropped image
        cropped_image_data = request.POST.get("cropped_thumbnail")
        if cropped_image_data:
            format, imgstr = cropped_image_data.split(';base64,')  
            ext = format.split('/')[-1]  

            # Convert Base64 to an image file
            image_data = ContentFile(base64.b64decode(imgstr), name=f"cropped_thumbnail.{ext}")
            form.instance.thumbnail = image_data  # Set it to the form

        if form.is_valid():
            form.instance.author = request.user
            form.save()
            messages.success(request, "Book published")
            return redirect("main:index")
    form = BookUploadForm(request.POST or None, request.FILES or None)
    return render(request, "author/write_book.html", {"form": form})

@login_required(login_url='accounts:login')
def create_news(request):
    if request.method == 'POST':
        form = NewsForm(request.POST)
        formset = NewsImageFormSet(request.POST, request.FILES)

        if form.is_valid() and formset.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news.save()
            images = formset.save(commit=False)
            for image in images:
                image.news = news
                image.save()
            messages.success(request, "News added")
            return redirect('main:index')
        else:
            messages.error(request, "News creation faild")
            return redirect('main:index')
    else:
        form = NewsForm()
        formset = NewsImageFormSet()
        return render(request, 'author/create_news.html', {'form': form, 'formset': formset})
    
@login_required(login_url='accounts:login')
def change_visibility(request, book_id, status):
    book = Book.objects.get(id=book_id)
    if book.author == request.user:
        book.status = status
        book.save()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'failed'})

def delete_book(request, book_id):
    book = Book.objects.get(id=book_id)
    if book.author == request.user:
        book.delete()
        messages.success(request, 'Book deleted')
        return redirect('author:author_content')
    messages.error(request, 'Book not deleted')
    return redirect('author:author_content')
