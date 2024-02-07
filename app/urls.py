from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("add-site/", views.add_site, name="add_site"),
    path("all-contacts/", views.all_contacts, name="all_contacts"),
    path("collectors/", views.collectors, name="collectors"),
]
