import base64
import csv

import django_filters
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils.encoding import force_str, force_bytes
from rest_framework import generics
# Create your views here.
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, permissions
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.filters import OrderingFilter
from rest_framework.generics import CreateAPIView, get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

from api_drf.modules.person import get_date, check_choise_field
from api_drf.serializers import *
from diap.models.callback import CallBack
from diap.models.front import ImportantNews, NewsDead
from diap.models.partners import Partners
from diap.models.person import *
from diap.models.telegram import TelegramUser

from diap.tokens import account_activation_token
from django.core.mail import EmailMessage, send_mail
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _


class PersonFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(lookup_expr='iexact')
    last_name = django_filters.CharFilter(lookup_expr='iexact')
    middle_name = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = Person
        fields = [
            'first_name',
            'last_name',
            'middle_name',
            'birthday',
            'publish_status'
        ]


class PersonPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 100000


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PersonFilter
    pagination_class = PersonPagination
    authentication_classes = [SessionAuthentication, BasicAuthentication, JWTAuthentication]
    permission_classes = [IsAdminUser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=isinstance(request.data, list))
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ImagesViewSet(viewsets.ModelViewSet):
    queryset = PersonImage.objects.all()
    serializer_class = ImageSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAdminUser]


class StatisticGroup(APIView):
    def get(self, request, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export.csv"'
        persons = Person.objects.all()
        name = kwargs.get('group')
        if request.GET:
            rq = request.GET
            date_from = rq.get('from') if rq.get('from') else "2020-01-01"
            date_to = rq.get('to') if rq.get('to') else str(timezone.now().strftime('%Y-%m-%d'))
        else:
            date_from = "2020-01-01"
            date_to = str(timezone.now().strftime('%Y-%m-%d'))
        print(date_from, date_to)
        if name == 'CHUVS':
            group = User.objects.all().filter(groups__name=name)
        elif name == 'NAVS':
            group = User.objects.all().filter(groups__name=name)
        elif name == 'DIAP':
            group = User.objects.all().filter(groups__name=name)
        else:
            group = []
        try:
            users = []
            employee_info = ['Username', 'Published', 'Processing', 'Deleted', 'For check']
            for i in group:
                users.append({
                        'Username': i.username,
                        'Published': persons.filter(task_published=i.username, task_published_date__range=[str(date_from), str(date_to)]).count(),
                        'Processing': persons.filter(task_processing=i.username, task_processing_date__range=[str(date_from), str(date_to)]).count(),
                        'Deleted': persons.filter(task_deleted=i.username, task_deleted_date__range=[str(date_from), str(date_to)]).count(),
                        'For check': persons.filter(task_for_check=i.username, task_for_check_date__range=[str(date_from), str(date_to)]).count(),
                })
            # w = csv.DictWriter(f, my_dict.keys())
            writer = csv.DictWriter(response, fieldnames=employee_info)
            writer.writeheader()
            writer.writerows(users)
            return response
        except:
            return Response(
                {
                    'Error': 'Send message to admin'
                }, status=status.HTTP_404_NOT_FOUND
            )


class TelegramUsersFilter(django_filters.FilterSet):
    class Meta:
        model = TelegramUser
        fields = '__all__'


class TelegramUsersViewSet(viewsets.ModelViewSet):
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUsersSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TelegramUsersFilter

    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAdminUser]


