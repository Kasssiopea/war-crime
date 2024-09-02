import csv

from django.core.exceptions import PermissionDenied
from django.db.models.functions import Coalesce, Cast
from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.contrib.auth import logout, login, get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage, send_mail
from django.db.models import Q, F, IntegerField
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views import View
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.generic import ListView, DetailView, CreateView, FormView
from django.db.models import Count
from io import StringIO
from django.shortcuts import render, redirect

from django.conf import settings
from DRF_DIAP import settings
from diap.forms.callback_form import CallBackForm
from diap.forms.client import ClientCreateForm, LogInClientForm
from diap.models.choices import StatusPersonPostPublished, StatusPersonPostChoices
from diap.models.partners import Partners
from diap.models.person import Person, PersonImage, SoursePersonImage
from diap.tokens import account_activation_token

from django.core.paginator import Paginator

from diap.models.front import NewsDead, ImportantNews
from diap.forms.callback_form import NewPerson, NewPersonImg


class IndexPage(ListView):
    model = Person
    template_name = 'diap/index.html'
    context_object_name = 'persons'

    def get_context_data(self, **kwargs):
        context = super(IndexPage, self).get_context_data(**kwargs)

        queryset = Person.objects.all().filter(publish_status=StatusPersonPostPublished.PUBLISHED,
                                               images__isnull=False). \
            annotate(num_images=Count('images')).order_by('-time_update', '-num_images', ).distinct()
        # persons_counter = Person.objects.all().filter(publish_status='PUBLISHED').count()
        news = NewsDead.objects.all().order_by('-time_create')

        important_news = ImportantNews.objects.all().filter(published=True)
        partners = Partners.objects.all().filter(published=True)
        context.update({
                'title': 'Потерь.НЕТ',
                'persons': queryset[:100],
                # 'persons_counter': persons_counter,
                'news': news,
                'important_news': important_news,
                'partners': partners,
        })
        return context


class Persons(ListView):
    model = Person
    template_name = 'diap/persons.html'
    context_object_name = 'persons'
    paginate_by = 40

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(Persons, self).get_context_data(**kwargs)
        queryset = Person.objects.all().filter(
            publish_status=StatusPersonPostPublished.PUBLISHED).filter(~Q(images=None)).annotate(num_images=Count('images'))\
            .order_by('-num_images').order_by('-time_create').distinct()

        if self.request.GET.get("search_pib"):
            search_pib = self.request.GET.get("search_pib")
            for word in search_pib.split():
                q_list = Q()
                q_list |= Q(first_name__icontains=word)
                q_list |= Q(last_name__icontains=word)
                q_list |= Q(middle_name__icontains=word)
                queryset = queryset.filter(q_list)
        queryset = Paginator(queryset, self.paginate_by)
        context.update({
                'title': _('Пошук'),
                'persons': queryset.page(context['page_obj'].number)
            })

        return context


class DetailPerson(DetailView, CreateView):
    model = Person
    # queryset = Person.objects.all().filter(publish_status=StatusPersonPostPublished.PUBLISHED)
    template_name = 'diap/person.html'
    pk_url_kwarg = 'post_person_pk'
    context_object_name = 'person'
    allow_empty = False
    form_class = CallBackForm

    def get_object(self, queryset=None):
        obj = super(DetailPerson, self).get_object()
        if self.request.user.is_staff:
            return obj
        elif obj.post_status == StatusPersonPostPublished.PUBLISHED:
            return obj
        else:
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super(DetailPerson, self).get_context_data(**kwargs)
        person = context.get('person')
        context.update({
                'title': person.last_name,
                'images': PersonImage.objects.all().filter(person_id=person.pk),
                'source_images': SoursePersonImage.objects.all().filter(person_id=person.pk),
            })
        return context


    def form_valid(self, form):
        person = self.get_object()
        callback = form.save(commit=False)
        callback.person = person
        callback.user = self.request.user
        callback.save()
        return redirect(person.get_absolute_url())


class RegisterClient(CreateView):
    form_class = ClientCreateForm
    template_name = 'diap/reg.html'
    success_url = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            redirect_to = self.get_success_url()
            if redirect_to == self.request.path:
                raise ValueError(
                    "Redirection loop for authenticated user detected. Check that "
                    "your LOGIN_REDIRECT_URL doesn't point to a login page."
                )
            return HttpResponseRedirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
                'title': _("Реєстрація користувача"),
            })
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        activateEmail(request=self.request, user=user, to_email=form.cleaned_data.get('email'))
        return redirect('home')

    def get_success_url(self):
        return reverse_lazy('home')


class LoginClient(LoginView):
    form_class = LogInClientForm
    template_name = 'diap/login.html'
    redirect_authenticated_user = True

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
                'title': _("Вхід"),
            })
        return context

    def get_success_url(self):
        return reverse_lazy('home')
# Statistic


