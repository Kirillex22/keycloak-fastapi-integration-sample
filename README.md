# Установка Keycloak

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

# Запуск

## Venv
```bash
    python -m venv .venv
```

## Requirements
```bash
    source .venv/bin/activate
    pip install -r requirements.txt
```

## Launch

```bash
    python -m src.main
```