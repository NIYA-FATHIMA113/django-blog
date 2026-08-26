from unicodedata import category
from webbrowser import get
from django.utils.text import slugify

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.template import context

from blogs.models import Blog, Category
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from dashboards.forms import AddUserForm, CategoryForm, BlogPostForm, EditUserForm, ProfileForm, ProfileUserForm
from assignments.models import Profile


def require_staff(user):
    if not user.is_authenticated or not user.is_staff:
        raise PermissionDenied


def require_authenticated(user):
    if not user.is_authenticated:
        raise PermissionDenied


def require_superuser(user):
    if not user.is_authenticated or not (user.is_superuser or user.groups.filter(name='Manager').exists()):
        raise PermissionDenied


def unique_blog_slug(title, post_id=None):
    """Return a URL-safe slug that does not clash with another blog post."""
    base_slug = slugify(title) or 'post'
    slug = base_slug
    suffix = 2

    matching_posts = Blog.objects.exclude(pk=post_id) if post_id else Blog.objects.all()
    while matching_posts.filter(slug=slug).exists():
        slug = f'{base_slug}-{suffix}'
        suffix += 1

    return slug


# Create your views here.
@login_required(login_url='login')
def dashboard(request):
    require_authenticated(request.user)
    category_count=Category.objects.all().count() if request.user.is_staff else 0
    blogs_count=Blog.objects.count() if request.user.is_staff else Blog.objects.filter(author=request.user).count()
    context={
        'category_count':category_count,
        'blogs_count':blogs_count
    }
    return render(request,'dashboard/dashboard.html',context)


@login_required(login_url='login')
def profile(request):
    user_profile, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user_form = ProfileUserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
    else:
        user_form = ProfileUserForm(instance=request.user)
        profile_form = ProfileForm(instance=user_profile)
    return render(request, 'dashboard/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile_user': request.user,
    })


def categories(request):
    require_staff(request.user)
    return render(request,'dashboard/categories.html')
def add_category(request):
    require_staff(request.user)
    if request.method=='POST':
        form=CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories')
    form=CategoryForm()
    context={
        'form':form
    }
    return render(request,'dashboard/add_category.html',context)

def edit_category(request,pk):
    require_staff(request.user)
    category=get_object_or_404(Category,pk=pk)
    if request.method=='POST':
        form=CategoryForm(request.POST,instance=category)
        if form.is_valid():
            form.save()
            return redirect('categories')
        
    form=CategoryForm(instance=category)
    context={
        'form':form,
        'category':category
    }
    return render(request,'dashboard/edit_category.html',context)

def delete_category(request,pk):
    require_staff(request.user)
    category=get_object_or_404(Category,pk=pk)
    category.delete()
    return redirect('categories')



def posts(request):
    require_authenticated(request.user)
    posts=Blog.objects.all() if request.user.is_staff else Blog.objects.filter(author=request.user)
    context={
        'posts':posts
    }
    return render(request,'dashboard/posts.html',context)


def add_post(request):
    require_authenticated(request.user)
    if request.method=='POST':
        form=BlogPostForm(request.POST,request.FILES)
        if form.is_valid():
            post=form.save(commit=False) #temporarily saving the form
            post.author=request.user
            post.slug = unique_blog_slug(form.cleaned_data['title'])
            post.save()
            return redirect('posts')
        
            

    form=BlogPostForm()
    context={
        'form':form
    }
    return render(request,'dashboard/add_post.html',context)

def edit_post(request, pk):
    post = get_object_or_404(Blog, pk=pk)
    require_authenticated(request.user)
    if not request.user.is_staff and post.author != request.user:
        raise PermissionDenied

    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)

        if form.is_valid():
            post = form.save()
            post.slug = unique_blog_slug(form.cleaned_data['title'], post.id)
            post.save()
            return redirect('posts')
        else:
            print(form.errors)   # <-- Add this

    else:
        form = BlogPostForm(instance=post)

    return render(request, 'dashboard/edit_post.html', {
        'form': form,
        'post': post,
    })


def delete_post(request,pk):
    require_authenticated(request.user)
    post=get_object_or_404(Blog,pk=pk)
    if not request.user.is_staff and post.author != request.user:
        raise PermissionDenied
    post.delete()
    return redirect('posts')


@login_required(login_url='login')
def users(request):
    require_superuser(request.user)
    users=User.objects.all()
    context={
        'users':users,
    }
    return render(request, 'dashboard/users.html', context)



def add_user(request):
    require_superuser(request.user)
    if request.method=='POST':
        form=AddUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users')
        else:
            print(form.errors)
    else:
        form=AddUserForm()
    
    context={
        'form':form,
    }
    return render(request,'dashboard/add_user.html',context)


def edit_user(request,pk):
    require_superuser(request.user)
    user=get_object_or_404(User,pk=pk)
    if request.method=='POST':
        form=EditUserForm(request.POST,instance=user)
        if form.is_valid():
            form.save()
            return redirect('users')
    form=EditUserForm(instance=user)
    context={
        'form':form
    }

    return render(request,'dashboard/edit_user.html',context)

def delete_user(request,pk):
    require_superuser(request.user)
    user=get_object_or_404(User,pk=pk)
    user.delete()
    return redirect('users')
