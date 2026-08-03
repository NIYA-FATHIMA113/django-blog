"""
URL configuration for blog_main project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings

import dashboards
from . import views
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.views.static import serve
from blogs import views as Blogsview
urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home,name="home"),
    path('category/',include('blogs.urls')),
    path('blogs/search/',Blogsview.search,name='search'),
    path('register/',views.register,name='register'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
        
    path('blogSs/<slug:slug>/',Blogsview.blogs,name='blogs'),
    path('dashboard/',include('dashboards.urls')),
    
]

# The project uses local media while no hosted database is configured.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
elif settings.IS_LOCAL_DEVELOPMENT:
    urlpatterns += [
        path('media/<path:path>', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
