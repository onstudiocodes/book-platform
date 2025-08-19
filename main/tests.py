from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from django.db import IntegrityError
from unittest.mock import patch, Mock
import json
import tempfile
from PIL import Image
import io

from .models import (
    Book, Category, News, NewsCategory, NewsImage, TravelStory, TravelCategory, 
    TravelImage, Comment, Rating, Collection, ReadingList, Notification, 
    Report, Tag, History, AudioBook, Booktranslation, ObjView, ReadingTime
)
from accounts.models import UserProfile, UserFollow
from .forms import TravelStoryForm
from .views import index, book_view, CommentView
from .utils import log_book_view, create_notification


class CategoryModelTest(TestCase):
    """Test Category model"""
    
    def setUp(self):
        self.category = Category.objects.create(name="Fiction")
    
    def test_category_creation(self):
        self.assertEqual(self.category.name, "Fiction")
        self.assertEqual(str(self.category), "Fiction")
        self.assertTrue(self.category.slug)
    
    def test_category_slug_generation(self):
        category = Category.objects.create(name="Science Fiction")
        self.assertEqual(category.slug, "science-fiction")


class BookModelTest(TestCase):
    """Test Book model and manager"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.category = Category.objects.create(name="Fiction")
        self.book = Book.objects.create(
            title="Test Book",
            description="A test book",
            content="Test content",
            author=self.user,
            category=self.category
        )
    
    def test_book_creation(self):
        self.assertEqual(self.book.title, "Test Book")
        self.assertEqual(self.book.author, self.user)
        self.assertEqual(self.book.category, self.category)
        self.assertEqual(str(self.book), "Test Book")
        self.assertTrue(self.book.slug)
    
    def test_book_slug_generation(self):
        book = Book.objects.create(
            title="Another Test Book",
            description="Another test",
            content="Content",
            author=self.user
        )
        self.assertEqual(book.slug, "another-test-book")
    
    def test_likes_count(self):
        user2 = User.objects.create_user('user2', 'user2@test.com', 'pass')
        self.book.likes.add(self.user, user2)
        self.assertEqual(self.book.likes_count(), 2)
    
    def test_dislikes_count(self):
        user2 = User.objects.create_user('user2', 'user2@test.com', 'pass')
        self.book.dislikes.add(self.user, user2)
        self.assertEqual(self.book.dislikes_count(), 2)
    
    def test_reading_time(self):
        ReadingTime.objects.create(
            user=self.user,
            book=self.book,
            total_time=3600  # 1 hour
        )
        self.assertEqual(self.book.reading_time(), "1.00")
    
    def test_get_absolute_url(self):
        expected_url = reverse('main:book_view', args=[self.book.slug])
        self.assertEqual(self.book.get_absolute_url(), expected_url)
    
    def test_public_book_manager(self):
        # Test public books are returned
        public_books = Book.public_objects.all()
        self.assertIn(self.book, public_books)
        
        # Test private books are excluded
        private_book = Book.objects.create(
            title="Private Book",
            description="Private",
            content="Private content",
            author=self.user,
            status="Private"
        )
        public_books = Book.public_objects.all()
        self.assertNotIn(private_book, public_books)
        self.assertIn(self.book, public_books)


class NewsModelTest(TestCase):
    """Test News model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='newsuser',
            email='news@test.com',
            password='pass123'
        )
        self.news_category = NewsCategory.objects.create(name="Technology")
        self.news = News.objects.create(
            title="Tech News",
            description="Latest tech news",
            content="Tech content",
            author=self.user,
            category=self.news_category
        )
    
    def test_news_creation(self):
        self.assertEqual(self.news.title, "Tech News")
        self.assertEqual(self.news.author, self.user)
        self.assertEqual(str(self.news), "Tech News")
        self.assertTrue(self.news.slug)
    
    def test_news_likes_count(self):
        user2 = User.objects.create_user('user2', 'user2@test.com', 'pass')
        self.news.likes.add(self.user, user2)
        self.assertEqual(self.news.likes_count(), 2)
    
    # def test_news_thumbnail(self):
    #     # Create a test image
    #     image_data = io.BytesIO()
    #     img = Image.new('RGB', (100, 100), color='red')
    #     img.save(image_data, format='JPEG')
    #     image_data.seek(0)
    #     
    #     test_image = SimpleUploadedFile(
    #         "test.jpg",
    #         image_data.getvalue(),
    #         content_type="image/jpeg"
    #     )
    #     
    #     news_image = NewsImage.objects.create(
    #         news=self.news,
    #         image=test_image
    #     )
    #     
    #     self.assertEqual(self.news.thumbnail(), news_image.image)


