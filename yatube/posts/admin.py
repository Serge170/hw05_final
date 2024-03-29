from django.contrib import admin

from .models import Group, Post, Comment, Follow


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """ Добавляем в админ панель поле Group"."""
    list_display = ('pk', 'title', 'description', 'slug',)
    search_fields = ('title', 'description',)
    list_filter = ('title',)
    empty_value_display = '-пусто-'


@admin.register(Post)
class PostsAdmin(admin.ModelAdmin):
    """ Добавляем в админ панель поле Post"."""
    list_display = ('pk', 'text', 'created', 'author', 'group', 'image',)
    search_fields = ('text',)
    list_filter = ('created',)
    list_editable = ('group',)
    empty_value_display = '-пусто-'


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """ Добавляем в админ панель поле Comment"."""
    list_display = ('pk', 'text', 'created', 'author', 'post',)
    search_fields = ('text',)
    list_editable = ('author',)
    list_filter = ('author',)
    empty_value_display = '-пусто-'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """ Добавляем в админ панель поле Follow"."""
    list_display = ('pk', 'author', 'user',)
    list_editable = ('author',)
    search_fields = ('author',)
    empty_value_display = '-пусто-'
    list_filter = ('author',)
