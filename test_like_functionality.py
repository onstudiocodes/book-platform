#!/usr/bin/env python3
"""
Test script to verify the like functionality for TravelStory
"""
import os
import sys
import django

# Add the project root to Python path
sys.path.append('/home/mahamudh472/Projects/book_platform2/book-platform')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_platform.settings')
django.setup()

from django.contrib.auth.models import User
from main.models import TravelStory, TravelCategory
from accounts.models import UserProfile

def test_like_functionality():
    print("Testing TravelStory like functionality...")
    
    # Create or get test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'password': 'testpass123'
        }
    )
    if created:
        UserProfile.objects.create(user=user, full_name="Test User")
        print(f"Created test user: {user.username}")
    else:
        print(f"Using existing test user: {user.username}")
    
    # Create or get test category
    category, created = TravelCategory.objects.get_or_create(
        name='Test Category'
    )
    if created:
        print(f"Created test category: {category.name}")
    else:
        print(f"Using existing test category: {category.name}")
    
    # Create test travel story
    story, created = TravelStory.objects.get_or_create(
        title='Test Travel Story for Likes',
        defaults={
            'story': 'This is a test travel story to test the like functionality.',
            'author': user,
            'category': category,
            'location': 'Test Location',
            'published': True
        }
    )
    if created:
        print(f"Created test travel story: {story.title}")
    else:
        print(f"Using existing test travel story: {story.title}")
    
    # Test initial state
    print(f"\nInitial state:")
    print(f"Likes: {story.likes_count()}")
    print(f"Dislikes: {story.dislikes_count()}")
    print(f"User has liked: {user in story.likes.all()}")
    print(f"User has disliked: {user in story.dislikes.all()}")
    
    # Test liking
    story.likes.add(user)
    print(f"\nAfter liking:")
    print(f"Likes: {story.likes_count()}")
    print(f"Dislikes: {story.dislikes_count()}")
    print(f"User has liked: {user in story.likes.all()}")
    print(f"User has disliked: {user in story.dislikes.all()}")
    
    # Test disliking (should remove like and add dislike)
    story.likes.remove(user)
    story.dislikes.add(user)
    print(f"\nAfter disliking:")
    print(f"Likes: {story.likes_count()}")
    print(f"Dislikes: {story.dislikes_count()}")
    print(f"User has liked: {user in story.likes.all()}")
    print(f"User has disliked: {user in story.dislikes.all()}")
    
    # Test removing dislike
    story.dislikes.remove(user)
    print(f"\nAfter removing dislike:")
    print(f"Likes: {story.likes_count()}")
    print(f"Dislikes: {story.dislikes_count()}")
    print(f"User has liked: {user in story.likes.all()}")
    print(f"User has disliked: {user in story.dislikes.all()}")
    
    print("\n✅ Like functionality test completed successfully!")
    print(f"Story ID: {story.id}")
    print(f"Story Slug: {story.slug}")
    print(f"Visit: http://127.0.0.1:8000/travel/tour_details/{story.slug}")

if __name__ == '__main__':
    test_like_functionality()
