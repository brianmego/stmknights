from django.shortcuts import render
from .models import Order


def fish_fry_agg_report(request):
    return aggregate_report(request, 'Lenten Fish Fry')


def fish_fry_detail_report(request):
    return detail_report(request, 'Lenten Fish Fry')


def nut_sales_agg_report(request):
    return aggregate_report(request, 'Nut Sales')


def nut_sales_detail_report(request):
    return detail_report(request, 'Nut Sales')


def aggregate_report(request, campaign):
    order_list = Order.objects.filter(
        braintree_id__isnull=False
    )
    campaign_order_list = []
    for order in order_list:
        if order.lineitem_set.first().product.campaign.name == campaign:
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
        'row_list': row_list
    }
    return render(request, 'campaigns/report.html', substitutions)


def detail_report(request, campaign):
    order_list = Order.objects.filter(
        braintree_id__isnull=False
    )
    campaign_order_list = []
    for order in order_list:
        if order.lineitem_set.first().product.campaign.name == campaign:
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
                'order': order_to_display
            }
            continue

        row_dict[customer.email] = {
            'name': '{} {}'.format(customer.first_name, customer.last_name),
            'unique_id': customer.email,
            'order': order_to_display
        }
    row_list = []
    row_list.append(['Name', 'Email', 'Order'])
    for item in row_dict.items():
        row_list.append([item[1]['name'], item[0], item[1]['order']])

    substitutions = {
        'row_list': row_list
    }
    return render(request, 'campaigns/report.html', substitutions)
