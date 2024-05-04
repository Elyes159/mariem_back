import datetime
from django.shortcuts import render
from myapp.models import ResrvationStagiaire, Stagiaire, StagiaireAdmin, TokenPourStagiaire
from django.http import  JsonResponse
import json
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, authentication_classes, permission_classes

from myapp.utils import token_response


@csrf_exempt
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def create_account(request):
    if request.method == 'POST':
        try:
            cin = request.data.get('cin')
            password = request.data.get('password')
            confirm_passord = request.data.get('confirm_passord')
            if cin and password and confirm_passord : 
                cin_stg_admin = StagiaireAdmin.objects.filter(cin = cin)
                if cin_stg_admin and (password == confirm_passord) : 
                    stagiaire =  Stagiaire.objects.create(cin = cin, password = password, confirm_passord = confirm_passord)
                    return JsonResponse({"bienvenue": "Votre compte à été creer avec succes"}, status=200)
                elif (not(cin_stg_admin) and (password == confirm_passord)) : 
                    return JsonResponse({"désolé": "Veuillez contacter l'admin"}, status=400)
                elif(cin_stg_admin and (password !=confirm_passord)) : 
                    return JsonResponse({"password probleme": "reviser votre password svp!"}, status=400)
            else : 
                return JsonResponse({"donnee manquant": "une des donnees manquante!"}, status=400)


        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format in the request body"}, status=400)

        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({"error": "An error occurred while processing the request"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt 
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def login(request):
    cin = request.data.get('cin')
    password = request.data.get('password')
    if cin:
        user1 = Stagiaire.objects.filter(cin=cin).first()
        password1 = user1.password if user1 else None
    else:
        print("haja 8alta houni")
        return JsonResponse({'error': 'data missing'}, status=400)
    if user1 :
        if password == password1:
            return token_response(user1)
        else :
            print("haja 8alta 8adi")
            return JsonResponse({'response':'mdpincorrecte'})
    else:
        return JsonResponse({'error': 'incorrect password'}, status=400)
    
    
@csrf_exempt
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def create_reservation_stagiaire(request,token):
    if request.method =="POST" : 
        token_obj = TokenPourStagiaire.objects.filter(token = token).first()
        if token_obj : 
            petit_dej = request.data.get('petit_dej')
            repas_midi = request.data.get('repas_midi')
            if repas_midi or petit_dej:
                try:
                    stagiaire = token_obj.user
                    now = datetime.datetime.now()
                    current_time_str = now.strftime('%Y-%m-%d %H:%M:%S')
                    reservation = ResrvationStagiaire.objects.create(temps=current_time_str , stagiaire = stagiaire , petit_dej = petit_dej , repas_midi = repas_midi)
                    reservation.save()
                    return JsonResponse({'message': 'Reservation created successfully'}, status=201)
                except Exception as e:
                    return JsonResponse({'error': str(e)}, status=500)
            else:
                return JsonResponse({'error': 'Datetime field is required'}, status=400)
            
@csrf_exempt
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def create_reservation_Etranger(request,code):
    if request.method =="POST" : 
        etranger = Etranger.objects.filter(id = code).first()
        if etranger : 
            petit_dej = request.data.get('petit_dej')
            repas_midi = request.data.get('repas_midi')
            diner = request.data.get('diner')
            nombre_personne = request.data.get("nombre_personne")
            if (repas_midi or petit_dej or diner) and nombre_personne:
                try:
                    
                    now = datetime.datetime.now()
                    current_time_str = now.strftime('%Y-%m-%d %H:%M:%S')
                    etranger_reserve = ResrvationEtranger.objects.filter(etranger__id = code).first()
                    print("houni")
                    if not (etranger_reserve) : 
                        reservation = ResrvationEtranger.objects.create(temps=current_time_str , etranger = etranger , petit_dej = petit_dej , repas_midi = repas_midi , diner = diner , nombre_personne = nombre_personne)
                        reservation.save()
                        return JsonResponse({'message': 'Reservation created successfully'}, status=201)
                    else : 
                        reservation = ResrvationEtranger.objects.update(temps=current_time_str , petit_dej = petit_dej , repas_midi = repas_midi , diner = diner , nombre_personne = nombre_personne)
                        return JsonResponse({'message': 'Reservation updated successfully'}, status=201)
                except Exception as e: 
                    return JsonResponse({'error': str(e)}, status=500)
            else:
                return JsonResponse({'error': 'Datetime field is required'}, status=400)



from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from .models import  Etranger, ResrvationEtranger, TokenPourStagiaire
import random
import string

@csrf_exempt
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def send_password_reset_email_with_new_password(request, email):
    if request.method == "POST":
        try:
            
            email = request.data.get('email')
            new_password = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(12))
            email_exist = StagiaireAdmin.objects.filter(email = email )
            email_subject = "Réinitialisation du mot de passe"
            print(new_password)
            email_body = f"""
            Votre nouveau mot de passe temporaire est : {new_password}

            Veuillez vous connecter avec ce mot de passe temporaire, puis changer votre mot de passe dans vos paramètres de compte.

            Ce lien est valide pendant 24 heures.

            Cordialement,

            L'équipe du site
            """
            send_mail(
                email_subject,
                email_body,
                "elyesmlik307@gmail.com",
                [email],
                fail_silently=False
            )
            password_updated = Stagiaire.objects.update(password = new_password ,confirm_passord = new_password )

        except StagiaireAdmin.DoesNotExist:
            print("Aucun objet TokenPourStagiaire trouvé pour ce token")
            return JsonResponse({"message": "Token invalide"}, status=400)

        except Exception as e:
            print(f"Erreur lors de l'envoi de l'e-mail de réinitialisation du mot de passe : {e}")
            return JsonResponse({"message": "Une erreur est survenue"}, status=500)

        else:
            return JsonResponse({"message": "Email de réinitialisation de mot de passe envoyé avec succès"}, status=200)
   
   
@csrf_exempt
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def login_etranger(request) : 
    if request.method =="POST" : 
        id = request.data.get("id")
        if id :
            etranger = Etranger.objects.filter(id = id).first()
            if etranger : 
                return JsonResponse({"success":"bienvenu!!!"},status = 200)
            else :
                return JsonResponse({"failed":"etranger not found!!!"},status = 400)
        else : 
            return JsonResponse({"failed":"entrer l'id!!!"},status = 400)
        
@csrf_exempt
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def delete_reservation(request,code):
    try:
        reservation = ResrvationEtranger.objects.filter(etranger__id = code).first()
        reservation.delete()  
        return JsonResponse({"message": "Dernière réservation supprimée avec succès"}, status=200)
    except ResrvationEtranger.DoesNotExist:
        return JsonResponse({"message": "Aucune réservation trouvée"}, status=404)
    except Exception as e:
        return JsonResponse({"message": f"Une erreur est survenue : {e}"}, status=500)
    


@csrf_exempt
@api_view(['POST', 'PUT'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def create_or_update_stagiaire(request):
    if request.method == "POST":
        cin = request.data.get("cin")
        prenom = request.data.get("prenom")
        nom = request.data.get("nom")
        tel = request.data.get("tel")
        date_naissance = request.data.get("date_naissance")
        lieu_naissance = request.data.get("lieu_naissance")
        gouv = request.data.get("gouv")
        code_postal = request.data.get("code_postal")
        code_qr = request.data.get("code_qr")
        email = request.data.get("email")
        stagiaire_admin = StagiaireAdmin.objects.create(
            cin=cin,
            prenom=prenom,
            nom=nom,
            tel=tel,
            date_naissance=date_naissance,
            lieu_naissance=lieu_naissance,
            gouv=gouv,
            code_postal=code_postal,
            code_qr=code_qr,
            email=email
        )
        stagiaire_admin.save()
        return JsonResponse({"message": "Stagiaire créé avec succès"}, status=201)
    elif request.method == "PUT":
        cin = request.data.get("cin")
        stagiaire_admin = StagiaireAdmin.objects.get(cin=cin)
        if stagiaire_admin:
            stagiaire_admin.prenom = request.data.get("prenom", stagiaire_admin.prenom)
            stagiaire_admin.nom = request.data.get("nom", stagiaire_admin.nom)
            stagiaire_admin.tel = request.data.get("tel", stagiaire_admin.tel)
            stagiaire_admin.date_naissance = request.data.get("date_naissance", stagiaire_admin.date_naissance)
            stagiaire_admin.lieu_naissance = request.data.get("lieu_naissance", stagiaire_admin.lieu_naissance)
            stagiaire_admin.gouv = request.data.get("gouv", stagiaire_admin.gouv)
            stagiaire_admin.code_postal = request.data.get("code_postal", stagiaire_admin.code_postal)
            stagiaire_admin.code_qr = request.data.get("code_qr", stagiaire_admin.code_qr)
            stagiaire_admin.email = request.data.get("email", stagiaire_admin.email)
            stagiaire_admin.save()
            return JsonResponse({"message": "Stagiaire mis à jour avec succès"}, status=200)
        else:
            return JsonResponse({"message": "Stagiaire non trouvé"}, status=404)
    else:
        return JsonResponse({"message": "Méthode non autorisée"}, status=405)

     
@csrf_exempt
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def delete_stagiaire(request,cin) : 
    if request.method =="DELETE" : 
        stagiaire_admin_efface = StagiaireAdmin.objects.filter(cin = cin).first()
        stagiaire_admin_efface.delete()
        stagiaire_efface = Stagiaire.objects.filter(cin = cin).first()
        stagiaire_efface.delete()
    else : 
         return JsonResponse({"message": "methodeeeee"}, status=404)
     
@csrf_exempt
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])    
def get_all_stagiaires(request):
    if request.method == 'GET':
        stagiaires = StagiaireAdmin.objects.all().values()  # Récupère tous les stagiaires sous forme de dictionnaires
        return JsonResponse({'stagiaires': list(stagiaires)}, safe=False)
    else:
        return JsonResponse({'message': 'Méthode non autorisée'}, status=405)
@csrf_exempt
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])    
def get_all_Etranger(request):
    if request.method == 'GET':
        stagiaires = Etranger.objects.all().values()  # Récupère tous les stagiaires sous forme de dictionnaires
        return JsonResponse({'etranger': list(stagiaires)}, safe=False)
    else:
        return JsonResponse({'message': 'Méthode non autorisée'}, status=405)
    
    
