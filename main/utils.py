from django.utils import timezone
from datetime import timedelta
from main.models import BookView
from django.db.models import Count
from collections import defaultdict
from django.db.models.functions import TruncDate
from accounts.models import UserFollow

def get_last_n_days_data(model, n, user=None, book=None, formatted=False):
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
    if user and model!=BookView:
        print('1')
        filters["user"] = user
    elif user and model==BookView:
        filters["book__author"] = user
        print(2)
    if book:
        filters["book"] = book

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


def year_specific_data(model, year, user=None, book=None):
    filters = {
        "created_at__year": year
    }
    if user:
        filters["author"] = user
    
    if book:
        filters["book"] = book

    return model.objects.filter(**filters)

def log_book_view(book, user=None):
    BookView.objects.create(book=book, user=user)
    book.views = BookView.objects.filter(book=book).count()
    book.save()

def create_notification(user, message):
    from .models import Notification
    Notification.objects.create(
        user=user,
        content=message
    )

# utils/pdf_utils.py
from weasyprint import HTML, CSS
from django.template.loader import render_to_string
from io import BytesIO
import os

def generate_book_pdf(book):
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

    # Define custom page size (e.g., 270x480 pt for mobile-like view)
    custom_css = CSS(string='''
        @page {
            size: 270pt 480pt;
            margin: 20pt;
        }

        body {
            font-family: "Arial", sans-serif;
            font-size: 12pt;
            line-height: 1.4;
        }

        h1, h2, h3 {
            page-break-after: avoid;
        }
    ''')

    # Generate PDF
    HTML(string=html_string, base_url=os.getcwd()).write_pdf(pdf_buffer, stylesheets=[custom_css])
    pdf_buffer.seek(0)

    return pdf_buffer

