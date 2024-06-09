from django.shortcuts import render,redirect,get_object_or_404
from .models import produit, vente, ligne_commande, element, dépence_gain, product_stat, cmd,  notif, production, ligne_produit, refresh_prod, ligne_commande_stat, impression
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
import datetime, json
from datetime import date 
from django.http import HttpResponse
import os

   

def home_view(request):
    return render(request,"app/index.html")

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password= request.POST.get("pass")
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('/dash/')  
        else:
            return render(request,'app/login.html',{'message':'erreur : réssayez'})  
    else:
        return render(request,'app/login.html')  

def logout_view(request):
    logout(request)
    return redirect('/') 


def make_notif():
    products = produit.objects.all()
    elements = element.objects.all()
    for p in products :
        if p.quantite <= p.minimum :
            c = "Le Produit " + str(p.nom) + " est bientot en rupture : quantité disponible ("+str(p.quantite)+")"
            if notif.objects.filter(content=c):
                pass
            else:            
                notif.objects.create(content=c)

    for e in elements :
        if e.quantite <= e.minimum :
            c = "Le stock " + str(e.nom) + " est bientot en rupture : quantité disponible ("+str(e.quantite)+")"
            if notif.objects.filter(content=c):
                pass
            else:            
                notif.objects.create(content=c)



def presentoire_view(request):

    active_link = 'presentoire'
    if not request.user.is_authenticated:
        return redirect("/login/")
    if not request.user.is_superuser and not request.user.is_staff :
        return redirect("/commercial/")  
         
    make_notif()
    notif_count = notif.objects.filter(etat=notif.etats.NONLU).count()
    produits = produit.objects.all()  
    categories = dict(produit.p_categorie.choices)    
    if request.method =='GET':
        return render(request,'app/presentoire.html',{'active_link':active_link,'produits':produits,'categories':categories, "notif_count":notif_count})
    else:
        nom=request.POST.get('nom')
        prix=request.POST.get('prix')
        categorie=request.POST.get('categorie')
        quantite=request.POST.get('quantite')
        min=request.POST.get('min')
        prix_achat = float(request.POST.get('prix_achat'))      
        if produit.objects.filter(nom=nom):
            message = "Il existe déja un produit qui a le même nom !"
            return render(request,'app/presentoire.html',{'active_link':active_link,'produits':produits,'categories':categories, "notif_count":notif_count,"message":message})
        else:
            produit.objects.create(nom=nom,prix=prix,categorie=categorie,quantite=quantite,minimum=min,prix_achat=prix_achat)
            return redirect('/presentoire')

def single_produit_view(request,current_id):
    active_link = 'presentoire'
    if not request.user.is_authenticated:
        return redirect("/login/")
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("/commercial/")  
        
    make_notif()
    notif_count = notif.objects.filter(etat=notif.etats.NONLU).count()    
    if request.method == 'GET':
        if 'ajout' in request.GET.get('action'):
            if request.GET.get('ajout_q'):
             plus = request.GET.get('ajout_q')
            else:
                 plus=0
            id = current_id
            o = produit.objects.get(id=current_id)
            o.quantite += float(plus)
            o.save()
            product_stat.objects.create(product=produit.objects.get(pk=id),quantity=produit.objects.get(pk=id).quantite)       
            return redirect('/presentoire')
        elif 'details' in request.GET.get('action') :
            o = produit.objects.get(id=current_id)
            categories = dict(produit.p_categorie.choices)
            return render(request,'app/single_produit.html',{'active_link':active_link,'produit': o,'categories':categories, "notif_count":notif_count})
    else:
        if 'Sauvegarder' in request.POST:
            id=request.POST.get('id') 
            nom = request.POST.get('nom') 
            prix = request.POST.get('prix') 
            categorie = request.POST.get('categorie')
            quantite = request.POST.get('quantite') 
            min = request.POST.get('min') 
            prix_achat = float(request.POST.get('prix_achat'))
            o = produit.objects.get(id=current_id)
            categories = dict(produit.p_categorie.choices)
            if produit.objects.filter(nom=nom) and nom != o.nom:
                message = "Il existe déja un produit qui a le même nom !"
                return render(request,'app/single_produit.html',{'active_link':active_link,'produit': o,'categories':categories, "notif_count":notif_count,"message":message})
            else:
                produit.objects.filter(id=id).update(nom=nom,prix=prix,categorie=categorie,quantite=quantite,minimum=min,prix_achat=prix_achat)
                return redirect('/presentoire')
        else :
            id=request.POST.get('id') 
            i=produit.objects.get(id=id)
            i.delete()  
            return redirect('/presentoire')          


