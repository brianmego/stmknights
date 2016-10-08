from django.shortcuts import redirect, render
from .forms import DegreeRegistrationForm
from .models import DegreeRegistration, Product, Attendee, AttendeeType


def degree_thank_you(request, pk):
    reg = DegreeRegistration.objects.get(pk=pk)
    candidate_cost = reg.attendees.all().count() * 40
    medallion_cost = reg.medallions * 8
    guest_cost = reg.attendees.all().count() * 8
    admin_fee = reg.attendees.all().count()
    subtotal = sum([candidate_cost, medallion_cost, guest_cost])
    return render(
        request,
        'campaigns/thankyou.html',
        {
            'header': 'Thank You!',
            'candidates': reg.attendees.all().count(),
            'guests': reg.attendees.all().count(),
            'medallions': reg.medallions,
            'subtotal': subtotal,
            'admin_fee': admin_fee,
            'grand_total': subtotal + admin_fee
        }
    )


def degree_registration_new(request):
    if request.method == 'POST':
        post = request.POST
        form = DegreeRegistrationForm(post)
        if form.is_valid():
            reg = form.save(commit=False)
            reg.attending_council = post['attending_council']
            reg.attending_council_num = post['attending_council_num']
            reg.medallions = post['medallions']
            reg.save()
            attendee_types = ['Candidate', 'Guest']
            for att_type in attendee_types:
                for name in post.getlist(att_type.lower()):
                    if not name:
                        continue
                    Attendee.objects.create(
                        name=name,
                        attendee_type=AttendeeType.objects.get(label=att_type),
                        degree_registration_id=reg.pk
                    )
            return redirect('degree_thank_you', pk=reg.pk)
    form = DegreeRegistrationForm()

    products = Product.objects.all()
    costs = {x.name: x.cost for x in products}
    substitutions = {
        'form': form,
        'costs': costs,
        'header': 'Major Degree Registration'
    }

    return render(request, 'campaigns/registrant_edit.html', substitutions)
