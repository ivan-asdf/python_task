from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

# from django.http import HttpResponse

from .models import Domain, Contact, Collector
from .tasks import add

# Create your views here.


@login_required
def index(request):
    return redirect("/add-site")


@login_required
def add_site(request):
    result = add.delay(4, 4)
    print("SERVER", result)

    user = request.user
    message = ""

    if request.method == "POST":
        domain_name = request.POST.get("domain_name")
        message = {"isError": False, "errors": ""}
        try:
            # Check if FQDN
            new_domain = Domain.objects.create(user=user, domain_name=domain_name)
            new_domain.save()
        except Exception as e:
            message["isError"] = True
            message["errors"] = e

    context = {"username": user.username, "message": message}
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
        c = Collector.objects.get(pk=collector_id)
        c.status = not c.status
        c.save()

    collectors = Collector.objects.filter(user_id=request.user.id)
    context = {"collectors": collectors, "username": request.user.username}
    return render(request, "collectors.html", context)