@csrf_exempt
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def create_etranger(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id = data.get('id')
            nom = data.get('nom')
            
            # Crée un nouvel objet Etranger
            etranger = Etranger.objects.create(id=id, nom=nom)
            
            # Retourne une réponse avec l'ID de l'Etranger créé
            return JsonResponse({'id': etranger.id}, status=201)
        except Exception as e:
            # En cas d'erreur, retourne une réponse avec le message d'erreur
            return JsonResponse({'error': str(e)}, status=400)
    else:
        # Retourne une réponse indiquant que la méthode n'est pas autorisée pour cette vue
        return JsonResponse({'message': 'Méthode non autorisée'}, status=405)
@csrf_exempt
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])   
def get_reservations(request):
    if request.method == 'GET':
        reservations_etranger = list(ResrvationEtranger.objects.values())
        reservations_stagiaire = list(ResrvationStagiaire.objects.values())
        return JsonResponse({'reservations_etranger': reservations_etranger, 'reservations_stagiaire': reservations_stagiaire})
    else:
        return JsonResponse({'message': 'Méthode non autorisée'}, status=405)
    
@csrf_exempt
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def delete_Etranger(request,id) : 
    if request.method =="DELETE" : 
        stagiaire_admin_efface = Etranger.objects.filter(id = id).first()
        stagiaire_admin_efface.delete()
        
    else : 
         return JsonResponse({"message": "methodeeeee"}, status=404)

