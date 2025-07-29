from django.contrib import admin
from .models import Book, Category,Collection,Comment,Notification,Rating,ReadingList,Report,Tag, News, NewsImage, History
from django.utils.html import format_html
from .models import TravelCategory, TravelStory, TravelImage
# Register your models here.

admin.site.register(Category)
admin.site.register(Collection)
admin.site.register(Comment)
admin.site.register(Notification)
admin.site.register(Rating)
admin.site.register(ReadingList)
admin.site.register(Report)
admin.site.register(Tag)
admin.site.register(History)


class NewsImageInline(admin.TabularInline):
    model = NewsImage
    extra = 1
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    inlines = [NewsImageInline]


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'likes_count', 'dislikes_count', 'views']


class TravelImageInline(admin.TabularInline):
    model = TravelImage
    extra = 1
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Preview'

class TravelStoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'country', 'published', 'created_at')
    list_filter = ('category', 'country', 'published', 'created_at')
    search_fields = ('title', 'story', 'location', 'pro_tips')
    inlines = [TravelImageInline]
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('thumbnail','title', 'category', 'story', 'published')
        }),
        ('Location Details', {
            'fields': ('country', 'location', 'latitude', 'longitude')
        }),
        ('Trip Information', {
            'fields': ('duration', 'season', 'budget_level')
        }),
        ('Additional Information', {
            'fields': ('pro_tips', 'tags')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

class TravelCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'story_count')
    search_fields = ('name',)
    
    def story_count(self, obj):
        return obj.stories.count()
    story_count.short_description = 'Stories'

class TravelImageAdmin(admin.ModelAdmin):
    list_display = ('travel_story', 'image_preview')
    list_filter = ('travel_story__category', 'travel_story__country')
    search_fields = ('travel_story__title',)
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px; max-width: 100px;" />', obj.image.url)
        return "-"
    image_preview.short_description = 'Preview'

admin.site.register(TravelCategory, TravelCategoryAdmin)
admin.site.register(TravelStory, TravelStoryAdmin)
admin.site.register(TravelImage, TravelImageAdmin)