def commercial_view(request): 
    active_link = 'commercial'
    if not request.user.is_authenticated:
        return redirect("/login/")
        
    make_notif()
    notif_count = notif.objects.filter(etat=notif.etats.NONLU).count()    
    produits = produit.objects.all()  
    categories = dict(produit.p_categorie.choices)
    if request.method =='GET':
        return render(request,'app/commercial.html',{'active_link':active_link,'produits':produits,'categories':categories, "notif_count":notif_count})
    else:
        if (request.POST.getlist('p_id')):
            p_id_list = request.POST.getlist('p_id')
            p_quantite_list = request.POST.getlist('p_quantite')
            l=len(p_id_list)

            
            n=vente.objects.create()
            n.save()
            id_vente=n.id
            
            for i in range(l):
                pr=p_id_list[i]
                qt=int(p_quantite_list[i]) 
                pp = get_object_or_404(produit,pk=int(pr))
                e=None  
                if (qt > 0 ):
                    lc=ligne_commande.objects.create(produit=produit.objects.get(pk=int(pr)),quantite=qt)
                    lc.save()
                    lc_id=lc.id
                    prix_lc=ligne_commande.objects.get(pk=lc_id).price()       
                    e=vente.objects.get(pk=id_vente)
                    e.commandes.add(ligne_commande.objects.get(pk=lc_id))
                    e.save()
                    pr_qt=pp.quantite-int(qt)
                    produit.objects.filter(pk=int(pr)).update(quantite=pr_qt)
                    e.tt_prix+=prix_lc
                    e.save()
                    product_stat.objects.create(product=produit.objects.get(pk=int(pr)),quantity=produit.objects.get(pk=int(pr)).quantite)       
            if e:
                e.by = request.user.first_name + request.user.last_name
                e.save()
                montant=e.tt_prix
                motif=str(" Vente Numero (" + str(e.id) + ")")
                tpg= dépence_gain.types.GAIN
                dépence_gain.objects.create(type=tpg,motif=motif,montant=montant,by=request.user.username) 
        return redirect('/commercial')

def labo_view(request): 
    active_link = 'labo'
    if not request.user.is_authenticated:
        return redirect("/login/")
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("/commercial/")  
        
    make_notif()
    notif_count = notif.objects.filter(etat=notif.etats.NONLU).count()
    elements = element.objects.all()
    if request.method == "GET":  
        return render (request,'app/labo.html',{'active_link':active_link,"elements": elements, "notif_count":notif_count})       
            
    else :
        nom = request.POST.get('nom')   
        prix_u = request.POST.get('prix')         
        prix_tt = request.POST.get('prix_tt') 
        quantite = request.POST.get('quantite') 
        min=  request.POST.get('min')
        if element.objects.filter(nom=nom):
            message="Il existe déja un produit qui a le même nom !"
            return render (request,'app/labo.html',{'active_link':active_link,"elements": elements, "notif_count":notif_count,"message":message})   
        else:
            element.objects.create(nom=nom,prix_u=prix_u,prix_tt=prix_tt,quantite=quantite,minimum=min)
            tpg= dépence_gain.types.DEPENCE
            motif = "Approvisionement (" + nom + ") * (" + str(quantite) + ")" 
            p= float(prix_u)*float(quantite)
            if float(prix_tt)>0 :
                dépence_gain.objects.create(type=tpg,motif=motif,montant=float(prix_tt))
            else:    
                dépence_gain.objects.create(type=tpg,motif=motif,montant=p)
            return redirect("/labo")
    
