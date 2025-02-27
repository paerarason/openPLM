# Generated by Django 5.0.1 on 2024-01-28 13:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('plmapp', '0002_alter_invitation_token'),
    ]

    operations = [
        migrations.CreateModel(
            name='CAE',
            fields=[
                ('document_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='plmapp.document')),
            ],
            options={
                'abstract': False,
            },
            bases=('plmapp.document',),
        ),
        migrations.CreateModel(
            name='BoundaryConditions',
            fields=[
                ('cae_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='cae.cae')),
            ],
            options={
                'abstract': False,
            },
            bases=('cae.cae',),
        ),
        migrations.CreateModel(
            name='Geometry',
            fields=[
                ('cae_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='cae.cae')),
            ],
            options={
                'abstract': False,
            },
            bases=('cae.cae',),
        ),
        migrations.CreateModel(
            name='Mesh',
            fields=[
                ('cae_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='cae.cae')),
            ],
            options={
                'abstract': False,
            },
            bases=('cae.cae',),
        ),
        migrations.CreateModel(
            name='Results',
            fields=[
                ('cae_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='cae.cae')),
            ],
            options={
                'abstract': False,
            },
            bases=('cae.cae',),
        ),
    ]
