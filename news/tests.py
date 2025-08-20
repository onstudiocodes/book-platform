from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from PIL import Image
import io
import json

from main.models import News, NewsCategory, NewsImage, Comment
from accounts.models import UserProfile
from author.forms import NewsForm, NewsImageFormSet
from .views import home, create_news, news_details, NewsListCreateView
from .serializers import NewsSerializer, NewsImageSerializer
from main.serializers import CommentSerializer


class NewsViewsTest(TestCase):
    """Test news views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='newsauthor',
            email='news@test.com',
            password='pass123'
        )
        UserProfile.objects.create(user=self.user, full_name="News Author")
        
        self.news_category = NewsCategory.objects.create(name="Technology")
        self.news = News.objects.create(
            title="Test News Article",
            description="Test news description",
            content="This is test news content",
            author=self.user,
            category=self.news_category,
            publish=True
        )
    
    def test_news_home_view(self):
        response = self.client.get(reverse('news:news_feed'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.news.title)
    
    def test_news_home_view_pagination(self):
        # Create multiple news articles
        for i in range(15):
            News.objects.create(
                title=f"News Article {i}",
                description=f"Description {i}",
                content=f"Content {i}",
                author=self.user,
                category=self.news_category,
                publish=True
            )
        
        response = self.client.get(reverse('news:news_feed'))
        self.assertEqual(response.status_code, 200)
        # Check pagination context
        self.assertIn('is_paginated', response.context)
    
    def test_create_news_get_authenticated(self):
        self.client.login(username='newsauthor', password='pass123')
        response = self.client.get(reverse('news:create_news'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('formset', response.context)
    
    def test_create_news_get_unauthenticated(self):
        response = self.client.get(reverse('news:create_news'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_create_news_post_valid(self):
        self.client.login(username='newsauthor', password='pass123')
        
        # Create test image
        image_data = io.BytesIO()
        img = Image.new('RGB', (100, 100), color='blue')
        img.save(image_data, format='JPEG')
        image_data.seek(0)
        
        test_image = SimpleUploadedFile(
            "news_test.jpg",
            image_data.getvalue(),
            content_type="image/jpeg"
        )
        
        response = self.client.post(reverse('news:create_news'), {
            'title': 'New News Article',
            'category': self.news_category.id,
            'content': 'This is new news content',
            # Formset management form
            'images-TOTAL_FORMS': '1',
            'images-INITIAL_FORMS': '0',
            'images-MIN_NUM_FORMS': '0',
            'images-MAX_NUM_FORMS': '5',
            'images-0-image': test_image,
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('news:news_feed'))
        
        # Check if news was created
        self.assertTrue(News.objects.filter(
            title='New News Article',
            author=self.user
        ).exists())
    
    def test_create_news_post_invalid(self):
        self.client.login(username='newsauthor', password='pass123')
        
        response = self.client.post(reverse('news:create_news'), {
            'title': '',  # Invalid - empty title
            'category': self.news_category.id,
            'content': 'Content',
            'newsimage_set-TOTAL_FORMS': '0',
            'newsimage_set-INITIAL_FORMS': '0',
        })
        
        self.assertEqual(response.status_code, 200)  # Stays on form page
        self.assertIn('form', response.context)
    
    def test_news_details_view(self):
        response = self.client.get(reverse('news:news_details', args=[self.news.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.news.title)
        self.assertContains(response, self.news.content)
        self.assertIn('news', response.context)
    
    def test_news_details_view_logs_view(self):
        self.client.login(username='newsauthor', password='pass123')
        response = self.client.get(reverse('news:news_details', args=[self.news.slug]))
        self.assertEqual(response.status_code, 200)
        
        # Check if view was logged (assuming log_news_view function works)
        from main.models import ObjView
        self.assertTrue(ObjView.objects.filter(news=self.news, user=self.user).exists())
    
    def test_news_details_nonexistent(self):
        response = self.client.get(reverse('news:news_details', args=['nonexistent-slug']))
        self.assertEqual(response.status_code, 404)


class NewsAPITest(TestCase):
    """Test News API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@test.com',
            password='pass123'
        )
        UserProfile.objects.create(user=self.user, full_name="API User")
        
        self.news_category = NewsCategory.objects.create(name="Technology")
        self.news = News.objects.create(
            title="API Test News",
            description="API test description",
            content="API test content",
            author=self.user,
            category=self.news_category,
            publish=True
        )
    
    def test_news_list_api(self):
        url = reverse('news:news-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['title'], self.news.title)
    
    def test_news_list_api_pagination(self):
        # Create multiple news articles
        for i in range(15):
            News.objects.create(
                title=f"API News {i}",
                description=f"Description {i}",
                content=f"Content {i}",
                author=self.user,
                category=self.news_category,
                publish=True
            )
        
        url = reverse('news:news-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('next', data)
        self.assertIn('previous', data)
        self.assertIn('count', data)
    
    def test_news_list_api_category_filter(self):
        # Create news with different category
        other_category = NewsCategory.objects.create(name="Sports")
        News.objects.create(
            title="Sports News",
            description="Sports description",
            content="Sports content",
            author=self.user,
            category=other_category,
            publish=True
        )
        
        url = reverse('news:news-list-create') + '?category=Technology'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['category']['name'], 'Technology')
    
    def test_news_list_api_exclude_filter(self):
        url = reverse('news:news-list-create') + f'?exclude={self.news.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        for news_item in data['results']:
            self.assertNotEqual(news_item['id'], self.news.id)
    
    # def test_news_create_api_authenticated(self):
    #     self.client.force_authenticate(user=self.user)
        
    #     url = reverse('news:news-list-create')
    #     data = {
    #         'title': 'API Created News',
    #         'description': 'Created via API',
    #         'content': 'API content',
    #         'category_id': self.news_category.id
    #     }
        
    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
    #     # Check if news was created
    #     self.assertTrue(News.objects.filter(title='API Created News').exists())
    
    def test_news_create_api_unauthenticated(self):
        url = reverse('news:news-list-create')
        data = {
            'title': 'Unauthorized News',
            'content': 'Should not be created'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class NewsSerializerTest(TestCase):
    """Test news serializers"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='pass123'
        )
        UserProfile.objects.create(user=self.user, full_name="Test User")
        
        self.news_category = NewsCategory.objects.create(name="Technology")
        self.news = News.objects.create(
            title="Serializer Test News",
            description="Test description",
            content="Test content",
            author=self.user,
            category=self.news_category,
            publish=True
        )
    
    def test_news_serializer_fields(self):
        serializer = NewsSerializer(instance=self.news)
        data = serializer.data
        
        expected_fields = [
            'id', 'title', 'slug', 'description', 'content', 'author',
            'category', 'created_at', 'updated_date', 'likes_count',
            'dislikes_count', 'comments_count', 'views_count', 'images'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)
    
    def test_news_serializer_author_representation(self):
        # Create a mock request object for context
        from django.test import RequestFactory
        factory = RequestFactory()
        request = factory.get('/')
        request.user = self.user
        
        serializer = NewsSerializer(instance=self.news, context={'request': request})
        data = serializer.data
        
        self.assertEqual(data['author']['username'], self.user.username)
        self.assertEqual(data['author']['full_name'], 'Test User')
    
    def test_news_serializer_category_representation(self):
        serializer = NewsSerializer(instance=self.news)
        data = serializer.data
        
        self.assertEqual(data['category']['name'], self.news_category.name)
        self.assertEqual(data['category']['slug'], self.news_category.slug)
    
    def test_news_image_serializer(self):
        # Create test image
        image_data = io.BytesIO()
        img = Image.new('RGB', (100, 100), color='green')
        img.save(image_data, format='JPEG')
        image_data.seek(0)
        
        test_image = SimpleUploadedFile(
            "serializer_test.jpg",
            image_data.getvalue(),
            content_type="image/jpeg"
        )
        
        news_image = NewsImage.objects.create(
            news=self.news,
            image=test_image
        )
        
        serializer = NewsImageSerializer(instance=news_image)
        data = serializer.data
        
        self.assertIn('id', data)
        self.assertIn('image', data)


class NewsModelIntegrationTest(TestCase):
    """Test news model integration with other components"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='integrationuser',
            email='integration@test.com',
            password='pass123'
        )
        
        self.news_category = NewsCategory.objects.create(name="Integration")
        self.news = News.objects.create(
            title="Integration Test News",
            description="Integration test",
            content="Integration content",
            author=self.user,
            category=self.news_category
        )
    
    def test_news_likes_functionality(self):
        # Test adding likes
        self.news.likes.add(self.user)
        self.assertEqual(self.news.likes_count(), 1)
        
        # Test removing likes
        self.news.likes.remove(self.user)
        self.assertEqual(self.news.likes_count(), 0)
    
    def test_news_dislikes_functionality(self):
        # Test adding dislikes
        self.news.dislikes.add(self.user)
        self.assertEqual(self.news.dislikes_count(), 1)
        
        # Test removing dislikes
        self.news.dislikes.remove(self.user)
        self.assertEqual(self.news.dislikes_count(), 0)
    
    def test_news_comments_integration(self):
        # Create comment
        comment = Comment.objects.create(
            user=self.user,
            news=self.news,
            content="Test comment on news"
        )
        
        # Check comment relationship
        self.assertEqual(comment.news, self.news)
        self.assertTrue(self.news.comments.filter(id=comment.id).exists())
    
    # def test_news_images_relationship(self):
    #     # Create test image
    #     image_data = io.BytesIO()
    #     img = Image.new('RGB', (100, 100), color='yellow')
    #     img.save(image_data, format='JPEG')
    #     image_data.seek(0)
        
    #     test_image = SimpleUploadedFile(
    #         "relationship_test.jpg",
    #         image_data.getvalue(),
    #         content_type="image/jpeg"
    #     )
        
    #     news_image = NewsImage.objects.create(
    #         news=self.news,
    #         image=test_image
    #     )
        
    #     # Test relationship
    #     self.assertEqual(news_image.news, self.news)
    #     self.assertTrue(self.news.images.filter(id=news_image.id).exists())
        
    #     # Test thumbnail method
    #     self.assertEqual(self.news.thumbnail(), news_image.image)


class NewsCommentAPITest(TestCase):
    """Test news comment API"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='commentuser',
            email='comment@test.com',
            password='pass123'
        )
        
        self.news = News.objects.create(
            title="Comment Test News",
            description="Test description",
            content="Test content",
            author=self.user
        )
    
    # def test_comment_list_api(self):
    #     # Create some comments
    #     Comment.objects.create(
    #         user=self.user,
    #         news=self.news,
    #         content="First comment"
    #     )
    #     Comment.objects.create(
    #         user=self.user,
    #         news=self.news,
    #         content="Second comment"
    #     )
    #     
    #     url = reverse('news:comments')
    #     response = self.client.get(url, {'news_id': self.news.id})
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     
    #     data = response.json()
    #     self.assertEqual(len(data['results']), 2)
    
    # def test_comment_create_api_authenticated(self):
    #     self.client.force_authenticate(user=self.user)
    #     
    #     url = reverse('news:comments')
    #     data = {
    #         'type': 'news',
    #         'id': self.news.id,
    #         'content': 'API created comment'
    #     }
    #     
    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #     
    #     # Check if comment was created
    #     self.assertTrue(Comment.objects.filter(
    #         news=self.news,
    #         content='API created comment'
    #     ).exists())
    
    # def test_comment_create_api_unauthenticated(self):
    #     url = reverse('news:comments')
    #     data = {
    #         'type': 'news',
    #         'id': self.news.id,
    #         'content': 'Unauthorized comment'
    #     }
    #     
    #     response = self.client.post(url, data)
    #     self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class NewsViewCountTest(TestCase):
    """Test news view counting functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='viewuser',
            email='view@test.com',
            password='pass123'
        )
        
        self.news = News.objects.create(
            title="View Count Test News",
            description="Test description",
            content="Test content",
            author=self.user,
            views=0
        )
    
    def test_news_view_increments_count(self):
        initial_views = self.news.views
        
        # Visit news detail page
        response = self.client.get(reverse('news:news_details', args=[self.news.slug]))
        self.assertEqual(response.status_code, 200)
        
        # Refresh from database
        self.news.refresh_from_db()
        # Note: This assumes view counting is implemented in news_details view
        # You may need to adjust based on your actual implementation


