
from django.shortcuts import render

from assignments.models import About
from blogs.models import Blog, Category

def home(request):
    query = request.GET.get('q', '').strip()
    featured_posts=Blog.objects.filter(is_featured=True,status='Published').order_by('-updated_at')

    posts=Blog.objects.filter(is_featured=False,status='Published').order_by('-updated_at')
    if query:
        posts = Blog.objects.filter(status='Published', title__icontains=query).order_by('-updated_at')
        featured_posts = Blog.objects.none()
    try:
        about=About.objects.get()
    except:
        about=None
    context={
        
        'featured_posts':featured_posts,
        'posts':posts,
        'about':about,
        'query':query,
    }
    return render(request,'home.html',context)



