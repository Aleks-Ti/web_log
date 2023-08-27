import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post

User = get_user_model()


def index(request):
    post_list = Post.objects.select_related(
        'author', 'group'
    ).prefetch_related('comments')
    paginator = Paginator(post_list, settings.COUNT_ENTRY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'posts/index.html',
        context={
            'page_obj': page_obj,
        },
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.groups.all()
    paginator = Paginator(post_list, settings.COUNT_ENTRY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'posts/group_list.html',
        {
            'page_obj': page_obj,
            'group': group,
        },
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    paginator = Paginator(posts, settings.COUNT_ENTRY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    follow = False
    if request.user.is_authenticated and request.user != author:
        follow = Follow.objects.filter(
            user=request.user,
            author=author,
        ).exists()

    return render(
        request,
        'posts/profile.html',
        context={
            'page_obj': page_obj,
            'author': author,
            'following': follow,
        },
    )


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author', 'group'),
        id=post_id,
    )
    form = CommentForm(request.POST or None)
    if request.user.id == post.author.id:
        return render(
            request,
            'posts/post_detail.html',
            context={
                'post': post,
                'form': form,
                'edit_post': True,
            },
        )

    return render(
        request,
        'posts/post_detail.html',
        context={
            'post': post,
            'form': form,
        },
    )


@login_required
def post_create(request):
    form = PostForm(request.POST, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})

    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', post.author)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if request.user == post.author:
        if form.is_valid():
            form.save()
            return redirect(
                'posts:post_detail',
                post_id,
            )

    return render(
        request,
        'posts/create_post.html',
        {
            'post': post,
            'form': form,
            'is_edit': True,
        },
    )


@login_required
def add_comment(request, post_id):
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = get_object_or_404(Post, id=post_id)
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(
        author__following__user=request.user,
    ).select_related('author', 'group')
    paginator = Paginator(post_list, settings.COUNT_ENTRY)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'posts/follow.html',
        context={
            'page_obj': page_obj,
        },
    )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
        return redirect('posts:profile', author)
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request, username):
    get_object_or_404(
        Follow,
        user=request.user,
        author__username=username,
    ).delete()
    return redirect('posts:profile', username)


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)
    back_point = request.META.get('HTTP_REFERER')
    post.delete()
    if post.image:
        if os.path.isfile(post.image.path):
            os.remove(post.image.path)
    if (f'posts/{post_id}/') not in back_point:
        cache.clear()
        return redirect(back_point)
    return redirect(
        'posts:profile',
        username=request.user.username,
    )
