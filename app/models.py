from django.db import models
import datetime,json
from datetime import datetime as dt

# Create your models here.

class produit(models.Model):
    class p_categorie(models.TextChoices):
        VENOISERIE = 'Viennoiserie' 
        PATISSERIE = "Patisserie"
        BS = 'Boisson chaude'
        BF = 'Boisson fraiche'
        SP = 'Suplément'
        SALE = 'Salé'
        BOISSON = 'Boisson'
        GATEAUSEC ="Gateau sec"
        DIVERS = 'Divers'
    nom = models.CharField(max_length=30,null=True)
    prix = models.FloatField(max_length=10,null=True)
    categorie = models.CharField(max_length=30,
        choices=p_categorie.choices,
        default=p_categorie.PATISSERIE,
    )
    quantite = models.FloatField(max_length=100,null=True)
    vendu = models.FloatField(max_length=10,null=True,default=0)
    date_dernier_ajout = models.DateField(default=datetime.date.today)
    minimum = models.FloatField(max_length=100,null=True)
    prix_achat = models.FloatField(max_length=10,null=True)
     
class ligne_commande(models.Model):
    produit = models.ForeignKey(produit,on_delete=models.CASCADE)
    quantite = models.IntegerField(default=1)

    def price(self):
        return self.produit.prix*self.quantite     


class vente(models.Model):

    commandes = models.ManyToManyField(ligne_commande) 
    date_commande=models.DateField(default=datetime.date.today,)
    heure = models.DateTimeField(default=dt.now)
    tt_prix = models.FloatField(default=0)
    by = models.TextField(default="Aucun")


    def total_price(self):
        tt_price=0.0
        for lc in self.commandes.all():
            tt_price += lc.price()
        return tt_price    
   
    """
    
    def __str__(self) -> str:
        return self.client.client_firstname +" "+ self.client.client_familyname + " "+ "Cmd({})".format(self.id)

    """

class element(models.Model):
    class e_categorie(models.TextChoices):
        VENOISERIE = 'Vénoiserie' 
        PATISSERIE = "Patisserie"
        SALE = 'Salé'
        DIVERS = 'Divers'
    nom = models.CharField(max_length=30,null=True)
    prix_u = models.FloatField(max_length=10,null=True)
    prix_tt= models.FloatField(max_length=10,null=True)
    categorie = models.CharField(max_length=30,
        choices=e_categorie.choices,
        default=e_categorie.DIVERS,
    )
    quantite = models.FloatField(max_length=10,null=True)
    utilise = models.FloatField(max_length=10,null=True,default=0)
    date_dernier_ajout = models.DateField(default=datetime.date.today)
    minimum = models.FloatField(max_length=100,null=True)


class dépence_gain(models.Model):
    class types(models.TextChoices):
        DEPENCE = 'Dépence'
        GAIN = 'Gain'
    type = models.CharField(max_length=30,choices=types.choices,default=types.DEPENCE)
    date = models.DateField(default=datetime.date.today)   
    heure = models.DateTimeField(default=dt.now)
    montant = models.FloatField()
    motif = models.CharField(max_length=300)    
    by=models.TextField(default="/")


class product_stat(models.Model):
    product=models.ForeignKey(produit,on_delete=models.CASCADE)   
    date = models.DateField(default=datetime.date.today)
    quantity = models.IntegerField(default=0)
    def set_quantity(self):
        self.quantity=self.product.product_quantity    



class notif(models.Model):
    class etats(models.TextChoices):
        LU = 'Lu'
        NONLU = 'Non lu'
    content = models.CharField(max_length=300)
    date = models.DateField(default=datetime.date.today)
    etat = models.CharField(max_length=300,choices=etats.choices,default=etats.NONLU)



class ligne_produit (models.Model):
    produit=models.ForeignKey(element,on_delete=models.CASCADE)
    quantite=models.IntegerField()


class production (models.Model):
    class status(models.TextChoices):
        APRODUIRE = 'A Produire' 
        ENCOURS = "En cours"
        TERMINE = 'Terminé'

    nom=models.CharField(max_length=100)
    quantite=models.IntegerField()
    statut = models.CharField(max_length=30,
        choices=status.choices,
        default=status.APRODUIRE,
    )
    produits_requis=models.ManyToManyField(ligne_produit)
    produits_manquants=models.TextField(default='')
    
    def set_liste(self, liste):
        self.produits_manquants = json.dumps(liste)

    def get_liste(self):
        return json.loads(self.produits_manquants)
    

    def push(self):
        list_prmq=[]
        for c in self.produits_requis.all():
            if c.produit.quantite < c.quantite:
                mq = c.quantite - c.produit.quantite
                data = {"nom":c.produit.nom,"quantite":c.produit.quantite,"manquant":mq}
                list_prmq.append(data)
        self.set_liste(list_prmq)    
        self.save()  
                        
                    
                

    
    def etat(self):
        pret="Prêt"
        if self.statut == production.status.APRODUIRE:
            for c in self.produits_requis.all():
                if c.produit.quantite < c.quantite:
                    pret = "Produits manquants"
            if self.statut == 'Terminé' :
                pret="Prêt"         
        return pret



def refresh_prod():
    prods = production.objects.all()
    for prod in prods:
        prod.etat()
        prod.push()

class ligne_commande_stat(models.Model):
    produit = models.ForeignKey(produit,on_delete=models.CASCADE)
    quantite = models.IntegerField(default=0)


class impression(models.Model):
    nom = models.TextField()    
    details = models.TextField()
    code_bar = models.TextField(default="000000000000")
    expiration = models.DateField(null=True,default=None)

class cmd(models.Model):
    class status(models.TextChoices):
        DELIVRE = 'Delivré' 
        NONDELIVRE = "Non delivré"
    designation = models.CharField(max_length=100)
    client = models.CharField(max_length=100)
    prix = models.FloatField(max_length=10,null=True)
    prix_achat = models.FloatField(max_length=10,default=0)
    acompte = models.FloatField(max_length=10,null=True)
    by = models.CharField(max_length=100)
    date_commande = models.DateField(default=datetime.date.today,)
    heure = models.DateTimeField(default=dt.now)
    statut = models.CharField(max_length=30,
            choices=status.choices,
            default=status.NONDELIVRE,
        )
        