import base64
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect, render
from .models import Campaign, CampaignTag, Customer, LineItem, Order, Product
import requests
import logging

LOGGER = logging.getLogger(__name__)
CARDCONNECT_API_URL = settings.CARDCONNECT_API_URL
CARDCONNECT_TOKEN_URL = settings.CARDCONNECT_TOKEN_URL
MERCHANT_ID = settings.CARDCONNECT_MERCHANT_ID
USERNAME = settings.CARDCONNECT_USERNAME
PASSWORD = settings.CARDCONNECT_PASSWORD
AUTH_TOKEN = base64.b64encode(f'{USERNAME}:{PASSWORD}'.encode()).decode()


def redirect_to_official(request):
    return redirect('https://uknight.org/CouncilSite/?CNO=9997')


def generic_order(request, campaign, pk=None):
    campaign_obj = Campaign.objects.get(lookup_name=campaign)

    if campaign_obj.closed:
        closed_message = campaign_obj.closed_message
        if not closed_message:
            closed_message = 'This campaign is now closed for sales'
        substitutions = {
            'header': campaign_obj.name,
            'message': closed_message
        }
        return render(request, 'campaigns/campaign_closed.html', substitutions)


    products = Product.objects.filter(campaign=campaign_obj)

    cart = {}
    for product in products:
        cart[product.pk] = {
            'id': product.pk,
            'name': product.name,
            'meta_field_one': product.meta_field_one,
            'quantity': 0,
            'cost': product.cost,
            'order': product.sort_order,
            'meta_field_two': product.meta_field_two
        }

    if pk:
        order = Order.objects.get(pk=pk)
        for line_item in order.lineitem_set.all():
            cart[line_item.product.pk]['quantity'] = line_item.quantity

    header = campaign_obj.header
    if not header:
        header = '{} Order Form'.format(campaign_obj.name)

    substitutions = {
        'order': pk,
        'campaign': campaign_obj.lookup_name,
        'products': sorted(cart.values(), key=lambda x: x['order']),
        'header': header,
        'where': campaign_obj.where,
        'when': campaign_obj.when,
        'details': campaign_obj.details,
        'tags': campaign_obj.campaigntag_set.all()
    }
    template_name = 'campaigns/{}.html'.format(campaign_obj.template_name)
    return render(request, template_name, substitutions)


def payment_confirmation_view(request):
    next_page = 'campaigns/sales_thankyou.html'

    order = Order.objects.get(pk=request.POST['order_id'])
    first_name = request.POST['first-name']
    last_name = request.POST['last-name']
    phone_number = request.POST['phone-number']
    street_address = request.POST['street-address']
    postal_code = request.POST['postal-code']
    email = request.POST['email']
    campaign_lookup = request.POST['campaign']

    expiration_date = request.POST.get('expiration-date')
    if expiration_date:
        expiration_date = ''.join(x for x in expiration_date if x.isdigit())
    payment_amount = request.POST.get('payment-amount', 0)
    token = request.POST.get('token')
    cvv = request.POST.get('cvv')

    campaign = Campaign.objects.get(lookup_name=campaign_lookup)
    substitutions = {
        'campaign': campaign.lookup_name
    }

    Customer.objects.create(
        first_name=first_name,
        last_name=last_name,
        phone_number=phone_number,
        email=email,
        street_address=street_address,
        postal_code=postal_code,
        order=order
    )

    if not order.get_total() or order.deferred:
        next_page = 'campaigns/free_thankyou.html'
    else:
        transaction_sale_body = {
            "merchid": MERCHANT_ID,
            "amount": payment_amount,
            "expiry": expiration_date,
            "account": token,
            "name": f"{first_name} {last_name}",
            "address": street_address,
            "postal": postal_code,
            "email": email,
            "orderid": str(order.id),
            "taxexempt": "Y",
            "cvv2": cvv,
            "capture": "Y"
        }

        result = requests.post(
            f'{CARDCONNECT_API_URL}/auth',
            json=transaction_sale_body,
            headers={
                'Authorization': f'Basic {AUTH_TOKEN}'
            }
        )
        if not result.ok:
            substitutions = {
                'header': 'Checkout',
                'order': order,
                # 'nonce': braintree.ClientToken.generate(),
                'error_message': 'There was an issue processing the order',
            }
            return render(request, 'campaigns/checkout.html', substitutions)

        substitutions['result'] = result.json()
        order.braintree_id = result.json()['retref']
        order.save()

    order_list = list(order.lineitem_set.filter(quantity__gt=0).values_list('product__name', 'quantity'))
    email_body = [
        'Name: {} {}'.format(first_name, last_name),
        'Address: {}'.format(street_address),
        'Postal Code: {}'.format(postal_code),
        'Phone: {}'.format(phone_number),
        'Amount: ${}'.format(payment_amount),
        'Order: {}'.format(order_list),
        'Campaign: {}'.format(campaign.lookup_name),
    ]
    if order.extra:
        email_body.append('Extra Info: {}'.format(order.extra))

    email_addrs = list(campaign.contact.all().values_list('email', flat=True))
    email_addrs.append(request.POST['email'])

    msg = EmailMultiAlternatives(
            'STM Knights Website Order Confirmation',
            ''.join(email_body),
            'noreply@STMKnights.org',
            set(email_addrs),
    )
    msg.attach_alternative('<br>'.join(email_body), "text/html")
    try:
        msg.send()
    except ImproperlyConfigured:
        LOGGER.error('ERROR: Sendgrid not configured')
    return render(request, next_page, substitutions)


