#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_platform.settings')
django.setup()

from main.views import get_books_queryset
from main.query_optimizers import generate_cursor, parse_cursor, apply_cursor_pagination

def simulate_frontend_pagination():
    print("=== SIMULATING FRONTEND PAGINATION ===")
    
    # 1. Initial load (what index view does)
    print("\n1. Initial load (first 12 books):")
    books_queryset = get_books_queryset('trending')
    initial_books = list(books_queryset[:13])  # Load 13 to check if there are more
    
    has_more = len(initial_books) > 12
    if has_more:
        initial_books = initial_books[:12]
    
    print(f"   Got {len(initial_books)} books, has_more: {has_more}")
    
    for i, book in enumerate(initial_books):
        print(f'   {i+1:2d}. {book.title[:30]:30} | Views: {book.views:3d} | ID: {book.id}')
    
    if initial_books:
        last_cursor = generate_cursor(initial_books[-1], 'trending')
        print(f"   Last cursor: {last_cursor}")
        
        # 2. Simulate AJAX load_more_data request
        print(f"\n2. AJAX load_more_data with cursor: {last_cursor}")
        
        # This is what load_more_data does
        limit = 12
        books_queryset = get_books_queryset('trending')
        cursor_data = parse_cursor(last_cursor, 'trending')
        print(f"   Parsed cursor: {cursor_data}")
        
        if cursor_data:
            books_queryset = apply_cursor_pagination(books_queryset, 'trending', cursor_data)
        
        books = list(books_queryset[:limit + 1])  # Get one extra
        has_more = len(books) > limit
        
        if has_more:
            books = books[:limit]
        
        print(f"   Got {len(books)} more books, has_more: {has_more}")
        
        for i, book in enumerate(books):
            print(f'   {i+13:2d}. {book.title[:30]:30} | Views: {book.views:3d} | ID: {book.id}')

if __name__ == '__main__':
    simulate_frontend_pagination()