class Statistic(ListView):
    model = Person
    template_name = 'diap/statistic.html'
    statistic = []

    def get(self, *args, **kwargs):
        if not self.request.user.is_superuser:
            return redirect('home')
        if self.request.GET:
            response = self.request.GET
            persons = Person.objects.all()
            date_from = response.get('startDate') if response.get('startDate') else "2020-01-01"
            date_to = response.get('endDate') if response.get('endDate') else str(timezone.now().strftime('%Y-%m-%d'))
            zvit = True if response.get('Zvit') == 'on' else False
            group = response.get('Group')
            if group in ['CHNUVS', 'NAVS', 'DIAP', 'DDUVS', 'LDUVS', 'ODUVS']:
                groups = User.objects.all().filter(groups__name=group)
                group = groups.filter(is_staff=True)
                user_not_staff = groups.filter(is_staff=False)
                user_not_staff_usernames = list(user_not_staff.values_list('username', flat=True))
                print(user_not_staff_usernames)
            else:
                group = []
                user_not_staff_usernames = []
            users = []
            for i in group:
                users.append({
                        'Username': i.username,
                        'Published': persons.filter(task_published=i.username, task_published_date__range=[str(date_from), str(date_to)]).count(),
                        'Processing': persons.filter(task_processing=i.username, task_processing_date__range=[str(date_from), str(date_to)]).count(),
                        'Deleted': persons.filter(task_deleted=i.username, task_deleted_date__range=[str(date_from), str(date_to)]).count(),
                        'For_check': persons.filter(task_for_check=i.username, task_for_check_date__range=[str(date_from), str(date_to)]).count(),
                })
            users.append({
                'Username': 'Deleted users',
                'Published': persons.filter(task_published__in=user_not_staff_usernames,
                                            task_published_date__range=[str(date_from), str(date_to)]).count(),
                'Processing': persons.filter(task_processing__in=user_not_staff_usernames,
                                             task_processing_date__range=[str(date_from), str(date_to)]).count(),
                'Deleted': persons.filter(task_deleted__in=user_not_staff_usernames,
                                          task_deleted_date__range=[str(date_from), str(date_to)]).count(),
                'For_check': persons.filter(task_for_check__in=user_not_staff_usernames,
                                            task_for_check_date__range=[str(date_from), str(date_to)]).count(),
            })

            if zvit:
                employee_info = ['Username', 'Published', 'Processing', 'Deleted', 'For_check']
                response = HttpResponse(content_type='text/csv')
                response['Content-Disposition'] = 'attachment; filename="export.csv"'
                writer = csv.DictWriter(response, fieldnames=employee_info)
                writer.writeheader()
                writer.writerows(users)
                redirect('statistic')
                return response
            else:
                self.statistic = users
        return super(Statistic, self).get(*args, **kwargs)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'title': "Статистика",
            'users': self.statistic
        })
        return context


# For Email
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
        return redirect('login')
    else:
        messages.error(request, 'Error')
    return redirect('home')


def logout_user(request):
    logout(request)
    return redirect('home')


def pageNotFound(request, exception):
    return render(request, 'diap/404.html', status=404)


class News(ListView):
    template_name = 'diap/news.html'
    context_object_name = 'news'
    model = ImportantNews

    def get_context_data(self, **kwargs):
        context = super(News, self).get_context_data(**kwargs)
        important_news = ImportantNews.objects.all().filter(published=True)
        context.update({
                'title': _('Новини'),
                'important_news': important_news,
        })
        return context


class TestForm(FormView):
    template_name = 'diap/message.html'
    new_person = None
    new_person_img = None
    new_person_img2 = None
    new_person_img3 = None

    def get(self, request, *args, **kwargs):
        self.new_person = NewPerson()
        self.new_person_img = NewPersonImg(prefix='photo')
        self.new_person_img2 = NewPersonImg(prefix='photo2')
        self.new_person_img3 = NewPersonImg(prefix='photo3')

        context = {'person': self.new_person, 'photo': self.new_person_img, 'photo2': self.new_person_img2, 'photo3': self.new_person_img3, 'title': _('Повідомити про загиблого'),}
        return render(request, self.template_name, context)

    def post(self, request):
        if request.method == 'POST':
            if self.new_person is None:
                self.new_person = NewPerson(request.POST)
            if self.new_person_img is None:
                self.new_person_img = NewPersonImg(request.POST, request.FILES, prefix='photo')
            if self.new_person_img2 is None:
                self.new_person_img2 = NewPersonImg(request.POST, request.FILES, prefix='photo2')
            if self.new_person_img3 is None:
                self.new_person_img3 = NewPersonImg(request.POST, request.FILES, prefix='photo3')

            if self.new_person.is_valid() and self.new_person_img.is_valid() and self.new_person_img2.is_valid() and self.new_person_img3.is_valid():
                np = self.new_person.save(commit=False)
                np.post_status = StatusPersonPostChoices.INCOMING

                np_img = self.new_person_img.save(commit=False)
                np_img.person = np

                np_img2 = self.new_person_img2.save(commit=False)
                np_img2.person = np

                np_img3 = self.new_person_img3.save(commit=False)
                np_img3.person = np

                np.save()

                if request.FILES.get('photo-image'):
                    np_img.save()
                if request.FILES.get('photo2-image'):
                    np_img2.save()
                if request.FILES.get('photo3-image'):
                    np_img3.save()
                return redirect('home')
        else:
            self.new_person = NewPerson()
            self.new_person_img = NewPersonImg(prefix='photo')
            self.new_person_img2 = NewPersonImg(prefix='photo2')
            self.new_person_img3 = NewPersonImg(prefix='photo3')

        errors_np = self.new_person.errors.items() if self.new_person.errors else None
        errors_np_img = self.new_person_img.errors.items() if self.new_person_img.errors else None
        errors_np_img2 = self.new_person_img2.errors.items() if self.new_person_img2.errors else None
        errors_np_img3 = self.new_person_img3.errors.items() if self.new_person_img3.errors else None

        context = {'person': self.new_person, 'photo': self.new_person_img, 'photo2': self.new_person_img2, 
                   'errors_np': errors_np, 'errors_np_img': errors_np_img, 'errors_np_img2': errors_np_img2, 'errors_np_img3': errors_np_img3}
        return render(request, self.template_name, context)


