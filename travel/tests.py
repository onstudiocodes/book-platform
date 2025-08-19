from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from PIL import Image
import io
import json

from main.models import TravelStory, TravelCategory, TravelImage
from accounts.models import UserProfile
from main.forms import TravelStoryForm
from .views import tour_wall, tour_details, add_travel_story, TravelStoryListAPIView
from .serializers import TravelStorySerializer


class TravelStoryModelTest(TestCase):
    """Test TravelStory model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='traveler',
            email='traveler@test.com',
            password='pass123'
        )
        self.category = TravelCategory.objects.create(name="Adventure")
        self.travel_story = TravelStory.objects.create(
            title="Amazing Mountain Trek",
            story="This was an incredible journey through the mountains",
            author=self.user,
            category=self.category,
            location="Himalayas",
            country="Nepal",
            duration="1 week",
            season="Spring",
            budget_level="Budget"
        )
    
    def test_travel_story_creation(self):
        self.assertEqual(self.travel_story.title, "Amazing Mountain Trek")
        self.assertEqual(self.travel_story.author, self.user)
        self.assertEqual(self.travel_story.category, self.category)
        self.assertEqual(self.travel_story.location, "Himalayas")
        self.assertTrue(self.travel_story.slug)
    
    def test_travel_story_str_method(self):
        self.assertEqual(str(self.travel_story), "Amazing Mountain Trek")
    
    # def test_travel_story_get_absolute_url(self):
    #     expected_url = reverse('travel:tour_details', args=[self.travel_story.slug])
    #     self.assertEqual(self.travel_story.get_absolute_url(), expected_url)
    
    def test_travel_story_slug_generation(self):
        story = TravelStory.objects.create(
            title="Another Great Adventure",
            story="Another story",
            author=self.user,
            location="Alps"
        )
        self.assertEqual(story.slug, "another-great-adventure")


class TravelCategoryModelTest(TestCase):
    """Test TravelCategory model"""
    
    def setUp(self):
        self.category = TravelCategory.objects.create(name="Beach Holiday")
    
    def test_category_creation(self):
        self.assertEqual(self.category.name, "Beach Holiday")
        self.assertTrue(self.category.slug)
        self.assertEqual(str(self.category), "Beach Holiday")
    
    def test_category_slug_generation(self):
        category = TravelCategory.objects.create(name="Cultural Experience")
        self.assertEqual(category.slug, "cultural-experience")


class TravelImageModelTest(TestCase):
    """Test TravelImage model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='photographer',
            email='photo@test.com',
            password='pass123'
        )
        self.travel_story = TravelStory.objects.create(
            title="Photo Story",
            story="A story with photos",
            author=self.user,
            location="Paris"
        )
        
        # Create test image
        image_data = io.BytesIO()
        img = Image.new('RGB', (100, 100), color='blue')
        img.save(image_data, format='JPEG')
        image_data.seek(0)
        
        test_image = SimpleUploadedFile(
            "travel_test.jpg",
            image_data.getvalue(),
            content_type="image/jpeg"
        )
        
        self.travel_image = TravelImage.objects.create(
            travel_story=self.travel_story,
            image=test_image
        )
    
    # def test_travel_image_creation(self):
    #     self.assertEqual(self.travel_image.travel_story, self.travel_story)
    #     self.assertTrue(self.travel_image.image)
    #     self.assertTrue(self.travel_image.uploaded_at)
    
    def test_travel_image_str_method(self):
        expected_str = f"Image for {self.travel_story.title}"
        self.assertEqual(str(self.travel_image), expected_str)


