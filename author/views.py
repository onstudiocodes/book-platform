from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from main.models import Book, User, Comment, ObjView, Booktranslation, News, TravelStory, TravelImage, NewsImage
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
from main.forms import TravelStoryForm

# Create your views here.
@login_required(login_url='accounts:login')
def author_dashboard(request):
    followers_in_28 = get_last_n_days_data(UserFollow, user=request.user, n=28)
    total_books = Book.objects.filter(author=request.user).count()
    total_views = ObjView.objects.filter(book__author=request.user).count()
    
    context = {
        'followers_in_28': followers_in_28,
        'total_books': total_books,
        'total_views': total_views
    }
    return render(request, 'author/admin_dashboard.html', context)

@login_required(login_url='accounts:login')
def author_content(request, content_type):
    if content_type == 'books':
        items = Book.objects.filter(author=request.user)
    elif content_type == 'news':
        items = News.objects.filter(author=request.user)
    elif content_type == 'tour':
        items = TravelStory.objects.filter(author=request.user)

    rows_per_page = request.session.get('rows_per_page')
    if not rows_per_page:
        request.session['rows_per_page'] = 10
        rows_per_page = 10
    
    paginator = Paginator(items, rows_per_page)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    context = {
        'content': page_obj,
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
    entries = get_last_n_days_data(ObjView, days, user=request.user, formatted=True)
    follower_entries = get_last_n_days_data(UserFollow, days, user=request.user, formatted=True)

    start_date = (timezone.now() - datetime.timedelta(days=days)).date()
    end_date = timezone.now()
    views = ObjView.objects.filter(book__author=request.user, created_at__gte=start_date)

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
    followers = request.user.followers_users.all()
    context = {
        'comments': comments,
        'followers': followers
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
def content_details(request, content_type, slug):
    if content_type == 'books':
        obj = Book.objects.get(slug=slug)
        content_type = "books"
    elif content_type == "news":
        obj = News.objects.get(slug=slug)
        content_type = "news"
    elif content_type == "tour":
        obj = TravelStory.objects.get(slug=slug)
        content_type = "tour"
    
    if request.method == "POST":
        if content_type == "tour":
            # Redirect to separate update view for tours
            return redirect('author:update_travel_story', slug=slug)
        elif content_type == "news":
            # Redirect to separate update view for news
            return redirect('author:update_news', slug=slug)
        elif content_type == "books":
            # Redirect to separate update view for books
            return redirect('author:update_book', slug=slug)

    # Initialize forms
    if content_type == "books":
        form = BookUploadForm(instance=obj)
    elif content_type == "news":
        form = NewsForm(instance=obj)
    elif content_type == "tour":
        form = TravelStoryForm(instance=obj)

    context = {
        'obj': obj,
        'form': form,
        'content_type': content_type
    }
    return render(request, 'author/content_details.html', context)

@login_required(login_url='accounts:login')
def update_book(request, slug):
    """
    Separate view for handling book updates
    """
    try:
        book = Book.objects.get(slug=slug, author=request.user)
    except Book.DoesNotExist:
        messages.error(request, 'Book not found or you do not have permission to edit it.')
        return redirect('author:author_content', content_type='books')
    
    if request.method == "POST":
        form = BookUploadForm(request.POST, request.FILES, instance=book)
        
        if form.is_valid():
            # Save the form data
            obj = form.save(commit=False)
            obj.author = request.user
            
            # Handle thumbnail upload
            if 'thumbnail' in request.FILES:
                obj.thumbnail = request.FILES['thumbnail']
            
            obj.save()
            messages.success(request, 'Book updated successfully!')
            
            # Redirect back to the details page
            return redirect('author:content_details', content_type='books', slug=obj.slug)
        
        else:
            # Form has errors
            messages.error(request, 'Please correct the errors below.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    # If GET request or form errors, redirect back to details page
    return redirect('author:content_details', content_type='books', slug=book.slug)

@login_required(login_url='accounts:login')
def update_news(request, slug):
    """
    Separate view for handling news updates
    """
    try:
        news = News.objects.get(slug=slug, author=request.user)
    except News.DoesNotExist:
        messages.error(request, 'News article not found or you do not have permission to edit it.')
        return redirect('author:author_content', content_type='news')
    
    if request.method == "POST":
        form = NewsForm(request.POST, request.FILES, instance=news)
        
        if form.is_valid():
            # Save the form data
            obj = form.save(commit=False)
            obj.author = request.user
            
            # Handle description manually since it's not in the form
            if 'description' in request.POST:
                obj.description = request.POST['description']
            
            # Handle publish/draft logic
            if 'publish' in request.POST:
                obj.publish = True
                messages.success(request, 'News article published successfully!')
            elif 'draft' in request.POST:
                obj.publish = False
                messages.success(request, 'News article saved as draft!')
            else:
                messages.success(request, 'News article updated successfully!')
            
            obj.save()
            
            # Handle multiple image uploads
            if 'news_images' in request.FILES:
                uploaded_images = request.FILES.getlist('news_images')
                for image in uploaded_images:
                    NewsImage.objects.create(news=obj, image=image)
                messages.info(request, f'{len(uploaded_images)} new images added to your article.')
            
            # Redirect back to the details page
            return redirect('author:content_details', content_type='news', slug=obj.slug)
        
        else:
            # Form has errors
            messages.error(request, 'Please correct the errors below.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    # If GET request or form errors, redirect back to details page
    return redirect('author:content_details', content_type='news', slug=news.slug)

@login_required(login_url='accounts:login')
def update_travel_story(request, slug):
    """
    Separate view for handling travel story updates
    """
    try:
        travel_story = TravelStory.objects.get(slug=slug, author=request.user)
    except TravelStory.DoesNotExist:
        messages.error(request, 'Travel story not found or you do not have permission to edit it.')
        return redirect('author:author_content', content_type='tour')
    
    if request.method == "POST":
        form = TravelStoryForm(request.POST, request.FILES, instance=travel_story)
        
        if form.is_valid():
            # Save the form data
            obj = form.save(commit=False)
            obj.author = request.user
            
            # Handle thumbnail upload
            if 'thumbnail' in request.FILES:
                obj.thumbnail = request.FILES['thumbnail']
            
            # Handle publish/draft logic
            if 'publish' in request.POST:
                obj.published = True
                messages.success(request, 'Travel story published successfully!')
            elif 'draft' in request.POST:
                obj.published = False
                messages.success(request, 'Travel story saved as draft!')
            else:
                messages.success(request, 'Travel story updated successfully!')
            
            obj.save()
            
            # Handle multiple image uploads
            if 'images' in request.FILES:
                uploaded_images = request.FILES.getlist('images')
                for image in uploaded_images:
                    TravelImage.objects.create(travel_story=obj, image=image)
                messages.info(request, f'{len(uploaded_images)} new images added to your story.')
            
            # Redirect back to the details page
            return redirect('author:content_details', content_type='tour', slug=obj.slug)
        
        else:
            # Form has errors
            messages.error(request, 'Please correct the errors below.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    # If GET request or form errors, redirect back to details page
    return redirect('author:content_details', content_type='tour', slug=travel_story.slug)

def tour_details(request, slug):
    return render(request, 'author/content_details.html')


@login_required(login_url='accounts:login')
def content_analytics(request, content_type, slug):
    if content_type == "books":
        obj = Book.objects.get(slug=slug)
    elif content_type == "news":
        obj = News.objects.get(slug=slug)
    elif content_type == "tour":
        obj = TravelStory.objects.get(slug=slug)
    days = request.GET.get('days', 90)
        
    days = int(days)
    if content_type == "books":
        views = get_last_n_days_data(ObjView, days, book=obj)
        entries = get_last_n_days_data(ObjView, days, user=request.user, book=obj, formatted=True)
        follower_entries = get_last_n_days_data(UserFollow, days, user=request.user, formatted=True, book=obj)
    elif content_type == "news":
        views = get_last_n_days_data(ObjView, days, news=obj)
        entries = get_last_n_days_data(ObjView, days, user=request.user, news=obj, formatted=True)
        follower_entries = get_last_n_days_data(UserFollow, days, user=request.user, formatted=True)
    elif content_type == "tour":
        views = get_last_n_days_data(ObjView, days, travel_story=obj)
        entries = get_last_n_days_data(ObjView, days, user=request.user, travel_story=obj, formatted=True)
        follower_entries = get_last_n_days_data(UserFollow, days, user=request.user, formatted=True)

    start_date = (timezone.now() - datetime.timedelta(days=days)).date()
    end_date = timezone.now()
    labels = [item['date'] for item in entries]
    data = [item['count'] for item in entries]
    follower_entries_labels = [item['date'] for item in follower_entries]
    follower_entries_data = [item['count'] for item in follower_entries]

    if content_type == "books":
        followers = get_last_n_days_data(UserFollow, days, user=request.user, book=obj).count()
    elif content_type == "news":
        followers = get_last_n_days_data(UserFollow, days, user=request.user).count()
    elif content_type == "tour":
        followers = get_last_n_days_data(UserFollow, days, user=request.user).count()

    context = {
        'views': views,
        'entries': entries,
        'followers': followers,
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'start_date': start_date,
        'end_date': end_date,
        'days': days,
        'obj': obj,
        'follower_entries_labels': json.dumps(follower_entries_labels),
        'follower_entries_data': json.dumps(follower_entries_data),
        'content_type': content_type
    }
    
    return render(request, 'author/content_analytics.html', context)

@login_required(login_url='accounts:login')
def content_comments(request, content_type, slug):
    if content_type=="books":
        obj = Book.objects.get(slug=slug)
    elif content_type=="news":
        obj = News.objects.get(slug=slug)
    elif content_type=="tour":
        obj = TravelStory.objects.get(slug=slug)
    context = {
        'obj': obj,
        'content_type': content_type
    }
    return render(request, 'author/content_comments.html', context)

@login_required(login_url='accounts:login')
def content_copyright(request, content_type, slug):
    if content_type=="books":
        obj = Book.objects.get(slug=slug)
    elif content_type=="news":
        obj = News.objects.get(slug=slug)
    elif content_type=="tour":
        obj = TravelStory.objects.get(slug=slug)
    context = {
        'obj': obj,
        'content_type': content_type
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
        'obj': book,
        'form': form,
        'content_type': 'books'
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
        'obj': book,
        'form': form,
        'content_type': 'books'
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
def create_travel_story(request):
    """
    View for creating new travel stories
    """
    if request.method == 'POST':
        form = TravelStoryForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Save the form data
            travel_story = form.save(commit=False)
            travel_story.author = request.user
            
            # Handle publish/draft logic
            if 'publish' in request.POST:
                travel_story.published = True
                messages.success(request, 'Travel story published successfully!')
            else:
                travel_story.published = False
                messages.success(request, 'Travel story saved as draft!')
            
            travel_story.save()
            
            # Handle multiple image uploads
            if 'images' in request.FILES:
                uploaded_images = request.FILES.getlist('images')
                for image in uploaded_images:
                    TravelImage.objects.create(travel_story=travel_story, image=image)
                messages.info(request, f'{len(uploaded_images)} images added to your story.')
            
            # Redirect to the details page of the new story
            return redirect('author:content_details', content_type='tour', slug=travel_story.slug)
        
        else:
            # Form has errors
            messages.error(request, 'Please correct the errors below.')
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    
    else:
        form = TravelStoryForm()
    
    context = {
        'form': form,
        'is_create': True
    }
    return render(request, 'author/create_travel_story.html', context)

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

@login_required(login_url='accounts:login')
def change_news_visibility(request, news_id, publish_status):
    """
    Change the publication status of a news article
    """
    try:
        news = News.objects.get(id=news_id)
        if news.author == request.user:
            news.publish = publish_status.lower() == 'true'
            news.save()
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'failed', 'message': 'Permission denied'})
    except News.DoesNotExist:
        return JsonResponse({'status': 'failed', 'message': 'News not found'})

def delete_book(request, book_id):
    book = Book.objects.get(id=book_id)
    if book.author == request.user:
        book.delete()
        messages.success(request, 'Book deleted')
        return redirect('author:author_content')
    messages.error(request, 'Book not deleted')
    return redirect('author:author_content')

@login_required(login_url='accounts:login')
def delete_news_image(request, image_id):
    """
    Delete a news image if the user owns the news article
    """
    if request.method == 'POST':
        try:
            image = NewsImage.objects.get(id=image_id)
            # Check if the current user owns the news article
            if image.news.author == request.user:
                image.delete()
                return JsonResponse({'success': True, 'message': 'Image deleted successfully'})
            else:
                return JsonResponse({'success': False, 'message': 'Permission denied'})
        except NewsImage.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Image not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})

@login_required(login_url='accounts:login')
def delete_travel_image(request, image_id):
    """
    Delete a travel image if the user owns the travel story
    """
    if request.method == 'POST':
        try:
            image = TravelImage.objects.get(id=image_id)
            # Check if the current user owns the travel story
            if image.travel_story.author == request.user:
                image.delete()
                return JsonResponse({'success': True, 'message': 'Image deleted successfully'})
            else:
                return JsonResponse({'success': False, 'message': 'Permission denied'})
        except TravelImage.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Image not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'})
