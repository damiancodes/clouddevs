# Generated by Django 4.2 on 2025-03-25 12:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='QuoteRequest',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('company', models.CharField(blank=True, max_length=100, null=True)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=20)),
                ('project_description', models.TextField()),
                ('requirements', models.TextField()),
                ('budget', models.CharField(blank=True, max_length=100, null=True)),
                ('timeline', models.CharField(blank=True, max_length=100, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('quoted', 'Quoted'), ('accepted', 'Accepted'), ('rejected', 'Rejected')], default='pending', max_length=20)),
                ('quoted_amount', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ServiceEstimate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=20)),
                ('service_type', models.CharField(choices=[('web', 'Web Development'), ('app', 'App Development'), ('pos', 'POS System')], max_length=10)),
                ('project_description', models.TextField()),
                ('complexity', models.CharField(choices=[('simple', 'Simple'), ('moderate', 'Moderate'), ('complex', 'Complex')], max_length=10)),
                ('estimated_budget', models.DecimalField(decimal_places=2, max_digits=10)),
                ('estimated_timeline', models.PositiveIntegerField(help_text='Estimated days to complete')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