class TravelViewsTest(TestCase):
    """Test travel views"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='traveler',
            email='traveler@test.com',
            password='pass123'
        )
        UserProfile.objects.create(user=self.user, full_name="Travel User")
        
        self.category = TravelCategory.objects.create(name="Adventure")
        self.travel_story = TravelStory.objects.create(
            title="Test Travel Story",
            story="Test travel content",
            author=self.user,
            category=self.category,
            location="Test Location",
            published=True
        )
    
    def test_tour_wall_view(self):
        response = self.client.get(reverse('travel:tour_wall'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.travel_story.title)
    
    def test_tour_details_view(self):
        response = self.client.get(reverse('travel:tour_details', args=[self.travel_story.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.travel_story.title)
        self.assertContains(response, self.travel_story.story)
        self.assertIn('story', response.context)
    
    # def test_tour_details_nonexistent(self):
    #     response = self.client.get(reverse('travel:tour_details', args=['nonexistent-slug']))
    #     self.assertEqual(response.status_code, 404)
    
    def test_add_travel_story_get_authenticated(self):
        self.client.login(username='traveler', password='pass123')
        response = self.client.get(reverse('travel:add_travel_story'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
    
    def test_add_travel_story_get_unauthenticated(self):
        response = self.client.get(reverse('travel:add_travel_story'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    # def test_add_travel_story_post_valid(self):
    #     self.client.login(username='traveler', password='pass123')
    #     
    #     # Create test images
    #     images = []
    #     for i in range(3):
    #         image_data = io.BytesIO()
    #         img = Image.new('RGB', (100, 100), color='red')
    #         img.save(image_data, format='JPEG')
    #         image_data.seek(0)
    #         
    #         test_image = SimpleUploadedFile(
    #             f"test_image_{i}.jpg",
    #             image_data.getvalue(),
    #             content_type="image/jpeg"
    #         )
    #         images.append(test_image)
    #     
    #     response = self.client.post(reverse('travel:add_travel_story'), {
    #         'title': 'New Travel Story',
    #         'story': 'New travel story content',
    #         'category': self.category.id,
    #         'location': 'New Location',
    #         'duration': '1-3',
    #         'season': 'summer',
    #         'budget_level': 'budget',
    #         'images': images
    #     })
    #     
    #     self.assertEqual(response.status_code, 302)
    #     
    #     # Check if travel story was created
    #     self.assertTrue(TravelStory.objects.filter(
    #         title='New Travel Story',
    #         author=self.user
    #     ).exists())
    #     
    #     # Check if images were created
    #     new_story = TravelStory.objects.get(title='New Travel Story')
    #     self.assertEqual(new_story.images.count(), 3)
    
    def test_add_travel_story_post_insufficient_images(self):
        self.client.login(username='traveler', password='pass123')
        
        # Create only 2 images (less than required 3)
        images = []
        for i in range(2):
            image_data = io.BytesIO()
            img = Image.new('RGB', (100, 100), color='green')
            img.save(image_data, format='JPEG')
            image_data.seek(0)
            
            test_image = SimpleUploadedFile(
                f"insufficient_{i}.jpg",
                image_data.getvalue(),
                content_type="image/jpeg"
            )
            images.append(test_image)
        
        response = self.client.post(reverse('travel:add_travel_story'), {
            'title': 'Story with Few Images',
            'story': 'Story content',
            'category': self.category.id,
            'location': 'Location',
            'images': images
        })
        
        self.assertEqual(response.status_code, 200)  # Stays on form page
        self.assertContains(response, 'At least 3 photos are required')
    
    # def test_add_travel_story_publish(self):
    #     self.client.login(username='traveler', password='pass123')
    #     
    #     # Create test images
    #     images = []
    #     for i in range(3):
    #         image_data = io.BytesIO()
    #         img = Image.new('RGB', (100, 100), color='yellow')
    #         img.save(image_data, format='JPEG')
    #         image_data.seek(0)
    #         
    #         test_image = SimpleUploadedFile(
    #             f"publish_test_{i}.jpg",
    #             image_data.getvalue(),
    #             content_type="image/jpeg"
    #         )
    #         images.append(test_image)
    #     
    #     response = self.client.post(reverse('travel:add_travel_story'), {
    #         'title': 'Published Story',
    #         'story': 'Published content',
    #         'category': self.category.id,
    #         'location': 'Published Location',
    #         'images': images,
    #         'publish': 'true'  # Publish the story
    #     })
    #     
    #     self.assertEqual(response.status_code, 302)
    #     
    #     # Check if story was published
    #     story = TravelStory.objects.get(title='Published Story')
    #     self.assertTrue(story.published)
    
    # def test_search_view(self):
    #     response = self.client.get(reverse('travel:search'), {'q': 'Test'})
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, self.travel_story.title)
    
    # def test_search_view_no_results(self):
    #     response = self.client.get(reverse('travel:search'), {'q': 'NonexistentTerm'})
    #     self.assertEqual(response.status_code, 200)
    #     self.assertNotContains(response, self.travel_story.title)


class TravelAPITest(TestCase):
    """Test Travel API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@test.com',
            password='pass123'
        )
        UserProfile.objects.create(user=self.user, full_name="API User")
        
        self.category = TravelCategory.objects.create(name="API Category")
        self.travel_story = TravelStory.objects.create(
            title="API Test Story",
            story="API test content",
            author=self.user,
            category=self.category,
            location="API Location",
            published=True
        )
    
    def test_travel_story_list_api(self):
        url = reverse('travel:travel')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['title'], self.travel_story.title)
    
    def test_travel_story_list_api_pagination(self):
        # Create multiple travel stories
        for i in range(15):
            TravelStory.objects.create(
                title=f"API Story {i}",
                story=f"Content {i}",
                author=self.user,
                category=self.category,
                location=f"Location {i}",
                published=True
            )
        
        url = reverse('travel:travel')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('next', data)
        self.assertIn('previous', data)
        self.assertIn('count', data)
    
    # def test_travel_story_list_api_filtering(self):
    #     # Create unpublished story
    #     TravelStory.objects.create(
    #         title="Unpublished Story",
    #         story="Unpublished content",
    #         author=self.user,
    #         category=self.category,
    #         location="Private Location",
    #         published=False
    #     )
    #     
    #     url = reverse('travel:travel')
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     
    #     data = response.json()
    #     # Should only return published stories
    #     for story in data['results']:
    #         self.assertTrue(story.get('published', True))


