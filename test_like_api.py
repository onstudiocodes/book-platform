#!/usr/bin/env python3
"""
Test script to test the like API endpoint
"""
import os
import sys
import django

# Add the project root to Python path
sys.path.append('/home/mahamudh472/Projects/book_platform2/book-platform')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_platform.settings')
django.setup()

from django.test.client import Client
from django.contrib.auth.models import User
from main.models import TravelStory
import json

def test_like_api():
    print("Testing TravelStory like API...")
    
    client = Client()
    
    # Get a test user and story
    user = User.objects.filter(username='testuser').first()
    story = TravelStory.objects.first()
    
    if not user or not story:
        print("❌ No test user or story found. Run the setup test first.")
        return
    
    # Login the user
    client.force_login(user)
    print(f"✅ Logged in as {user.username}")
    
    # Test toggle like endpoint
    response = client.post('/travel/toggle_travel_story_like', {
        'story_id': story.id,
        'op': 'like'
    })
    
    print(f"Toggle like response status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response data: {data}")
        print("✅ Toggle like API works!")
    else:
        print(f"❌ Toggle like API failed with status {response.status_code}")
        print(f"Response content: {response.content}")
    
    # Test REST API like endpoint
    response = client.post(f'/travel/like_travel_story/{story.id}')
    print(f"REST API like response status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response data: {data}")
        print("✅ REST API like works!")
    else:
        print(f"❌ REST API like failed with status {response.status_code}")
        print(f"Response content: {response.content}")

if __name__ == '__main__':
    test_like_api()
