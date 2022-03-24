from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.views.decorators.cache import cache_page
from posts.forms import PostForm, CommentForm
from posts.models import Group, Post, User, Follow


@cache_page(20)
def index(request):
    title = 'Последние обновления на сайте'
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.NUM_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'title': title,
        'page_obj': page_obj, }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    paginator = Paginator(posts, settings.NUM_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj, }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    name = author.get_full_name()
    post_list = author.posts.all()
    count = post_list.count()
    paginator = Paginator(post_list, settings.NUM_POSTS)
    page_number = request.GET.get('page')
    following = False
    authenticated = request.user.is_authenticated
    if authenticated and Follow.objects.filter(author=request.user,
                                               user=author):
        following = True
    page_obj = paginator.get_page(page_number)
    context = {
        'author': author,
        'count': count,
        'name': name,
        'page_obj': page_obj,
        'following': following,
        'authenticated': authenticated, }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    group = post.group
    form = CommentForm(request.POST)
    comments = post.comments.all()
    context = {
        'group': group,
        'post': post,
        'form': form,
        'comments': comments, }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    groups = Group.objects.all()
    if request.method != "POST":
        form = PostForm()
        return render(
            request,
            'posts/create_post.html',
            {'form': form, 'groups': groups})
    form = PostForm(request.POST, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect(
        'posts:profile',
        post.author)


@login_required
def post_edit(request, post_id):
    groups = Group.objects.all()
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    form = PostForm(instance=post)
    context = {
        'is_edit': True,
        'post': post,
        'form': form,
        'groups': groups, }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    authors_id = request.user.follower.all().values_list('author', flat=True)
    post_list = Post.objects.filter(author_id__in=authors_id)
    paginator = Paginator(post_list, settings.NUM_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj, }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    if user_to_follow != request.user:
        Follow.objects.get_or_create(user=request.user, author=user_to_follow)
    return redirect('posts:profile', username)


@login_required
def profile_unfollow(request, username):
    user_to_unfollow = User.objects.get(username=username)
    entry = Follow.objects.filter(user=request.user, author=user_to_unfollow)
    entry.delete()
    return redirect('posts:profile', username)
