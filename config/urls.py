"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from catalog.views import debug_media
urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/admin/catalog/", include("catalog.admin_api.urls")),
    path("api/admin/users/", include("user.admin_api.urls")),
    path("debug-media/", debug_media),
    path("api/user/", include("user.urls")),
    path("api/", include("user.urls")),
    path('api/catalog/', include('catalog.urls')), 
    path("api/user/", include("user.urls")),
    path("api/admin/", include("user.admin_api.urls")),

]
# ✅ ALWAYS serve media on Render
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)