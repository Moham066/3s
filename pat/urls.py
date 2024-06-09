from django.contrib import admin
from django.urls import path
from app import views as v 
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', v.home_view),
    path('dash/', v.dashboard_view),
    path('login/', v.login_view),
    path('logout/', v.logout_view),
    path('presentoire/', v.presentoire_view),
    path('presentoire/<int:current_id>/',v.single_produit_view),
    path('commercial/', v.commercial_view),
    path('labo/', v.labo_view),
    path('labo/<int:current_id>/', v.single_labo_view),
    path('finance/', v.finance_view),
    path('finance/<int:current_id>/', v.single_depencegain_view),
    path('ventes/', v.list_ventes_view),
    path('ventes/<int:current_id>/', v.single_vente_view),
    path('notifications/', v.notification_view),
    path('users/', v.users_view),
    path('production/', v.production_view),
    path('production/<int:current_id>/', v.single_prod_view),
    path('dash/gains/', v.gain_reports_view),
    path('impression/', v.impression_view),
    path('impression/<int:current_id>/', v.single_imp_view),
    path('commandes/', v.commandes_view),
    path('commandes/<int:current_id>/', v.single_commande_view),
    path('expire/', v.expire_view),

]


