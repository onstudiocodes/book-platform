from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
import io

from main.models import Book, Category, News, NewsCategory, Comment, ObjView, ReadingTime
from accounts.models import UserProfile


class SimpleBookModelTest(TestCase):
    """Simple test for Book model"""
    
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
        """Test that book is created correctly"""
        self.assertEqual(self.book.title, "Test Book")
        self.assertEqual(self.book.author, self.user)
        self.assertEqual(self.book.category, self.category)
        self.assertTrue(self.book.slug)
    
    def test_book_likes_count(self):
        """Test likes count method"""
        user2 = User.objects.create_user('user2', 'user2@test.com', 'pass')
        self.book.likes.add(self.user, user2)
        self.assertEqual(self.book.likes_count(), 2)
    
    def test_book_get_absolute_url(self):
        """Test get_absolute_url method"""
        expected_url = reverse('main:book_view', args=[self.book.slug])
        self.assertEqual(self.book.get_absolute_url(), expected_url)


class SimpleViewTest(TestCase):
    """Simple test for views that don't require templates"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        UserProfile.objects.create(user=self.user, full_name="Test User")
        
        # Create book with thumbnail to avoid template errors
        image_data = io.BytesIO()
        img = Image.new('RGB', (100, 100), color='red')
        img.save(image_data, format='JPEG')
        image_data.seek(0)
        
        test_image = SimpleUploadedFile(
            "test.jpg",
            image_data.getvalue(),
            content_type="image/jpeg"
        )
        
        self.book = Book.objects.create(
            title="Test Book",
            description="A test book",
            content="Test content",
            author=self.user,
            thumbnail=test_image
        )
    
    def test_login_required_views(self):
        """Test that protected views redirect to login"""
        protected_urls = [
            reverse('main:collections'),
            reverse('main:history'),
            reverse('main:continue_reading'),
        ]
        
        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn('/accounts/login', response.url)
    
    def test_profile_view(self):
        """Test profile view"""
        response = self.client.get(reverse('main:profile', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)


class SimpleUserTest(TestCase):
    """Simple test for user functionality"""
    
    def setUp(self):
        self.client = Client()
    
    def test_user_creation(self):
        """Test user can be created"""
        user = User.objects.create_user(
            username='newuser',
            email='new@example.com',
            password='pass123'
        )
        self.assertEqual(user.username, 'newuser')
        self.assertEqual(user.email, 'new@example.com')
    
    def test_user_profile_creation(self):
        """Test user profile can be created"""
        user = User.objects.create_user(
            username='profileuser',
            email='profile@example.com',
            password='pass123'
        )
        profile = UserProfile.objects.create(
            user=user,
            full_name="Profile User"
        )
        self.assertEqual(profile.user, user)
        self.assertEqual(profile.full_name, "Profile User")


class SimpleModelMethodTest(TestCase):
    """Test model methods without complex dependencies"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.book = Book.objects.create(
            title="Test Book",
            description="Test description",
            content="Test content",
            author=self.user
        )
    
    def test_category_str_method(self):
        """Test Category string representation"""
        category = Category.objects.create(name="Test Category")
        self.assertEqual(str(category), "Test Category")
    
    def test_reading_time_creation(self):
        """Test ReadingTime model"""
        reading_time = ReadingTime.objects.create(
            user=self.user,
            book=self.book,
            total_time=3600  # 1 hour
        )
        self.assertEqual(reading_time.get_hours(), "1.00")


class SimpleAuthTest(TestCase):
    """Simple authentication tests"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='authuser',
            email='auth@example.com',
            password='pass123'
        )
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post(reverse('accounts:login'), {
            'email': 'auth@example.com',
            'password': 'wrongpassword'
        })
        # Should redirect (to main page with error message)
        self.assertEqual(response.status_code, 302)
    
    def test_signup_basic(self):
        """Test basic signup functionality"""
        response = self.client.post(reverse('accounts:register'), {
            'full-name': 'New User',
            'email': 'newuser@example.com',
            'password': 'password123',
            'password2': 'password123'
        })
        # Should redirect after successful signup
        self.assertEqual(response.status_code, 302)
        
        # Check user was created
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())


class DatabaseIntegritySimpleTest(TestCase):
    """Simple database integrity tests"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_book_slug_uniqueness(self):
        """Test that book slugs are unique"""
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
        
        # Slugs should be different
        book1 = Book.objects.filter(description="First book").first()
        self.assertNotEqual(book1.slug, book2.slug)
    
    def test_foreign_key_relationships(self):
        """Test foreign key relationships work"""
        category = Category.objects.create(name="Test Category")
        book = Book.objects.create(
            title="Category Book",
            description="Book with category",
            content="Content",
            author=self.user,
            category=category
        )
        
        self.assertEqual(book.category, category)
        self.assertIn(book, category.books.all())
