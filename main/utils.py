from django.utils import timezone
from datetime import timedelta
from main.models import ObjView
from django.db.models import Count
from collections import defaultdict
from django.db.models.functions import TruncDate
from accounts.models import UserFollow
from dateutil.relativedelta import relativedelta

def get_last_n_days_data(model, n, user=None, book=None, news=None, travel_story=None, formatted=False):
    startdate = (timezone.now() - timedelta(days=n)).date()  # Ensure date only
    
    if model==UserFollow:
        filters = {'followed_at__date__gte': startdate}
        filters['following'] = user
        if book:
            filters['from_book'] = book
        if not formatted:
            return UserFollow.objects.filter(**filters)

        # Query & aggregate by date
        queryset = (
            UserFollow.objects.filter(**filters)
            .annotate(date=TruncDate("followed_at"))  # Truncate DateTime to Date
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )

        # Convert queryset to dict {date: count}
        data_dict = {entry["date"]: entry["count"] for entry in queryset}

        # Generate full date range with default count = 0
        result = []
        for i in range(n + 1):
            date = startdate + timedelta(days=i)
            result.append({"date": date.strftime("%Y-%m-%d"),"count" : data_dict.get(date, 0)})

        return result
    
    filters = {"created_at__date__gte": startdate}  # Filter by date only
    if user and model!=ObjView:
        filters["user"] = user
    elif user and model==ObjView:
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

    # Query & aggregate by date
    queryset = (
        model.objects.filter(**filters)
        .annotate(date=TruncDate("created_at"))  # Truncate DateTime to Date
        .values("date")
        .annotate(count=Count("id"))
        .order_by("date")
    )

    # Convert queryset to dict {date: count}
    data_dict = {entry["date"]: entry["count"] for entry in queryset}

    # Generate full date range with default count = 0
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
    ObjView.objects.create(book=book, user=user)

def log_news_view(news, user=None, session_key=None):
    ObjView.objects.create(news=news, user=user)

def log_travel_story_view(travel_story, user=None, session_key=None):
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

    # Define custom page size (e.g., 270x480 px for mobile-like view)
    custom_css = CSS(string=f'''
        @page {{
            size: {width_px}px {height_px}px;
            margin: 5px;
        }}

        body {{
            font-family: "Arial", sans-serif;
            font-size: 20px;
            line-height: 1.4;
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