def single_labo_view(request,current_id): 
    active_link = 'labo'
    if not request.user.is_authenticated:
        return redirect("/login/")
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("/commercial/")  
        
    make_notif()
    notif_count = notif.objects.filter(etat=notif.etats.NONLU).count()
    o = element.objects.get(id=current_id)
    if request.method == 'GET':
        if 'ajout' in request.GET.get('action') and request.GET.get('ajout_q'):
            quantite = request.GET.get('ajout_q')
            id = current_id
            o = element.objects.get(id=current_id)
            o.quantite += float(quantite)
            o.save()
            tpg= dépence_gain.types.DEPENCE
            motif = "Approvisionement (" + o.nom + ") * (" + str(quantite) + ")" 
            p= float(o.prix_u)*float(quantite)            
            dépence_gain.objects.create(type=tpg,motif=motif,montant=p)
            return redirect('/labo')
        
        elif 'utiliser' in request.GET.get('action') and request.GET.get('ajout_q') :
            quantite = request.GET.get('ajout_q')
            id = current_id
            o = element.objects.get(id=current_id)
            o.quantite -= float(quantite)
            o.utilise += float(quantite)
            o.save()
            return redirect('/labo')
        
        elif 'details' in request.GET.get('action') :
            o = element.objects.get(id=current_id)
            return render(request,'app/single_labo.html',{'active_link':active_link,'element': o, "notif_count":notif_count})
        else:
            return redirect('/labo/')
    else:
        if 'Sauvegarder' in request.POST:
            id=request.POST.get('id') 
            nom = request.POST.get('nom') 
            prix = request.POST.get('prix') 
            quantite = request.POST.get('quantite') 
            quantite_m = request.POST.get('quantite_m') 
            q = element.objects.get(nom=nom)
            if q and q.id != current_id:
                message="Il existe déja un produit qui a le même nom !"
                return render (request,'app/single_labo.html',{'active_link':active_link,'element': o, "notif_count":notif_count,"message":message})
            else:
                element.objects.filter(id=id).update(nom=nom,prix_u=prix,quantite=quantite,minimum=quantite_m)
                return redirect('/labo')
        else :
            id=request.POST.get('id') 
            i=element.objects.get(id=id)
            i.delete()  
            return redirect('/labo')    
        

def finance_view(request): 
    active_link = 'finance'
    if not request.user.is_authenticated:
        return redirect("/login/")
    if not request.user.is_superuser:
        return redirect("/commercial/")  
        
    make_notif()
    notif_count = notif.objects.filter(etat=notif.etats.NONLU).count()    
    gain_taux=0
    dépence_taux=0
    if request.method == 'POST':
        if 'Dépence'in request.POST:
            depgain= dépence_gain.objects.filter(type='Dépence')
            return render(request,'app/finance.html',{'active_link':active_link,'depgain':depgain, "notif_count":notif_count})            
        elif 'Gain'in request.POST:
            depgain= dépence_gain.objects.filter(type='Gain')
            return render(request,'app/finance.html',{'active_link':active_link,'depgain':depgain, "notif_count":notif_count})  
        elif 'filtrer'in request.POST:
            date_de=request.POST.get('date_de')
            date_a=request.POST.get('date_a')
            depgain= dépence_gain.objects.filter(date__gte=date_de,date__lte=date_a)
            for dp in depgain:
                if dp.type == 'Dépence':
                    dépence_taux += dp.montant
                elif dp.type == 'Gain':
                    gain_taux+= dp.montant    
            bénef=gain_taux-dépence_taux
            return render(request,'app/finance.html',{'gain_taux':gain_taux,'dépence_taux':dépence_taux,'active_link':active_link,'depgain':depgain,'date_de':date_de,'date_a':date_a,'bénef':bénef, "notif_count":notif_count})
        elif 'ajouter' in request.POST:
            date = request.POST.get('date')
            type = request.POST.get('select_type')
            montant = request.POST.get('montant')
            motif = request.POST.get('motif')
            dépence_gain.objects.create(type=type,date=date,montant=montant,motif=motif)
            return redirect('/finance/') 
    else:        
        depgain= dépence_gain.objects.all()
        
        for dp in depgain:
            if dp.type == 'Dépence':
                dépence_taux+= dp.montant
            else:
                gain_taux += dp.montant
        types = dépence_gain.types.choices
        bénef=gain_taux-dépence_taux
        reversed_depgain = depgain.reverse()

        return render(request,'app/finance.html',{'active_link':active_link,'depgain':reversed_depgain,'bénef':bénef,'types':types, "notif_count":notif_count})


