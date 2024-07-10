# Generated by Django 5.0.6 on 2024-06-15 17:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ohi', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Data',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('variable', models.CharField(max_length=10)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('lon', models.FloatField()),
                ('lat', models.FloatField()),
                ('radius', models.IntegerField()),
            ],
        ),
    ]