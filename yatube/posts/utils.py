from django.core.paginator import Paginator

# Количество постов отображаемых на странице
NUMBER_OF_POSTS: int = 10


def get_page(request, posts):
    """Шаблон Paginator."""
    paginator = Paginator(posts, NUMBER_OF_POSTS)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