def single_depencegain_view(request,current_id):
    active_link = 'finance'
    if not request.user.is_authenticated:
        return redirect("/login/")
    if not request.user.is_superuser:
        return redirect("/commercial/")  
        
    make_notif()
    notif_count = notif.objects.filter(etat=notif.etats.NONLU).count()    
    if request.method == 'POST':
        if 'sauvegarder' in request.POST:
            if request.POST.get('date'):
                date = request.POST.get('date')
                type = request.POST.get('select_type')
                montant = request.POST.get('montant')
                motif = request.POST.get('motif')
                dépence_gain.objects.filter(pk=current_id).update(date=date,type=type,montant=montant,motif=motif) 
                return redirect('/finance/') 
            else:
                type = request.POST.get('select_type')
                montant = request.POST.get('montant')
                motif = request.POST.get('motif')
                dépence_gain.objects.filter(pk=current_id).update(type=type,montant=montant,motif=motif) 
                return redirect('/finance/') 
        elif 'supprimer' in request.POST:
            dépence_gain.objects.filter(pk=current_id).delete()
            return redirect('/finance/')
    else:
        depgain= dépence_gain.objects.filter(pk=current_id)
        types=dépence_gain.types.choices
        return render(request,'app/single_depence_gain.html',{'active_link':active_link,'depgain':depgain,'types':types, "notif_count":notif_count})





