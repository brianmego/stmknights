from django.shortcuts import redirect, render
from .forms import DegreeRegistrationForm
from .models import DegreeRegistration


def degree_thank_you(request, pk):

    reg = DegreeRegistration.objects.get(pk=pk)
    candidate_cost = reg.candidates * 40
    medallion_cost = reg.medallions * 8
    guest_cost = reg.guests * 8
    admin_fee = reg.candidates + reg.guests
    subtotal = sum([candidate_cost, medallion_cost, guest_cost])
    return render(
        request,
        'campaigns/thankyou.html',
        {
            'header': 'Thank You!',
            'candidates': reg.candidates,
            'guests': reg.guests,
            'medallions': reg.medallions,
            'subtotal': subtotal,
            'admin_fee': admin_fee,
            'grand_total': subtotal + admin_fee
        }
    )


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
            return redirect('degree_thank_you', pk=reg.pk)
    form = DegreeRegistrationForm()
    substitutions = {
        'form': form,
        'header': 'Major Degree Registration'
    }

    return render(request, 'campaigns/registrant_edit.html', substitutions)
