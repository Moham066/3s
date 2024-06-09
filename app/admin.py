from django.contrib import admin
from .models import produit, ligne_commande, vente, element, dépence_gain, product_stat,notif, production, cmd, ligne_commande_stat, impression


# Register your models here.
admin.site.register(produit)
admin.site.register(ligne_commande)
admin.site.register(vente)
admin.site.register(element)
admin.site.register(dépence_gain)
admin.site.register(product_stat)
admin.site.register(notif)
admin.site.register(production)
admin.site.register(ligne_commande_stat)
admin.site.register(impression)
admin.site.register(cmd)


