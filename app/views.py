from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# from django.http import HttpResponse

from .models import Contact, Collector

# Create your views here.


@login_required
def index():
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
    contacts = Contact.objects.all()
    context = {"contacts": contacts, "username": request.user.username}
    return render(request, "all_contacts.html", context)


@login_required
def collectors(request):
    if request.method == "POST":
        collector_id = request.POST.get("collector_id")
        print(collector_id)
        c = Collector.objects.get(pk=collector_id)
        c.status = not c.status
        c.save()

    collectors = Collector.objects.filter(user_id=request.user.id)
    context = {"collectors": collectors, "username": request.user.username}
    return render(request, "collectors.html", context)
