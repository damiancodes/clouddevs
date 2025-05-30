# Generated by Django 4.2 on 2025-03-25 18:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='clients/')),
                ('website', models.URLField(blank=True, null=True)),
                ('industry', models.CharField(blank=True, max_length=100)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['name'], 'verbose_name': 'Category', 'verbose_name_plural': 'Categories'},
        ),
        migrations.AlterModelOptions(
            name='technology',
            options={'ordering': ['name'], 'verbose_name': 'Technology', 'verbose_name_plural': 'Technologies'},
        ),
        migrations.AlterModelOptions(
            name='testimonial',
            options={'ordering': ['-id']},
        ),
        migrations.RenameField(
            model_name='project',
            old_name='is_featured',
            new_name='featured',
        ),
        migrations.RemoveField(
            model_name='project',
            name='category',
        ),
        migrations.RemoveField(
            model_name='technology',
            name='icon',
        ),
        migrations.RemoveField(
            model_name='testimonial',
            name='client_company',
        ),
        migrations.RemoveField(
            model_name='testimonial',
            name='is_active',
        ),
        migrations.RemoveField(
            model_name='testimonial',
            name='rating',
        ),
        migrations.AddField(
            model_name='category',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='project',
            name='app_store_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='categories',
            field=models.ManyToManyField(related_name='projects', to='portfolio.category'),
        ),
        migrations.AddField(
            model_name='project',
            name='image_1',
            field=models.ImageField(blank=True, null=True, upload_to='projects/'),
        ),
        migrations.AddField(
            model_name='project',
            name='image_2',
            field=models.ImageField(blank=True, null=True, upload_to='projects/'),
        ),
        migrations.AddField(
            model_name='project',
            name='image_3',
            field=models.ImageField(blank=True, null=True, upload_to='projects/'),
        ),
        migrations.AddField(
            model_name='project',
            name='play_store_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='project',
            name='short_description',
            field=models.TextField(blank=True, default='', max_length=200),
        ),
        migrations.AddField(
            model_name='project',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='technology',
            name='slug',
            field=models.SlugField(default='default-technology-slug', max_length=100, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='challenge',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='featured_image',
            field=models.ImageField(upload_to='projects/'),
        ),
        migrations.AlterField(
            model_name='project',
            name='results',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='slug',
            field=models.SlugField(default='default-slug', unique=True),
        ),
        migrations.AlterField(
            model_name='project',
            name='solution',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='technology',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='testimonial',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='testimonials', to='portfolio.project'),
        ),
        migrations.DeleteModel(
            name='ProjectImage',
        ),
        migrations.AlterField(
            model_name='project',
            name='client',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='portfolio.client'),
        ),
    ]
