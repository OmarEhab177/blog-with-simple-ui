from django.contrib import admin
from django.contrib.admin.decorators import register
from .models import Post, Comment
# Register your models here.



class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status')
    list_editable = ('author', 'status')
    list_filter = ('status', 'crated', 'publish', 'author')
    fieldsets = (
        ('Title',{"fields": ['author', 'title', 'slug','tags']}),
        ('Content',{"fields": ['body', 'publish', 'status']}),
    )
    search_fields = ('title', 'body', 'author_id__username')
    prepopulated_fields = {'slug':('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_editable = ('active',)
    list_filter = ('created', 'active', 'updated')
    search_fields = ('name', 'email', 'body')
    # list_display_links = ('name', post',)



admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)