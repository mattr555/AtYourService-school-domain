from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

import datetime
import pytz

from main.models import Organization, Event

@login_required
def manage_home(request):
    if not request.user.user_profile.is_org_admin():
        messages.error(request, "You aren't an organization administrator!")
        return HttpResponseRedirect('/')
    return render(request, 'main/manage_home.html', {'organizations': request.user.orgs_admin.all()})

@login_required
def org_home(request, pk):
    o = get_object_or_404(Organization.objects, pk=pk)
    if not request.user.id == o.admin_id:
        messages.error(request, "You aren't authorized to do that!")
        return HttpResponseRedirect('/')
    events = o.events.order_by('-date_start')
    return render(request, 'main/org_home.html', {'org': o, 'events': events})

def validate_org(request, o):
    errors = []
    if request.POST.get('name'):
        o.name = request.POST.get('name')
    else:
        errors.append('A name is required')
    if request.POST.get('description'):
        o.description = request.POST.get('description')
    else:
        errors.append('A description is required')
    if request.POST.get('location'):
        o.location = request.POST.get('location')
    else:
        errors.append('A location is required')
    if request.POST.get('lat'):
        o.geo_lat = float(request.POST.get('lat'))
        o.geo_lon = float(request.POST.get('lon'))
    if errors:
        return (errors, o)
    o.save()
    return True

@login_required
def org_edit(request, pk):
    o = get_object_or_404(Organization.objects, pk=pk)
    if o not in request.user.orgs_admin.all():
        messages.error(request, "That's not your organization!")
        return HttpResponseRedirect(reverse('main:org_manage'))
    if request.method == "GET":
        return render(request, 'main/org_edit.html', {'org': o})
    else:
        err = validate_org(request, o)
        if isinstance(err, tuple):
            return render(request, 'main/org_edit.html', {'org': err[1], 'errors': err[0]})
        messages.success(request, 'Organization successfully edited')
        return HttpResponseRedirect(reverse('main:manage_home'))

@login_required
def org_new(request):
    if request.user.user_profile.is_org_admin():
        if request.method == "GET":
            return render(request, 'main/org_new.html')
        else:
            o = Organization(admin_id=request.user.id)
            err = validate_org(request, o)
            if isinstance(err, tuple):
                return render(request, 'main/org_new.html', {'org': err[1], 'errors': err[0]})
            messages.success(request, 'Organization successfully created')
            return HttpResponseRedirect(reverse('main:manage_home'))
    else:
        messages.error(request, "You aren't an organization administrator!")
        return HttpResponseRedirect('/')

@login_required
def org_delete(request, pk):
    o = Organization.objects.get(pk=pk)
    if o:
        if request.user.id == o.admin_id:
            o.delete()
            messages.info(request, "Organization successfully deleted")
        else:
            messages.error(request, "You aren't authorized to do that!")
    else:
        messages.error(request, "Organization not found!")
    if request.GET.get('next'):
        return HttpResponseRedirect(request.GET.get('next'))
    return HttpResponseRedirect('/')

def validate_event(request, e):
    errors = []
    if request.POST.get('organization'):
        o = Organization.objects.get(pk=int(request.POST.get('organization')))
        if request.user.id == o.admin_id:
            e.organization = o
        else:
            errors.append("You aren't authorized to do that!")
    else:
        errors.append("An organization is required")
    if request.POST.get('name'):
        e.name = request.POST.get('name')
    else:
        errors.append('A name is required')
    if request.POST.get('description'):
        e.description = request.POST.get('description')
    else:
        errors.append('A description is required')
    if request.POST.get('location'):
        e.location = request.POST.get('location')
    else:
        errors.append('A location is required')
    if request.POST.get('date-start'):
        naive = datetime.datetime.strptime(request.POST.get('date-start'), '%m/%d/%y %I:%M %p')
        tz = pytz.timezone(request.user.user_profile.timezone)
        e.date_start = tz.localize(naive)
    else:
        errors.append('A start date is required')
    if request.POST.get('date-end'):
        naive = datetime.datetime.strptime(request.POST.get('date-end'), '%m/%d/%y %I:%M %p')
        tz = pytz.timezone(request.user.user_profile.timezone)
        e.date_end = tz.localize(naive)
    else:
        errors.append('An end date is required')
    if request.POST.get('lat'):
        e.geo_lat = float(request.POST.get('lat'))
        e.geo_lon = float(request.POST.get('lon'))
    if errors:
        return (errors, e)
    try:
        e.save()
    except Exception as err:
        errors.append(repr(err))
        return (errors, e)
    return True

@login_required
def event_home(request, pk):
    e = get_object_or_404(Event.objects, pk=pk)
    if request.user.id == e.organizer_id:
        user_statuses = []
        for u in e.participants.all():
            user_statuses.append([u, e.confirm_status(u)])
        return render(request, 'main/event_home.html', {'event': e, 'user_statuses': user_statuses})
    messages.error(request, "That's not your event!")
    return HttpResponseRedirect(reverse('main:manage_home'))

@login_required
def event_new(request):
    if request.method == "GET":
        return render(request, 'main/event_new.html')
    else:
        e = Event(organizer_id=request.user.id)
        err = validate_event(request, e)
        if isinstance(err, tuple):
            return render(request, 'main/event_new.html', {'event': err[1], 'errors': err[0]})
        messages.success(request, 'Event created successfully')
        return HttpResponseRedirect(reverse('main:org_home', args=(request.POST.get('organization'))))

@login_required
def event_edit(request, pk):
    e = get_object_or_404(Event.objects, pk=pk)
    if not request.user.id == e.organizer_id:
        messages.error(request, "You aren't authorized to do that!")
        return HttpResponseRedirect(reverse('main:manage_home'))
    if request.method == "GET":
        return render(request, 'main/event_edit.html', {'event': e})
    else:
        err = validate_event(request, e)
        if isinstance(err, tuple):
            return render(request, 'main/event_edit.html', {'event': err[1], 'errors': err[0]})
        messages.success(request, 'Event created successfully')
        return HttpResponseRedirect(reverse('main:org_home', args=(request.POST.get('organization'))))

@login_required
def event_delete(request, pk):
    e = Event.objects.get(pk=pk)
    if e:
        if request.user.id == e.organizer_id:
            e.delete()
            messages.info(request, "Event successfully deleted")
        else:
            messages.error(request, "You aren't authorized to do that!")
    else:
        messages.error(request, "Event not found!")
    if request.GET.get('next'):
        return HttpResponseRedirect(request.GET.get('next'))
    return HttpResponseRedirect('/')

