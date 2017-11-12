from django.shortcuts import render
import datetime
from .models import Campaign, Order


def aggregate_report(request):
    requested_campaign = request.path.split('/')[-1].rsplit('_', 1)[0]
    campaign = Campaign.objects.get(lookup_name=requested_campaign)
    order_list = Order.objects.filter(
        braintree_id__isnull=False,
        voided=False
    )
    campaign_order_list = []
    for order in order_list:
        if order.lineitem_set.first() is None:
            continue
        if order.lineitem_set.first().product.campaign.name == campaign.name:
            campaign_order_list.append(order)

    row_dict = {}
    for order in campaign_order_list:
        for item in order.lineitem_set.all():
            row_dict.setdefault(
                item.product.name,
                {
                    'count': 0,
                    'total': 0,
                }
            )
            row_dict[item.product.name]['count'] += item.quantity
            row_dict[item.product.name]['total'] += item.quantity * item.price_snapshot
    header_row = ['Product', 'Count Sold', 'Total Collected']
    row_list = []
    for item in row_dict.items():
        row_list.append([item[0], item[1]['count'], '${}'.format(item[1]['total'])])

    row_list = sorted(row_list, key=lambda x: x[0].lower())
    substitutions = {
        'row_list': [header_row] + row_list,
        'column_widths': [4, 4, 4]
    }
    return render(request, 'campaigns/report.html', substitutions)


def detail_report(request):
    requested_campaign = request.path.split('/')[-1].rsplit('_', 1)[0]
    campaign = Campaign.objects.get(lookup_name=requested_campaign)
    order_list = Order.objects.filter(
        braintree_id__isnull=False,
        voided=False
    )
    campaign_order_list = []
    for order in order_list:
        if order.lineitem_set.first() is None:
            continue
        if order.lineitem_set.first().product.campaign.name == campaign.name:
            campaign_order_list.append(order)

    row_dict = {}
    for order in campaign_order_list:
        order_to_display = []
        for line_item in order.lineitem_set.all():
            if line_item.quantity == 0:
                continue
            order_to_display.append(
                '{} - {}'.format(
                    line_item.product.name,
                    line_item.quantity
                )
            )
        order_to_display = ", ".join(order_to_display)

        customer = order.customer_set.first()
        if not customer:
            row_dict[order.pk] = {
                'name': 'N/A',
                'unique_id': order.pk,
                'date': 'N/A',
                'order': order_to_display
            }
            continue

        try:
            name = '{}, {}'.format(customer.last_name, customer.first_name)
        except AttributeError:
            name = 'Missing Data'

        try:
            unique_id = customer.email
        except AttributeError:
            unique_id = 'Missing Data'

        row_dict[order.pk] = {
            'name': name,
            'unique_id': unique_id,
            'date': order.created_time,
            'order': order_to_display,
            'extra': order.extra
        }

    header_row = ['Name', 'Date', 'Email', 'Order', 'Extra']
    row_list = []
    for value in row_dict.values():
        row_list.append([value['name'], value['date'], value['unique_id'], value['order'], value.get('extra')])

    row_list = sorted(row_list, key=lambda x: x[0].lower())
    substitutions = {
        'row_list': [header_row] + row_list,
        'column_widths': [2, 2, 4, 2, 2]
    }
    return render(request, 'campaigns/report.html', substitutions)


def customer_report(request):
    requested_campaign = request.path.split('/')[-1].rsplit('_', 1)[0]
    campaign = Campaign.objects.get(lookup_name=requested_campaign)
    order_list = Order.objects.filter(
        braintree_id__isnull=False,
        voided=False
    )
    campaign_order_list = []
    for order in order_list:
        if order.lineitem_set.first() is None:
            continue
        if order.lineitem_set.first().product.campaign.name == campaign.name:
            if order.created_time.date() >= campaign.reporting_start:
                campaign_order_list.append(order)

    row_dict = {}
    for order in campaign_order_list:
        order_to_display = []
        total = 0
        for line_item in order.lineitem_set.all():
            if line_item.quantity == 0:
                continue
            total += line_item.quantity * line_item.price_snapshot

        customer = order.customer_set.first()

        try:
            name = '{}, {}'.format(customer.last_name, customer.first_name)
        except AttributeError:
            name = 'Missing Data'
        row_dict[order.pk] = {
            'name': name,
            'date': order.created_time,
            'total': total,
        }

    header_row = ['Name', 'Date', 'Total']
    row_list = []

    for value in row_dict.values():
        row_list.append([value['name'], value['date'], value['total']])

    row_list = sorted(row_list, key=lambda x: x[0].lower())
    column_widths = [4, 4, 4]
    substitutions = {
        'row_list': [header_row] + row_list,
        'column_widths': column_widths
    }
    return render(request, 'campaigns/report.html', substitutions)
