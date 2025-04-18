"""
URL configuration for web_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path
import api.views
app_name = 'Companies'

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/paper/search/paperIds", api.views.FindPaperByPaperIds),
    path("api/paper/search/doi", api.views.FindPaperByDoi),
    path("api/paper/search/title", api.views.FindPaperByTitle),
    path("api/paper/search/arxiv_id", api.views.FindPaperByArxivId),
]