def checkout_view(request):
    if request.method == 'POST':
        product_inputs = {x[0]: x[1] for x in request.POST.items() if x[0].startswith('product-')}
        campaign_tags = {x[0]: x[1] for x in request.POST.items() if x[0].startswith('tag-')}
        existing_order_id = request.POST['order_id']
        campaign = request.POST['campaign']
        if existing_order_id != 'None':
            order = Order.objects.get(pk=existing_order_id)
            order.lineitem_set.all().delete()
        else:
            order = Order.objects.create()

        for name, value in product_inputs.items():
            if not value:
                continue
            if value.startswith('product-'):
                pk = value.split('product-')[1]
                quantity = 1
            else:
                pk = name.split('product-')[1]
                quantity = int(float(value))
            product = Product.objects.get(pk=pk)
            LineItem.objects.create(
                product=product,
                order=order,
                quantity=quantity,
                price_snapshot=product.cost
            )

        extra = []
        for name, value in campaign_tags.items():
            pk = name.split('tag-')[1]
            tag = CampaignTag.objects.get(pk=pk)
            extra.append('{}: {}'.format(tag.key, value))
        if extra:
            order.extra = '<br>'.join(extra)
            order.save()

        campaign_specific_checkout(campaign, request, order)

        substitutions = {
            'header': 'Checkout',
            'order': order,
            'campaign': campaign,
            'token_url': CARDCONNECT_TOKEN_URL
        }

        deferred_payment = request.POST.get('deferred')
        if deferred_payment:
            order.deferred = True
            order.save()
        # if order.get_total() and not deferred_payment:
        #     substitutions['nonce'] = braintree.ClientToken.generate()
        return render(request, 'campaigns/checkout.html', substitutions)


def campaign_specific_checkout(campaign, request, order):
    product_inputs = {x[0]: x[1] for x in request.POST.items() if x[0].startswith('product-')}
    if campaign == 'golf':
        player_product = Product.objects.get(campaign__lookup_name=campaign, name='Player')
        players = int(product_inputs.get('product-{}'.format(player_product.pk)))
        sponsorship = product_inputs.get('product-sponsorship')
        donation = request.POST['donation']
        players_to_charge = players
        if sponsorship:
            sponsorship_name = Product.objects.get(pk=sponsorship.split('-')[1]).name
            if sponsorship_name == 'Silver Sponsor':
                players_to_charge -= 4
            elif sponsorship_name == 'Gold Sponsor':
                players_to_charge -= 8
            elif sponsorship_name == 'Platinum Sponsor':
                players_to_charge -= 8
            if players_to_charge < 0:
                players_to_charge = 0
        discounts = players - players_to_charge
        if discounts > 0:
            discount_product = Product.objects.get(campaign__lookup_name=campaign, name='Complementary Player')
            LineItem.objects.create(
                product=discount_product,
                order=order,
                quantity=discounts,
                price_snapshot=player_product.cost * -1
            )
        is_donation = False
        try:
            float(donation)
            is_donation = True
        except:
            pass

        if is_donation:
            donation_product = Product.objects.get(campaign__lookup_name=campaign, name='Donation')
            donation_amt = int(float(donation))
            LineItem.objects.create(
                product=donation_product,
                order=order,
                quantity=donation_amt,
                price_snapshot=1
            )

        player_names = request.POST.getlist('player')
        extra_text = 'Player Names: {}'.format(', '.join(player_names))
        order.extra = '{} - {}'.format(extra_text, order.extra)
        order.save()


