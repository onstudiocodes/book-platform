from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Book, Comment, News, History, Collection, ReadingList, Notification
from django.contrib.auth.models import User
from django.http import JsonResponse
from accounts.models import UserProfile, UserFollow
from django.views import View
from .utils import log_book_view, create_notification
from django.utils import timezone, html
from collections import defaultdict
from django.contrib import messages
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import ReadingTime
from django.core.paginator import Paginator
import json
from .forms import TravelStoryForm
from .models import TravelImage, TravelStory, TravelCategory
from django.db.models import Count

def index(request):
    context = {}
    path_info = request.META.get('PATH_INFO')
    items_per_page = 10  # Number of books to load initially

    # Determine the sorting based on the path
    if path_info == "/trending":
        books = Book.public_objects.all().prefetch_related('author__userprofile').order_by('-views')
        context['page'] = "Trending"
    elif path_info == "/recent":
        books = Book.public_objects.all().prefetch_related('author__userprofile').order_by('-published_date')
        context['page'] = "Recent"
    elif path_info == "/popular":
        books = Book.public_objects.all().prefetch_related('author__userprofile').order_by('-views')
        context['page'] = "Popular"
    else:
        books = Book.public_objects.all().prefetch_related('author__userprofile').order_by('?')
        context['page'] = "Recommended"

    # Paginate the initial set of books
    paginator = Paginator(books, items_per_page)
    initial_books = paginator.page(1)
    context['books'] = initial_books

    if request.user.is_authenticated:
        context['following'] = UserFollow.objects.filter(follower=request.user)[:3]

    return render(request, 'main/index.html', context)

def get_news_items():
    return News.objects.order_by('-published_date')  # or however you want

def load_more_data(request):
    page = int(request.GET.get('page', 1))
    items_per_page = 10

    # Match filter with index logic
    path_info = request.META.get('HTTP_REFERER', '')
    if "/trending" in path_info:
        books = Book.public_objects.all().prefetch_related('author__userprofile').order_by('-views')
    elif "/recent" in path_info:
        books = Book.public_objects.all().prefetch_related('author__userprofile').order_by('-published_date')
    elif "/popular" in path_info:
        books = Book.public_objects.all().prefetch_related('author__userprofile').order_by('-views')
    else:
        books = Book.public_objects.all().prefetch_related('author__userprofile').order_by('?')

    paginator = Paginator(books, items_per_page)

    if page > paginator.num_pages:
        return JsonResponse({'data': [], 'has_next': False})

    current_books = paginator.page(page)
    data = []

    

    for idx, book in enumerate(current_books):
        html = render_to_string('components/book_card.html', {'book': book, 'request': request})
        data.append(html)

    

    return JsonResponse({
        'data': data,
        'has_next': page < paginator.num_pages
    })

@csrf_exempt
@login_required
def save_reading_time(request):
    if request.method == "POST":
        data = json.loads(request.body)
        book_id = data.get("book_id")
        reading_time = data.get("reading_time", 0)

        if reading_time > 0:
            book = Book.objects.get(id=book_id)
            reading_record, created = ReadingTime.objects.get_or_create(user=request.user, book=book)

            # Increment total reading time
            reading_record.total_time += reading_time
            reading_record.save()

        return JsonResponse({"message": "Reading time saved!"})

    return JsonResponse({"error": "Invalid request"}, status=400)


from accounts.forms import profileForm
def profile(request, username):
    
    profile = User.objects.get(username=username)
    follower = False
    if request.user.is_authenticated and UserFollow.objects.filter(follower=request.user, following=profile).exists():
        follower = True
    context = {'profile': profile, 'follower': follower}

    books = Book.objects.filter(author__username=username)
    paginator = Paginator(books, 10)
    initial_books = paginator.page(1)
    context['books'] = initial_books

    if request.user.is_authenticated and request.user.username == username:
        
        if request.method == "POST":
            form = profileForm(request.POST, request.FILES, instance=profile.userprofile)
            if form.is_valid():
                form.save()
                return redirect(request.META.get('HTTP_REFERER', '/fallback-url/'))
        form = profileForm(request.POST or None, request.FILES or None, instance=profile.userprofile)
        context['form'] = form
    return render(request, 'main/profile.html', context)


def subscriptions(request):

    return render(request, 'main/subscriptions.html')

