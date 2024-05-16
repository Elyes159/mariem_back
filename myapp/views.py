import base64
import datetime
import os
from django.shortcuts import get_object_or_404, render
from myapp.models import ResrvationStagiaire, Stagiaire, StagiaireAdmin, TokenPourStagiaire
from django.http import  HttpResponse, JsonResponse
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
        user2 = StagiaireAdmin.objects.filter(cin = cin).first()
        
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
    elif (not(user1)and user2):
        return JsonResponse({'error': 'incorrect password'}, status=470)
    else : 
        return JsonResponse({'error': 'incorrect password'}, status=400)

    
@csrf_exempt
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def create_reservation_stagiaire(request, token):
    if request.method == "POST":
        token_obj = TokenPourStagiaire.objects.filter(token=token).first()
        if token_obj:
            stagiaire = token_obj.user
            existing_reservation = ResrvationStagiaire.objects.filter(stagiaire=stagiaire).first()
            if existing_reservation:
                return JsonResponse({'error': 'Stagiaire already has a reservation'}, status=480)
            petit_dej = request.data.get('petit_dej')
            repas_midi = request.data.get('repas_midi')
            if repas_midi or petit_dej:
                try:
                    now = datetime.datetime.now()
                    current_time_str = now.strftime('%Y-%m-%d %H:%M:%S')
                    reservation = ResrvationStagiaire.objects.create(
                        temps=current_time_str,
                        stagiaire=stagiaire,
                        petit_dej=petit_dej,
                        repas_midi=repas_midi
                    )
                    reservation.save()
                    return JsonResponse({'message': 'Reservation created successfully'}, status=201)
                except Exception as e:
                    return JsonResponse({'error': str(e)}, status=500)
            else:
                return JsonResponse({'error': 'Datetime field is required'}, status=400)
        else:
            return JsonResponse({'error': 'Invalid token'}, status=401)
            
@csrf_exempt
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def create_reservation_Etranger(request, code):
    if request.method == "POST":
        etranger = Etranger.objects.filter(id=code).first()
        if etranger:
            petit_dej = request.data.get('petit_dej')
            repas_midi = request.data.get('repas_midi')
            diner = request.data.get('diner')
            nombre_personne = request.data.get("nombre_personne")
            if (repas_midi or petit_dej or diner) and nombre_personne:
                try:
                    now = datetime.datetime.now()
                    current_time_str = now.strftime('%Y-%m-%d %H:%M:%S')
                    etranger_reservation = ResrvationEtranger.objects.filter(etranger__id=code).first()
                    if not etranger_reservation:
                        reservation = ResrvationEtranger.objects.create(
                            temps=current_time_str, etranger=etranger, petit_dej=petit_dej, repas_midi=repas_midi, diner=diner, nombre_personne=nombre_personne)
                        reservation.save()
                        return JsonResponse({'message': 'Reservation created successfully'}, status=201)
                    else:
                        # Renvoyer le statut 480 si la réservation existe déjà
                        return JsonResponse({'error': 'Reservation with this foreigner already exists'}, status=480)
                except Exception as e:
                    return JsonResponse({'error': str(e)}, status=500)
            else:
                return JsonResponse({'error': 'Datetime field is required'}, status=400)
        else:
            return JsonResponse({'error': 'Foreigner not found'}, status=404)




