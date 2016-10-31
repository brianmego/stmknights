from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect, render
import braintree
from .forms import DegreeRegistrationForm
from .models import DegreeRegistration, Product, Attendee, Campaign


braintree.Configuration.configure(
    braintree.Environment.Sandbox,
    merchant_id=settings.BRAINTREE_MERCHANT_ID,
    public_key=settings.BRAINTREE_PUBLIC_KEY,
    private_key=settings.BRAINTREE_PRIVATE_KEY
)


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
    products = Product.objects.filter(campaign__name='Nut Sales')
    substitutions = {
        'products': products,
        'header': 'Nuts Order Form'
    }
    return render(request, 'campaigns/nuts_order.html', substitutions)


def payment_confirmation_view(request):
    if request.method == 'POST':
        result = braintree.Transaction.sale(
            {
                "amount": request.POST['payment-amount'],
                "billing": {
                    "first_name": request.POST['first-name'],
                    "last_name": request.POST['last-name'],
                    "street_address": request.POST['street-address'],
                    "postal_code": request.POST['postal-code'],
                },
                "payment_method_nonce": request.POST['payment-method-nonce'],
                "options": {
                    "submit_for_settlement": True
                }
            }
        )
        substitutions = {
            'result': result
        }

        if not result.is_success:
            raise Exception('Error with braintree payment')

        email_body = [
            'name: {}'.format(request.POST['first-name']),
            'address: {}'.format(request.POST['street-address']),
            'postal_code: {}'.format(request.POST['postal-code']),
            'amount: ${}'.format(request.POST['payment-amount']),
            'order: {}'.format(request.POST.getlist('product'))
        ]

        campaign = Campaign.objects.get(name='Nut Sales')
        email_addrs = campaign.contact.all().values_list('email', flat=True)

        msg = EmailMultiAlternatives(
                'There has been a sale of nuts!',
                ''.join(email_body),
                'NutSales@STMKnights.org',
                email_addrs,
        )
        msg.attach_alternative('<br>'.join(email_body), "text/html")
        msg.send()
        return render(request, 'campaigns/sales_thankyou.html', substitutions)


def checkout_view(request):
    if request.method == 'POST':
        product_inputs = {x[0]: x[1] for x in request.POST.items() if x[0].startswith('product-')}
        products = []
        for key, value in product_inputs.items():
            if not value:
                continue
            pk = key.split('product-')[1]
            products.append((Product.objects.get(pk=pk), value))
        total = sum([x[0].cost * int(x[1]) for x in products])
        substitutions = {
            'header': 'Checkout',
            'products': products,
            'grand_total': total,
            'nonce': braintree.ClientToken.generate()
        }
        return render(request, 'campaigns/checkout.html', substitutions)