class TokenObtainPairView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        refresh = RefreshToken.for_user(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return Response(data, status=status.HTTP_200_OK)


class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        user = User.objects.get(pk=serializer.data.get('pk'))
        activateEmail(request=request, user=user, to_email=request.data.get('email'))

        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Activate accaunt
def activateEmail(request, user, to_email):

    mail_subject = 'Активація акаунту на Потерь.НЕТ'
    message = render_to_string("emails/activate_account.html",
                               {
                                   'user': user.username,
                                   'domain': get_current_site(request).domain,
                                   'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                                   'token': account_activation_token.make_token(user),
                                   'protocol': 'https' if request.is_secure() else 'http'
                               })
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        print('success')
        messages.success(request, f'Dear {user} check your email')
    else:
        print('Error')
        messages.error(request, f'Dear {user} your email is incorrect, just check it again')


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except:
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Success')
        return redirect('https://demo.poternet.site')
    else:
        messages.error(request, 'Error')
    return redirect('https://demo.poternet.site/registration')


# Carousel
class CarouselHomeView(APIView):

    def get(self, request):
        persons = Person.objects.filter(
            publish_status=StatusPersonPostPublished.PUBLISHED,
            images__isnull=False
        ).annotate(
            num_images=Count('images')
        ).order_by('-time_update', '-num_images').distinct()[:30]

        person_list = []
        for person in persons:
            image_data = None
            if person.images.first():
                try:
                    image_data = person.images.first().image.url
                except:
                    image_data = None

            person_dict = {
                'last_name': person.last_name,
                'first_name': person.first_name,
                'middle_name': person.middle_name,
                'image': image_data
            }
            person_list.append(person_dict)

        return Response(person_list, status=status.HTTP_200_OK)


class ImportantNewsView(APIView):
    def get(self, request):
        important_news = ImportantNews.objects.all().filter(published=True)
        important_news_list = []
        for i in important_news:
            try:
                with open(i.image.path, "rb") as image_file:
                    image_data = f"data:image/jpeg;base64,{base64.b64encode(image_file.read()).decode('utf-8')}"
            except:
                image_data = None
            important_news_list.append({
                'url_news': i.url_news,
                'title': i.title,
                'span_date': i.span_date,
                'news_name': i.news_name,
                'text': i.text,
                'image': image_data
            })

        return Response(important_news_list, status=status.HTTP_200_OK)


class DailyNewsView(APIView):
    def get(self, request):
        news_dead = NewsDead.objects.all().filter(published=True).order_by('-time_create').first()
        try:
            with open(news_dead.image.path, "rb") as image_file:
                image_data = f"data:image/jpeg;base64,{base64.b64encode(image_file.read()).decode('utf-8')}"
        except:
            image_data = None

        return Response({'image': image_data}, status=status.HTTP_200_OK)


class PartnersView(APIView):
    def get(self, request):
        partners = Partners.objects.all().filter(published=True).order_by('-time_create')
        partners_list = []
        for i in partners:
            try:
                image_data = i.image.url
            except:
                image_data = None
            partners_list.append({
                'id': i.pk,
                'name': i.name,
                'url': i.url,
                'image': image_data
            })

        return Response(partners_list, status=status.HTTP_200_OK)


class ChartStatisticView(APIView):
    def get(self, request):
        person = Person.objects.all().filter(post_status=StatusPersonPostChoices.PUBLISHED)
        def sort_dictionary(dictionary, order):
            sorted_dict = {}
            for key in order:
                if key in dictionary:
                    sorted_dict[key] = dictionary[key]
            return sorted_dict
        sort_type_of_army = [
            str(_('Сухопутные войска')),
            str(_('Воздушно-космические силы')),
            str(_('Военно-Морской Флот')),
            str(_('Ракетные войска стратегического назначения')),
            str(_('Воздушно-десантные войска')),
            str(_('Другие подразделения МО РФ')),
            str(_('Войска нац иональной гвардии Российской Федерации')),
            str(_('МВД')), str(_('ЧВК')),
            str(_('Незаконные вооружённые формирования.'))
        ]
        sort_rank_army = [
            str(_('РЯДОВОЙ')),
            str(_('ЕФРЕЙТОР')),
            str(_('МЛАДШИЙ СЕРЖАНТ')),
            str(_('СЕРЖАНТ')),
            str(_('СТАРШИЙ СЕРЖАНТ')),
            str(_('СТАРШИНА')),
            str(_('ПРАПОРЩИК')),
            str(_('СТАРШИЙ ПРАПОРЩИК')),
            str(_('МЛАДШИЙ ЛЕЙТЕНАНТ')),
            str(_('ЛЕЙТЕНАНТ')),
            str(_('СТАРШИЙ ЛЕЙТЕНАНТ')),
            str(_('КАПИТАН')),
            str(_('МАЙОР')),
            str(_('ПОДПОЛКОВНИК')),
            str(_('ПОЛКОВНИК')),
            str(_('ГЕНЕРАЛ-МАЙОР')),
            str(_('ГЕНЕРАЛ-ЛЕЙТЕНАНТ')),
            str(_('ГЕНЕРАЛ-ПОЛКОВНИК')),
            str(_('ГЕНЕРАЛ АРМИИ')),
            str(_('МАРШАЛ РОССИЙСКОЙ ФЕДЕРАЦИИ')),
        ]
        sort_rank_fleet = [
            str(_('МАТРОС')),
            str(_('СТАРШИЙ МАТРОС')),
            str(_('СТАРШИНА 2 СТАТЬИ')),
            str(_('СТАРШИНА 1 СТАТЬИ')),
            str(_('ГЛАВНЫЙ СТАРШИНА')),
            str(_('ГЛАВНЫЙ КОРАБЕЛЬНЫЙ СТАРШИНА')),
            str(_('МИЧМАН')),
            str(_('СТАРШИЙ МИЧМАН')),
            str(_('КАПИТАН-ЛЕЙТЕНАНТ')),
            str(_('КАПИТАН 3 РАНГА')),
            str(_('КАПИТАН 2 РАНГА')),
            str(_('КАПИТАН 1 РАНГА')),
            str(_('КОНТР-АДМИРАЛ')),
            str(_('ВИЦЕ-АДМИРАЛ')),
            str(_('АДМИРАЛ"')),
            str(_('АДМИРАЛ ФЛОТА'))
        ]
        ranks = person.filter(rank_choice__isnull=False) \
            .exclude(rank_choice='00').values('rank_choice').annotate(count=Count('id'))
        ranks = {str(_(item['rank_choice'])): item['count'] for item in ranks}
        sorted_ranks_army = sort_dictionary(ranks, sort_rank_army)
        sorted_ranks_fleet = sort_dictionary(ranks, sort_rank_fleet)
        # sorted_ranks_fleet['АДМИРАЛ'] = sorted_ranks_fleet.pop('АДМИРАЛ"')
        # Type of army response
        type_of_army = person.filter(type_of_army_choice__isnull=False) \
            .exclude(type_of_army_choice='00').values('type_of_army_choice').annotate(count=Count('id'))
        type_of_army = {str(_(item['type_of_army_choice'])): item['count'] for item in type_of_army}
        sorted_type_of_army = sort_dictionary(type_of_army, sort_type_of_army)
        # Birth response
        births = person.annotate(
            birth=Coalesce('birthday_year', 'birthday__year')
        ).filter(birth__gt=1940, birth__lt=2006)
        births = births.values('birth').annotate(
            count=Count('id')
        ).values(
            'birth',
            'count'
        )
        itervals = [
            {"start": 17, "end": 25, "name": str(_("Від 18 до 25"))},
            {"start": 25, "end": 35, "name": str(_("Від 25 до 35"))},
            {"start": 35, "end": 45, "name": str(_("Від 35 до 45"))},
            {"start": 45, "end": 55, "name": str(_("Від 45 до 55"))},
            {"start": 55, "end": 100, "name": "55+"},
        ]
        birth = {}
        for i in births:
            for j in itervals:
                if j.get('start') <= 2022 - i.get('birth') < j.get('end'):
                    if birth.get(j.get('name')) is None:
                        birth[j.get('name')] = i.get('count')
                    else:
                        birth[j.get('name')] += i.get('count')

        # Dead response
        date_of_death = person.annotate(
            year=Coalesce(
                'data_when_accident_year',
                'data_when_accident__year',
                'place_of_rip_date_year'
            )
        ).annotate(count=Count('id')).values('year', 'count')
        death = {}
        for i in date_of_death:
            if death.get(i.get('year')) is None:
                if i.get('year'):
                    death[i.get('year')] = i.get('count')
            else:
                if i.get('year'):
                    death[i.get('year')] += i.get('count')
        # Dead month

        # JSON response
        response_data = {
            'ranks': [
                sorted_ranks_army,
                sorted_ranks_fleet
            ],
            'type_of_army': sorted_type_of_army,
            'birth': birth,
            'death': death,
        }
        return Response(response_data, status=status.HTTP_200_OK)


class PersonSearchView(APIView):
    def post(self, request):
        if request.data:
            pib = request.data.get('search_pib')
            if isinstance(pib, str):
                queryset = Person.objects.all().filter(
                    publish_status=StatusPersonPostPublished.PUBLISHED).filter(~Q(images=None)).annotate(
                    num_images=Count('images')) \
                    .order_by('-num_images').order_by('-time_create').distinct()
                for word in pib.split():
                    q_list = Q()
                    q_list |= Q(first_name__icontains=word)
                    q_list |= Q(last_name__icontains=word)
                    q_list |= Q(middle_name__icontains=word)
                    queryset = queryset.filter(q_list)
                if queryset:
                    person_list = []
                    for i in queryset:
                        date_of_birthday = get_date(date={
                            "date": i.birthday,
                            "date_day": i.birthday_day,
                            "date_month": i.birthday_month,
                            "date_year": i.birthday_year
                        })
                        if i.images.first():
                            try:
                                    image_data = i.images.first().image.url
                            except:
                                image_data = None
                        else:
                            image_data = None
                        person_list.append({
                            "pk": i.pk,
                            "first_name": i.first_name,
                            "last_name": i.last_name,
                            "middle_name": i.middle_name,
                            "date_of_birthday": date_of_birthday,
                            "military_unit": i.military_unit,
                            "image": image_data,
                        })
                    return Response({'persons': person_list}, status=status.HTTP_200_OK)
                else:
                    return Response({'persons': []}, status=status.HTTP_200_OK)
            return Response({'Exception': 'value must be str'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'Exception': 'Key error'}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        persons = Person.objects.filter(
            publish_status=StatusPersonPostPublished.PUBLISHED,
            images__isnull=False
        ).annotate(
            num_images=Count('images')
        ).order_by('-time_update', '-num_images').distinct()[:42]
        person_list = []
        for i in persons:
            date_of_birthday = get_date(date={
                "date": i.birthday,
                "date_day": i.birthday_day,
                "date_month": i.birthday_month,
                "date_year": i.birthday_year
            })
            if i.images.first():
                try:
                    image_data = i.images.first().image.url
                except:
                    image_data = None
            else:
                image_data = None
            person_list.append({
                "pk": i.pk,
                "first_name": i.first_name,
                "last_name": i.last_name,
                "middle_name": i.middle_name,
                "date_of_birthday": date_of_birthday,
                "military_unit": i.military_unit,
                "image": image_data,
            })
        return Response({'persons': person_list}, status=status.HTTP_200_OK)


class DetailPersonView(APIView):

    def get(self, request, id):
        persons = Person.objects.filter(
            publish_status=StatusPersonPostPublished.PUBLISHED,
            images__isnull=False,
            pk=id,
        ).annotate(
            num_images=Count('images')
        ).order_by('-time_update', '-num_images').distinct()[:42]
        person_list = []
        for i in persons:
            date_of_birthday = get_date(date={
                "date": i.birthday,
                "date_day": i.birthday_day,
                "date_month": i.birthday_month,
                "date_year": i.birthday_year
            })
            date_of_dead = get_date(date={
                "date": i.data_when_accident,
                "date_day": i.data_when_accident_day,
                "date_month": i.data_when_accident_month,
                "date_year": i.data_when_accident_year,
            })
            date_of_rip = get_date(date={
                "date_day": i.place_of_rip_date_day,
                "date_month": i.place_of_rip_date_month,
                "date_year": i.place_of_rip_date_year,
            })
            images = []
            images_query = PersonImage.objects.all().filter(person_id=i.pk)
            for image in images_query:
                images.append({
                    "image": image.image.url,
                    "main_image": image.main_image
                })
            source_image = []
            source_image_query = SoursePersonImage.objects.all().filter(person_id=i.pk)
            for image in source_image_query:
                source_image.append({
                    "image": image.image.url,
                })
            person_list.append({
                "pk": i.pk,
                "first_name": i.first_name,
                "last_name": i.last_name,
                "middle_name": i.middle_name,
                "date_of_birthday": date_of_birthday,
                "citizenship": i.citizenship,
                "passport": i.passport,
                "individual_identification_number": i.individual_identification_number,
                "place_of_birthday": i.place_of_birthday,
                "place_of_living": i.place_of_living,
                "additional_info": i.additional_info,
                "source": i.source.split("\n"),
                "rank": i.rank,
                "rank_choice": check_choise_field('АДМИРАЛ' if i.rank_choice == 'АДМИРАЛ"' else i.rank_choice),
                "job_title": i.job_title,
                "type_of_army": i.type_of_army,
                "type_of_army_choice": check_choise_field(i.type_of_army_choice),
                "military_from": i.military_from,
                "status_person": i.status_person,
                "place_where_accident": i.place_where_accident,
                "commander": i.commander,
                "date_of_dead": date_of_dead,
                "data_when_accident": i.data_when_accident,
                "data_when_accident_year": i.data_when_accident_year,
                "data_when_accident_month": i.data_when_accident_month,
                "data_when_accident_day": i.data_when_accident_day,
                "place_of_rip": i.place_of_rip,
                "date_of_rip": date_of_rip,
                "place_of_rip_date_year": i.place_of_rip_date_year,
                "place_of_rip_date_month": i.place_of_rip_date_month,
                "place_of_rip_date_day": i.place_of_rip_date_day,
                "military_unit": i.military_unit,
                "images": images,
                "source_image": source_image,
            })
        return Response({'person': person_list}, status=status.HTTP_200_OK)


class CallBackCreateAPIView(CreateAPIView):
    queryset = CallBack.objects.all()
    serializer_class = CallBackSerializer

    def perform_create(self, serializer):
        guest = User.objects.all().get(username='Guest')
        person_id = self.request.data.get('person_id')

        person = get_object_or_404(Person, id=person_id)
        serializer.save(
            published=CallBack.StatusCallBackPostChoices.PROCESSING,
            user=guest,
            person=person
        )


class PersonCreateAPIView(generics.CreateAPIView):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = (permissions.IsAuthenticated,)