class TravelStoryModelTest(TestCase):
    """Test TravelStory model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='traveler',
            email='travel@test.com',
            password='pass123'
        )
        self.travel_category = TravelCategory.objects.create(name="Adventure")
        self.travel_story = TravelStory.objects.create(
            title="Mountain Adventure",
            story="Great mountain trip",
            author=self.user,
            category=self.travel_category,
            location="Himalayas"
        )
    
    def test_travel_story_creation(self):
        self.assertEqual(self.travel_story.title, "Mountain Adventure")
        self.assertEqual(self.travel_story.author, self.user)
        self.assertEqual(self.travel_story.location, "Himalayas")
        self.assertTrue(self.travel_story.slug)
    
    # def test_travel_story_get_absolute_url(self):
    #     expected_url = reverse('travel:tour_details', args=[self.travel_story.slug])
    #     self.assertEqual(self.travel_story.get_absolute_url(), expected_url)


class CommentModelTest(TestCase):
    """Test Comment model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='commenter',
            email='comment@test.com',
            password='pass123'
        )
        self.book = Book.objects.create(
            title="Commented Book",
            description="Book with comments",
            content="Content",
            author=self.user
        )
        self.comment = Comment.objects.create(
            user=self.user,
            book=self.book,
            content="Great book!"
        )
    
    # def test_comment_creation(self):
    #     self.assertEqual(self.comment.user, self.user)
    #     self.assertEqual(self.comment.book, self.book)
    #     self.assertEqual(self.comment.content, "Great book!")
    #     self.assertEqual(str(self.comment), f"{self.user.username} - Great book!")
    
    def test_comment_with_parent(self):
        reply = Comment.objects.create(
            user=self.user,
            book=self.book,
            content="Reply to comment",
            parent=self.comment
        )
        self.assertEqual(reply.parent, self.comment)


class ViewsTest(TestCase):
    """Test main views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=self.user, full_name="Test User")
        
        # Create a separate author for the book
        self.author = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='authorpass123'
        )
        UserProfile.objects.create(user=self.author, full_name="Test Author")
        
        self.category = Category.objects.create(name="Fiction")
        self.book = Book.objects.create(
            title="Test Book",
            description="A test book",
            content="Test content for the book",
            author=self.author,  # Use separate author
            category=self.category
        )
    
    def test_index_view(self):
        response = self.client.get(reverse('main:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Book")
        self.assertIn('books', response.context)
    
    def test_trending_view(self):
        response = self.client.get(reverse('main:trending'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page'], "Trending")
    
    def test_recent_view(self):
        response = self.client.get(reverse('main:recent'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page'], "Recent")
    
    def test_popular_view(self):
        response = self.client.get(reverse('main:popular'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['page'], "Popular")
    
    def test_book_view(self):
        response = self.client.get(reverse('main:book_view', args=[self.book.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book.title)
        self.assertIn('book', response.context)
    
    def test_book_view_with_authenticated_user(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('main:book_view', args=[self.book.slug]))
        self.assertEqual(response.status_code, 200)
        
        # Check if view was logged
        self.assertTrue(ObjView.objects.filter(book=self.book, user=self.user).exists())
    
    def test_profile_view(self):
        response = self.client.get(reverse('main:profile', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
    
    def test_search_results(self):
        response = self.client.get(reverse('main:search'), {'q': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book.title)
    
    def test_collections_view_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('main:collections'))
        self.assertEqual(response.status_code, 200)
    
    def test_collections_view_unauthenticated(self):
        response = self.client.get(reverse('main:collections'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_toggle_like_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('main:toggle_like'), {
            'book_id': self.book.id,
            'op': 'like'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('status', data)


class CommentViewTest(TestCase):
    """Test CommentView class"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=self.user, full_name="Test User")
        
        self.book = Book.objects.create(
            title="Test Book",
            description="A test book",
            content="Test content",
            author=self.user
        )
    
    def test_comment_submission(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('main:submit_comment'), {
            'comment': 'Great book!',
            'book_id': self.book.id
        })
        self.assertEqual(response.status_code, 200)
        
        # Check comment was created
        self.assertTrue(Comment.objects.filter(
            book=self.book,
            user=self.user,
            content='Great book!'
        ).exists())
    
    def test_empty_comment_submission(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('main:submit_comment'), {
            'comment': '',
            'book_id': self.book.id
        })
        self.assertEqual(response.status_code, 400)


