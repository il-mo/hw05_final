from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_GET

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


@require_GET
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
        'posts/group.html',
        {
            'group': group,
            'page': page,
        },
    )


@require_GET
def index(request):
    post_list = Post.objects.all()

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
        'index.html',
        {
            'page': page,
        },
    )


@require_http_methods(['GET', 'POST'])
@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)

    if not form.is_valid():
        return render(
            request,
            'posts/new_post.html',
            {
                'form': form,
            },
        )

    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('index')


@require_GET
def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.filter(author=author)

    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    count_post = posts.count()

    if request.user.is_authenticated:
        following = request.user.follower.filter(author=author).exists()
    else:
        following = False

    return render(
        request,
        'profile.html',
        {
            'page': page,
            'author': author,
            'count_post': count_post,
            'following': following,
        },
    )


@require_GET
def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    author = post.author
    post_count = author.posts.count()
    form = CommentForm(request.POST or None)

    context = {
        'post': post,
        'comments': comments,
        'author': author,
        'post_count': post_count,
        'post_id': post_id,
        'form': form,
    }
    return render(request, 'posts/post_view.html', context)


@require_http_methods(['GET', 'POST'])
@login_required
def post_edit(request, username, post_id):
    post_changed = get_object_or_404(
        Post, pk=post_id, author__username=username
    )
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post_changed,
    )

    if post_changed.author != request.user:
        return redirect('post', username, post_id)

    if not form.is_valid():
        return render(
            request,
            'posts/new_post.html',
            {
                'form': form,
                'post_changed': post_changed,
            },
        )

    form.save()
    return redirect('post', username, post_id)


@require_http_methods(['GET', 'POST'])
@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)

    if request.method == 'GET' or not form.is_valid():
        return redirect('post', username, post_id)

    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    comment.save()

    return redirect('post', username, post_id)


@require_GET
@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)

    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    return render(
        request,
        'posts/follow.html',
        {
            'page': page,
        },
    )


@require_GET
@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)

    if request.user != author:
        try:
            Follow.objects.get(
                user=request.user, author=author
            )
        except Follow.DoesNotExist:
            Follow.objects.create(user=request.user, author=author)

    return redirect('profile', username=username)


@require_GET
@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(
        user=request.user, author=author
    ).delete()

    return redirect('profile', username=username)
