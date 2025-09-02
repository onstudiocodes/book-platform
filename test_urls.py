#!/usr/bin/env python3
"""
Test script to verify the URL patterns are working
"""
import os
import sys
import django

# Add the project root to Python path
sys.path.append('/home/mahamudh472/Projects/book_platform2/book-platform')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_platform.settings')
django.setup()

from django.urls import reverse
from django.test.client import Client
from django.contrib.auth.models import User
from main.models import TravelStory

def test_urls():
    print("Testing URL patterns...")
    client = Client()
    
    # Test if we can access a travel story
    story = TravelStory.objects.first()
    if story:
        print(f"Testing story: {story.title}")
        
        # Test tour details URL
        try:
            url = reverse('travel:tour_details', args=[story.slug])
            print(f"Tour details URL: {url}")
            
            response = client.get(url)
            print(f"Tour details response status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Tour details page loads successfully")
            else:
                print(f"❌ Tour details page failed with status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error accessing tour details: {e}")
        
        # Test toggle like URL
        try:
            url = reverse('travel:toggle_travel_story_like')
            print(f"Toggle like URL: {url}")
            print("✅ Toggle like URL pattern exists")
        except Exception as e:
            print(f"❌ Error with toggle like URL: {e}")
            
        # Test API like URL
        try:
            url = reverse('travel:like_travel_story', args=[story.id])
            print(f"API like URL: {url}")
            print("✅ API like URL pattern exists")
        except Exception as e:
            print(f"❌ Error with API like URL: {e}")
            
    else:
        print("❌ No travel stories found in database")

def add_categories():
    from main.models import Category
    categories = [
        "Literary Fiction",
        "Mystery",
        "Thriller & Suspense",
        "Horror",
        "Historical Fiction",
        "Romance",
        "Science Fiction",
        "Fantasy",
        "Young Adult (YA) Fiction",
        "Children's Fiction",
        "Graphic Novels & Comics",
        "Biography & Autobiography",
        "Memoir",
        "History",
        "Travel",
        "True Crime",
        "Science & Nature",
        "Philosophy",
        "Religion & Spirituality",
        "Self-Help & Personal Development",
        "Business & Economics",
        "Cookbooks, Food & Wine",
        "Art, Architecture & Photography",
        "Health, Fitness & Dieting",
        "Parenting & Relationships",
        "Crafts, Hobbies & Home",
        "Essays & Journalism",
        "Poetry Collections",
        "Plays & Dramatic Works",
        "Textbooks",
        "Reference Books (Dictionaries, Encyclopedias)",
        "Academic & Scholarly Works",
        "Professional & Technical Guides",
        "Test Preparation & Study Guides",
        "Language Learning Books",
        "Short Story & Essay"
    ]
    for item in categories:
        Category.objects.get_or_create(name=item)
        print(Category.objects.count())
    print("Categories added.")

if __name__ == '__main__':
    # test_urls()
    add_categories()
