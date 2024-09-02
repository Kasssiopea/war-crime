from django.urls import path

from .views import *

urlpatterns = [
    path('', IndexPage.as_view(), name='home'),
    path('persons/', Persons.as_view(), name='persons'),
    path('person/<int:post_person_pk>', DetailPerson.as_view(), name='person'),
    path('registration/', RegisterClient.as_view(), name='reg'),
    path('activate/<uidb64>/<token>', activate, name='activate'),
    path('login/', LoginClient.as_view(), name='login'),
    path('logout/', logout_user, name='logout'),
    path('news/', News.as_view(), name='news'),
    #
    path('admin/statistic/', Statistic.as_view(), name='statistic'),
    #
    path('admin/export/', extractData, name='export'),
    path('message/', TestForm.as_view(), name='message'),
    #
    path('admin/check/', CheckDuplicateView.as_view(), name='check'),
    path('charts/', ChartsJs.as_view(), name='charts'),
    path('ajax_charts/', ajax_charts, name='ajax_charts')
]

