"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from backend.view.tweet import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tweet/upload', tweet_upload),
    path('stats/historic', historic_zones),
    path('stats/realtime/words', top_words),
    path('stats/realtime/topics', top_topics),
    path('stats/realtime/topics/location', top_topics_with_location),
    path('stats/realtime', realtime_zones),
    path('stats/historic/minmax', stats_min_max)
]