def dashboard_view(request):
    active_link = 'dashboard'
    if not request.user.is_authenticated:
        return redirect("/login/")
    if not request.user.is_superuser:
        return redirect("/commercial/")  

    rd='app/dashboard.html'  

    make_notif()
    notif_count = notif.objects.filter(etat=notif.etats.NONLU).count()    
    date_aujourdhui = date.today()
    gain_auj=0
    for c in dépence_gain.objects.filter(type=dépence_gain.types.GAIN,date=date_aujourdhui):
        gain_auj+=c.montant
    dep_auj=0
    for c in dépence_gain.objects.filter(type=dépence_gain.types.DEPENCE,date=date_aujourdhui):
        dep_auj+=c.montant   
    dico=[]
    for u in User.objects.all():
        for c in dépence_gain.objects.filter(type=dépence_gain.types.GAIN,date=date_aujourdhui):
            if c.by == u.username:
                for item in dico:
                    if item["username"] == u.username:
                         item["gain"] +=c.montant 
                         break
                else:
                    new_item = {"username": u.username, "gain": c.montant} 
                    dico.append(new_item)


    if request.method == 'POST':
        if 'submit_product' in request.POST:
            
            pro_id = request.POST.get('select_produit')
            if pro_id :
                pr_stat=product_stat.objects.filter(product=produit.objects.get(pk=int(pro_id)))
                pr=produit.objects.get(pk=pro_id)
                products=produit.objects.all()
                count_products=produit.objects.filter(quantite__gte=1).count()
                
                count_ventes=vente.objects.filter(date_commande=date_aujourdhui).count()
                return render(request,rd,{"dico":dico,"active_link":active_link,"gain_auj":gain_auj,"dep_auj":dep_auj,'products':products,'pr_stat':pr_stat,'pr':pr,'count_products':count_products,'count_ventes':count_ventes, "notif_count":notif_count})
            else:
                return redirect("/dash/")
        elif 'produits' in request.POST:
            pr_stat=product_stat.objects.filter(product=produit.objects.get(pk=2))
            pr=produit.objects.get(pk=2)
            products=produit.objects.all()
            count_products=produit.objects.filter(quantite__gte=1).count()
            date_aujourdhui = date.today()
            count_ventes=vente.objects.filter(date_commande=date_aujourdhui).count()
            return render(request,rd,{"dico":dico,"active_link":active_link,"gain_auj":gain_auj,"dep_auj":dep_auj,'products':products,'pr_stat':pr_stat,'pr':pr,'count_products':count_products,'count_ventes':count_ventes, "notif_count":notif_count})

    else:
        products=produit.objects.all()
        count_products=produit.objects.filter(quantite__gte=1).count()
        date_aujourdhui = date.today()
        count_ventes=vente.objects.filter(date_commande=date_aujourdhui).count()
        return render(request,rd ,{"dico":dico,"active_link":active_link,"gain_auj":gain_auj,"dep_auj":dep_auj,'products':products,'count_products':count_products,'count_ventes':count_ventes, "notif_count":notif_count})      
    


def list_ventes_view(request):
    active_link = 'commercial'
    if not request.user.is_authenticated:
        return redirect("/login/")
 
        
    make_notif()
    notif_count = notif.objects.filter(etat=notif.etats.NONLU).count()    
    ventes = vente.objects.all()
    if request.method == 'GET':
        return render(request,"app/ventes.html",{"active_link":active_link,"ventes":ventes, "notif_count":notif_count})    

def single_vente_view(request,current_id):
    active_link = 'commercial'
    if not request.user.is_authenticated:
        return redirect("/login/")

        
    make_notif()
    notif_count = notif.objects.filter(etat=notif.etats.NONLU).count()    
    id=current_id
    ventes = vente.objects.filter(id=id)
    return render (request,"app/single_vente.html",{"active_link":active_link,"vente":ventes, "notif_count":notif_count})


def notification_view(request):
    if not request.user.is_authenticated:
        return redirect("/login/")
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("/commercial/")  
        
    make_notif()
    notif_count = notif.objects.filter(etat=notif.etats.NONLU).count()   
    notifs = notif.objects.all() 
    if request.method == 'POST':
        if "lu" in request.POST:
            notif.objects.all().update(etat=notif.etats.LU) 
            return redirect("/notifications/")
        else:
            notif.objects.all().delete()
            return redirect("/notifications/")
    
    else:
        return render(request,"app/notifications.html",{"notifs":notifs, "notif_count":notif_count})
          
    

def users_view(request):
    if not request.user.is_authenticated:
        return redirect("/login/")
    if not request.user.is_superuser:
        return redirect("/commercial/")  
        
    make_notif()
    notif_count = notif.objects.filter(etat=notif.etats.NONLU).count() 
    if request.method=="POST":
        if "ajouter" in request.POST:
            nom = request.POST.get('name')
            prenom = request.POST.get('l_name')
            email = request.POST.get('email')
            password = request.POST.get('pass')
            tp = request.POST.get('type')
            if tp=='Admin':
                v=True
                t=True
            elif tp=='Responsable':
                v=True
                t=False
            else:
                t=False
                v=False    
            user = User.objects.create_user(
            username=email,
            password=password,
            first_name=nom,
            last_name=prenom,
            is_superuser=t,
            is_staff =v
             )      
            user.save()  
            return redirect('/users/')
        else:
            id = request.POST.get('id')
            User.objects.filter(id=id).delete()
            return redirect('/users/')
    else:
        users = User.objects.all()
        return render (request,"app/users.html",{"users":users,"notif_count":notif_count})    
    

