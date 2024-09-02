# Develop (як запустити)

## Загальна інформація

- Розробник може розгорнути локальне розробницьке середовище в режимі develop та staging.
  - develop - код оновлюється автоматично
  - staging - треба повторно робити "ребилд" (повторно виконати скрипт запуску)
  - За рахунок різних імен контейнеру, можна одночасно розгортати develop та staging
- Усе, що пов'язано з розробкою (розгортання локального розробницького середовища) знаходиться у директорії `develop`  
- Загалом, приклади команд будуть надані для Linux (bash)

## Який робочий процес

- Зробити нову гілку від `main`. Вносити зміни в рамках цієї нової гілки
- Розгорнути локальний Dev
  - За необхідності наповнити БД даними з дампу проекту
  - Додавати \ модифікувати функціонал, одразу перевіряючи роботу в браузері
- Перед мерджем:
  - Розгорнути локальний Staging
  - Перевірити роботу на ньому
- Вмерджити зміни до `main`

## URL сервісу

### Розгорнутий сервіс доступний на цих адресах : портах

- Develop: <http://127.0.0.1:8000>
- Staging: <http://127.0.0.1:8080>

### API Path

~~~plain
Url admin: http://127.0.0.1:8080/admin/
Url dashboard: http://127.0.0.1:8080/
Url api doc: http://127.0.0.1:8080/api/v1/
~~~

## Підготовка

### Встановити Docker

Встановити Docker Desktop

або  

Якщо розробка ведеться на Windows 10 \ Windows 11, то ідеальним варіантом буде використання wsl,
де налаштована робота Systemd
> це дозволяє запускати docker *без* використання Docker desktop

- Налаштувати `wsl`
- Налаштувати у `wsl` [Systemd](https://devblogs.microsoft.com/commandline/systemd-support-is-now-available-in-wsl/)
- Systemd треба для того, щоб запускати docker всередині `wsl`, не використовуючи Docker Desktop
- встановити docker (у різних дистрибутивах може робитися по-різному)

### Налаштувати env-файл для проекту

- Перейти до директорії `develop`
- Всередині директорії створити файл зі змінними середовища `env-develop` для `dev` середовища та `env-staging` для `staging` середовища, скопіювавши `template-env-develop` та змінивщи його для конкретних задач.  

  ~~~shell
  cp example_develop-env develop-env
  cp example_develop-env staging-env
  ~~~

- Додати до файлу `env-develop` значення змінної `SECRET_KEY_SC` (Django Secret Key)  
  *Його мають знати розробники, або скопіювати значення з CI Variables проекту*
- Додати до файлу `env-staging` значення змінних:
- 1 - `CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8080`
- 2 - `DEBUG=0`

## Як розгорнути

- Створено два окремих `docker compose` файли
  - `docker-compose-develop.yml`  
    Для підняття локального розробницького середовища. Корень проекту монтується, тому усі зміни одразу доступні
  - `docker-compose-staging.yml`  
    Для підняття локального staging-середовища. Максимально наближене до production,
    використовує entrypoint, що й production.  
    !!! Бажано синхронізувати з production compose, але БД брати з develop compose
- Для запуску використовуйте скрипти запуску \ видалення
  > Команда для запуску docker compose відповідного середовища досить довга
  > Тому і створено скрипти

  - Для Linux (shell, bash) вони йдуть з приставкою `linux-`
  - Для Windows (cmd / Powershell) вони йдуть з приставкою `windows-`

### Develop

#### Розгорнути локальний develop  

Для запуску запустити відповідний скрипт.  
*приклад:* `./linux-start-develop.sh`

#### Зупинити та видалити локальний develop

> Compose розгртається в звичайному режимі, не в `detached` (аргумент -d)  
> Тому, якщо просто треба зупинити контейнер, то виконайте комбінацію клавіш `CTRL+C` або закрийте термінал
> Щоб повторно запустити сервіс, то просто повторно виконайте `start-скрипт` (як при початковому розгортані)

Для ВИДАЛЕННЯ сервісу запустити відповідний скрипт  
*приклад:* `./linux-remove-develop.sh` (!!!дані БД буде втрачено)

### Staging

Для розгортання локального Staging-середовища використовується схожий набір команд, але з приставкою `staging`

- `linux-start-staging.sh` - початкове розгортання сервісу + перезапуск (перебилд) Docker-image
- `linux-remove-staging.sh` - видалення сервісу (!!!дані БД буде втрачено)

## Як завантажити dump до бази сервісу

- Отримати останній дамп poternet (для прикладу, його назва `war_crime.2023-04-14-0200.sql.gz`)
- Скопіювати його до директорії проекту `develop`
- Команди треба виконувати всередині директорії `develop`
- Виконати команду
  - Якщо розширення файлу `*.sql.gz`
    - Develop

        ~~~shell
        gunzip < war_crime.2023-04-14-0200.sql.gz | docker compose -f docker-compose-develop.yml --project-name "war-crime-develop" exec -T poternet_db psql -U war_crime_user -d war_crime
        ~~~

    - Staging

        ~~~shell
        gunzip < war_crime.2023-04-14-0200.sql.gz | docker compose -f docker-compose-staging.yml --project-name "war-crime-staging" exec -T poternet_db psql -U war_crime_user -d war_crime
        ~~~

  - Якщо розширення файлу `*.sql`  
    - Develop

        ~~~shell
        cat < war_crime.2023-04-14-0200.sql | docker compose -f docker-compose-develop.yml --project-name "war-crime-develop" exec -T poternet_db psql -U war_crime_user -d war_crime
        ~~~

    - Staging

        ~~~shell
        cat < war_crime.2023-04-14-0200.sql | docker compose -f docker-compose-staging.yml --project-name "war-crime-staging" exec -T poternet_db psql -U war_crime_user -d war_crime
        ~~~

## Як підготувати міграцю

- Міграція виконується розробником на локальній машині з розгорнутим середовищем в **режимі Develop**
- Виконати міграцію (виконати команду) `python manage.py migrate`
  - Або підключившись до контейнеру, де працює сервіс (`war-crime-develop-web-1`)
  - Або перейти в директорію `develop` та виконати команду

    ~~~shell
    docker compose -f docker-compose-develop.yml --project-name "war-crime-develop" exec -T web python manage.py makemigrations
    ~~~

- Так як в режимі Develop повністю монтується директорія проекту (вона доступна в контейнері), 
  то результуючий файл (для прикладу `0025_migration.py`) просто з'явиться в директорії з міграціями `diap/migrations`
- Залишиться лише закомітити зміни до проекту, а при розгортані Staging\Production вони підтянуться (виконаються)
