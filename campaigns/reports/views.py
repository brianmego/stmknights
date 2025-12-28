from __future__ import annotations
import csv
from dataclasses import dataclass
from enum import StrEnum, auto
import io

from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.db import connection
from django.http import HttpResponse
from django.shortcuts import render


class ReportType(StrEnum):
    Aggregate = auto()
    Customer = auto()
    Detail = auto()
    DetailByLastName = auto()

    @classmethod
    def from_str(cls, inp: str) -> ReportType:
        match inp:
            case "aggregate":
                return ReportType.Aggregate
            case "customer":
                return ReportType.Customer
            case "detail":
                return ReportType.Detail
            case "detail_by_name":
                return ReportType.DetailByLastName
        raise NotImplementedError()

    def into_report(self) -> Report:
        match self:
            case ReportType.Aggregate:
                return AggregateReport(AGGREGATE_SQL, ["Product", "Count Sold", "Total Collected"])
            case ReportType.Customer:
                return CustomerReport(CUSTOMER_SQL, ["Name", "Date", "Total"])
            case ReportType.Detail:
                return DetailReport(DETAIL_SQL, ['Name', 'Date', 'Email', 'Order', 'Amount', 'Id', 'Deferred', 'Extra'])
            case ReportType.DetailByLastName:
                return DetailReport(DETAIL_SQL_BY_NAME, ['Name', 'Date', 'Email', 'Order', 'Amount', 'Id', 'Deferred', 'Extra'])


@dataclass
class Report:
    sql: str
    headers: list[str]
    type: ReportType

    def get_rows_from_db(self, campaign: str) -> list[tuple]:
        with connection.cursor() as cursor:
            cursor.execute(self.sql, [campaign])
            row_list = cursor.fetchall()
        return row_list

    def row_formatter(self, row: tuple) -> list[str]:
        raise NotImplementedError

    def serialize_as_csv(self, campaign: str) -> str:
        row_list = self.get_rows_from_db(campaign)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(self.headers)
        for row in row_list:
            writer.writerow(self.row_formatter(row))
        csv_content = output.getvalue()
        output.close()
        return csv_content



@dataclass
class AggregateReport(Report):
    type: ReportType=ReportType.Aggregate

    def row_formatter(self, row: tuple) -> list[str]:
        return [
            row[0],
            row[1],
            row[2],
        ]


@dataclass
class CustomerReport(Report):
    type: ReportType=ReportType.Customer

    def row_formatter(self, row: tuple) -> list[str]:
        return [
            f"{row[1]}, {row[0]}",
            row[2],
            row[3],
        ]

@dataclass
class DetailReport(Report):
    type: ReportType=ReportType.Detail

    def row_formatter(self, row: tuple) -> list[str]:
        return [
            f'{row[1]}, {row[0]}',  # Name
            row[2].strftime('%m/%d/%y'),  # Date
            row[3],  # Email
            f'{row[4]} - {row[5]}',  # Order
            f'${row[8]:.2f}',  # Amount
            row[9],  # Order ID
            row[6], # Deferred
            row[7], # extra
        ]

@login_required
def generic_report(request: WSGIRequest, report_type: str, campaign: str) -> HttpResponse:
    content_type = "text/csv"
    status = 200
    body = ReportType.from_str(report_type).into_report().serialize_as_csv(campaign)
    return HttpResponse(body.encode(), content_type, status)

def generic_report_as_html(request):
    report = ReportType.from_str(request.resolver_match.url_name).into_report()
    requested_campaign = request.path.split("/")[-1].rsplit("_", 1)[0]
    row_list = report.get_rows_from_db(requested_campaign)

    formatted_rows = []
    for row in row_list:
        formatted_rows.append(report.row_formatter(row))
    substitutions = {
        "row_list": formatted_rows,
        "header_row": report.headers,
        "campaign": requested_campaign,
        "report_type": report.type,
    }
    return render(request, "campaigns/report.html", substitutions)

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
           ord.extra,
           (lineitem.price_snapshot * lineitem.quantity) as amount,
           ord.id
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
           ord.extra,
           (lineitem.price_snapshot * lineitem.quantity) as amount,
           ord.id
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
