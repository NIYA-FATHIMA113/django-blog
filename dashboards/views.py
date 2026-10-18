from django.utils.text import slugify

from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from blogs.models import Blog, Category
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from dashboards.forms import AddUserForm, CategoryForm,BlogPostForm, EditUserForm


def staff_required(view_func):
    """Require an authenticated staff member for dashboard administration."""
    return login_required(
        user_passes_test(lambda user: user.is_staff, login_url='login')(view_func),
        login_url='login',
    )


def superuser_required(view_func):
    """Restrict user administration to superusers."""
    return login_required(
        user_passes_test(lambda user: user.is_superuser, login_url='login')(view_func),
        login_url='login',
    )


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
    category_count=Category.objects.all().count()
    blogs_count=Blog.objects.all().count()
    context={
        'category_count':category_count,
        'blogs_count':blogs_count
    }
    return render(request,'dashboard/dashboard.html',context)


@staff_required
def categories(request):
    return render(request,'dashboard/categories.html')
@staff_required
def add_category(request):
    if request.method=='POST':
        form=CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('categories')
    else:
        form=CategoryForm()
    context={
        'form':form
    }
    return render(request,'dashboard/add_category.html',context)

@staff_required
def edit_category(request,pk):
    category=get_object_or_404(Category,pk=pk)
    if request.method=='POST':
        form=CategoryForm(request.POST,instance=category)
        if form.is_valid():
            form.save()
            return redirect('categories')
        
    else:
        form=CategoryForm(instance=category)
    context={
        'form':form,
        'category':category
    }
    return render(request,'dashboard/edit_category.html',context)

@staff_required
def delete_category(request,pk):
    category=get_object_or_404(Category,pk=pk)
    category.delete()
    return redirect('categories')



@login_required(login_url='login')
def posts(request):
    posts = Blog.objects.all() if request.user.is_staff else Blog.objects.filter(author=request.user)
    context={
        'posts':posts
    }
    return render(request,'dashboard/posts.html',context)


@login_required(login_url='login')
def add_post(request):
    if request.method=='POST':
        form=BlogPostForm(request.POST,request.FILES)
        if form.is_valid():
            post=form.save(commit=False) #temporarily saving the form
            post.author=request.user
            post.slug = unique_blog_slug(form.cleaned_data['title'])
            post.save()
            return redirect('posts')
        
            

    else:
        form=BlogPostForm()
    context={
        'form':form
    }
    return render(request,'dashboard/add_post.html',context)

@login_required(login_url='login')
def edit_post(request, pk):
    post = get_object_or_404(Blog, pk=pk)
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
        form = BlogPostForm(instance=post)

    return render(request, 'dashboard/edit_post.html', {
        'form': form,
        'post': post,
    })


@login_required(login_url='login')
def delete_post(request,pk):
    post=get_object_or_404(Blog,pk=pk)
    if not request.user.is_staff and post.author != request.user:
        raise PermissionDenied
    post.delete()
    return redirect('posts')


@superuser_required
def users(request):
    users=User.objects.all()
    context={
        'users':users,
    }
    return render(request, 'dashboard/users.html', context)



@superuser_required
def add_user(request):
    if request.method=='POST':
        form=AddUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users')
    else:
        form=AddUserForm()
    
    context={
        'form':form,
    }
    return render(request,'dashboard/add_user.html',context)


@superuser_required
def edit_user(request,pk):
    user=get_object_or_404(User,pk=pk)
    if request.method=='POST':
        form=EditUserForm(request.POST,instance=user)
        if form.is_valid():
            form.save()
            return redirect('users')
    else:
        form=EditUserForm(instance=user)
    context={
        'form':form
    }

    return render(request,'dashboard/edit_user.html',context)

@superuser_required
def delete_user(request,pk):
    user=get_object_or_404(User,pk=pk)
    user.delete()
    return redirect('users')
