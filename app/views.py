from django.shortcuts import render, redirect
# from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Contact, Collector

# Create your views here.


@login_required
def index(request):
    return redirect("/add-site")


@login_required
def add_site(request):
    if request.method == "POST":
        # Handle form submission logic here
        pass
    context = {"username": request.user.username}
    return render(request, "add_site.html", context)


@login_required
def all_contacts(request):
    # Assuming you have some contacts data to pass to the template
    contacts = Contact.objects.all()  # Assuming Contact is your model
    context = {"contacts": contacts, "username": request.user.username}
    return render(request, "all_contacts.html", context)


@login_required
def collectors(request):
    # Assuming you have some collectors data to pass to the template
    collectors = Collector.objects.all()  # Assuming Collector is your model
    context = {"collectors": collectors, "username": request.user.username}
    return render(request, "collectors.html", context)