from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from .models import  Abscence, Demande, Emploi, Etranger, Evaluation, Group, Matiere, PeriodeExamen, ResrvationEtranger, SousAdmin, Specialite, TokenPourStagiaire
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
        code_group = request.data.get("code_group")
        email = request.data.get("email")
        group = Group.objects.filter(numgr = code_group).first()
        stagiaire_admin = StagiaireAdmin.objects.create(
            cin=cin,
            prenom=prenom,
            nom=nom,
            tel=tel,
            date_naissance=date_naissance,
            lieu_naissance=lieu_naissance,
            gouv=gouv,
            code_postal=code_postal,
            group=group,
            email=email,
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
            stagiaire_admin.email = request.data.get("email", stagiaire_admin.email)
        
            code_group = request.data.get("code_group", stagiaire_admin.group.numgr if stagiaire_admin.group else None)
            if code_group:
                group = Group.objects.filter(numgr=code_group).first()
                stagiaire_admin.group = group
        
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
        for stagiaire in stagiaires:
            # Vérifier si 'image' est une chaîne de caractères (chemin de fichier)
            if isinstance(stagiaire['image'], str) and os.path.isfile(stagiaire['image']):
                with open(stagiaire['image'], 'rb') as image_file:
                    encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                    stagiaire['image'] = encoded_image
        return JsonResponse({'stagiaires': list(stagiaires)}, safe=False)
    else:
        return JsonResponse({'message': 'Méthode non autorisée'}, status=405)
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
from django.db.models import Count

@csrf_exempt
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])   
def get_reservations(request):
    if request.method == 'GET':
        reservations_etranger = ResrvationEtranger.objects.all()
        reservations_stagiaire = ResrvationStagiaire.objects.all()

        # Nombre total de réservations pour chaque modèle
        total_reservations_etranger = reservations_etranger.count()
        total_reservations_stagiaire = reservations_stagiaire.count()

        # Convertir les queryset en liste de dictionnaires
        reservations_etranger_data = list(reservations_etranger.values())
        reservations_stagiaire_data = list(reservations_stagiaire.values())

        return JsonResponse({
            'reservations_etranger': reservations_etranger_data,
            'reservations_stagiaire': reservations_stagiaire_data,
            'nombre_total_reservations_etranger': total_reservations_etranger,
            'nombre_total_reservations_stagiaire': total_reservations_stagiaire
        })
    else:
        return JsonResponse({'message': 'Méthode non autorisée'}, status=405)

    
    
    
    
@csrf_exempt
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def delete_reservation_stagiaire(request, token):
    if request.method == "DELETE":
        token_obj = TokenPourStagiaire.objects.filter(token=token).first()
        if token_obj:
            stagiaire = token_obj.user
            existing_reservation = ResrvationStagiaire.objects.filter(stagiaire=stagiaire).first()
            if existing_reservation:
                try:
                    existing_reservation.delete()
                    return JsonResponse({'message': 'Reservation deleted successfully'}, status=200)
                except Exception as e:
                    return JsonResponse({'error': str(e)}, status=500)
            else:
                return JsonResponse({'error': 'Stagiaire does not have any reservation'}, status=404)
        else:
            return JsonResponse({'error': 'Invalid token'}, status=401)

    
    
    
    
    
@csrf_exempt
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def delete_Etranger(request,id) : 
    if request.method =="DELETE" : 
        stagiaire_admin_efface = Etranger.objects.filter(id = id).first()
        stagiaire_admin_efface.delete()
        
    else : 
         return JsonResponse({"message": "methodeeeee"}, status=404)
     
from django.core.files.base import ContentFile
import base64

@csrf_exempt
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def consulter_profil(request, token):
    token_obj = TokenPourStagiaire.objects.filter(token=token).first()
    if request.method == "GET" and token_obj:
        user_obj = token_obj.user
        stagadmin = StagiaireAdmin.objects.filter(cin=user_obj.cin).first()

        # Vérifier si le stagiaire a une image
        if stagadmin.image:
            # Lire les données binaires de l'image
            # photo_data = [{"photo": base64.b64encode(photo.photo.read()).decode('utf-8')} for photo in photos]

            image_data = stagadmin.image.read()
            # Encoder les données binaires en base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        else:
            # Si le stagiaire n'a pas d'image, définir image_base64 sur None
            image_base64 = None

        profile_data = {
            "cin": stagadmin.cin,
            "prenom": stagadmin.prenom,
            "nom": stagadmin.nom,
            "tel": stagadmin.tel,
            "date_naissance": stagadmin.date_naissance,
            "lieu_naissance": stagadmin.lieu_naissance,
            "gouv": stagadmin.gouv,
            "code_postal": stagadmin.code_postal,
            "code_groupe": stagadmin.group.numgr,
            "email": stagadmin.email,
            "photo": image_base64  # Utilisez image_base64 au lieu de image
        }

        return JsonResponse(profile_data)
    else:
        return JsonResponse({"message": "Token non trouvé ou profil non trouvé"})

    
