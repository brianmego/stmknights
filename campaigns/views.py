from django.shortcuts import redirect, render
from .forms import DegreeRegistrationForm
from .models import DegreeRegistration, Product, Attendee, Campaign


def degree_thank_you(request, pk):
    reg = DegreeRegistration.objects.get(pk=pk)
    candidate_count = reg.attendees.filter(attendee_type__name='Candidate').count()
    guest_count = reg.attendees.filter(attendee_type__name='Guest').count()
    return render(
        request,
        'campaigns/thankyou.html',
        {
            'header': 'Thank You!',
            'candidates': candidate_count,
            'guests': guest_count,
            'medallions': reg.medallions,
            'cost': reg.cost
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
            reg.cost = 0
            reg.save()
            attendee_types = ['Candidate', 'Guest']
            total_cost = int(reg.medallions) * Product.objects.get(name='Medallion').cost
            for att_type in attendee_types:
                for name in post.getlist(att_type.lower()):
                    if not name:
                        continue
                    attendee = Attendee.objects.create(
                        name=name,
                        attendee_type=Product.objects.get(
                            name=att_type,
                            campaign=Campaign.objects.get(name='Major Degree')
                        ),
                        degree_registration_id=reg.pk
                    )
                    total_cost += attendee.attendee_type.cost
                    total_cost += 1  # Admin fee
            reg.cost = total_cost
            reg.save()
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


def nuts_order(request):
    # if request.method == 'POST':
    #     return redirect('degree_thank_you', pk=reg.pk)
    products = Product.objects.filter(campaign__name='Nut Sales')
    substitutions = {
        'products': products,
        'header': 'Nuts Orders'
    }

    return render(request, 'campaigns/nuts_order.html', substitutions)
