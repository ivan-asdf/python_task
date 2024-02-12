from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .models import Domain, Contact, Collector


@login_required
def index(request):
    return redirect("/add-site")


@login_required
def add_site(request):
    user = request.user
    message = ""

    if request.method == "POST":
        domain_name = request.POST.get("domain_name")
        message = {"isError": False, "errors": ""}
        try:
            # Fails if not FQDN
            Domain.objects.create(user=user, name=domain_name)
        except ValidationError as e:
            message["isError"] = True
            message["errors"] = e

    context = {"username": user.username, "message": message}
    return render(request, "add_site.html", context)


@login_required
def all_contacts(request):
    user = request.user
    contacts = Contact.objects.filter(user=user)
    context = {"contacts": contacts, "username": user.username}
    return render(request, "all_contacts.html", context)


@login_required
def collectors(request):
    if request.method == "POST":
        collector_id = request.POST.get("collector_id")
        c = Collector.objects.get(pk=collector_id)
        c.status = not c.status
        c.save()

    user = request.user
    collectors = Collector.objects.filter(user_id=user.id)
    context = {"collectors": collectors, "username": user.username}
    return render(request, "collectors.html", context)
