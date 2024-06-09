# Generated by Django 5.0.2 on 2024-03-15 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_alter_ligne_produit_produit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='produit',
            name='categorie',
            field=models.CharField(choices=[('Viennoiserie', 'Venoiserie'), ('Patisserie', 'Patisserie'), ('Boisson chaude', 'Bs'), ('Boisson fraiche', 'Bf'), ('Suplément', 'Sp'), ('Salé', 'Sale'), ('Boisson', 'Boisson'), ('Gateau sec', 'Gateausec'), ('Divers', 'Divers')], default='Patisserie', max_length=30),
        ),
    ]
