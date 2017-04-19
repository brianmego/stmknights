from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect, render
import braintree
from .forms import DegreeRegistrationForm
from .models import Attendee, Campaign, Customer, DegreeRegistration, \
    LineItem, Order, Product


braintree.Configuration.configure(
    braintree.Environment.All[settings.BRAINTREE_ENVIRONMENT],
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


def nuts_order(request, pk=None):
    products = Product.objects.filter(campaign__name='Nut Sales')

    cart = {}
    for product in products:
        cart[product.pk] = {
            'id': product.pk,
            'name': product.name,
            'weight': product.meta_field_one,
            'quantity': 0,
            'cost': product.cost,
            'image': product.meta_field_two
        }

    if pk:
        order = Order.objects.get(pk=pk)
        for line_item in order.lineitem_set.all():
            cart[line_item.product.pk]['quantity'] = line_item.quantity

    substitutions = {
        'order': pk,
        'products': cart.values(),
        'header': 'Nuts Order Form'
    }
    return render(request, 'campaigns/nuts_order.html', substitutions)


def fishfry_closed(request, pk=None):
    substitutions = {
        'message': 'Thank you for helping make the 2017 Fish Fry Fridays a success! Have a blessed Easter!'
    }
    return render(request, 'campaigns/campaign_closed.html', substitutions)


def fishfry_order(request, pk=None):
    products = Product.objects.filter(campaign__name='Lenten Fish Fry')

    cart = {}
    for product in products:
        cart[product.pk] = {
            'id': product.pk,
            'name': product.name,
            'quantity': 0,
            'cost': product.cost,
            'order': product.sort_order
        }

    if pk:
        order = Order.objects.get(pk=pk)
        for line_item in order.lineitem_set.all():
            cart[line_item.product.pk]['quantity'] = line_item.quantity

    substitutions = {
        'order': pk,
        'products': sorted(cart.values(), key=lambda x: x['order']),
        'header': 'Fish Fry Order Form'
    }
    return render(request, 'campaigns/fishfry_order.html', substitutions)


def crawfish_order(request, pk=None):
    products = Product.objects.filter(campaign__name='Crawfish Boil')

    cart = {}
    for product in products:
        cart[product.pk] = {
            'id': product.pk,
            'name': product.name,
            'quantity': 0,
            'cost': product.cost,
            'order': product.sort_order
        }

    if pk:
        order = Order.objects.get(pk=pk)
        for line_item in order.lineitem_set.all():
            cart[line_item.product.pk]['quantity'] = line_item.quantity

    substitutions = {
        'order': pk,
        'products': sorted(cart.values(), key=lambda x: x['order']),
        'header': '1st Annual STM Cajun Crawfish Boil'
    }
    return render(request, 'campaigns/crawfish_order.html', substitutions)


def payment_confirmation_view(request):
    if request.method == 'POST':
        nonce = request.POST['payment-method-nonce']
        order = Order.objects.get(pk=request.POST['order_id'])
        first_name = request.POST['first-name']
        last_name = request.POST['last-name']
        phone_number = request.POST['phone-number']
        street_address = request.POST['street-address']
        postal_code = request.POST['postal-code']
        email = request.POST['email']

        Customer.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email=email,
            street_address=street_address,
            postal_code=postal_code,
            order=order
        )

        result = braintree.Transaction.sale(
            {
                "amount": request.POST['payment-amount'],
                "customer": {
                    "first_name": first_name,
                    "last_name": last_name,
                    "phone": phone_number,
                    "email": email
                },
                "billing": {
                    "first_name": first_name,
                    "last_name": last_name,
                    "street_address": street_address,
                    "postal_code": postal_code,
                },
                "payment_method_nonce": nonce,
                "options": {
                    "submit_for_settlement": True
                }
            }
        )
        substitutions = {
            'result': result
        }

        if not result.is_success:
            substitutions = {
                'header': 'Checkout',
                'order': order,
                'nonce': braintree.ClientToken.generate(),
                'error_message': result.message
            }
            return render(request, 'campaigns/checkout.html', substitutions)

        order.braintree_id = result.transaction.id
        order.save()

        order_list = list(order.lineitem_set.filter(quantity__gt=0).values_list('product__name', 'quantity'))
        email_body = [
            'name: {} {}'.format(request.POST['first-name'], request.POST['last-name']),
            'address: {}'.format(request.POST['street-address']),
            'postal_code: {}'.format(request.POST['postal-code']),
            'phone: {}'.format(request.POST['phone-number']),
            'amount: ${}'.format(request.POST['payment-amount']),
            'order: {}'.format(order_list)
        ]

        campaign = Campaign.objects.get(name='Lenten Fish Fry')
        email_addrs = list(campaign.contact.all().values_list('email', flat=True))
        email_addrs.append(request.POST['email'])

        msg = EmailMultiAlternatives(
                'STM Knights Website Order Confirmation',
                ''.join(email_body),
                'noreply@STMKnights.org',
                set(email_addrs),
        )
        msg.attach_alternative('<br>'.join(email_body), "text/html")
        msg.send()
        return render(request, 'campaigns/sales_thankyou.html', substitutions)


def checkout_view(request):
    if request.method == 'POST':
        product_inputs = {x[0]: x[1] for x in request.POST.items() if x[0].startswith('product-')}
        existing_order_id = request.POST['order_id']
        if existing_order_id != 'None':
            order = Order.objects.get(pk=existing_order_id)
            order.lineitem_set.all().delete()
        else:
            order = Order.objects.create()

        for key, value in product_inputs.items():
            if not value:
                continue
            pk = key.split('product-')[1]
            product = Product.objects.get(pk=pk)
            LineItem.objects.create(
                product=product,
                order=order,
                quantity=value,
                price_snapshot=product.cost
            )

        substitutions = {
            'header': 'Checkout',
            'order': order,
            'nonce': braintree.ClientToken.generate()
        }
        return render(request, 'campaigns/checkout.html', substitutions)