def production_view(request):
    if not request.user.is_authenticated:
        return redirect("/login/")
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("/commercial/")  
        
    make_notif()
    notif_count = notif.objects.filter(etat=notif.etats.NONLU).count() 
    active_link = 'production'
    refresh_prod()
    produits=element.objects.all()
    status=production.status.choices

    if request.method == "POST" :
        if 'button' in request.POST:
            print (request.POST)
            if request.POST.get('article') and request.POST.get('quantity_pr') and request.POST.get('select_statut'):
                nom = request.POST.get('article')
                quantite = request.POST.get('quantity_pr')
                statut = request.POST.get('select_statut')
                list_produit= request.POST.getlist('item_id')
                list_quantite= request.POST.getlist('item_quantity')
                q=production.objects.create(nom=nom,quantite=quantite,statut=statut)
                q.save()
                prod_id=q.id
                obj_prod=get_object_or_404(production,pk=prod_id)
                e = len(list_produit)
                for i in range(e) :
                    lp=ligne_produit.objects.create(produit=element.objects.get(pk=list_produit[i]),quantite=float(list_quantite[i]))
                    lp.save()
                    lp_id = lp.id
                    obj_prod.produits_requis.add(ligne_produit.objects.get(pk=lp_id))
                
                obj_prod.push()
                return redirect('/production/')
            
        elif 'aproduire' in request.POST:
                prods = production.objects.filter(statut='A Produire')   
                return render(request,'app/production.html',{'active_link':active_link,"notif_count":notif_count,"produits":produits,"status":status,"prods":prods})
        elif 'encours' in request.POST:
                prods = production.objects.filter(statut='En cours')   
                return render(request,'app/production.html',{'active_link':active_link,"notif_count":notif_count,"produits":produits,"status":status,"prods":prods})
        elif 'terminé' in request.POST:
                prods = production.objects.filter(statut='Terminé')   
                return render(request,'app/production.html',{'active_link':active_link,"notif_count":notif_count,"produits":produits,"status":status,"prods":prods})   
    else:
        prods = production.objects.all()
        return render(request,'app/production.html',{'active_link':active_link,"notif_count":notif_count,"produits":produits,"status":status,"prods":prods})
    

def single_prod_view(request,current_id):
    if not request.user.is_authenticated:
        return redirect("/login/")
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("/commercial/")  
        
    make_notif()
    notif_count = notif.objects.filter(etat=notif.etats.NONLU).count()     
    active_link = 'production'
    current_prod = production.objects.get(pk=current_id) 
    status= production.status.choices 
    if request.method == 'POST':
        product_name=request.POST.get('Produit')
        product_quantity=request.POST.get('quantity')

        if 'sauvegarder' in request.POST:
            if request.POST.get('select_statut'):
                select_statut=request.POST.get('select_statut')
            
                if select_statut == 'Terminé':
                        production.objects.filter(pk=current_id).update(statut=select_statut)
                        if produit.objects.filter(nom=product_name) :
                            obj_product=produit.objects.get(nom=product_name)
                            qt=obj_product.quantite
                            qt_final=qt+int(product_quantity)
                            produit.objects.filter(nom=product_name).update(quantite=qt_final)
                            product_stat.objects.create(product=produit.objects.get(nom=product_name),quantity=produit.objects.get(nom=product_name).quantite)
                        else:
                            q=produit.objects.create(nom=product_name,quantite=product_quantity,prix=0,categorie=produit.p_categorie.DIVERS,minimum=0)
                            q.save()
                            p_id=q.id   
                            product_stat.objects.create(product=produit.objects.get(pk=p_id),quantity=produit.objects.get(pk=p_id).quantite)

                elif select_statut == 'En cours':
                        if production.objects.get(pk=current_id).etat() == 'Prêt':
                            production.objects.filter(pk=current_id).update(statut=select_statut)
                            product_ligne=production.objects.get(pk=current_id).produits_requis.all()
                            for pr in  product_ligne:
                                pr_id = pr.produit.id
                                prod_quantity = pr.quantite
                                pr_quantity = pr.produit.quantite
                                final_quantity = pr_quantity - prod_quantity
                                element.objects.filter(pk=pr_id).update(quantite=final_quantity)
            return redirect('/production/')
        else:
            production.objects.filter(pk=current_id).delete()
            return redirect('/production/')
    else:
        if current_prod.etat() == 'Produits manquants':
            produit_manquants = current_prod.get_liste()
        else:
            produit_manquants=''    
        produits = produit.objects.all()
        
        return render(request,'app/single_prod.html',{'prod':current_prod,"notif_count":notif_count,'status':status,'produit_manquants':produit_manquants,'produits':produits,'active_link':active_link})


