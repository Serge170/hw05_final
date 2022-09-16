from django.contrib import admin

from .models import *

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('pk', 'title', 'description', 'slug',)
    search_fields = ('title', 'description',)
    list_filter = ('title',)
    empty_value_display = '-пусто-'


@admin.register(Post)
class PostsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'created', 'author', 'group',)
    search_fields = ('text',)
    list_filter = ('created',)
    list_editable = ('group',)
    empty_value_display = '-пусто-'


