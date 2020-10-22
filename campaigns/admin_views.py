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
      AND (ord.braintree_id is not NULL OR ord.deferred = 1)
      AND ord.voided = 0
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
      AND (ord.braintree_id is not NULL OR ord.deferred = 1)
      AND ord.voided = 0
      AND ord.created_time >= campaign.reporting_start
    GROUP BY cust.id
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
    FROM campaigns_product product
           JOIN campaigns_campaign campaign on product.campaign_id = campaign.id
           JOIN campaigns_lineitem lineitem on product.id = lineitem.product_id
           JOIN campaigns_order ord on lineitem.order_id = ord.id
           JOIN campaigns_customer cust on ord.id = cust.order_id
    WHERE campaign.lookup_name = %s
      and (ord.braintree_id is not NULL or deferred = 1)
      AND ord.voided = 0
      AND ord.created_time >= campaign.reporting_start
      AND lineitem.quantity > 0
    ORDER BY ord.created_time DESC
"""

DETAIL_SQL_BY_NAME = """
    SELECT cust.first_name,
           cust.last_name,
           ord.created_time,
           cust.email,
           product.name,
           lineitem.quantity,
           ord.deferred,
           ord.extra
    FROM campaigns_product product
           JOIN campaigns_campaign campaign on product.campaign_id = campaign.id
           JOIN campaigns_lineitem lineitem on product.id = lineitem.product_id
           JOIN campaigns_order ord on lineitem.order_id = ord.id
           JOIN campaigns_customer cust on ord.id = cust.order_id
    WHERE campaign.lookup_name = %s
      and (ord.braintree_id is not NULL or deferred = 1)
      AND ord.voided = 0
      AND ord.created_time >= campaign.reporting_start
      AND lineitem.quantity > 0
    ORDER BY cust.last_name
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

    header_row = ['Product', 'Count Sold', 'Total Collected']
    formatted_rows = []
    for row in row_list:
        formatted_rows.append([row[0], row[1], row[2]])
    substitutions = {
        'header_row': header_row,
        'row_list': formatted_rows, 
    }
    return render(request, 'campaigns/report.html', substitutions)


def get_detail_header_row(row_list, deferred=False, extra=False):
    header_row = ['Name', 'Date', 'Email', 'Order']
    formatted_rows = []
    if deferred:
        header_row.append('Deferred')
    if extra:
        header_row.append('Extra')
    return header_row

def show_detailed_deferred(row_list):
    if any(x[6] for x in row_list if x != 0):
        return True
    return False

def show_detailed_extra(row_list):
    if any(x[7] for x in row_list if x is not None):
        return True
    return False

def detail_report_by_name(request):
    return detail_report(request, sql=DETAIL_SQL_BY_NAME)

def detail_report(request, sql=DETAIL_SQL):
    requested_campaign = request.path.split('/')[-1].rsplit('_', 1)[0]
    with connection.cursor() as cursor:
        cursor.execute(sql, [requested_campaign])
        row_list = cursor.fetchall()

    formatted_rows = []
    show_deferred = show_detailed_deferred(row_list)
    show_extra = show_detailed_extra(row_list)
    header_row = get_detail_header_row(
        row_list,
        deferred=show_deferred,
        extra=show_extra
    )

    for row in row_list:
        output_row = [
            f'{row[1]}, {row[0]}',  # Name
            row[2].strftime('%m/%d/%y'),  # Date
            row[3],  # Email
            f'{row[4]} - {row[5]}',  # Order
        ]
        if show_deferred:
            output_row.append(row[6])
        if show_extra:
            output_row.append(row[7])

        formatted_rows.append(output_row)

    substitutions = {
        'header_row': header_row,
        'row_list': formatted_rows,
    }
    return render(request, 'campaigns/report.html', substitutions)


def customer_report(request):
    requested_campaign = request.path.split('/')[-1].rsplit('_', 1)[0]
    with connection.cursor() as cursor:
        cursor.execute(CUSTOMER_SQL, [requested_campaign])
        row_list = cursor.fetchall()

    formatted_rows = []
    header_row = ['Name', 'Date', 'Total']  # Header row
    for row in row_list:
        formatted_rows.append([f'{row[1]}, {row[0]}', row[2], row[3]])
    substitutions = {
        'row_list': formatted_rows, 
        'header_row': header_row, 
    }
    return render(request, 'campaigns/report.html', substitutions)
