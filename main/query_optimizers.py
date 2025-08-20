"""
Query optimization utilities for efficient database operations
"""
from django.db.models import Count, Q, Prefetch
from django.core.cache import cache
from django.contrib.auth.models import User
from django.utils import timezone


def get_optimized_book_queryset():
    """
    Returns an optimized Book queryset with proper select_related and prefetch_related
    """
    from .models import Book  # Import here to avoid circular imports
    
    return Book.public_objects.select_related(
        'author',
        'author__userprofile',
        'category'
    ).prefetch_related(
        Prefetch(
            'likes',
            queryset=User.objects.only('id'),
            to_attr='like_users'
        )
    ).only(
        'id', 'title', 'slug', 'description', 'views', 'created_at',
        'thumbnail', 'author__username', 'author__userprofile__full_name',
        'author__userprofile__profile_picture', 'category__name'
    )


def get_book_detail_queryset():
    """
    Returns an optimized queryset for book detail view
    """
    from .models import Book, Comment  # Import here to avoid circular imports
    
    return Book.public_objects.select_related(
        'author',
        'author__userprofile',
        'category'
    ).prefetch_related(
        Prefetch(
            'comments',
            queryset=Comment.objects.filter(parent=None).select_related(
                'user', 'user__userprofile'
            ).order_by('-created_at')[:20],
            to_attr='top_comments'
        ),
        'audiobooks',
        'translations'
    )


def apply_cursor_pagination(queryset, sort_type, cursor_data):
    """
    Apply cursor-based pagination filtering to a queryset
    
    Args:
        queryset: Django QuerySet to filter
        sort_type: Type of sorting ('trending', 'recent', 'popular', 'recommended')
        cursor_data: Dictionary containing cursor information
    
    Returns:
        Filtered queryset
    """
    if not cursor_data:
        return queryset
    
    try:
        if sort_type == 'trending':
            if 'views' in cursor_data and 'timestamp' in cursor_data and 'id' in cursor_data:
                timestamp_dt = timezone.datetime.fromtimestamp(
                    cursor_data['timestamp'], tz=timezone.get_current_timezone()
                )
                return queryset.filter(
                    Q(views__lt=cursor_data['views']) |
                    (Q(views=cursor_data['views']) & Q(created_at__lt=timestamp_dt)) |
                    (Q(views=cursor_data['views']) & Q(created_at=timestamp_dt) & Q(id__lt=cursor_data['id']))
                )
        
        elif sort_type == 'popular':
            if all(key in cursor_data for key in ['like_count', 'views', 'timestamp', 'id']):
                timestamp_dt = timezone.datetime.fromtimestamp(
                    cursor_data['timestamp'], tz=timezone.get_current_timezone()
                )
                return queryset.annotate(
                    like_count=Count('likes')
                ).filter(
                    Q(like_count__lt=cursor_data['like_count']) |
                    (Q(like_count=cursor_data['like_count']) & Q(views__lt=cursor_data['views'])) |
                    (Q(like_count=cursor_data['like_count']) & Q(views=cursor_data['views']) & Q(created_at__lt=timestamp_dt)) |
                    (Q(like_count=cursor_data['like_count']) & Q(views=cursor_data['views']) & Q(created_at=timestamp_dt) & Q(id__lt=cursor_data['id']))
                )
        
        else:  # recent and recommended
            if 'timestamp' in cursor_data and 'id' in cursor_data:
                timestamp_dt = timezone.datetime.fromtimestamp(
                    cursor_data['timestamp'], tz=timezone.get_current_timezone()
                )
                return queryset.filter(
                    Q(created_at__lt=timestamp_dt) |
                    (Q(created_at=timestamp_dt) & Q(id__lt=cursor_data['id']))
                )
    
    except (ValueError, TypeError):
        # If cursor data is invalid, return original queryset
        pass
    
    return queryset


def parse_cursor(cursor_string, sort_type):
    """
    Parse cursor string into dictionary based on sort type
    
    Args:
        cursor_string: String representation of cursor
        sort_type: Type of sorting
    
    Returns:
        Dictionary with parsed cursor data
    """
    if not cursor_string:
        return {}
    
    try:
        cursor_parts = cursor_string.split('_')
        
        if sort_type == 'trending':
            if len(cursor_parts) >= 3:
                return {
                    'views': int(cursor_parts[0]),
                    'timestamp': float(cursor_parts[1]),
                    'id': int(cursor_parts[2])
                }
        
        elif sort_type == 'popular':
            if len(cursor_parts) >= 4:
                return {
                    'like_count': int(cursor_parts[0]),
                    'views': int(cursor_parts[1]),
                    'timestamp': float(cursor_parts[2]),
                    'id': int(cursor_parts[3])
                }
        
        else:  # recent and recommended
            if len(cursor_parts) >= 2:
                return {
                    'timestamp': float(cursor_parts[0]),
                    'id': int(cursor_parts[1])
                }
    
    except (ValueError, IndexError):
        pass
    
    return {}


def generate_cursor(book, sort_type):
    """
    Generate cursor string for a book based on sort type
    
    Args:
        book: Book instance
        sort_type: Type of sorting
    
    Returns:
        String cursor
    """
    try:
        if sort_type == 'trending':
            return f"{book.views}_{book.created_at.timestamp()}_{book.id}"
        elif sort_type == 'popular':
            like_count = getattr(book, 'like_count', 0)
            return f"{like_count}_{book.views}_{book.created_at.timestamp()}_{book.id}"
        else:  # recent and recommended
            return f"{book.created_at.timestamp()}_{book.id}"
    except AttributeError:
        return ''


def get_cached_user_data(user_id, data_type, timeout=300):
    """
    Get cached user-specific data
    
    Args:
        user_id: User ID
        data_type: Type of data ('following', 'preferences', etc.)
        timeout: Cache timeout in seconds
    
    Returns:
        Cached data or None
    """
    cache_key = f"user_{data_type}_{user_id}"
    return cache.get(cache_key)


def set_cached_user_data(user_id, data_type, data, timeout=300):
    """
    Set cached user-specific data
    
    Args:
        user_id: User ID
        data_type: Type of data
        data: Data to cache
        timeout: Cache timeout in seconds
    """
    cache_key = f"user_{data_type}_{user_id}"
    cache.set(cache_key, data, timeout)


def get_book_suggestions(book, limit=15):
    """
    Get optimized book suggestions for a given book
    
    Args:
        book: Book instance
        limit: Maximum number of suggestions
    
    Returns:
        List of suggested books
    """
    cache_key = f"book_suggestions_{book.id}_{limit}"
    suggestions = cache.get(cache_key)
    
    if suggestions is None:
        suggestions_query = get_optimized_book_queryset().exclude(id=book.id)
        
        suggestions = []
        
        # Get suggestions by category first
        if book.category:
            suggestions.extend(list(suggestions_query.filter(
                category=book.category
            ).order_by('-views')[:limit//2]))
        
        # Add suggestions by author
        author_books = list(suggestions_query.filter(
            author=book.author
        ).exclude(
            id__in=[s.id for s in suggestions]
        ).order_by('-created_at')[:limit//3])
        suggestions.extend(author_books)
        
        # Fill remaining with popular books
        if len(suggestions) < limit:
            popular_books = list(suggestions_query.exclude(
                id__in=[s.id for s in suggestions]
            ).order_by('-views')[:limit - len(suggestions)])
            suggestions.extend(popular_books)
        
        cache.set(cache_key, suggestions, 1800)  # Cache for 30 minutes
    
    return suggestions[:limit]
