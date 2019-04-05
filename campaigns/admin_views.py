from django.shortcuts import render
from django.db import connection
import datetime
from .models import Campaign, Order

AGGREGATE_SQL = """
    SELECT product.name,
           sum(quantity) as sold,
           sum(price_snapshot * quantity) as total
    FROM   campaigns_product product
      JOIN campaigns_campaign campaign on product.campaign_id = campaign.id
      JOIN campaigns_lineitem lineitem on product.id = lineitem.product_id
      JOIN campaigns_order ord on lineitem.order_id = ord.id
    WHERE campaign.lookup_name = %s
      AND ord.voided = FALSE
      AND ord.created_time >= campaign.reporting_start
    GROUP BY product.name
"""

def get_filtered_order_list(campaign):
    order_list = Order.objects.all()
    if sum([x.cost for x in campaign.product_set.all()]) > 0:
        order_list = order_list.exclude(
            voided=True
        ).exclude(
            braintree_id__isnull=True,
            deferred=False,
        )
    return order_list

def aggregate_report(request):
    requested_campaign = request.path.split('/')[-1].rsplit('_', 1)[0]
    with connection.cursor() as cursor:
        cursor.execute(AGGREGATE_SQL, [requested_campaign])
        row_list = cursor.fetchall()

    formatted_rows = []
    formatted_rows.append(['Product', 'Count Sold', 'Total Collected'])  # Header row
    for row in row_list:
        formatted_rows.append([row[0], row[1], row[2]])
    substitutions = {
        'row_list': formatted_rows, 
        'column_widths': [4, 4, 4]
    }
    return render(request, 'campaigns/report.html', substitutions)


def detail_report(request):
    requested_campaign = request.path.split('/')[-1].rsplit('_', 1)[0]
    campaign = Campaign.objects.get(lookup_name=requested_campaign)
    order_list = get_filtered_order_list(campaign)
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
                'order': order_to_display,
                'deferred': order.deferred,
                'extra': order.extra,
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
            'deferred': order.deferred,
            'extra': order.extra,
        }

    header_row = ['Name', 'Date', 'Email', 'Order', 'Deferred', 'Extra']
    row_list = []
    for value in row_dict.values():
        try:
            date_str = value['date'].strftime('%m/%d/%y')
        except AttributeError:
            date_str = 'N/A'
        row_list.append([value['name'], date_str, value['unique_id'], value['order'], value.get('deferred'), value.get('extra')])

    row_list = sorted(row_list, key=lambda x: x[0].lower())
    substitutions = {
        'header': '{} Detail Report'.format(campaign.name),
        'row_list': [header_row] + row_list,
        'column_widths': [2, 1, 4, 2, 1, 2]
    }
    return render(request, 'campaigns/report.html', substitutions)


def customer_report(request):
    requested_campaign = request.path.split('/')[-1].rsplit('_', 1)[0]
    campaign = Campaign.objects.get(lookup_name=requested_campaign)
    order_list = get_filtered_order_list(campaign)
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
