from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from main.utils import AnalyticsService
from django.utils import timezone
from datetime import timedelta
import json

@login_required
@require_http_methods(["GET"])
def analytics_api(request):
    """
    API endpoint for real-time analytics data
    """
    days = int(request.GET.get('days', 30))
    content_type = request.GET.get('content_type')
    content_id = request.GET.get('content_id')
    
    try:
        # Get content object if specified
        content_obj = None
        if content_type and content_id:
            if content_type == 'books':
                from main.models import Book
                content_obj = Book.objects.get(id=content_id, author=request.user)
            elif content_type == 'news':
                from main.models import News
                content_obj = News.objects.get(id=content_id, author=request.user)
            elif content_type == 'travel':
                from main.models import TravelStory
                content_obj = TravelStory.objects.get(id=content_id, author=request.user)
        
        # Get analytics data
        views_analytics = AnalyticsService.get_content_views_analytics(
            user=request.user,
            content_type=content_type,
            content_obj=content_obj,
            days=days
        )
        
        follower_analytics = AnalyticsService.get_follower_analytics(
            user=request.user,
            days=days
        )
        
        response_data = {
            'success': True,
            'data': {
                'views': views_analytics,
                'followers': follower_analytics,
                'last_updated': timezone.now().isoformat()
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
@require_http_methods(["GET"])
def realtime_stats(request):
    """
    Get real-time statistics for live updates
    """
    try:
        # Calculate stats for last 24 hours
        now = timezone.now()
        yesterday = now - timedelta(days=1)
        
        from main.models import ObjView
        from accounts.models import UserFollow
        from django.db.models import Q, Count
        
        # Views in last 24 hours
        recent_views = ObjView.objects.filter(
            Q(book__author=request.user) | 
            Q(news__author=request.user) | 
            Q(travel_story__author=request.user),
            created_at__gte=yesterday
        ).count()
        
        # New followers in last 24 hours
        recent_followers = UserFollow.objects.filter(
            following=request.user,
            followed_at__gte=yesterday
        ).count()
        
        # Total stats
        total_followers = request.user.followers_users.count()
        total_views = ObjView.objects.filter(
            Q(book__author=request.user) | 
            Q(news__author=request.user) | 
            Q(travel_story__author=request.user)
        ).count()
        
        response_data = {
            'success': True,
            'data': {
                'recent_views_24h': recent_views,
                'recent_followers_24h': recent_followers,
                'total_followers': total_followers,
                'total_views': total_views,
                'timestamp': now.isoformat()
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
@require_http_methods(["GET"])
def content_performance_api(request):
    """
    API for content performance comparison
    """
    days = int(request.GET.get('days', 30))
    
    try:
        performance_data = AnalyticsService.get_content_performance_comparison(
            user=request.user,
            days=days
        )
        
        top_content = AnalyticsService.get_top_performing_content(
            user=request.user,
            days=days,
            limit=10
        )
        
        response_data = {
            'success': True,
            'data': {
                'performance_comparison': performance_data,
                'top_content': top_content,
                'period_days': days
            }
        }
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
