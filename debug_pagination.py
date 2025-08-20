#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'book_platform.settings')
django.setup()

from main.models import Book
from main.query_optimizers import generate_cursor, parse_cursor, apply_cursor_pagination

def debug_pagination():
    print("=== DEBUGGING PAGINATION ===")
    
    # Test trending order
    print("\n1. Testing trending order (first 15 books):")
    books = Book.objects.order_by('-views', '-created_at')[:15]
    for i, book in enumerate(books):
        cursor = generate_cursor(book, 'trending')
        print(f'{i+1:2d}. {book.title[:30]:30} | Views: {book.views:3d} | ID: {book.id}')
        if i == 11:  # 12th book (index 11)
            print(f"    --> Cursor for 12th book: {cursor}")
            
            # Test what happens when we use this cursor
            print(f"\n2. Testing cursor pagination with cursor: {cursor}")
            cursor_data = parse_cursor(cursor, 'trending')
            print(f"    Parsed cursor data: {cursor_data}")
            
            # Apply cursor pagination
            queryset = Book.objects.order_by('-views', '-created_at')
            filtered_queryset = apply_cursor_pagination(queryset, 'trending', cursor_data)
            next_books = list(filtered_queryset[:5])
            
            print(f"    Next 5 books after cursor:")
            for j, next_book in enumerate(next_books):
                print(f'    {j+13:2d}. {next_book.title[:30]:30} | Views: {next_book.views:3d} | ID: {next_book.id}')
            
            break

if __name__ == '__main__':
    debug_pagination()
