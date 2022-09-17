from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page
from posts.utils import get_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User

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


@cache_page(20, key_prefix='index_page')
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
    comments = post.comments.all()
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
    """ Профиль автора."""
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('group')
    page_obj = get_page(request, post_list)
    following = False
    if request.user.is_authenticated:
        following = request.user.follower.filter(
            author=User.objects.get(username=author)).count()
    context = {'author': author,
               'page_obj': page_obj,
               'posts_count': post_list.count,
               'following': following,
               }
    return render(request, 'posts/profile.html', context)


@login_required
def follow_index(request):
    """ Информация о текущем пользователе."""
    user = request.user
    post_list = Post.objects.filter(author__following__user=request.user)
    page_obj = get_page(request, post_list)
    context = {'username': user,
               'page_obj': page_obj,
               }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """ Подписаться на автора."""
    user = request.user
    author = get_object_or_404(User, username=username)
    if user != author:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """ Дизлайк, отписка."""
    user = request.user
    author = get_object_or_404(User, username=username)
    follow_to_delete = get_object_or_404(
        Follow,
        user=user,
        author=author
    )
    follow_to_delete.delete()
    return redirect('posts:profile', username=username)
