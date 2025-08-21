from django.utils import timezone
from datetime import timedelta, date
from main.models import ObjView
from django.db.models import Count, Sum, Avg, Max, Min, Q
from collections import defaultdict
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncYear
from accounts.models import UserFollow
from dateutil.relativedelta import relativedelta
from django.core.cache import cache
import hashlib

class AnalyticsService:
    """
    Comprehensive analytics service for author content performance
    """
    
    @staticmethod
    def _get_cache_key(prefix, **kwargs):
        """Generate cache key based on parameters"""
        key_parts = [prefix]
        for k, v in sorted(kwargs.items()):
            if v is not None:
                key_parts.append(f"{k}:{v}")
        return hashlib.md5('_'.join(map(str, key_parts)).encode()).hexdigest()
    
    @staticmethod
    def _get_date_range(days=None, start_date=None, end_date=None):
        """Get date range for analytics"""
        if start_date and end_date:
            return start_date, end_date
        
        end_date = timezone.now().date()
        if days:
            start_date = end_date - timedelta(days=days)
        else:
            start_date = end_date - timedelta(days=30)  # Default 30 days
        
        return start_date, end_date
    
    @staticmethod
    def _fill_missing_dates(data_dict, start_date, end_date, date_format="%Y-%m-%d"):
        """Fill missing dates with zero values"""
        result = []
        current_date = start_date
        
        while current_date <= end_date:
            result.append({
                'date': current_date.strftime(date_format),
                'count': data_dict.get(current_date, 0)
            })
            current_date += timedelta(days=1)
        
        return result
    
    @staticmethod
    def get_content_views_analytics(user, content_type=None, content_obj=None, days=30, 
                                   start_date=None, end_date=None, group_by='day'):
        """
        Get comprehensive view analytics for author content
        """
        start_date, end_date = AnalyticsService._get_date_range(days, start_date, end_date)
        
        # Build base query
        base_filters = {
            'created_at__date__gte': start_date,
            'created_at__date__lte': end_date
        }
        
        # Content type filtering
        if content_obj:
            if hasattr(content_obj, 'author') and content_obj.author == user:
                if content_type == 'books':
                    base_filters['book'] = content_obj
                elif content_type == 'news':
                    base_filters['news'] = content_obj
                elif content_type == 'travel':
                    base_filters['travel_story'] = content_obj
        else:
            # All content by user
            base_filters['Q_filter'] = (
                Q(book__author=user) | 
                Q(news__author=user) | 
                Q(travel_story__author=user)
            )
        
        # Get queryset
        queryset = ObjView.objects.filter(**{k: v for k, v in base_filters.items() if k != 'Q_filter'})
        if 'Q_filter' in base_filters:
            queryset = queryset.filter(base_filters['Q_filter'])
        
        # Group by time period
        if group_by == 'day':
            trunc_func = TruncDate('created_at')
        elif group_by == 'week':
            trunc_func = TruncWeek('created_at')
        elif group_by == 'month':
            trunc_func = TruncMonth('created_at')
        else:
            trunc_func = TruncDate('created_at')
        
        # Aggregate data
        time_series = (
            queryset
            .annotate(period=trunc_func)
            .values('period')
            .annotate(
                views=Count('id'),
                unique_viewers=Count('user', distinct=True)
            )
            .order_by('period')
        )
        
        # Convert to dict and fill missing dates
        data_dict = {entry['period']: entry['views'] for entry in time_series}
        unique_viewers_dict = {entry['period']: entry['unique_viewers'] for entry in time_series}
        
        time_series_data = AnalyticsService._fill_missing_dates(data_dict, start_date, end_date)
        unique_viewers_data = AnalyticsService._fill_missing_dates(unique_viewers_dict, start_date, end_date)
        
        # Calculate summary statistics
        total_views = queryset.count()
        unique_viewers_total = queryset.values('user').distinct().count()
        avg_daily_views = total_views / max((end_date - start_date).days, 1)
        
        return {
            'time_series': time_series_data,
            'unique_viewers_series': unique_viewers_data,
            'summary': {
                'total_views': total_views,
                'unique_viewers': unique_viewers_total,
                'avg_daily_views': round(avg_daily_views, 2),
                'date_range': {
                    'start': start_date,
                    'end': end_date,
                    'days': (end_date - start_date).days
                }
            }
        }
    
    @staticmethod
    def get_follower_analytics(user, days=30, start_date=None, end_date=None):
        """
        Get follower growth analytics
        """
        start_date, end_date = AnalyticsService._get_date_range(days, start_date, end_date)
        
        # Get follower data
        followers_queryset = UserFollow.objects.filter(
            following=user,
            followed_at__date__gte=start_date,
            followed_at__date__lte=end_date
        )
        
        # Time series data
        time_series = (
            followers_queryset
            .annotate(date=TruncDate('followed_at'))
            .values('date')
            .annotate(new_followers=Count('id'))
            .order_by('date')
        )
        
        data_dict = {entry['date']: entry['new_followers'] for entry in time_series}
        time_series_data = AnalyticsService._fill_missing_dates(data_dict, start_date, end_date)
        
        # Calculate cumulative followers over time
        cumulative_data = []
        running_total = user.followers_users.filter(followed_at__date__lt=start_date).count()
        
        for entry in time_series_data:
            running_total += entry['count']
            cumulative_data.append({
                'date': entry['date'],
                'total_followers': running_total
            })
        
        return {
            'new_followers_series': time_series_data,
            'cumulative_followers_series': cumulative_data,
            'summary': {
                'total_followers': user.followers_users.count(),
                'new_followers_period': sum(entry['count'] for entry in time_series_data),
                'growth_rate': round((sum(entry['count'] for entry in time_series_data) / 
                                   max(running_total - sum(entry['count'] for entry in time_series_data), 1)) * 100, 2)
            }
        }
    
    @staticmethod
    def get_content_performance_comparison(user, days=30):
        """
        Compare performance across different content types
        """
        start_date, end_date = AnalyticsService._get_date_range(days)
        
        content_stats = {}
        
                # Books performance
        books_views = ObjView.objects.filter(
            book__author=user,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        content_stats['books'] = {
            'views': books_views.count(),
            'unique_viewers': books_views.values('user').distinct().count(),
            'content_count': user.books.count()
        }
        
        # News performance
        news_views = ObjView.objects.filter(
            news__author=user,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        content_stats['news'] = {
            'views': news_views.count(),
            'unique_viewers': news_views.values('user').distinct().count(),
            'content_count': user.news.count()
        }
        
        # Travel stories performance
        travel_views = ObjView.objects.filter(
            travel_story__author=user,
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        content_stats['travel'] = {
            'views': travel_views.count(),
            'unique_viewers': travel_views.values('user').distinct().count(),
            'content_count': user.travelstory_set.count()
        }
        
        return content_stats
    
    @staticmethod
    def get_top_performing_content(user, content_type=None, days=30, limit=10):
        """
        Get top performing content by views
        """
        start_date, end_date = AnalyticsService._get_date_range(days)
        
        results = {}
        
        if not content_type or content_type == 'books':
            books = (
                user.books.annotate(
                    period_views=Count(
                        'book_views',
                        filter=Q(
                            book_views__created_at__date__gte=start_date,
                            book_views__created_at__date__lte=end_date
                        )
                    )
                )
                .order_by('-period_views')[:limit]
            )
            results['books'] = [
                {
                    'id': book.id,
                    'title': book.title,
                    'slug': book.slug,
                    'views': book.period_views,
                    'total_views': book.views
                }
                for book in books
            ]
        
        if not content_type or content_type == 'news':
            news = (
                user.news.annotate(
                    period_views=Count(
                        'news_views',
                        filter=Q(
                            news_views__created_at__date__gte=start_date,
                            news_views__created_at__date__lte=end_date
                        )
                    )
                )
                .order_by('-period_views')[:limit]
            )
            results['news'] = [
                {
                    'id': article.id,
                    'title': article.title,
                    'slug': article.slug,
                    'views': article.period_views,
                    'total_views': article.views
                }
                for article in news
            ]
        
        if not content_type or content_type == 'travel':
            travel_stories = (
                user.travelstory_set.annotate(
                    period_views=Count(
                        'travel_story_views',
                        filter=Q(
                            travel_story_views__created_at__date__gte=start_date,
                            travel_story_views__created_at__date__lte=end_date
                        )
                    )
                )
                .order_by('-period_views')[:limit]
            )
            results['travel'] = [
                {
                    'id': story.id,
                    'title': story.title,
                    'slug': story.slug,
                    'views': story.period_views,
                    'total_views': story.period_views  # TravelStory doesn't have a views field, use period views
                }
                for story in travel_stories
            ]
        
        return results

# Legacy function for backward compatibility
def get_last_n_days_data(model, n, user=None, book=None, news=None, travel_story=None, formatted=False):
    """Legacy function - use AnalyticsService for new implementations"""
    startdate = (timezone.now() - timedelta(days=n)).date()
    
    if model == UserFollow:
        filters = {'followed_at__date__gte': startdate}
        filters['following'] = user
        if book:
            filters['from_book'] = book
        if not formatted:
            return UserFollow.objects.filter(**filters)

        queryset = (
            UserFollow.objects.filter(**filters)
            .annotate(date=TruncDate("followed_at"))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        data_dict = {entry["date"]: entry["count"] for entry in queryset}
        result = []
        for i in range(n + 1):
            date = startdate + timedelta(days=i)
            result.append({"date": date.strftime("%Y-%m-%d"), "count": data_dict.get(date, 0)})

        return result
    
    filters = {"created_at__date__gte": startdate}
    if user and model != ObjView:
        filters["user"] = user
    elif user and model == ObjView:
        if book:
            filters["book__author"] = user
        elif news:
            filters["news__author"] = user
        elif travel_story:
            filters["travel_story__author"] = user
    if book:
        filters["book"] = book
    if news:
        filters['news'] = news
    if travel_story:
        filters['travel_story'] = travel_story

    if not formatted:
        return model.objects.filter(**filters)

    queryset = (
        model.objects.filter(**filters)
        .annotate(date=TruncDate("created_at"))
        .values("date")
        .annotate(count=Count("id"))
        .order_by("date")
    )

    data_dict = {entry["date"]: entry["count"] for entry in queryset}
    result = []
    for i in range(n + 1):
        date = startdate + timedelta(days=i)
        result.append({'date': date.strftime("%Y-%m-%d"), 'count': data_dict.get(date, 0)})

    return result


def year_specific_data(model, year, user=None, book=None, news=None, travel_story=None):
    filters = {
        "created_at__year": year
    }
    if user:
        filters["author"] = user
    
    if book:
        filters["book"] = book
    if news:
        filters["news"] = news
    if travel_story:
        filters["travel_story"] = travel_story

    return model.objects.filter(**filters)

def log_book_view(book, user=None, session_key=None):
    """
    Log a book view by creating an ObjView record and incrementing the book's view count
    """
    # Create the detailed view record
    ObjView.objects.create(book=book, user=user)
    
    # Increment the book's view counter
    # Using F() to avoid race conditions and make it atomic
    from django.db.models import F
    book.__class__.objects.filter(id=book.id).update(views=F('views') + 1)
    
    # Refresh the book instance to get the updated view count
    book.refresh_from_db(fields=['views'])

def log_news_view(news, user=None):
    """
    Log a news view by creating an ObjView record and incrementing the news's view count
    """
    ObjView.objects.create(news=news, user=user)
    
    # Increment the news view counter
    from django.db.models import F
    news.__class__.objects.filter(id=news.id).update(views=F('views') + 1)
    
    # Refresh the news instance to get the updated view count
    news.refresh_from_db(fields=['views'])

def log_travel_story_view(travel_story, user=None):
    """
    Log a travel story view by creating an ObjView record
    """
    ObjView.objects.create(travel_story=travel_story, user=user)

def create_notification(user, message):
    from .models import Notification
    Notification.objects.create(
        user=user,
        content=message
    )

# pdf_utils.py
from weasyprint import HTML, CSS
from django.template.loader import render_to_string
from io import BytesIO
import os

def generate_book_pdf(book, width_px=270, height_px=480):
    """
    Generate a PDF file for a given Book instance.
    Returns a BytesIO stream containing the PDF.
    """
    # Render HTML template with book content
    html_string = render_to_string("components/pdf_template.html", {
        "book": book,
    })

    # Create in-memory buffer
    pdf_buffer = BytesIO()

    # Define custom page size and justified text
    custom_css = CSS(string=f'''
        @page {{
            size: {width_px}px {height_px}px;
            margin: 5px;
        }}

        body {{
            font-family: "Arial", sans-serif;
            font-size: 20px;
            line-height: 1.4;
            text-align: justify;
        }}

        h1, h2, h3 {{
            page-break-after: avoid;
        }}
    ''')

    # Generate PDF
    HTML(string=html_string, base_url=os.getcwd()).write_pdf(pdf_buffer, stylesheets=[custom_css])
    pdf_buffer.seek(0)

    return pdf_buffer

def time_since_custom(dt):
    """
    Returns a human-readable time difference like:
    'just now', '5 minutes ago', '3 hours ago', '2 days ago', '1 month ago', '2 years ago'
    """
    if not dt:
        return ""

    current_time = timezone.now()
    diff = relativedelta(current_time, dt)

    if diff.years > 0:
        return f"{diff.years} year{'s' if diff.years > 1 else ''} ago"
    elif diff.months > 0:
        return f"{diff.months} month{'s' if diff.months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.hours > 0:
        return f"{diff.hours} hour{'s' if diff.hours > 1 else ''} ago"
    elif diff.minutes > 0:
        return f"{diff.minutes} minute{'s' if diff.minutes > 1 else ''} ago"
    else:
        return "just now"