@api_view(['POST'])
def ajouter_photo_stagiaire(request,token):
    token_obj = TokenPourStagiaire.objects.filter(token = token).first() 
    user_obj = token_obj.user
    if request.method == 'POST':
        photo = request.FILES.get('photo')
        stagiaire = StagiaireAdmin.objects.filter(cin=user_obj.cin).first()
        stagiaire.image = photo
        stagiaire.save()
            
        return JsonResponse({'message': 'Photo ajoutée avec succès'})
        
    else:
        return JsonResponse({'message': 'Méthode non autorisée'}, status=405)
    
@csrf_exempt
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])   
def create_emploi(request):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        photo = request.FILES.get('photo')
        group = Group.objects.filter(numgr = group_id).first()

        if group is None or photo is None:
            return JsonResponse({"message": "Données manquantes"}, status=400)

        try:
            # Créez une instance de l'emploi avec les données fournies
            emploi = Emploi.objects.create(group=group, photo=photo)
            emploi.save()
            return JsonResponse({"message": "Emploi créé avec succès"}, status=201)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

    else:
        return JsonResponse({"message": "Méthode non autorisée"}, status=405)
    
@csrf_exempt
def get_emplois(request):
    if request.method == 'GET':
        emplois = Emploi.objects.all()
        emplois_data = []
        for emploi in emplois:
            with open(emploi.photo.path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            emplois_data.append({
                'group_id': emploi.group.numgr,
                'photo': encoded_string,
            })
        return JsonResponse({'emplois': emplois_data}, status=200)
    else:
        return JsonResponse({'message': 'Méthode non autorisée'}, status=405)
    
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def delete_emploi(request, group_id):
    if request.method == 'DELETE':
        try:
            emploi = Emploi.objects.get(group__numgr=group_id)
            emploi.delete()
            return JsonResponse({'message': 'Emploi supprimé avec succès'}, status=200)
        except Emploi.DoesNotExist:
            return JsonResponse({'error': 'Emploi non trouvé'}, status=404)
    else:
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)


@csrf_exempt
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def creer_sous_admin(request)  :
    if request.method =="POST" :
        identifiant = request.data.get("identifiant")
        password = request.data.get("password")
        if identifiant and password : 
            sous_admin = SousAdmin.objects.create(identifiant = identifiant,password = password)
            sous_admin.save()
            return JsonResponse({"message":"succes"},status=200)
        else : 
            return JsonResponse({"erroe":"noo!!"},status=400)
    else : 
        return JsonResponse({"method":"not allowed"},status=415)



@csrf_exempt
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def login_sous_admin(request) : 
    if request.method =="POST" : 
        identifiant = request.data.get("identifiant")
        password = request.data.get("password")
        if identifiant and password : 
            sous_ad = SousAdmin.objects.filter(identifiant = identifiant , password = password).first()
            if sous_ad : 
                return JsonResponse({"message":"succes"},status=200)
            else :
                return JsonResponse({"erreur":"donnee erroné"},status=400)
        else : 
            return JsonResponse({"erreur":"donnees manquant"},status = 400)
    else : 
        return JsonResponse({"erreru":"fezfezfezfez"},status=415)


    
    
@csrf_exempt
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def get_photos_by_group_id(request, group_id):
    if request.method == 'GET':
        try:
            group = Group.objects.get(numgr=group_id)
            photos = Emploi.objects.filter(group=group)
            photo_data = [{"photo": base64.b64encode(photo.photo.read()).decode('utf-8')} for photo in photos]
            return JsonResponse({"photos": photo_data}, status=200)
        except Group.DoesNotExist:
            return JsonResponse({"message": "Le groupe spécifié n'existe pas"}, status=404)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Méthode non autorisée"}, status=405)
