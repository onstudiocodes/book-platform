import random
import string
from io import BytesIO
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
from faker import Faker
from main.models import Book, Category

fake = Faker()
User = get_user_model()

def generate_random_title():
    return fake.sentence(nb_words=4).rstrip(".")

def generate_rich_html_content(min_paragraphs=20, max_paragraphs=40):
    content = ""
    total_paragraphs = random.randint(min_paragraphs, max_paragraphs)

    for i in range(total_paragraphs):
        if i % 8 == 0:
            content += f"<h2>{fake.sentence(nb_words=6)}</h2>"
        elif i % 9 == 0:
            content += "<ul>" + ''.join([f"<li>{fake.sentence()}</li>" for _ in range(3)]) + "</ul>"
        elif i % 11 == 0:
            content += f"<blockquote>{fake.text(max_nb_chars=250)}</blockquote>"
        else:
            content += f"<p>{fake.paragraph(nb_sentences=7)}</p>"

    return content

def generate_random_thumbnail(title):
    img = Image.new('RGB', (400, 600), color=(random.randint(10, 240), random.randint(10, 240), random.randint(10, 240)))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()

    draw.text((20, 270), title[:20], fill="white", font=font)

    thumb_io = BytesIO()
    img.save(thumb_io, format='JPEG')
    return ContentFile(thumb_io.getvalue(), name=f"{title.replace(' ', '_').lower()}.jpg")

class Command(BaseCommand):
    help = 'Create books with PIL thumbnails and long CKEditor content using Faker'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=5, help='Number of books to create')

    def handle(self, *args, **options):
        count = options['count']

        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR("No users found. Please create a user first."))
            return

        category, _ = Category.objects.get_or_create(name='Sample Category')

        for _ in range(count):
            title = generate_random_title()
            content = generate_rich_html_content()
            thumbnail = generate_random_thumbnail(title)

            book = Book.objects.create(
                title=title,
                description=fake.text(max_nb_chars=200),
                content=content,
                author=user,
                category=category,
                status='Public',
                language=random.choice(['English', 'Bangla', 'Spanish', 'Hindi']),
            )

            book.thumbnail.save(thumbnail.name, thumbnail, save=True)
            self.stdout.write(self.style.SUCCESS(f"✅ Created book: {book.title}"))