class TravelSerializerTest(TestCase):
    """Test travel serializers"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='serializeruser',
            email='serializer@test.com',
            password='pass123'
        )
        UserProfile.objects.create(user=self.user, full_name="Serializer User")
        
        self.category = TravelCategory.objects.create(name="Serializer Category")
        self.travel_story = TravelStory.objects.create(
            title="Serializer Test Story",
            story="Serializer test content",
            author=self.user,
            category=self.category,
            location="Serializer Location",
            latitude=27.7172,
            longitude=85.3240,
            duration="1 week",
            season="Spring",
            budget_level="Mid-range"
        )
    
    def test_travel_story_serializer_fields(self):
        serializer = TravelStorySerializer(instance=self.travel_story)
        data = serializer.data
        
        expected_fields = [
            'id', 'title', 'slug', 'story', 'author', 'category',
            'location', 'latitude', 'longitude', 'duration', 'season',
            'budget_level', 'published', 'created_at', 'images'
        ]
        
        for field in expected_fields:
            self.assertIn(field, data)
    
    def test_travel_story_serializer_author_representation(self):
        serializer = TravelStorySerializer(instance=self.travel_story)
        data = serializer.data
        
        self.assertEqual(data['author']['username'], self.user.username)
        self.assertEqual(data['author']['full_name'], 'Serializer User')
    
    # def test_travel_story_serializer_category_representation(self):
    #     serializer = TravelStorySerializer(instance=self.travel_story)
    #     data = serializer.data
    #     
    #     self.assertEqual(data['category']['name'], self.category.name)
    #     self.assertEqual(data['category']['slug'], self.category.slug)
    
    def test_travel_story_serializer_coordinates(self):
        serializer = TravelStorySerializer(instance=self.travel_story)
        data = serializer.data
        
        self.assertEqual(data['latitude'], 27.7172)
        self.assertEqual(data['longitude'], 85.3240)


class TravelFormTest(TestCase):
    """Test travel forms"""
    
    def setUp(self):
        self.category = TravelCategory.objects.create(name="Form Test Category")
    
    def test_travel_story_form_valid_data(self):
        # Create mock image files
        from django.core.files.uploadedfile import SimpleUploadedFile
        import io
        from PIL import Image
        
        # Create test images
        image_data1 = io.BytesIO()
        img1 = Image.new('RGB', (100, 100), color='red')
        img1.save(image_data1, format='JPEG')
        image_data1.seek(0)
        
        image_data2 = io.BytesIO()
        img2 = Image.new('RGB', (100, 100), color='green')
        img2.save(image_data2, format='JPEG')
        image_data2.seek(0)
        
        image_data3 = io.BytesIO()
        img3 = Image.new('RGB', (100, 100), color='blue')
        img3.save(image_data3, format='JPEG')
        image_data3.seek(0)
        
        test_images = [
            SimpleUploadedFile("test1.jpg", image_data1.getvalue(), content_type="image/jpeg"),
            SimpleUploadedFile("test2.jpg", image_data2.getvalue(), content_type="image/jpeg"),
            SimpleUploadedFile("test3.jpg", image_data3.getvalue(), content_type="image/jpeg")
        ]
        
        form_data = {
            'title': 'Form Test Story',
            'story': 'Form test content',
            'category': self.category.id,
            'location': 'Form Location',
            'duration': '1-3',
            'season': 'summer',
            'budget_level': 'budget',
            'pro_tips': 'Some helpful tips',
            'tags': 'adventure, hiking'
        }
        
        form = TravelStoryForm(data=form_data, files={'images': test_images})
        self.assertTrue(form.is_valid())
    
    def test_travel_story_form_invalid_data(self):
        form_data = {
            'title': '',  # Required field
            'story': 'Story without title',
            'location': 'Location'
        }
        
        form = TravelStoryForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_travel_story_form_widget_attributes(self):
        form = TravelStoryForm()
        
        # Check that form widgets have proper CSS classes
        title_widget = form.fields['title'].widget
        self.assertIn('class', title_widget.attrs)
        self.assertIn('w-full', title_widget.attrs['class'])


class TravelIntegrationTest(TestCase):
    """Test travel integration with other components"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='integration',
            email='integration@test.com',
            password='pass123'
        )
        
        self.category = TravelCategory.objects.create(name="Integration")
        self.travel_story = TravelStory.objects.create(
            title="Integration Story",
            story="Integration content",
            author=self.user,
            category=self.category,
            location="Integration Location"
        )
    
    def test_travel_story_images_relationship(self):
        # Create test image
        image_data = io.BytesIO()
        img = Image.new('RGB', (100, 100), color='purple')
        img.save(image_data, format='JPEG')
        image_data.seek(0)
        
        test_image = SimpleUploadedFile(
            "integration_test.jpg",
            image_data.getvalue(),
            content_type="image/jpeg"
        )
        
        travel_image = TravelImage.objects.create(
            travel_story=self.travel_story,
            image=test_image
        )
        
        # Test relationship
        self.assertEqual(travel_image.travel_story, self.travel_story)
        self.assertTrue(self.travel_story.images.filter(id=travel_image.id).exists())
    
    def test_travel_story_author_relationship(self):
        # Test that author relationship works correctly
        self.assertEqual(self.travel_story.author, self.user)
        self.assertTrue(self.user.travelstory_set.filter(id=self.travel_story.id).exists())
    
    def test_travel_story_category_relationship(self):
        # Test category relationship
        self.assertEqual(self.travel_story.category, self.category)
        self.assertTrue(self.category.stories.filter(id=self.travel_story.id).exists())


