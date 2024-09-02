# (DRF_DIAP) Django DRF DIAP project

## Develop

Опис того, як робити локальну викатку зроблено в [окремому README](develop/README.md)

## Production

Викатка йде через GitLab CI на VM в мережі інтернет  
Більш детальна інформація в [корпоративній вікі](https://confluence.in.np.gov.ua/pages/viewpage.action?pageId=117309674)

## Environment variables

> Перелік змінних середовища, що використовуються у проекті

| Environment variable | Description | Default value |
| -------------------- | ----------- | ------------- |
| PUBLIC_URL | (лише для `production`) вказується зовнішя адреса сервісу для Traefik (load balancer) (приклад: \`195.0.0.1\`) |  |
| USERS_API | (лише для `production`) user\pass для "Basic Auth with an HTTP load balancer" - авторизація за допомогою Traefik   |  |
**БД**
| DATABASE_NAME | назва БД (схеми) в БД, до якої буде підключення |  |
| DATABASE_USER | користувач (user) БД для підключення |  |
| DATABASE_PASSWORD | пароль користувача DATABASE_USER для підключення до БД |  |
| DATABASE_HOST | адреса (хост) БД, до якої проект буде підключатися |  |
| DATABASE_PORT | порт бази даних для підключення |  |
| SECRET_KEY_SC | Django Secret Key (секретний ключ Django)|  |
| CSRF_TRUSTED_ORIGINS | схоже на ALLOWED_HOSTS АЛЕ з приставкою протоколу (`приклад - https://127.0.0.1`) |  |
| ALLOWED_HOSTS | вказується IP, на якому працює проект (з якого доступний) |  |
| DEBUG | вказує, в якому режимі запускається проект. | 1 (True) - числом |
**Email**
| EMAIL_HOST | Host пошти |  |
| EMAIL_HOST_USER | логін пошти |  |
| EMAIL_HOST_PASSWORD | пароль до пошти |  |
| EMAIL_PORT | на якому порту працює пошта (щоб відправити) |  |
| EMAIL_USE_TLS | Whether to use TLS for email connection | 1 (True) - числом |
| EMAIL_USE_SSL | Whether to use SSL for email connection | 0 (False) - числом |
**IP для підключення боту \ власника ?** (уточняти у розробника, що за owner і для чого воно)
| ALLOW_IP_API_BOT | (можливо неактуально, але є у коді) прописується в ALLOW_IP_API. IP TG бота. |  |
| ALLOW_IP_API_OWNER | (можливо неактуально, але є у коді) рописується в ALLOW_IP_API. IP одного із розробників. Редагує (тестує?) API. |  |
