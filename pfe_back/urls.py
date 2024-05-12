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
]
if settings.DEBUG:
    urlpatterns+= static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