@csrf_exempt
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def get_group_id(request, token):
    if request.method == 'GET':
        try:
            token_obj = TokenPourStagiaire.objects.filter(token = token).first()
            user = token_obj.user
            stagiaire = StagiaireAdmin.objects.filter(cin = user.cin).first()
            group = stagiaire.group
            profile_data = {
            "group_id" : group.numgr,
            }
            return JsonResponse({"message":profile_data}, status=200)
        except Group.DoesNotExist:
            return JsonResponse({"message": "Le groupe spécifié n'existe pas"}, status=404)
        except Exception as e:
            print(e)
            return JsonResponse({"message": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Méthode non autorisée"}, status=405)
    
@csrf_exempt
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def demande(request):
    if request.method == "POST":
        nom_prenom = request.data.get("nom_prenom")
        cin = request.data.get("cin")
        email = request.data.get("email")
        cause = request.data.get("cause")

        if nom_prenom and cin and email and cause:
            demandee = Demande.objects.create(nom_prenom=nom_prenom, cin=cin, email=email, cause=cause)
            demandee.save()
            # Return success response with created Demande data (optional)
            return JsonResponse({"success": True})  # Customize data
        else:
            return JsonResponse({"error": "Données manquantes"}, status=400)  # Use 400 for bad request
    else:
        return JsonResponse({"message": "Méthode non autorisée"}, status=405)


@csrf_exempt
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def get_demandes(request):
    if request.method == 'GET':
        try:
            # Récupérer toutes les demandes de la base de données
            demandes = Demande.objects.all()

            # Serializer les données des demandes si nécessaire
            demande_data = [{"nom_prenom": demande.nom_prenom,
                             "cin": demande.cin,
                             "email": demande.email,
                             "cause": demande.cause} for demande in demandes]
            

            # Retourner les données des demandes en tant que réponse JSON
            return JsonResponse({"demandes": demande_data}, status=200)
        except Exception as e:
            # En cas d'erreur, renvoyer un message d'erreur avec le statut 500
            return JsonResponse({"error": str(e)}, status=500)
    else:
        # Si la méthode HTTP n'est pas autorisée, renvoyer un message avec le statut 405
        return JsonResponse({"message": "Méthode non autorisée"}, status=405)
    
    
@csrf_exempt
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def send_email_confirm_demande(request, email):
    if request.method == "POST":
        try:
            
            email_subject = "demande accepté"
            email_body = f"""
            votre demande est accepté
            """
            send_mail(
                email_subject,
                email_body,
                "elyesmlik307@gmail.com",
                [email],
                fail_silently=False
            )
            Demande.objects.filter(email=email).delete()
            

        

        except Exception as e:
            print(f"Erreur lors de l'envoi de l'e-mail de réinitialisation du mot de passe : {e}")
            return JsonResponse({"message": "Une erreur est survenue"}, status=500)

        else:
            return JsonResponse({"message": "Email de réinitialisation de mot de passe envoyé avec succès"}, status=200)
        
@csrf_exempt
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])        
def get_absences(request,token):
    token_obj = TokenPourStagiaire.objects.filter(token = token ).first()
    user = token_obj.user
    if request.method == 'GET':
        try:
            # Récupérer toutes les absences de la base de données
            absences = Abscence.objects.filter(stagiaire = user)

            # Serializer les données des absences si nécessaire
            absences_data = [{
                "stagiaire": absence.stagiaire.cin,
                "matiere": absence.matiere.id,
                "nb_heure": absence.nb_heure,
                "periode": absence.periode.id
            } for absence in absences]

            # Retourner les données des absences en tant que réponse JSON
            return JsonResponse({"absences": absences_data}, status=200)
        except Exception as e:
            # En cas d'erreur, renvoyer un message d'erreur avec le statut 500
            print(e)
            return JsonResponse({"error": str(e)}, status=500)
    else:
        # Si la méthode HTTP n'est pas autorisée, renvoyer un message avec le statut 405
        return JsonResponse({"message": "Méthode non autorisée"}, status=405)
    
    
