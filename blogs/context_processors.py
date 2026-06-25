from assignments.models import SocialLink
from blogs.models import Blog, Category


def get_categories(request):
    categories=Category.objects.all()
    blog_suggestions = Blog.objects.filter(status='Published').order_by('title').values_list('title', flat=True)
    return dict(categories=categories, blog_suggestions=blog_suggestions)

def get_social_links(request):
    social_links=SocialLink.objects.all()
    return dict(social_links=social_links)