@login_required(login_url='accounts:login')
def collections(request):
    if request.method == "POST":
        collection_name = request.POST.get('collection_name')
        collection, created = Collection.objects.get_or_create(
            user=request.user,
            name=collection_name
        )
        if created:
            messages.success(request, 'Collection added')
        else:
            messages.error(request, "Collection alreay exists.")
        return redirect('main:collections')
    return render(request, 'main/collections.html')

def delete_collection(request, collection_id):
    collection = Collection.objects.filter(user=request.user, id=collection_id)
    if collection.exists():
        collection.first().delete()
        messages.success(request, 'Collection deleted.')
    else:
        messages.error(request, 'Collection not found.')
    return redirect('main:collections')

def collection(request, collection_name):
    print("Collection name:", collection_name)
    if collection_name == "Liked":
        liked_books = Book.public_objects.filter(likes=request.user)
        liked_news = News.objects.filter(likes=request.user)
        print(liked_books, liked_news)
        return render(request, 'main/single_collection.html', {
            'liked_books': liked_books,
            'liked_news': liked_news,
            'liked': True
        })
    coll = Collection.objects.filter(name=collection_name, user=request.user)
    if coll.exists():
        return render(request, 'main/single_collection.html', {'collection': coll.first()})
    else:
        messages.error(request, "Collection not found.")
        return redirect(request.META.get('HTTP_REFERER', '/fallback-url/'))

def add_to_collection(request, slug, collection_name):
    book = Book.public_objects.get(slug=slug)
    coll = Collection.objects.filter(user=request.user, name=collection_name)
    if coll.exists():
        obj, created =ReadingList.objects.get_or_create(
            collection=coll.first(),
            book=book
        )
        if created:
            messages.success(request, f"Book add to {coll.first().name}")
        else:
            messages.error(request, "Book already in this collection")
    else:
        messages.error(request, 'Failed adding in collection')
    return redirect(request.META.get('HTTP_REFERER', '/fallback-url/'))

def remove_from_collection(request, slug, collection_name):
    book = Book.public_objects.get(slug=slug)
    coll = Collection.objects.filter(user=request.user, name=collection_name)
    if coll.exists():
        obj = ReadingList.objects.get(collection=coll.first(), book=book)
        if obj:
            obj.delete()
            messages.success(request, f"Book removed from {coll.first().name}")
        else:
            messages.error(request, "Book not in collection")
    else:
        messages.error(request, 'Failed removing book from collection')
    return redirect(request.META.get('HTTP_REFERER', '/fallback-url/'))


def book_view(request, slug):
    book = Book.public_objects.get(slug=slug)
    user = request.user if request.user.is_authenticated else None

    
    book_pdf_url = reverse('main:book_pdf_view', kwargs={'slug': book.slug})

    # Add to history
    if request.user.is_authenticated:
        if request.user != book.author:
            log_book_view(book=book, user=user)

        history, created = History.objects.update_or_create(
            user=request.user,
            book=book,
            defaults={'updated_at': timezone.now()}
        )

    comments = Comment.objects.filter(book=book, parent=None).order_by('-created_at')
    follower = False
    if request.user.is_authenticated and UserFollow.objects.filter(follower=request.user, following=book.author).exists():
        follower = True
    
    suggestions = Book.public_objects.all().order_by('?').exclude(id__in=[book.id])[:20]
    return render(request, 'main/book_view.html', {
        'book': book, 
        'suggestions': suggestions, 
        'follower': follower,
        'comments': comments,
        'book_pdf_url': book_pdf_url
        })

from django.http import HttpResponse
from .utils import generate_book_pdf