def gain_reports_view(request):
    if not request.user.is_authenticated:
        return redirect("/login/")
    if not request.user.is_superuser:
        return redirect("/commercial/")      
    make_notif()
    notif_count = notif.objects.filter(etat=notif.etats.NONLU).count()     
    active_link = 'dashboard'
    categories = produit.p_categorie
    if request.method == 'GET':
        return render (request,"app/gain_reports.html",{"categories":categories,"notif_count":notif_count})
    else:
        cat = request.POST.get("categorie")
        date_de = request.POST.get("date_de")
        date_a = request.POST.get("date_a")
        cmds = cmd.objects.filter(date_commande__gte=date_de,date_commande__lte=date_a)
        ventes = vente.objects.filter(date_commande__gte=date_de,date_commande__lte=date_a)
        gains=0
        vendu=0
        cmd_stat=[]
        ligne_commande_stat.objects.all().delete()
        if cat == "Commandes":
            for cm in cmds:
                if cm.prix_achat > 0:
                    gains += cm.prix - cm.prix_achat
                    vendu += 1
                else :
                    gains +=  cm.prix 
                    vendu += 1 
        else:
            for v in ventes:
                for lp in v.commandes.all():
                    if lp.produit.categorie == cat:
                        if ligne_commande_stat.objects.filter(produit=produit.objects.get(id=lp.produit.id)):
                            query = ligne_commande_stat.objects.get(produit=produit.objects.get(id=lp.produit.id))
                            query.quantite += lp.quantite
                            query.save()                      
                        else:
                            ligne_commande_stat.objects.create(produit=produit.objects.get(id=lp.produit.id),quantite=lp.quantite)    
                        if lp.produit.prix_achat :
                            g=(lp.produit.prix-lp.produit.prix_achat) * lp.quantite
                        else:    
                            g = lp.produit.prix * lp.quantite
                        gains += g
                        vendu += lp.quantite 
            cmd_stat = ligne_commande_stat.objects.all().order_by('-quantite')
        return render(request,"app/gain_reports.html",{"active_link":active_link,"notif_count":notif_count,"categories":categories,"gain":gains,"vendu":vendu,"cmd_stat":cmd_stat})
    
def impression_view(request):
    if not request.user.is_authenticated:
        return redirect("/login/")
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("/commercial/")  
        
    make_notif()
    notif_count = notif.objects.filter(etat=notif.etats.NONLU).count()     
    active_link = 'impression'
    imps = impression.objects.all()    
    if request.method == 'POST':
        nom = request.POST.get('nom') 
        details = request.POST.get('details') 
        bar = request.POST.get('bar') 
        impression.objects.create(nom=nom,details=details,code_bar=bar)
        return redirect('/impression/')
    else:
        return render(request,'app/impression.html',{"active_link":active_link,"imps":imps,"notif_count":notif_count})