@csrf_exempt
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def create_absence(request):
    if request.method == 'POST':
        try:
            matiere_id = request.data.get("matiere_id")
            nb_heure = request.data.get("nb_heure")
            periode_id = request.data.get("periode_id")
            cin = request.data.get("cin")
            
            user = Stagiaire.objects.filter(cin = cin).first()
            periode = PeriodeExamen.objects.filter(id = periode_id).first()
            matiere = Matiere.objects.filter(id = matiere_id).first()

            # Vérifier si toutes les données nécessaires sont fournies
            if matiere_id and nb_heure and periode_id:
                # Créer une nouvelle absence dans la base de données
                absence = Abscence.objects.create(
                    stagiaire=user,
                    matiere=matiere,
                    nb_heure=nb_heure,
                    periode=periode
                )
                absence.save()
                return JsonResponse({"success": True}, status=201)
            else:
                return JsonResponse({"error": "Données manquantes"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Méthode non autorisée"}, status=405)
    
    
####matiere ####

from django.http import JsonResponse
@csrf_exempt
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def get_matiere(request):
    try:
        matieres = Matiere.objects.all()
        matieres_data = []
        for matiere in matieres:
            matiere_data = {
                'id': matiere.id,
                'module': matiere.module,
                'titre_module': matiere.titre_module,
                'nb_heure': matiere.nb_heure,
                'type': matiere.type,
                'specialite': matiere.specialite.code_spec
            }
            matieres_data.append(matiere_data)
        return JsonResponse({'matieres': matieres_data}, status=200)
    except Exception as e:
        print(e)
        return JsonResponse({'error': str(e)}, status=500)
    
def get_specialites(request):
    if request.method == 'GET':
        specialites = Specialite.objects.all().values()
        return JsonResponse({'specialites': list(specialites)}, status=200)
    else:
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    
@csrf_exempt
def delete_specialite(request, code_spec):
    if request.method == 'DELETE':
        try:
            specialite = Specialite.objects.get(code_spec=code_spec)
            specialite.delete()
            return JsonResponse({'message': 'Specialité supprimée avec succès'}, status=200)
        except Specialite.DoesNotExist:
            return JsonResponse({'message': 'Specialité non trouvée'}, status=404)
    else:
        return JsonResponse({'message': 'Méthode non autorisée'}, status=405)
    
@csrf_exempt
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def create_matiere(request):
    if request.method == 'POST':
        try:
            id = request.data.get("id")
            module = request.data.get('module')
            titre_module = request.data.get('titre_module')
            nb_heure = request.data.get('nb_heure')
            type = request.data.get('type')
            specialite_id = request.data.get('specialite_id')

            if module and titre_module and nb_heure and type and specialite_id:
                specialite = Specialite.objects.get(code_spec=specialite_id)
                matiere = Matiere.objects.create(id = id,module=module, titre_module=titre_module, nb_heure=nb_heure, type=type, specialite=specialite)
                matiere.save()
                return JsonResponse({'success': True}, status=201)
            else:
                return JsonResponse({'error': 'Données manquantes'}, status=400)
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'message': 'Méthode non autorisée'}, status=405)
    
from django.http import JsonResponse
from .models import Matiere

def get_matieres(request):
    matieres = Matiere.objects.all()
    matiere_list = [
        {
            'id': matiere.id,
            'module': matiere.module,
            'titre_module': matiere.titre_module,
            'nb_heure': matiere.nb_heure,
            'type': matiere.type,
            'specialite': matiere.specialite.code_spec,
        }
        for matiere in matieres
    ]
    return JsonResponse({'matieres': matiere_list})

