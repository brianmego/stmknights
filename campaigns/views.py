from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import redirect, render
import braintree
from .models import Campaign, CampaignTag, Customer, LineItem, Order, Product


braintree.Configuration.configure(
    braintree.Environment.All[settings.BRAINTREE_ENVIRONMENT],
    merchant_id=settings.BRAINTREE_MERCHANT_ID,
    public_key=settings.BRAINTREE_PUBLIC_KEY,
    private_key=settings.BRAINTREE_PRIVATE_KEY
)

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
    if request.method == 'POST':
        nonce = request.POST['payment-method-nonce']
        order = Order.objects.get(pk=request.POST['order_id'])
        first_name = request.POST['first-name']
        last_name = request.POST['last-name']
        phone_number = request.POST['phone-number']
        street_address = request.POST['street-address']
        postal_code = request.POST['postal-code']
        email = request.POST['email']
        campaign_lookup = request.POST['campaign']
        payment_amount = request.POST['payment-amount']
        campaign = Campaign.objects.get(lookup_name=campaign_lookup)

        Customer.objects.create(
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            email=email,
            street_address=street_address,
            postal_code=postal_code,
            order=order
        )

        transaction_sale_body = {
            "amount": payment_amount,
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
        if campaign.merchant_account_id:
            transaction_sale_body['merchant_account_id'] = campaign.merchant_account_id.label

        result = braintree.Transaction.sale(transaction_sale_body)
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
        substitutions['campaign'] = campaign.lookup_name

        order.braintree_id = result.transaction.id
        order.save()

        order_list = list(order.lineitem_set.filter(quantity__gt=0).values_list('product__name', 'quantity'))
        email_body = [
            'Name: {} {}'.format(first_name, last_name),
            'Address: {}'.format(street_address),
            'Postal Code: {}'.format(postal_code),
            'Phone: {}'.format(phone_number),
            'Amount: ${}'.format(payment_amount),
            'Order: {}'.format(order_list)
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
        msg.send()
        return render(request, 'campaigns/sales_thankyou.html', substitutions)


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

        for name, value in campaign_tags.items():
            pk = name.split('tag-')[1]
            tag = CampaignTag.objects.get(pk=pk)
            order.extra = '{}:{}'.format(tag.key, value)
            order.save()

        campaign_specific_checkout(campaign, request, order)

        substitutions = {
            'header': 'Checkout',
            'order': order,
            'campaign': campaign,
            'nonce': braintree.ClientToken.generate()
        }
        return render(request, 'campaigns/checkout.html', substitutions)


def campaign_specific_checkout(campaign, request, order):
    product_inputs = {x[0]: x[1] for x in request.POST.items() if x[0].startswith('product-')}
    campaign_lookup_name = 'golf2017'
    if campaign == campaign_lookup_name:
        player_product = Product.objects.get(campaign__lookup_name=campaign_lookup_name, name='Player')
        players = int(product_inputs.get('product-{}'.format(player_product.pk)))
        sponsorship = product_inputs.get('product-sponsorship')
        donation = request.POST['donation']
        players_to_charge = players
        if sponsorship:
            sponsorship_name = Product.objects.get(pk=sponsorship.split('-')[1]).name
            if sponsorship_name == 'Par Sponsor':
                players_to_charge -= 1
            elif sponsorship_name == 'Birdie Sponsor':
                players_to_charge -= 2
            elif sponsorship_name == 'Eagle Sponsor':
                players_to_charge -= 4
            elif sponsorship_name == 'Tournament Sponsor':
                players_to_charge -= 8
            if players_to_charge < 0:
                players_to_charge = 0
        discounts = players - players_to_charge
        if discounts > 0:
            discount_product = Product.objects.get(campaign__lookup_name=campaign_lookup_name, name='Complementary Player')
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
            donation_product = Product.objects.get(campaign__lookup_name=campaign_lookup_name, name='Donation')
            donation_amt = int(float(donation))
            LineItem.objects.create(
                product=donation_product,
                order=order,
                quantity=donation_amt,
                price_snapshot=1
            )

        player_names = request.POST.getlist('player')
        extra_text = 'Player Names: {}'.format(', '.join(player_names))
        order.extra = extra_text
        order.save()


