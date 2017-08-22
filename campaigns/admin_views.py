from django.shortcuts import render
from .models import Campaign, Order


def aggregate_report(request):
    requested_campaign = request.path.split('/')[-1].rsplit('_')[0]
    campaign = Campaign.objects.get(name=requested_campaign)
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
    row_list = []
    row_list.append(['Product', 'Count Sold', 'Total Collected'])
    for item in row_dict.items():
        row_list.append([item[0], item[1]['count'], '${}'.format(item[1]['total'])])

    substitutions = {
        'row_list': row_list,
        'column_width': int(12 / len(row_list[0]))
    }
    return render(request, 'campaigns/report.html', substitutions)


def detail_report(request):
    requested_campaign = request.path.split('/')[-1].rsplit('_')[0]
    campaign = Campaign.objects.get(name=requested_campaign)
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

        row_dict[order.pk] = {
            'name': '{} {}'.format(customer.first_name, customer.last_name),
            'unique_id': customer.email,
            'date': order.created_time,
            'order': order_to_display,
            'extra': order.extra
        }

    header_row = ['Name', 'Date', 'Email', 'Order', 'Extra']
    row_list = []
    for value in row_dict.values():
        row_list.append([value['name'], value['date'], value['unique_id'], value['order'], value['extra']])

    row_list = sorted(row_list, key=lambda x: x[0])
    substitutions = {
        'row_list': [header_row] + row_list,
        'column_width': int(12 / len(header_row))
    }
    return render(request, 'campaigns/report.html', substitutions)