class TravelPermissionsTest(TestCase):
    """Test travel permissions and access control"""
    
    def setUp(self):
        self.client = Client()
        self.author = User.objects.create_user(
            username='storyauthor',
            email='author@test.com',
            password='pass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@test.com',
            password='pass123'
        )
        
        self.travel_story = TravelStory.objects.create(
            title="Author's Story",
            story="Author's content",
            author=self.author,
            location="Author's Location"
        )
    
    def test_add_travel_story_requires_authentication(self):
        response = self.client.get(reverse('travel:add_travel_story'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login', response.url)
    
    def test_authenticated_user_can_add_story(self):
        self.client.login(username='storyauthor', password='pass123')
        response = self.client.get(reverse('travel:add_travel_story'))
        self.assertEqual(response.status_code, 200)


# class TravelSearchTest(TestCase):
#     """Test travel search functionality"""
#     
#     def setUp(self):
#         self.client = Client()
#         self.user = User.objects.create_user(
#             username='searchuser',
#             email='search@test.com',
#             password='pass123'
#         )
#         
#         self.category = TravelCategory.objects.create(name="Search Category")
#         
#         # Create multiple travel stories for search testing
#         self.stories = []
#         search_terms = [
#             ("Mountain Adventure", "Epic mountain climbing adventure"),
#             ("Beach Paradise", "Relaxing beach vacation story"),
#             ("City Explorer", "Urban exploration and culture"),
#             ("Desert Journey", "Camel trekking through the desert")
#         ]
#         
#         for title, story in search_terms:
#             travel_story = TravelStory.objects.create(
#                 title=title,
#                 story=story,
#                 author=self.user,
#                 category=self.category,
#                 location=f"{title} Location",
#                 published=True
#             )
#             self.stories.append(travel_story)
#     
#     def test_search_by_title(self):
#         response = self.client.get(reverse('travel:search'), {'q': 'Mountain'})
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "Mountain Adventure")
#         self.assertNotContains(response, "Beach Paradise")
#     
#     def test_search_by_content(self):
#         response = self.client.get(reverse('travel:search'), {'q': 'climbing'})
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "Mountain Adventure")
#     
#     def test_search_by_location(self):
#         response = self.client.get(reverse('travel:search'), {'q': 'Beach Paradise Location'})
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "Beach Paradise")
#     
#     def test_search_no_results(self):
#         response = self.client.get(reverse('travel:search'), {'q': 'NonexistentTerm'})
#         self.assertEqual(response.status_code, 200)
#         # Should show no results message or empty results
#         for story in self.stories:
#             self.assertNotContains(response, story.title)
#     
#     def test_search_empty_query(self):
#         response = self.client.get(reverse('travel:search'), {'q': ''})
#         self.assertEqual(response.status_code, 200)
#         # Should handle empty search gracefully
#     
#     def test_search_case_insensitive(self):
#         response = self.client.get(reverse('travel:search'), {'q': 'MOUNTAIN'})
#         self.assertEqual(response.status_code, 200)
#         self.assertContains(response, "Mountain Adventure")
