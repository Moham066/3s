# Generated by Django 4.2.10 on 2024-02-28 19:35

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='dépence_gain',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('Dépence', 'Depence'), ('Gain', 'Gain')], default='Dépence', max_length=30)),
                ('date', models.DateField(default=datetime.date.today)),
                ('montant', models.FloatField()),
                ('motif', models.CharField(max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='element',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=30, null=True)),
                ('prix_u', models.FloatField(max_length=10, null=True)),
                ('prix_tt', models.FloatField(max_length=10, null=True)),
                ('categorie', models.CharField(choices=[('Vénoiserie', 'Venoiserie'), ('Patisserie', 'Patisserie'), ('Salé', 'Sale'), ('Divers', 'Divers')], default='Divers', max_length=30)),
                ('quantite', models.FloatField(max_length=10, null=True)),
                ('utilise', models.FloatField(default=0, max_length=10, null=True)),
                ('date_dernier_ajout', models.DateField(default=datetime.date.today)),
                ('minimum', models.FloatField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ligne_commande',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantite', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='notif',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=300)),
                ('date', models.DateField(default=datetime.date.today)),
                ('etat', models.CharField(choices=[('Lu', 'Lu'), ('Non lu', 'Nonlu')], default='Non lu', max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='produit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nom', models.CharField(max_length=30, null=True)),
                ('prix', models.FloatField(max_length=10, null=True)),
                ('categorie', models.CharField(choices=[('Vénoiserie', 'Venoiserie'), ('Patisserie', 'Patisserie'), ('Boisson chaude', 'Bs'), ('Boisson fraiche', 'Bf'), ('Suplément', 'Sp'), ('Salé', 'Sale'), ('Divers', 'Divers')], default='Patisserie', max_length=30)),
                ('quantite', models.FloatField(max_length=100, null=True)),
                ('vendu', models.FloatField(default=0, max_length=10, null=True)),
                ('date_dernier_ajout', models.DateField(default=datetime.date.today)),
                ('minimum', models.FloatField(max_length=100, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='vente',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_commande', models.DateField(default=datetime.date.today)),
                ('tt_prix', models.FloatField(default=0)),
                ('commandes', models.ManyToManyField(to='app.ligne_commande')),
            ],
        ),
        migrations.CreateModel(
            name='product_stat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date.today)),
                ('quantity', models.IntegerField(default=0)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.produit')),
            ],
        ),
        migrations.AddField(
            model_name='ligne_commande',
            name='produit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.produit'),
        ),
    ]