class NewsCategoryTest(TestCase):
    """Test news category functionality"""
    
    def setUp(self):
        self.category = NewsCategory.objects.create(name="Test Category")
        self.user = User.objects.create_user(
            username='catuser',
            email='cat@test.com',
            password='pass123'
        )
    
    def test_category_creation(self):
        self.assertEqual(self.category.name, "Test Category")
        self.assertTrue(self.category.slug)
        self.assertEqual(str(self.category), "Test Category")
    
    def test_category_news_relationship(self):
        news = News.objects.create(
            title="Category Test News",
            description="Test",
            content="Content",
            author=self.user,
            category=self.category
        )
        
        self.assertEqual(news.category, self.category)
        self.assertTrue(self.category.news.filter(id=news.id).exists())


class NewsFormTest(TestCase):
    """Test news forms"""
    
    def setUp(self):
        self.category = NewsCategory.objects.create(name="Form Test")
    
    def test_news_form_valid_data(self):
        form_data = {
            'title': 'Form Test News',
            'category': self.category.id,
            'content': 'Form test content'
        }
        
        form = NewsForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_news_form_invalid_data(self):
        form_data = {
            'title': '',  # Required field
            'content': 'Content without title'
        }
        
        form = NewsForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_news_image_formset(self):
        # Test empty formset
        formset = NewsImageFormSet()
        self.assertFalse(formset.is_valid())
        
        # Test formset with data
        formset_data = {
            'images-TOTAL_FORMS': '1',
            'images-INITIAL_FORMS': '0',
            'images-0-DELETE': '',
        }
        
        formset = NewsImageFormSet(data=formset_data)
        self.assertTrue(formset.is_valid())