from django.core.paginator import Paginator
from django.http import JsonResponse

def extractData(request):
    if request.user.is_superuser:
        # Определите количество записей на странице
        items_per_page = 400

        # Получите номер страницы из параметра запроса, если он предоставлен
        page_number = request.GET.get('page', 1)

        # Создайте Paginator и получите объект Page для текущей страницы
        persons = Person.objects.prefetch_related('images', 'source_images').all()
        paginator = Paginator(persons, items_per_page)
        current_page = paginator.page(page_number)

        csv_buffer = StringIO()
        writer = csv.writer(csv_buffer)

        # Получаем все имена полей из модели Person
        field_names = [field.name for field in Person._meta.fields]

        # Добавляем дополнительные поля для фотографий
        field_names += ['Фото', 'Джерело фото']

        writer.writerow(field_names)

        for person in current_page:
            # Получаем значения для всех полей
            values = [getattr(person, field) for field in field_names[:-2]]

            # Получаем URL-адреса фотографий
            image_urls = [photo.image.url for photo in person.images.all()]
            values.append(','.join(image_urls))

            source_photo_urls = [photo.image.url for photo in person.source_images.all()]
            values.append(','.join(source_photo_urls))

            writer.writerow(values)

        response = HttpResponse(csv_buffer.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="persons.csv"'

        csv_buffer.close()

        return response

    return JsonResponse({'error': 'Permission denied'})





class CheckDuplicateView(ListView):
    template_name = 'diap/check.html'
    context_object_name = 'check'
    def post(self, request, *args, **kwargs):
        if request.method == 'POST':
            data = request.POST.dict()
            surname = data["surname"]
            name = data["name"]
            last_name = data["last_name"]
            # persons = Person.objects.filter(
            #     Q(last_name__icontains=surname),
            #     Q(first_name__icontains=name),
            #     Q(middle_name__icontains=last_name) | Q(middle_name__isnull=True),
            # )
            persons = Person.objects.filter(
                Q(last_name__icontains=surname),
                Q(first_name__icontains=name),
                Q(middle_name__icontains=last_name) | Q(middle_name__isnull=True)
            ) | Person.objects.filter(
                Q(last_name__icontains=name),
                Q(first_name__icontains=surname),
                Q(middle_name__icontains=last_name) | Q(middle_name__isnull=True)
            ) | Person.objects.filter(
                Q(first_name__icontains=name),
                Q(last_name__icontains=surname),
                Q(middle_name__icontains=last_name) | Q(middle_name__isnull=True)
            ) | Person.objects.filter(
                Q(first_name__icontains=surname),
                Q(last_name__icontains=name),
                Q(middle_name__icontains=last_name) | Q(middle_name__isnull=True)
            )
            data = {'persons': persons}
            return render(request, self.template_name, context=data)


class ChartsJs(View):
    template_name = 'diap/charts.html'

    def get(self, request):
        return render(request, self.template_name, context={
            'title': _('Статистика')}
        )


@ensure_csrf_cookie
def ajax_charts(request):
    if request.method == 'POST':

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


        # Ranks response
        ranks = person.filter(rank_choice__isnull=False)\
            .exclude(rank_choice='00').values('rank_choice').annotate(count=Count('id'))
        ranks = {str(_(item['rank_choice'])): item['count'] for item in ranks}
        sorted_ranks_army = sort_dictionary(ranks, sort_rank_army)
        sorted_ranks_fleet = sort_dictionary(ranks, sort_rank_fleet)
        # Type of army response
        type_of_army = person.filter(type_of_army_choice__isnull=False)\
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
        return JsonResponse(response_data)

    response_data = {
        'message': 'Invalid request method'
    }
    return JsonResponse(response_data, status=400)
