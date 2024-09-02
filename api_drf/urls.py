from django.urls import path, include
from rest_framework import routers

from api_drf.views import *

router = routers.DefaultRouter()

router.register(r'person', PersonViewSet)
router.register(r'image', ImagesViewSet)
router.register(r'telegram_users', TelegramUsersViewSet)

urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/registration/', UserRegistrationView.as_view(), name='user-registration'),
    path('api/v1/activate/<uidb64>/<token>', activate, name='activate_accaunt'),

    path('api/v1/carouselhomeview/', CarouselHomeView.as_view(), name='person_carousel'),
    path('api/v1/important_news/', ImportantNewsView.as_view(), name='important_news'),
    path('api/v1/daily_news/', DailyNewsView.as_view(), name='daily_news'),
    path('api/v1/partners/', PartnersView.as_view(), name='partners'),
    path('api/v1/chart_js_statistic/', ChartStatisticView.as_view(), name='chart_statistic'),
    path('api/v1/person_search/', PersonSearchView.as_view(), name='person_search'),
    path('api/v1/persons/<int:id>/', DetailPersonView.as_view(), name="detail_person"),
    path('api/v1/persons/callbacks/', CallBackCreateAPIView.as_view(), name='callback-create'),

    path('api/v1/persons/message/', PersonCreateAPIView.as_view(), name='callback-create'),
]
