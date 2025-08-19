from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.messages import get_messages
from PIL import Image
import io
import json

from .forms import BookUploadForm, NewsForm, NewsImageFormSet, AudioForm, TranslationForm
from .views import (
    author_dashboard, author_content, author_analytics, 
    content_details, content_analytics, write_book, create_news
)
from main.models import (
    Book, Category, News, NewsCategory, NewsImage, 
    AudioBook, Booktranslation, ObjView, Comment
)
from accounts.models import UserProfile, UserFollow


class AuthorFormsTest(TestCase):
    """Test author forms"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='author',
            email='author@test.com',
            password='pass123'
        )
        self.category = Category.objects.create(name="Fiction")
        
        # Create a test image
        image_data = io.BytesIO()
        img = Image.new('RGB', (100, 100), color='red')
        img.save(image_data, format='JPEG')
        image_data.seek(0)
        
        self.test_image = SimpleUploadedFile(
            "test.jpg",
            image_data.getvalue(),
            content_type="image/jpeg"
        )
    
    def test_book_upload_form_valid(self):
        form_data = {
            'title': 'Test Book',
            'description': 'A test book description',
            'content': 'This is the book content',
            'language': 'English',
            'category': self.category.id
        }
        file_data = {
            'thumbnail': self.test_image
        }
        
        form = BookUploadForm(data=form_data, files=file_data)
        self.assertTrue(form.is_valid())
    
    def test_book_upload_form_invalid(self):
        form_data = {
            'title': '',  # Required field
            'description': 'A test book description',
            'content': 'This is the book content'
        }
        
        form = BookUploadForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_news_form_valid(self):
        news_category = NewsCategory.objects.create(name="Technology")
        form_data = {
            'title': 'Test News',
            'category': news_category.id,
            'content': 'This is news content'
        }
        
        form = NewsForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_news_form_invalid(self):
        form_data = {
            'title': '',  # Required field
            'content': 'This is news content'
        }
        
        form = NewsForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    # def test_audio_form_valid(self):
    #     book = Book.objects.create(
    #         title="Test Book",
    #         description="Test",
    #         content="Content",
    #         author=self.user
    #     )
    #     
    #     # Create test audio file
    #     audio_data = b"fake audio data"
    #     audio_file = SimpleUploadedFile(
    #         "test.mp3",
    #         audio_data,
    #         content_type="audio/mpeg"
    #     )
    #     
    #     form_data = {
    #         'book': book.id,
    #         'title': 'Test Audio',
    #         'description': 'Test audio description'
    #     }
    #     file_data = {
    #         'audio_file': audio_file
    #     }
    #     
    #     form = AudioForm(data=form_data, files=file_data)
    #     self.assertTrue(form.is_valid())
    
    # def test_translation_form_valid(self):
    #     book = Book.objects.create(
    #         title="Test Book",
    #         description="Test",
    #         content="Content",
    #         author=self.user
    #     )
    #     
    #     form_data = {
    #         'book': book.id,
    #         'language': 'Spanish',
    #         'title': 'Libro de Prueba',
    #         'content': 'Contenido traducido'
    #     }
    #     
    #     form = TranslationForm(data=form_data)
    #     self.assertTrue(form.is_valid())


class AuthorViewsTest(TestCase):
    """Test author views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='author',
            email='author@test.com',
            password='pass123'
        )
        UserProfile.objects.create(user=self.user, full_name="Author User")
        
        self.category = Category.objects.create(name="Fiction")
        self.book = Book.objects.create(
            title="Test Book",
            description="Test description",
            content="Test content",
            author=self.user,
            category=self.category
        )
        
        self.client.login(username='author', password='pass123')
    
    def test_author_dashboard_authenticated(self):
        response = self.client.get(reverse('author:author_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Dashboard')
    
    def test_author_dashboard_unauthenticated(self):
        self.client.logout()
        response = self.client.get(reverse('author:author_dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login', response.url)
    
    # def test_author_content_books(self):
    #     response = self.client.get(reverse('author:author_content', args=['books']))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, self.book.title)
    
    def test_author_content_news(self):
        news = News.objects.create(
            title="Test News",
            description="Test news",
            content="News content",
            author=self.user
        )
        
        response = self.client.get(reverse('author:author_content', args=['news']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, news.title)
    
    # def test_author_analytics(self):
    #     response = self.client.get(reverse('author:author_analytics'))
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('analytics_data', response.context)
    
    def test_content_details_get_books(self):
        response = self.client.get(reverse('author:content_details', 
                                         args=['books', self.book.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book.title)
        self.assertIn('form', response.context)
    
    # def test_content_details_post_books(self):
    #     # Create test image
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
    #     response = self.client.post(reverse('author:content_details', 
    #                                       args=['books', self.book.slug]), {
    #         'title': 'Updated Book Title',
    #         'description': 'Updated description',
    #         'content': 'Updated content',
    #         'language': 'English',
    #         'category': self.category.id,
    #         'thumbnail': test_image
    #     })
    #     
    #     self.assertEqual(response.status_code, 302)
    #     
    #     # Check if book was updated
    #     updated_book = Book.objects.get(id=self.book.id)
    #     self.assertEqual(updated_book.title, 'Updated Book Title')
    
    def test_content_analytics_books(self):
        # Create some view data
        ObjView.objects.create(book=self.book, user=self.user)
        
        response = self.client.get(reverse('author:content_analytics', 
                                         args=['books', self.book.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('views', response.context)
    
    def test_content_analytics_with_days_filter(self):
        response = self.client.get(reverse('author:content_analytics', 
                                         args=['books', self.book.slug]) + '?days=30')
        self.assertEqual(response.status_code, 200)
    
    def test_write_book_get(self):
        response = self.client.get(reverse('author:write_book'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
    
    def test_write_book_post_valid(self):
        response = self.client.post(reverse('author:write_book'), {
            'title': 'New Book',
            'description': 'New book description',
            'content': 'New book content',
            'language': 'English',
            'category': self.category.id
        })
        
        self.assertEqual(response.status_code, 302)
        
        # Check if book was created
        self.assertTrue(Book.objects.filter(title='New Book', author=self.user).exists())
    
    def test_create_news_get(self):
        response = self.client.get(reverse('author:create_news'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('formset', response.context)
    
    # def test_create_news_post_valid(self):
    #     news_category = NewsCategory.objects.create(name="Technology")
    #     
    #     # Create test image
    #     image_data = io.BytesIO()
    #     img = Image.new('RGB', (100, 100), color='red')
    #     img.save(image_data, format='JPEG')
    #     image_data.seek(0)
    #     
    #     test_image = SimpleUploadedFile(
    #         "news.jpg",
    #         image_data.getvalue(),
    #         content_type="image/jpeg"
    #     )
    #     
    #     response = self.client.post(reverse('author:create_news'), {
    #         'title': 'Test News Article',
    #         'category': news_category.id,
    #         'content': 'This is the news content',
    #         # Formset management form
    #         'newsimage_set-TOTAL_FORMS': '1',
    #         'newsimage_set-INITIAL_FORMS': '0',
    #         'newsimage_set-MIN_NUM_FORMS': '0',
    #         'newsimage_set-MAX_NUM_FORMS': '5',
    #         'newsimage_set-0-image': test_image,
    #     })
    #     
    #     self.assertEqual(response.status_code, 302)
    #     
    #     # Check if news was created
    #     self.assertTrue(News.objects.filter(title='Test News Article', author=self.user).exists())
    
    # def test_change_visibility(self):
    #     response = self.client.get(reverse('author:change_visibilty', 
    #                                      args=[self.book.id, 'Private']))
    #     self.assertEqual(response.status_code, 302)
    #     
    #     # Check if book status was changed
    #     updated_book = Book.objects.get(id=self.book.id)
    #     self.assertEqual(updated_book.status, 'Private')
    
    # def test_delete_book(self):
    #     book_id = self.book.id
    #     response = self.client.get(reverse('author:delete_book', args=[book_id]))
    #     self.assertEqual(response.status_code, 302)
    #     
    #     # Check if book was deleted
    #     self.assertFalse(Book.objects.filter(id=book_id).exists())
    
    def test_content_comments(self):
        # Create a comment
        Comment.objects.create(
            user=self.user,
            book=self.book,
            content="Test comment"
        )
        
        response = self.client.get(reverse('author:content_comments', 
                                         args=['books', self.book.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('obj', response.context)
    
    def test_content_copyright(self):
        response = self.client.get(reverse('author:content_copyright', 
                                         args=['books', self.book.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('obj', response.context)


class AuthorDashboardTest(TestCase):
    """Test author dashboard functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='author',
            email='author@test.com',
            password='pass123'
        )
        UserProfile.objects.create(user=self.user, full_name="Author User")
        self.client.login(username='author', password='pass123')
        
        # Create test data
        self.books = []
        for i in range(5):
            book = Book.objects.create(
                title=f"Book {i}",
                description=f"Description {i}",
                content=f"Content {i}",
                author=self.user,
                views=i * 10
            )
            self.books.append(book)
    
    # def test_dashboard_displays_books(self):
    #     response = self.client.get(reverse('author:author_dashboard'))
    #     self.assertEqual(response.status_code, 200)
    #     
    #     for book in self.books:
    #         self.assertContains(response, book.title)
    
    def test_dashboard_analytics_data(self):
        # Create some views
        for book in self.books[:3]:
            ObjView.objects.create(book=book, user=self.user)
        
        response = self.client.get(reverse('author:author_dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Check analytics context
        self.assertIn('total_books', response.context)
        self.assertIn('total_views', response.context)


class AuthorPermissionsTest(TestCase):
    """Test author permissions and access control"""
    
    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user(
            username='author',
            email='author@test.com',
            password='pass123'
        )
        self.other_user = User.objects.create_user(
            username='other',
            email='other@test.com',
            password='pass123'
        )
        
        self.book = Book.objects.create(
            title="Author's Book",
            description="Test",
            content="Content",
            author=self.author
        )
    
    def test_author_can_edit_own_book(self):
        self.client.login(username='author', password='pass123')
        response = self.client.get(reverse('author:content_details', 
                                         args=['books', self.book.slug]))
        self.assertEqual(response.status_code, 200)
    
    # def test_non_author_cannot_edit_book(self):
    #     self.client.login(username='other', password='pass123')
    #     response = self.client.get(reverse('author:content_details', 
    #                                      args=['books', self.book.slug]))
    #     # This might return 404 or 403 depending on your implementation
    #     self.assertIn(response.status_code, [403, 404])
    
    def test_unauthenticated_user_redirected(self):
        response = self.client.get(reverse('author:content_details', 
                                         args=['books', self.book.slug]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login', response.url)


class AuthorAnalyticsTest(TestCase):
    """Test author analytics functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='author',
            email='author@test.com',
            password='pass123'
        )
        UserProfile.objects.create(user=self.user, full_name="Author User")
        self.client.login(username='author', password='pass123')
        
        self.book = Book.objects.create(
            title="Analytics Book",
            description="Test",
            content="Content",
            author=self.user
        )
        
        # Create follow relationship
        self.follower = User.objects.create_user(
            username='follower',
            email='follower@test.com',
            password='pass123'
        )
        UserFollow.objects.create(follower=self.follower, following=self.user)
    
    def test_analytics_view_data(self):
        # Create some analytics data
        ObjView.objects.create(book=self.book, user=self.follower)
        
        response = self.client.get(reverse('author:content_analytics', 
                                         args=['books', self.book.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('views', response.context)
        self.assertIn('entries', response.context)
    
    def test_analytics_date_filtering(self):
        response = self.client.get(reverse('author:content_analytics', 
                                         args=['books', self.book.slug]) + '?days=7')
        self.assertEqual(response.status_code, 200)


class AuthorCommunityTest(TestCase):
    """Test author community features"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='author',
            email='author@test.com',
            password='pass123'
        )
        UserProfile.objects.create(user=self.user, full_name="Author User")
        self.client.login(username='author', password='pass123')
        
        # Create followers
        for i in range(3):
            follower = User.objects.create_user(
                username=f'follower{i}',
                email=f'follower{i}@test.com',
                password='pass123'
            )
            UserProfile.objects.create(user=follower, full_name=f"Follower {i}")
            UserFollow.objects.create(follower=follower, following=self.user)
    
    def test_author_community_view(self):
        response = self.client.get(reverse('author:author_community'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('followers', response.context)
    
    def test_community_followers_display(self):
        response = self.client.get(reverse('author:author_community'))
        self.assertEqual(response.status_code, 200)
        
        # Check that followers are displayed
        for i in range(3):
            self.assertContains(response, f'follower{i}')


class UpdateSessionKeyTest(TestCase):
    """Test CSRF session key update functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='pass123'
        )
        self.client.login(username='testuser', password='pass123')
    
    # def test_update_session_key(self):
    #     response = self.client.post(reverse('author:update_session_key'))
    #     self.assertEqual(response.status_code, 200)
    #     
    #     data = json.loads(response.content)
    #     self.assertIn('csrf_token', data)


# class BookTranslationTest(TestCase):
#     """Test book translation functionality"""
#     
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(
#             username='author',
#             email='author@test.com',
#             password='pass123'
#         )
#         self.client.login(username='author', password='pass123')
#         
#         self.book = Book.objects.create(
#             title="Original Book",
#             description="Original description",
#             content="Original content",
#             author=self.user
#         )
#         
#         self.translation = Booktranslation.objects.create(
#             book=self.book,
#             language="Spanish",
#             title="Libro Original",
#             content="Contenido original"
#         )
#     
#     def test_content_translate_view(self):
#         response = self.client.get(reverse('author:content_translate', args=[self.book.slug]))
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('book', response.context)
#     
#     def test_get_translation(self):
#         response = self.client.get(reverse('author:get_translation', 
#                                          args=[self.book.id, self.translation.id]))
#         self.assertEqual(response.status_code, 200)
#         
#         data = json.loads(response.content)
#         self.assertEqual(data['title'], "Libro Original")
#         self.assertEqual(data['content'], "Contenido original")


class AudioBookTest(TestCase):
    """Test audio book functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='author',
            email='author@test.com',
            password='pass123'
        )
        self.client.login(username='author', password='pass123')
        
        self.book = Book.objects.create(
            title="Audio Book",
            description="Book with audio",
            content="Content",
            author=self.user
        )
    
    def test_content_audio_view(self):
        response = self.client.get(reverse('author:content_audio', args=[self.book.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertIn('book', response.context)
