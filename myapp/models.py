from django.db import models
from django.utils import timezone  


class Etranger(models.Model) : 
    id = models.CharField(max_length=100,primary_key=True)
    nom = models.CharField(max_length=100)
    def __str__(self) : 
        return self.id
    
class StagiaireAdmin(models.Model) : 
    cin = models.CharField(max_length=8)
    prenom = models.CharField(max_length=50)
    nom = models.CharField(max_length=50)
    tel = models.CharField(max_length=20)
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=100)
    gouv = models.CharField(max_length=20)
    code_postal = models.CharField(max_length=10)
    code_qr = models.CharField(max_length=4)
    email = models.EmailField()
    def __str__(self) : 
        return self.cin
    

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
