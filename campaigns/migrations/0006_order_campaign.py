# Generated by Django 3.2.18 on 2023-02-22 02:44

from django.db import migrations, models
import django.db.models.deletion


def seed_campaigns(apps, schema_editor):
    order_model = apps.get_model("campaigns", "Order")
    for order in order_model.objects.all():
        first_lineitem = order.lineitem_set.first()
        if first_lineitem:
            order.campaign = first_lineitem.product.campaign
            order.save()

class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0005_campaign_columns'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='campaign',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='campaigns.campaign'),
        ),
        migrations.RunPython(seed_campaigns, reverse_code=lambda _, __: None)
    ]