def get_abscences(request):
    abscences = Abscence.objects.all()
    abscence_list = [
        {
            'id': abscence.id,
            'stagiaire_id': abscence.stagiaire.id,
            'matiere_id': abscence.matiere.id,
            'nb_heure': abscence.nb_heure,
            'periode_id': abscence.periode.id,
        }
        for abscence in abscences
    ]
    return JsonResponse({'abscences': abscence_list})

@csrf_exempt
def update_abscence(request, abscence_id):
    try:
        abscence = Abscence.objects.get(id=abscence_id)
    except Abscence.DoesNotExist:
        return JsonResponse({'error': 'Abscence not found'}, status=404)

    if request.method == 'PUT':
        data = json.loads(request.body)
        abscence.nb_heure = data.get('nb_heure', abscence.nb_heure)
        abscence.save()
        return JsonResponse({'message': 'Abscence updated successfully'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)
from django.http import JsonResponse
from .models import Abscence

def delete_abscence(request, abscence_id):
    try:
        abscence = Abscence.objects.get(id=abscence_id)
    except Abscence.DoesNotExist:
        return JsonResponse({'error': 'Abscence not found'}, status=404)

    abscence.delete()
    return JsonResponse({'message': 'Abscence deleted successfully'})

@csrf_exempt
@api_view(['DELETE'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def delete_matiere(request, matiere_id):
    if request.method == 'DELETE':
        try:
            matiere = Matiere.objects.get(id=matiere_id)
            matiere.delete()
            return JsonResponse({'success': True}, status=200)
        except Matiere.DoesNotExist:
            return JsonResponse({'message': 'La matière spécifiée n\'existe pas'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'message': 'Méthode non autorisée'}, status=405)
    


@csrf_exempt
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def get_evaluations_by_token(request, token):
    if request.method == 'GET':
        try:
            token_obj = TokenPourStagiaire.objects.filter(token = token).first()
            stagiaire = token_obj.user
            evaluations = Evaluation.objects.filter(stagiaire=stagiaire)
            evaluations_data = []
            for evaluation in evaluations:
                evaluation_data = {
                    'matiere_id': evaluation.matiere.id,
                    'note': evaluation.note,
                    'stagiaire_id': evaluation.stagiaire.id
                }
                evaluations_data.append(evaluation_data)
            return JsonResponse({"evaluations": evaluations_data}, status=200)
        except Stagiaire.DoesNotExist:
            return JsonResponse({"message": "Le stagiaire spécifié n'existe pas"}, status=404)
        except Exception as e:
            print(e)
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Méthode non autorisée"}, status=405)

@csrf_exempt
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def create_evaluation(request):
    if request.method == 'POST':
        try:
            matiere_id = request.data.get("matiere_id")
            note = request.data.get("note")
            stagiaire_id = request.data.get("stagiaire_cin")
            
            matiere = Matiere.objects.get(id=matiere_id)
            stagiaire = Stagiaire.objects.get(cin=stagiaire_id)

            evaluation = Evaluation.objects.create(matiere=matiere, note=note, stagiaire=stagiaire)
            evaluation.save()
            return JsonResponse({"success": True}, status=201)
        except Matiere.DoesNotExist:
            return JsonResponse({"message": "La matière spécifiée n'existe pas"}, status=404)
        except Stagiaire.DoesNotExist:
            return JsonResponse({"message": "Le stagiaire spécifié n'existe pas"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Méthode non autorisée"}, status=405)
    
@csrf_exempt
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def get_evaluations(request):
    if request.method == 'GET':
        try:
            evaluations = Evaluation.objects.all()
            evaluations_data = []
            for evaluation in evaluations:
                evaluation_data = {
                    'matiere_id': evaluation.matiere.id,
                    'note': evaluation.note,
                    'stagiaire_id': evaluation.stagiaire.cin
                }
                evaluations_data.append(evaluation_data)
            return JsonResponse({"evaluations": evaluations_data}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Méthode non autorisée"}, status=405)
@csrf_exempt
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def add_specialite(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code_spec = data.get('code_spec')
        nom_spec_ar = data.get('nom_spec_ar')
        type = data.get('type')

        if code_spec and nom_spec_ar and type:
            try:
                specialite = Specialite.objects.create(
                    code_spec=code_spec,
                    nom_spec_ar=nom_spec_ar,
                    type=type
                )
                specialite.save()
                return JsonResponse({'message': 'Spécialité ajoutée avec succès'}, status=201)
            except Exception as e:
                return JsonResponse({'error': str(e)}, status=500)
        else:
            return JsonResponse({'error': 'Tous les champs sont requis'}, status=400)
    else:
        return JsonResponse({'message': 'Méthode non autorisée'}, status=405)
@csrf_exempt
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def get_specialites(request):
    if request.method == 'GET':
        specialites = Specialite.objects.all()
        specialites_data = list(specialites.values())
        return JsonResponse({'specialites': specialites_data})
    else:
        return JsonResponse({'message': 'Méthode non autorisée'}, status=405)
    
@csrf_exempt
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def add_group(request):
    if request.method == 'POST':
        try:
            numgr = request.data.get('numgr')
            specialite_id = request.data.get('specialite_id')
            specialite = Specialite.objects.filter(code_spec =specialite_id).first()
            group = Group.objects.create(numgr=numgr, specialite=specialite)
            group.save()
            return JsonResponse({"success": True}, status=201)
        except Exception as e:
            print(e)
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Méthode non autorisée"}, status=405)

@csrf_exempt
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def get_groups(request):
    if request.method == 'GET':
        try:
            groups = Group.objects.all()
            groups_data = []
            for group in groups:
                group_data = {
                    'numgr': group.numgr,
                    'specialite_id': group.specialite.code_spec
                }
                groups_data.append(group_data)
            return JsonResponse({"groups": groups_data}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return JsonResponse({"message": "Méthode non autorisée"}, status=405)
    
# Fonction pour récupérer tous les objets SousAdmin
def get_all_sous_admin(request):
    if request.method == 'GET':
        sous_admins = SousAdmin.objects.all().values()
        return JsonResponse({'sous_admins': list(sous_admins)}, safe=False)
    else:
        return JsonResponse({'message': 'Méthode non autorisée'}, status=405)

@csrf_exempt
def delete_sous_admin(request, identifiant):
    if request.method == 'DELETE':
        try:
            sous_admin = SousAdmin.objects.get(identifiant=identifiant)
            sous_admin.delete()
            return JsonResponse({'message': 'Sous-admin supprimé avec succès'}, status=200)
        except SousAdmin.DoesNotExist:
            return JsonResponse({'message': 'Sous-admin non trouvé'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'message': 'Méthode non autorisée'}, status=405)
###########nest7a99hom###############
@csrf_exempt
@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
def get_all_stagiaire_cin(request):
    if request.method == 'GET':
        try:
            # Récupérer tous les stagiaires
            stagiaires = Stagiaire.objects.all()

            # Récupérer les CIN de tous les stagiaires
            cins = [stagiaire.cin for stagiaire in stagiaires]

            # Retourner la liste des CIN en tant que réponse JSON
            return JsonResponse({"cins": cins}, status=200)
        except Exception as e:
            # En cas d'erreur, renvoyer un message d'erreur avec le statut 500
            return JsonResponse({"error": str(e)}, status=500)
    else:
        # Si la méthode HTTP n'est pas autorisée, renvoyer un message avec le statut 405
        return JsonResponse({"message": "Méthode non autorisée"}, status=405)
    
def get_all_matiere_ids(request):
    if request.method == 'GET':
        try:
            # Récupérer tous les identifiants des objets Matiere
            matiere_ids = Matiere.objects.values_list('id', flat=True)

            # Convertir les identifiants en une liste
            matiere_ids_list = list(matiere_ids)

            # Retourner les identifiants en tant que réponse JSON
            return JsonResponse({'matiere_ids': matiere_ids_list}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'message': 'Méthode non autorisée'}, status=405)
    
    
    
@csrf_exempt
@api_view(['DELETE'])
def delete_reservation_etranger(request, id):
    try:
        reservation = ResrvationEtranger.objects.get(id=id)
        reservation.delete()
        return JsonResponse({'message': 'La réservation d\'étranger a été supprimée avec succès'}, status=200)
    except ResrvationEtranger.DoesNotExist:
        return JsonResponse({'message': 'La réservation d\'étranger spécifiée n\'existe pas'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Fonction pour supprimer une réservation de stagiaire
@csrf_exempt
@api_view(['DELETE'])
def delete_reservation_stagiaire(request, token):
    
    try:
        token_obj = TokenPourStagiaire.objects.filter(token = token).first()
        user = token_obj.user
        reservation = ResrvationStagiaire.objects.get(stagiaire=user)
        reservation.delete()
        return JsonResponse({'message': 'La réservation de stagiaire a été supprimée avec succès'}, status=200)
    except ResrvationStagiaire.DoesNotExist:
        return JsonResponse({'message': 'La réservation de stagiaire spécifiée n\'existe pas'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)    

    
    
def get_all_code_spec(request):
    if request.method == 'GET':
        code_specs = Specialite.objects.values_list('code_spec', flat=True)
        return JsonResponse({'code_specs': list(code_specs)}, safe=False)
    else:
        return JsonResponse({'message': 'Méthode non autorisée'}, status=405)
    
def get_all_numgr(request):
    if request.method == 'GET':
        numgrs = Group.objects.values_list('numgr', flat=True)
        return JsonResponse({'numgrs': list(numgrs)}, safe=False)
    else:
        return JsonResponse({'message': 'Méthode non autorisée'}, status=405)
    
    


def get_stagiaire_by_cin(request, cin):
    stagiaire = StagiaireAdmin.objects.filter(cin=cin).first()
    if stagiaire:
        # Sérialiser les champs nécessaires en JSON
        stagiaire_data = {
            'cin': stagiaire.cin,
            'prenom': stagiaire.prenom,
            'nom': stagiaire.nom,
            'tel': stagiaire.tel,
            'date_naissance': stagiaire.date_naissance,
            'lieu_naissance': stagiaire.lieu_naissance,
            'gouv': stagiaire.gouv,
            'code_postal': stagiaire.code_postal,
            'group': stagiaire.group.id,  # Exemple de sérialisation d'une clé étrangère
            'email': stagiaire.email,
            # Ajoutez d'autres champs si nécessaire
        }
        return JsonResponse({'stagiaire': stagiaire_data})
    else:
        return JsonResponse({'error': 'Aucun stagiaire trouvé'}, status=404)
    
@csrf_exempt
def delete_group(request, numgr):
    if request.method == 'DELETE':
        try:
            group = Group.objects.get(numgr=numgr)
            group.delete()
            return JsonResponse({'message': 'Group deleted successfully'}, status=200)
        except Group.DoesNotExist:
            return JsonResponse({'message': 'Group not found'}, status=404)
    else:
        return JsonResponse({'message': 'Method not allowed'}, status=405)
    
@csrf_exempt
def update_group(request, numgr):
    if request.method == 'PUT':
        try:
            group = Group.objects.get(numgr=numgr)
            # Mettre à jour les champs du groupe
            group.specialite.code_spec = request.POST.get('specialite_id', group.specialite.code_spec)
            group.save()
            return JsonResponse({'message': 'Group updated successfully'}, status=200)
        except Group.DoesNotExist:
            return JsonResponse({'message': 'Group not found'}, status=404)
    else:
        return JsonResponse({'message': 'Method not allowed'}, status=405)

        

                
         
        

