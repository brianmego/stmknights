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
      AND ord.braintree_id is not NULL
      AND ord.voided = FALSE
      AND ord.created_time >= campaign.reporting_start
    GROUP BY product.name
"""

CUSTOMER_SQL = """
    SELECT cust.first_name, cust.last_name, ord.created_time, sum(price_snapshot * quantity) as total
    FROM campaigns_product product
      JOIN campaigns_campaign campaign on product.campaign_id = campaign.id
      JOIN campaigns_lineitem lineitem on product.id = lineitem.product_id
      JOIN campaigns_order ord on lineitem.order_id = ord.id
      JOIN campaigns_customer cust on ord.id = cust.order_id
    WHERE campaign.lookup_name = %s
      AND ord.braintree_id is not NULL
      AND ord.voided = FALSE
      AND ord.created_time >= campaign.reporting_start
"""

DETAIL_SQL = """
    SELECT cust.first_name,
           cust.last_name,
           ord.created_time,
           cust.email,
           product.name,
           lineitem.quantity,
           ord.deferred,
           ord.extra
    FROM   campaigns_product product
      JOIN campaigns_campaign campaign on product.campaign_id = campaign.id
      JOIN campaigns_lineitem lineitem on product.id = lineitem.product_id
      JOIN campaigns_order ord on lineitem.order_id = ord.id
      JOIN campaigns_customer cust on ord.id = cust.order_id
    WHERE campaign.lookup_name = %s
      AND ord.braintree_id is not NULL
      AND ord.voided = FALSE
      AND ord.created_time >= campaign.reporting_start
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
    with connection.cursor() as cursor:
        cursor.execute(DETAIL_SQL, [requested_campaign])
        row_list = cursor.fetchall()

    formatted_rows = []
    formatted_rows.append(['Name', 'Date', 'Email', 'Order', 'Deferred', "Extra"])  # Header row
    for row in row_list:
        formatted_rows.append(
            [
                f'{row[1]}, {row[0]}',
                row[2].strftime('%m/%d/%y'),
                row[3],
                f'{row[4]} - {row[5]}',
                row[6],
                row[7]
            ]
        )

    substitutions = {
        'row_list': formatted_rows,
        'column_widths': [2, 1, 4, 2, 1, 2]
    }
    return render(request, 'campaigns/report.html', substitutions)


def customer_report(request):
    requested_campaign = request.path.split('/')[-1].rsplit('_', 1)[0]
    with connection.cursor() as cursor:
        cursor.execute(CUSTOMER_SQL, [requested_campaign])
        row_list = cursor.fetchall()

    formatted_rows = []
    formatted_rows.append(['Name', 'Date', 'Total'])  # Header row
    for row in row_list:
        formatted_rows.append([f'{row[1]}, {row[0]}', row[2], row[3]])
    substitutions = {
        'row_list': formatted_rows, 
        'column_widths': [4, 4, 4]
    }
    return render(request, 'campaigns/report.html', substitutions)
