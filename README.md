## Установка Keycloak

```bash
    docker run -d \
    --name keycloak \
    -p 8080:8080 \
    -e KEYCLOAK_ADMIN=admin \
    -e KEYCLOAK_ADMIN_PASSWORD=admin \
    -e KC_HOSTNAME=localhost \
    quay.io/keycloak/keycloak:26.4.4 \
    start-dev
```

## Конфигурация

1) Откройте Keycloak
2) Создайте `realm` и `client`, сконфигурируйте их на свое усмотрение
3) Скопируйте `secret` клиента
4) Заполните `.env.example` и переименуйте в `.env`

## Запуск

### Venv
```bash
    python -m venv .venv
```

### Requirements
```bash
    source .venv/bin/activate
    pip install -r requirements.txt
```

### Launch

```bash
    python -m src.main
```