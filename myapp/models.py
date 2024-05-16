from django.db import models
from django.utils import timezone  


class Etranger(models.Model) : 
    id = models.CharField(max_length=100,primary_key=True)
    nom = models.CharField(max_length=100)
    def __str__(self) : 
        return self.id


    

class Stagiaire(models.Model) : 
    cin = models.CharField(max_length=8)
    password = models.CharField(max_length=255)
    confirm_passord = models.CharField(max_length=255)
    def __str__(self) : 
        return self.cin
    
class ResrvationEtranger(models.Model) : 
    temps = models.DateTimeField()
    etranger = models.ForeignKey(Etranger, on_delete= models.CASCADE,related_name="reservation_ET")
    petit_dej = models.BooleanField(default=False)
    repas_midi = models.BooleanField(default = False)
    diner = models.BooleanField(default = False)
    nombre_personne = models.IntegerField()

    def __str__(self) : 
        return self.etranger.id
    
    
    
class ResrvationStagiaire(models.Model) : 
    temps = models.DateTimeField()
    stagiaire = models.ForeignKey(Stagiaire, on_delete= models.CASCADE,related_name="reservation_set")
    petit_dej = models.BooleanField(default=False)
    repas_midi = models.BooleanField(default = False)
    def __str__(self) : 
        return self.stagiaire.cin
    
class TokenPourStagiaire(models.Model) : 
    token = models.CharField(max_length = 255)
    user = models.ForeignKey(Stagiaire, on_delete= models.CASCADE,related_name="tokens_set")
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self) : 
        return self.user.cin
    
class PasswordResetToken(models.Model) : 
    token = models.CharField(max_length = 255)
    user = models.ForeignKey(Stagiaire, on_delete=models.CASCADE, related_name='password_reset_tokens')
    validity = models.DateTimeField(default=timezone.now) 
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self) : 
        return self.user.cin
    
class SousAdmin(models.Model) : 
    identifiant = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    def __str__(self) : 
        return self.identifiant
    
class Specialite(models.Model) : 
    code_spec = models.CharField(max_length=1000, unique=True)
    nom_spec_ar = models.CharField(max_length=100)
    type = models.CharField(max_length=50)

class Group(models.Model) : 
    numgr = models.CharField(unique=True,max_length=10)
    specialite = models.ForeignKey(Specialite ,on_delete = models.CASCADE ,related_name="spec")
    
class StagiaireAdmin(models.Model) : 
    cin = models.CharField(max_length=8, unique=True)
    prenom = models.CharField(max_length=50)
    nom = models.CharField(max_length=50)
    tel = models.CharField(max_length=20)
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=100)
    gouv = models.CharField(max_length=20)
    code_postal = models.CharField(max_length=10)
    group = models.ForeignKey(Group , on_delete=models.CASCADE , related_name="idjvpo")
    email = models.EmailField()
    image = models.ImageField(upload_to='categories/')
    def __str__(self) : 
        return self.cin

class Matiere(models.Model) : 
    id = models.CharField(max_length=200, primary_key=True)
    module = models.CharField(max_length=100)
    titre_module = models.CharField(max_length=100)
    nb_heure = models.IntegerField()
    type = models.CharField(max_length=100,choices=[
        ('Spécifique','Spécifique'),
        ('Générale','Générale')
    ])
    specialite = models.ForeignKey(Specialite ,on_delete = models.CASCADE ,related_name="spec1")
    
class Emploi(models.Model) : 
    group = models.OneToOneField(Group , on_delete=models.CASCADE,related_name="ygiuo")
    photo = models.ImageField(upload_to='categories/')
class Demande(models.Model) : 
    nom_prenom = models.CharField(max_length=200)
    cin = models.CharField(max_length=8)
    email = models.EmailField()
    cause = models.CharField(max_length=500)

    
class Evaluation(models.Model) : 
    matiere = models.ForeignKey(Matiere , on_delete=models.CASCADE , related_name="efv")
    note = models.CharField(max_length=6)
    stagiaire = models.ForeignKey(Stagiaire,on_delete=models.CASCADE , related_name="er")
    
    
class PeriodeExamen(models.Model) : 
    id = models.CharField(primary_key=True,max_length=2)
    libele_periode = models.CharField(max_length=100)
    
class Abscence(models.Model) : 
    stagiaire = models.ForeignKey(Stagiaire,on_delete=models.CASCADE , related_name="eouviho")
    matiere = models.ForeignKey(Matiere , on_delete=models.CASCADE , related_name="rv")
    nb_heure = models.IntegerField()
    periode = models.ForeignKey(PeriodeExamen , on_delete=models.CASCADE, related_name="oiev")
    

    
    