from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from posts.utils import get_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User

NUMBER_OF_POSTS = 10


def group_posts(request, slug):
    """ Страница со списком постов."""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = get_page(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


@cache_page(5, key_prefix='index_page')
def index(request):
    """Главная страница."""
    posts = Post.objects.all()
    page_obj = get_page(request, posts)
    context = {
        'page_obj': page_obj
    }
    return render(request, 'posts/index.html', context)


def post_detail(request, post_id):
    """Детали по посту."""
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm()
    comments = Comment.objects.filter(post=post)
    context = {
        'posts': post,
        'form': form,
        'comments': comments
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    """ Функцию для обработки отправленного комментария."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def post_create(request):
    """Создание нового поста."""
    form = PostForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """Редактирование текущего поста."""
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post = form.save()
        return redirect('posts:post_detail', post_id=post.id)
    context = {
        'form': form,
        'post': post,
        'is_edit': True
    }
    return render(request, template, context)


def profile(request, username):
    """Профиль автора."""
    template = 'posts/profile.html'
    user = get_object_or_404(User, username=username)
    following = Follow.objects.filter(
        author__following__user=request.user).exists()
    post_count = Post.objects.count()
    Post.objects.filter(
        author__following__user=user).exists()  
    profile_list = user.posts.select_related('author', 'group')
    paginator = Paginator(profile_list, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'author': user,
        'page_obj': page_obj,
        'post_count': post_count,
        'following': following,
    }
    return render(request, template, context)

@login_required
def follow_index(request):
    # информация о текущем пользователе доступна в переменной request.user
    # ...
    user = request.user
    author_pk_list = user.follower.all().values_list('author', flat=True)
    post_list = Post.objects.filter(author__in=author_pk_list)
    paginator = Paginator(post_list, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'username': user,
               'page_obj': page_obj,
               }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    user = request.user
    author = get_object_or_404(User, username=username)
    if user != author:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    # Дизлайк, отписка
    user = request.user
    author = get_object_or_404(User, username=username)
    follow_to_delete = get_object_or_404(
        Follow,
        user=user,
        author=author
    )
    follow_to_delete.delete()
    return redirect('posts:profile', username=username)