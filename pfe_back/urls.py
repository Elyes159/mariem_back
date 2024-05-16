"""
URL configuration for pfe_back project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from myapp.views import *
from pfe_back import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/create_account/',create_account),
    path('api/login/',login),
    path('api/createRsvForStg/<token>/',create_reservation_stagiaire),
    path('api/forgot_password/<email>/',send_password_reset_email_with_new_password),
    path('api/login_etranger/',login_etranger),
    path('api/createRsvForEtg/<code>/',create_reservation_Etranger),
    path('api/deleteRsv/<code>/',delete_reservation),
    path('api/admin/create_stagiaire/',create_or_update_stagiaire),
    path('api/admin/deleteStg/<cin>/',delete_stagiaire),
    path('api/admin/getAllStg/',get_all_stagiaires),
    path('api/admin/getAllEtr/',get_all_Etranger),
    path('api/admin/createEtr/',create_etranger),
    path('api/admin/getReserv/',get_reservations),
    path('api/admin/deleteEtr/<id>/',delete_Etranger),
    path('api/consulterprofil/<token>/',consulter_profil),
    path('api/ajouter-photo/<token>/',ajouter_photo_stagiaire),
    path('api/admin/create-admin/',creer_sous_admin),
    path('api/LoginSAdmin/',login_sous_admin),
    path('api/admin/createEmp/',create_emploi),
    path('api/getgroupid/<token>/',get_group_id),
    path('api/getemp/<group_id>/',get_photos_by_group_id),
    path('api/demande/',demande),
    path('api/admin/getdemande/',get_demandes),
    path('api/admin/acceptDemande/<email>/',send_email_confirm_demande),
    path('api/getabscence/<token>/',get_absences),
    path('api/admin/createabscence/',create_absence),
    path('api/admin/getmatiere/',get_matiere),
    path('api/admin/creatematiere/',create_matiere),
    path('api/admin/deletematiere/<matiere_id>/',delete_matiere),
    path('api/admin/geteval/',get_evaluations),
    path('api/admin/createeval/',create_evaluation),
    path('api/getAllcin/',get_all_stagiaire_cin),
    path('api/getAllMId/',get_all_matiere_ids),
    path('api/getevalbytoken/<token>/',get_evaluations_by_token),
    path('api/admin/addspec/',add_specialite),
    path('api/admin/getspec/',get_specialites),
    path('api/admin/addGroup/',add_group),
    path('api/admin/getGroup/',get_groups),
    path('api/getidspec/',get_all_code_spec),
    path('api/admin/getAllNumgr/',get_all_numgr),
    path('api/admin/getsousadmin/',get_all_sous_admin),
    path('api/admin/deletesousadmin/<identifiant>/',delete_sous_admin),
    path('api/admin/deleteReservationEtranger/<id>/',delete_reservation_etranger),
    path('api/admin/deleteReservationStagiaire/<id>/',delete_reservation_stagiaire),
    path('api/deleteReservation/<token>/',delete_reservation_stagiaire),
    path('api/admin/getstgbycin/<cin>/',get_stagiaire_by_cin),
    path('api/admin/deletegroup/<numgr>/',delete_group),
    path('api/admin/updategroup/<numgr>/',update_group),
    path('api/admin/getspec/',get_specialites),
    path('api/admin/deletespec/<code_spec>/', delete_specialite),
    path('api/admin/getemplois/', get_emplois, name='get_emplois'),
    path('api/admin/deleteemploi/<group_id>/', delete_emploi, name='delete_emploi'),
    path('api/admin/getmatieres/', get_matieres, name='get_matieres'),
    path('api/admin/getabscence/', get_abscences, name='absceceget'),
    path('api/admin/updatematieres/<abscence_id>/', update_abscence, name='update'),
    path('api/admin/deleteabsc/<abscence_id>/', delete_abscence, name='delte'),

]
if settings.DEBUG:
    urlpatterns+= static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
