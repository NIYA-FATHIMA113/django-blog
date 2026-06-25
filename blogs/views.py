from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse

from blogs.models import Blog, Category
# Create your views here.
from django.db.models import Q
def posts_by_category(request,category_id):
    posts=Blog.objects.filter(status='Published',category_id=category_id)



    category=get_object_or_404(Category,pk=category_id)
   


    context={
        'posts':posts,
        'category':category,

    }
    return render(request,'posts_by_category.html',context)

def blogs(request,slug):
    single_blog=get_object_or_404(Blog,slug=slug,status='Published')
    categories=Category.objects.all()
    context={
        'single_blog':single_blog,
        'categories':categories,
    }
    return render(request,'blogs.html',context)


def search(request):
    keyword=request.GET.get('q')
    blogs=Blog.objects.filter(Q(title__icontains=keyword )| Q(blog_body__icontains=keyword)| Q(short_description__icontains=keyword),status='Published')
    context={
        'blogs':blogs,
        'keyword':keyword
    }
    return render(request,'search.html',context)
