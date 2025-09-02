from django import forms
from django.forms import inlineformset_factory
from main.models import Book, News, NewsImage, AudioBook, Booktranslation, Category
from django_ckeditor_5.widgets import CKEditor5Widget

class BookUploadForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditor5Widget())
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate category choices from the database
        self.fields['category'].queryset = Category.objects.all()
        self.fields['category'].empty_label = "Select a category..."
    
    class Meta:
        model = Book
        fields = ['thumbnail', 'title', 'description','language', 'content', 'category']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-100 transition-all duration-300 text-lg placeholder-gray-400',
                'placeholder': 'Enter your captivating book title...'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-indigo-500 focus:ring-4 focus:ring-indigo-100 transition-all duration-300 placeholder-gray-400 resize-none',
                'placeholder': 'Write a compelling description that will attract readers...',
                'rows': 4
            }),
            'language': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-green-500 focus:ring-4 focus:ring-green-100 transition-all duration-300 placeholder-gray-400',
                'placeholder': 'e.g., English, Spanish, French...'
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:border-orange-500 focus:ring-4 focus:ring-orange-100 transition-all duration-300 bg-white'
            }),
        }

CATEGORY_CHOICES = [
    ('Politics', 'Politics'),
    ('Technology', 'Technology'),
    ('Business', 'Business'),
    ('Sports', 'Sports'),
    ('Health', 'Health'),
    ('Science', 'Science'),
]

class NewsForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditor5Widget())
    

    class Meta:
        model = News
        fields = ['title', 'category', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Enter a compelling headline'
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'rows': '12',
                'placeholder': 'Write your news content here...'
            }),
            'category': forms.RadioSelect(attrs={
                'class': 'hidden'  # We'll style the labels instead
            }),
        }

   

class NewsImageForm(forms.ModelForm):
    image = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'hidden',
            'accept': 'image/*',
            'multiple': False,  # Each form instance handles one file
        }),
        required=False
    )

    class Meta:
        model = NewsImage
        fields = ['image']

NewsImageFormSet = inlineformset_factory(
    News, 
    NewsImage, 
    form=NewsImageForm, 
    extra=5,
    max_num=5,
    can_delete=True
)

class AudioForm(forms.ModelForm):

    class Meta:
        model = AudioBook
        fields = ['language','narrator', 'file']
        widgets = {
            'language': forms.TextInput(attrs={'class': 'w-full border p-2 rounded mb-2'}),
            'narrator': forms.TextInput(attrs={'class': 'w-full border p-2 rounded mb-2'}),
            'file': forms.ClearableFileInput(attrs={'class': 'w-full border p-2 rounded' , 'accept': 'audio/*'})
        }

class TranslationForm(forms.ModelForm):
    translated_content = forms.CharField(widget=CKEditor5Widget())
    class Meta:
        model = Booktranslation
        fields = ['language', 'translated_title', 'translated_description', 'translated_content']
        widgets = {
            'language': forms.TextInput(attrs={'class': 'w-full border p-2 rounded mb-2'}),
            'translated_title': forms.TextInput(attrs={'class': 'w-full border p-2 rounded'}),
            'translated_description': forms.TextInput(attrs={'class': 'w-full border p-2 rounded'}),
            'translated_content': forms.Textarea(attrs={'class': 'w-full border p-2 rounded'}),
        }
