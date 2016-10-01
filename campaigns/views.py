from django.shortcuts import get_object_or_404, redirect, render
from .models import Campaign, Registrant
from .forms import DegreeRegistrationForm, PostForm


def registrant_list(request):
    registrants = Registrant.objects.all()
    return render(request, 'campaigns/registrant_list.html', {'registrants': registrants})


def registrant_detail(request, pk):
    registrant = get_object_or_404(Registrant, pk=pk)
    return render(request, 'campaigns/registrant_detail.html', {'registrant': registrant})


def registrant_new(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            registrant = form.save(commit=False)
            registrant.name = request.POST['name']
            registrant.email = request.POST['email']
            registrant.campaign = Campaign.objects.get(pk=request.POST['campaign'])
            registrant.save()
            return redirect('registrant_detail', pk=registrant.pk)
    else:
        form = PostForm()
    return render(request, 'campaigns/registrant_edit.html', {'form': form})


def degree_registration_new(request):
    if request.method == 'POST':
        form = DegreeRegistrationForm(request.POST)
        if form.is_valid():
            reg = form.save(commit=False)
            reg.attending_council = request.POST['attending_council']
            reg.attending_council_num = request.POST['attending_council_num']
            reg.candidates = request.POST['candidates']
            reg.guests = request.POST['guests']
            reg.medallions = request.POST['medallions']
            reg.save()
    form = DegreeRegistrationForm()
    substitutions = {
        'form': form,
        'header': 'Major Degree Registration'
    }

    return render(request, 'campaigns/registrant_edit.html', substitutions)
