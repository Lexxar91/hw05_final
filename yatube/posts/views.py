from django.conf import settings
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.core.cache import cache
from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow


def index(request):
    posts_cache = cache.get('index_page')
    if posts_cache is None:
        posts_cache = Post.objects.select_related(
            'group',
            'author').order_by('-pub_date')
        cache.set('index_page', posts_cache, timeout=20)
    paginator = Paginator(posts_cache, settings.PAG_VAL)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {'posts': posts_cache, 'page_obj': page_obj}
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, settings.PAG_VAL)
    page_obj = paginator.get_page(request.GET.get('page'))
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post = author.posts.all()
    paginator = Paginator(post, settings.PAG_VAL)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            author=author,
            user=request.user).exists()

    context = {
        'author': author,
        'posts_sum': author.posts.count(),
        'page_obj': page_obj,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    posts_count = post.author.posts.count()
    form = CommentForm(request.POST or None)
    comments = post.comments.filter(post_id=post.id)
    context = {
        'post': post,
        'comments': comments,
        'post_count': posts_count,
        'form': form
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', username=request.user.username)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if request.method == 'POST':
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('posts:post_detail', post_id=post.id)
        return render(request,
                      'posts/create_post.html',
                      {'form': form},
                      )
    context = {
        'form': form,
        'post': post,
        'title': 'Редактировать пост',
        'is_edit': True
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    user = request.user
    post_list = Post.objects.filter(
        author__following__user=user)
    paginator = Paginator(post_list, settings.PAG_VAL)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {'posts': post_list, 'page_obj': page_obj}
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    if author != user:
        Follow.objects.get_or_create(user=user, author=author)
    return redirect('posts:profile', username=(author.username))


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(User, username=username)
    unfollow = Follow.objects.filter(user=user, author=author)
    if unfollow.exists():
        unfollow.delete()
    return redirect('posts:profile', username=(author.username))