def book_pdf_view(request, slug):
    book = Book.public_objects.get(slug=slug)

    width = int(request.GET.get("w", 270))  # in pt, fallback default
    height = int(request.GET.get("h", 480))
    pdf_stream = generate_book_pdf(book, width, height)

    response = HttpResponse(pdf_stream, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{book.slug}.pdf"'
    return response


def search_results(request):
    if request.method == "GET":
        q = request.GET.get('q')
        if q == "":
            return redirect('main:index')
        books = Book.public_objects.filter(title__icontains=q) | Book.public_objects.filter(description__icontains=q) | Book.public_objects.filter(author__userprofile__full_name__icontains=q) | Book.public_objects.filter(category__name__icontains=q)
        books = books.distinct()
        return render(request, 'main/search_result.html', {'q': q, 'books': books})
    return redirect('main:index')

@login_required(login_url='accounts:login')
def history(request):
    histories = History.objects.filter(user=request.user).order_by('-updated_at')

    # Get current date and yesterday's date
    today = timezone.now().date()
    yesterday = today - timezone.timedelta(days=1)

    # Group histories by date
    history_dict = defaultdict(list)

    for history in histories:
        history_date = history.updated_at.date()
        if history_date == today:
            history_dict["Today"].append(history)
        elif history_date == yesterday:
            history_dict["Yesterday"].append(history)
        else:
            history_dict[history_date.strftime("%B %d, %Y")].append(history)

    return render(request, 'main/history.html', {'history_dict': dict(history_dict)})

def clear_notifications(request):
    Notification.objects.filter(user=request.user).delete()
    messages.error(request, 'Notifications cleared.')
    return redirect(request.META.get('HTTP_REFERER', '/fallback-url/'))


def mark_all_as_read(request):
    noti = Notification.objects.filter(user=request.user, is_read=False)
    for item in noti:
        item.is_read = True
        item.save()
    return redirect(request.META.get('HTTP_REFERER', '/fallback-url/'))


@login_required(login_url='accounts:login')
def continue_reading(request):
    histories = History.objects.filter(user=request.user).order_by('-updated_at')
    if histories.exists():
        his = histories.first()
        if his.book:
            return redirect('main:book_view', his.book.slug)
    messages.error(request, html.format_html("You haven't read anything yet."))
    return redirect(request.META.get('HTTP_REFERER', '/fallback-url/'))

@login_required(login_url='accounts:login')
def toggle_follow(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id') 
        target_profile = get_object_or_404(UserProfile, user_id=user_id)
        follower_user = request.user  # The logged-in user
        referer = request.META.get('HTTP_REFERER')
        followed_from_book = False
        if 'book_view' in referer:
            followed_from_book = True
            book_title = referer.split('/')[-1]
            from_book = Book.objects.get(slug=book_title)

        if target_profile.user == follower_user:
            return JsonResponse({'error': 'You cannot follow yourself.'}, status=400)

        # Check if the user is already following
        follow_instance = UserFollow.objects.filter(follower=follower_user, following=target_profile.user).first()

        if follow_instance:
            follow_instance.delete()  # Unfollow
            status = "unfollowed"
        else:
            obj = UserFollow.objects.create(follower=follower_user, following=target_profile.user)  # Follow
            status = "followed"
            if followed_from_book:
                obj.from_book = from_book
            obj.save()
            create_notification(target_profile.user, f"{follower_user.get_full_name()} followed you.")

        followers_count = UserFollow.objects.filter(following=target_profile.user).count()
        return JsonResponse({'status': status, 'followers_count': followers_count, 'target_user': target_profile.full_name})

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required(login_url='accounts:login')
def toggle_like(request):
    book_id = request.POST.get('book_id')
    op = request.POST.get("op")
    target_book = get_object_or_404(Book, id=book_id)
    user = request.user
    if op == "like":
        if user in target_book.dislikes.all():
            target_book.dislikes.remove(user)
        if user in target_book.likes.all():
            target_book.likes.remove(user)
        else:
            target_book.likes.add(user)
            if user != target_book.author: 
                create_notification(target_book.author, f"{user.userprofile.full_name} liked your book {target_book.title}")
        return JsonResponse({'status': 'success', 'likes': target_book.likes.count(), 'dislikes': target_book.dislikes.count()})
    elif op == "dislike":
        if user in target_book.likes.all():
            target_book.likes.remove(user)
        if user in target_book.dislikes.all():
            target_book.dislikes.remove(user)
        else:
            target_book.dislikes.add(user)
        return JsonResponse({'status': 'success', 'likes': target_book.likes.count(), 'dislikes': target_book.dislikes.count()})
    else:
        return JsonResponse({'error': 'Invalid request'})
    


class CommentView(View):
    def post(self, request, *args, **kwargs):
        comment = request.POST.get("comment", "").strip()
        book_id = int(request.POST.get("book_id"))
        parent_id = request.POST.get('parent_id')
        if parent_id:
            parent = Comment.objects.filter(id=parent_id)
        else:
            parent = Comment.objects.none()

        user=request.user
        if not comment:
            return JsonResponse({"error": "Comment cannot be empty"}, status=400)
        target_book = Book.public_objects.get(id=book_id)
        new_comment = Comment.objects.create(user=user, content=comment, book=target_book)
        if parent.exists():
            new_comment.parent = parent.first()
        new_comment.save()
        reply = False
        if new_comment.parent:
            reply = True
            create_notification(new_comment.parent.user, f"{user.userprofile.full_name} replied to your comment.")
        if request.user != target_book.author:
            create_notification(target_book.author, f"{user.userprofile.full_name} commentent on your book.")
        response = {
            "message": "Comment submitted successfully", 
            "comment": comment,
            "comment_count": Comment.objects.filter(book=target_book).count(),
            "username": user.username,
            "profile_img": user.userprofile.profile_picture.url,
            "time": "Just now",
            "comment_id": new_comment.id,
            "reply":reply,
            "parent_id": parent_id,
            "book_id": book_id
            }
        return JsonResponse(response)

def delete_comment(request, comment_id):
    if request.method == "GET":
        target_comment = Comment.objects.get(id=comment_id)
        if target_comment.user != request.user:
            return JsonResponse({'error': "You can't delete others comment."}, status=404)
        target_comment.delete()
        return JsonResponse({
            "success": "Comment deleted.",
            "comment_id": comment_id
        })
    
def news_cast(request):
    highlighted = request.GET.get('highlighted')
    return render(request, 'main/newscast.html', {'highlighted': highlighted})

def news(request, news_id):
    news_obj = News.objects.get(id=news_id)
    suggested_news = News.objects.exclude(id=news_id)
    context = {
        'news': news_obj,
        'suggested_news': suggested_news
    }
    return render(request, 'main/news.html', context)

from django.urls import reverse

def temp_book_view(request):
    book = Book.objects.get(slug="omujk-28fc-9bd0")

    # This will generate something like /book_pdf_view/omujk-28fc-9bd0/
    book_pdf_url = reverse('main:book_pdf_view', kwargs={'slug': book.slug})

    context = {
        'book': book,
        'book_pdf_url': book_pdf_url,
    }
    return render(request, 'temp_book_view.html', context)



from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from .models import News
from .serializers import NewsSerializer
from rest_framework.pagination import PageNumberPagination

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

# Like/Unlike a news item
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def like_news(request, pk):
    news = News.objects.get(id=pk)
    if not request.user.is_authenticated:
        return Response({'status': 'Not authenticated'})
    user = request.user
    context = {}
    
    if user in news.likes.all():
        news.likes.remove(user)
        context['status'] = "success"
        context['likes'] = news.likes.count()
        context['action'] = "unlike"
        context['message'] = "Unliked"
        return Response(context)
    else:
        news.likes.add(user)
        context['status'] = "success"
        context['likes'] = news.likes.count()
        context['action'] = "like"
        context['message'] = "Liked"
        if user != news.author:
            create_notification(news.author, f"{user.userprofile.full_name} liked your news {news.title}")
        return Response(context)

# Dislike/Undislike a news item
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def dislike_news(request, pk):
    news = News.objects.get(id=pk)
    user = request.user
    if user in news.dislikes.all():
        news.dislikes.remove(user)
        return Response({"message": "Undisliked"})
    else:
        news.dislikes.add(user)
        return Response({"message": "Disliked"})


def get_comments(request, news_id):
    news = get_object_or_404(News, id=news_id)
    comments = news.comments.all().order_by('-created_at')
    return JsonResponse({
        'comments': [
            {
                'text': c.content,
                'created_at': c.created_at.strftime("%b %d, %Y %H:%M"),
                'author': {
                    'full_name': c.user.userprofile.full_name,
                    'profile_picture': c.user.userprofile.profile_picture.url
                }
            } for c in comments
        ]
    })

@login_required
def post_comment(request, news_id):
    news = get_object_or_404(News, id=news_id)
    if request.method == 'POST':
        text = request.POST.get('text')
        comment = Comment.objects.create(
            news=news,
            user=request.user,
            content=text
        )
        return JsonResponse({
            'text': comment.content,
            'created_at': comment.created_at.strftime("%b %d, %Y %H:%M"),
            'author': {
                'full_name': request.user.userprofile.full_name,
                'profile_picture': request.user.userprofile.profile_picture.url
            }
        })
    return JsonResponse({'status': 'error'}, status=400)

def tour_wall(request):
    stories = TravelStory.objects.exclude(published=False).prefetch_related('images')
    return render(request, 'main/tour_wall.html', {'stories': stories})

def tour_details(request, slug):
    story = get_object_or_404(TravelStory, slug=slug)
    return render(request, 'main/tour_details.html', {'story': story})

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
            return redirect('main:tour_details', slug=travel_story.slug)
    else:
        form = TravelStoryForm()
    
    return render(request, 'main/add_travel_story.html', {'form': form})
    