def single_imp_view(request,current_id):
    if not request.user.is_authenticated:
        return redirect("/login/")
    if not request.user.is_superuser and not request.user.is_staff:
        return redirect("/commercial/")  
        
    make_notif()
    notif_count = notif.objects.filter(etat=notif.etats.NONLU).count()     
    active_link = 'impression'
    imp=impression.objects.get(id=current_id)
   
    if request.method == 'POST':
        if 'Sauvegarder' in request.POST:
            nom = request.POST.get('nom') 
            details = request.POST.get('details') 
            bar = request.POST.get('bar') 
            impression.objects.filter(id=current_id).update(nom=nom,details=details,code_bar=bar)
            return redirect('/impression/'+str(current_id))
        else:
            impression.objects.filter(id=current_id).delete()
            return redirect('/impression/')
    else:
        return render(request,'app/single_imp.html',{"active_link":active_link,"imp":imp,"notif_count":notif_count})    
    

def commandes_view(request):
    active_link = 'commercial'
    if not request.user.is_authenticated:
        return redirect("/login/")
        
    make_notif()
    notif_count = notif.objects.filter(etat=notif.etats.NONLU).count()  
    
    if request.method == 'GET':
        cmds= cmd.objects.all()
        return render (request,'app/commandes.html',{"active_link":active_link,"notif_count":notif_count,'cmds':cmds})
    else:
        if 'delivré' in request.POST:
            cmds= cmd.objects.filter(statut="Delivré")
            return render (request,'app/commandes.html',{"active_link":active_link,"notif_count":notif_count,'cmds':cmds})
        elif 'nondelivré' in request.POST:
            cmds= cmd.objects.filter(statut="Non delivré")
            return render (request,'app/commandes.html',{"active_link":active_link,"notif_count":notif_count,'cmds':cmds})
        else:
            designation=request.POST.get("designation")
            client =request.POST.get("client")
            prix=request.POST.get("prix")
            acompte = request.POST.get("acompte")
            by = request.user.username
            c=cmd.objects.create(designation=designation,client=client,prix=prix,acompte=acompte,by=by)
            c.save()
            if float(acompte) > 0 :
                tp= dépence_gain.types.GAIN
                motif = "Acompte Commande ("+str(c.id)+")"
                dépence_gain.objects.create(motif=motif,montant=acompte,by=by,type=tp)
            return redirect('/commandes/')    
        

def single_commande_view(request,current_id):
    active_link = 'commercial'
    if not request.user.is_authenticated:
        return redirect("/login/")
        
    make_notif()
    notif_count = notif.objects.filter(etat=notif.etats.NONLU).count()  

    cmdc= cmd.objects.get(id=int(current_id))
    status= cmd.status.choices
    if request.method == 'GET':
        return render (request,'app/single_commande.html',{"active_link":active_link,"notif_count":notif_count,"cmd":cmdc,"status":status})
    else:
        if 'Sauvegarder' in request.POST:
            delivre=True
            if cmd.objects.get(id=current_id).statut == cmd.status.NONDELIVRE:
                delivre=False
            designation=request.POST.get("designation")
            client =request.POST.get("client")
            statut =request.POST.get("select_statut")
            cmd.objects.filter(id=current_id).update(designation=designation,client=client,statut=statut)
            if cmd.objects.get(id=current_id).statut==cmd.status.DELIVRE and not delivre:           
                motif="Commande numero ("+str(current_id)+")" 
                montant = cmd.objects.get(id=current_id).prix - cmd.objects.get(id=current_id).acompte
                tp = dépence_gain.types.GAIN
                dépence_gain.objects.create(type=tp,montant=montant,motif=motif,by=request.user.username)
            
            return redirect('/commandes/'+str(current_id))
        else : 
            cmd.objects.filter(id=current_id).delete()
            return redirect('/commandes/')
            
def expire_view(request):     
    return render(request,'app/licence.html')               
            
            
            
            
            
            