class UtilsTest(TestCase):
    """Test utility functions"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.book = Book.objects.create(
            title="Test Book",
            description="A test book",
            content="Test content",
            author=self.user
        )
    
    # def test_log_book_view(self):
    #     log_book_view(self.user, self.book)
    #     
    #     # Check if view was logged
    #     self.assertTrue(ObjView.objects.filter(
    #         user=self.user,
    #         book=self.book
    #     ).exists())
    
    # def test_create_notification(self):
    #     create_notification(self.user, "Test notification")
    #     
    #     # Check if notification was created
    #     self.assertTrue(Notification.objects.filter(
    #         user=self.user,
    #         message="Test notification"
    #     ).exists())


class FormsTest(TestCase):
    """Test forms"""
    
    def setUp(self):
        self.travel_category = TravelCategory.objects.create(name="Adventure")
    
    # def test_travel_story_form_valid_data(self):
    #     form_data = {
    #         'title': 'Test Travel Story',
    #         'story': 'This is a test travel story',
    #         'category': self.travel_category.id,
    #         'location': 'Test Location',
    #         'duration': '1-3 days',
    #         'season': 'Summer',
    #         'budget_level': 'Budget',
    #         'tags': 'adventure, test'
    #     }
    #     form = TravelStoryForm(data=form_data)
    #     self.assertTrue(form.is_valid())
    
    def test_travel_story_form_invalid_data(self):
        form_data = {
            'title': '',  # Required field left empty
            'story': 'This is a test travel story',
        }
        form = TravelStoryForm(data=form_data)
        self.assertFalse(form.is_valid())


class ModelMethodsTest(TestCase):
    """Test custom model methods"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.book = Book.objects.create(
            title="Test Book",
            description="A test book",
            content="Test content",
            author=self.user
        )
    
    def test_reading_time_get_hours(self):
        reading_time = ReadingTime.objects.create(
            user=self.user,
            book=self.book,
            total_time=7200  # 2 hours
        )
        self.assertEqual(reading_time.get_hours(), "2.00")
    
    def test_collection_str_method(self):
        collection = Collection.objects.create(
            user=self.user,
            name="My Favorites"
        )
        self.assertEqual(str(collection), "My Favorites")
    
    # def test_notification_str_method(self):
    #     notification = Notification.objects.create(
    #         user=self.user,
    #         message="Test notification"
    #     )
    #     self.assertEqual(str(notification), "Test notification")


class DatabaseIntegrityTest(TestCase):
    """Test database constraints and integrity"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_unique_book_slug(self):
        Book.objects.create(
            title="Test Book",
            description="First book",
            content="Content",
            author=self.user
        )
        
        # Second book with same title should get different slug
        book2 = Book.objects.create(
            title="Test Book",
            description="Second book",
            content="Content",
            author=self.user
        )
        self.assertNotEqual(book2.slug, "test-book")
    
    def test_user_follow_unique_constraint(self):
        user2 = User.objects.create_user('user2', 'user2@test.com', 'pass')
        
        # Create first follow relationship
        UserFollow.objects.create(follower=self.user, following=user2)
        
        # Attempting to create duplicate should raise IntegrityError
        with self.assertRaises(IntegrityError):
            UserFollow.objects.create(follower=self.user, following=user2)


class PaginationTest(TestCase):
    """Test pagination functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create multiple books for pagination testing
        for i in range(15):
            Book.objects.create(
                title=f"Test Book {i}",
                description=f"Description {i}",
                content=f"Content {i}",
                author=self.user
            )
    
    # def test_index_pagination(self):
    #     response = self.client.get(reverse('main:index'))
    #     self.assertEqual(response.status_code, 200)
    #     
    #     # Should have pagination context
    #     self.assertIn('books', response.context)
    #     books = response.context['books']
    #     self.assertEqual(len(books), 10)  # Default page size
    
    # def test_load_more_data(self):
    #     response = self.client.get(reverse('main:load_more_data'), {
    #         'page': 2,
    #         'sort': 'recommended'
    #     })
    #     self.assertEqual(response.status_code, 200)
    #     data = json.loads(response.content)
    #     self.assertIn('html', data)
    #     self.assertIn('has_more', data)


class AuthenticationTest(TestCase):
    """Test authentication requirements"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_collections_requires_login(self):
        response = self.client.get(reverse('main:collections'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login', response.url)
    
    def test_history_requires_login(self):
        response = self.client.get(reverse('main:history'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login', response.url)
    
    def test_continue_reading_requires_login(self):
        response = self.client.get(reverse('main:continue_reading'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login', response.url)
