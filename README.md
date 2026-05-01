# API Starter — Litestar + Piccolo + PostgreSQL

Starter prêt à l'emploi pour construire une API REST async en Python.
Cloner, configurer le `.env`, implémenter les services — c'est tout.

---

## Stack

| Couche | Technologie |
|---|---|
| Framework | [Litestar](https://litestar.dev) — async ASGI, OpenAPI auto-généré |
| ORM & Migrations | [Piccolo](https://piccolo-orm.com) — async, migrations intégrées |
| Base de données | PostgreSQL 16 |
| Stockage fichiers | [MinIO](https://min.io) — S3-compatible, auto-hébergé |
| Auth | JWT (HTTP-only cookie) + Argon2 (hachage mot de passe) |
| Validation | Pydantic v2 + pydantic-settings |
| Email | aiosmtplib + Jinja2 (templates HTML) |
| Tests | Pytest + Litestar TestClient |
| Serveur prod | Gunicorn + Uvicorn workers |

---

## Structure

```
api-starter/
│
├── app.py                  # Entrypoint — instancie l'app Litestar
├── requirements.txt
├── Dockerfile
├── compose.yml             # API + PostgreSQL + MinIO + Adminer
├── Makefile                # Commandes dev
│
├── core/                   # Utilitaires partagés entre toutes les features
│   ├── settings.py         # Variables d'environnement (pydantic-settings)
│   ├── database.py         # Connexion PostgreSQL + registre des migrations Piccolo
│   ├── exceptions.py       # Hiérarchie d'erreurs + handlers HTTP
│   ├── guards.py           # auth_guard (vérifie le JWT cookie)
│   ├── mail.py             # send_email() — transport SMTP générique
│   └── storage.py          # MinIO — upload, delete, url publique
│
├── features/               # Un dossier par domaine métier
│   └── auth/               # Feature authentification (incluse par défaut)
│       ├── controller.py   # Routes HTTP (/auth/*, /users/*)
│       ├── service.py      # Logique métier (stubs à implémenter)
│       ├── schemas.py      # Pydantic request/response models
│       ├── tables.py       # Tables Piccolo (User, PasswordResetToken)
│       ├── helpers.py      # JWT, hachage, user_to_response, email helpers
│       ├── exceptions.py   # Exceptions spécifiques auth
│       ├── piccolo_app.py  # Déclaration des tables pour les migrations
│       ├── templates/      # Templates HTML des emails (Jinja2)
│       │   └── reset_password.html
│       └── test_auth.py    # Tests Pytest
│
└── scripts/
    └── new_feature.py      # Générateur de feature (voir Makefile)
```

---

## Démarrage rapide

### Prérequis
- Docker + Docker Compose
- Python 3.11+

### 1. Cloner et configurer

```bash
git clone <repo> my-project
cd my-project

cp .env.example .env
# Éditer .env et remplir toutes les valeurs requises
```

### 2. Lancer avec Docker

```bash
make up
```

Cela démarre :
- **API** → http://localhost:8000
- **Docs** → http://localhost:8000/docs
- **Adminer** (interface DB) → http://localhost:8080
- **MinIO Console** → http://localhost:9001

Les migrations sont appliquées automatiquement au démarrage.

### 3. Développement local (sans Docker)

```bash
# Installer les dépendances
make install

# Appliquer les migrations (PostgreSQL doit tourner)
make migrate

# Lancer le serveur avec hot-reload
make dev
```

---

## Variables d'environnement

Copier `.env.example` → `.env` et remplir les champs. Les champs sans valeur par défaut sont **obligatoires** — l'API refusera de démarrer si l'un d'eux est manquant.

| Variable | Obligatoire | Description |
|---|---|---|
| `POSTGRES_USER` | Oui | Utilisateur PostgreSQL |
| `POSTGRES_PASSWORD` | Oui | Mot de passe PostgreSQL |
| `POSTGRES_DB` | Oui | Nom de la base de données |
| `SECRET_KEY` | Oui | Clé de signature JWT |
| `ADMIN_EMAIL` | Oui | Email du compte admin créé au démarrage |
| `ADMIN_PASSWORD` | Oui | Mot de passe du compte admin |
| `MINIO_ACCESS_KEY` | Oui | Clé d'accès MinIO |
| `MINIO_SECRET_KEY` | Oui | Clé secrète MinIO |
| `APP_NAME` | Non | Nom affiché dans les emails et l'OpenAPI |
| `ALLOWED_ORIGINS` | Non | Liste JSON des origines CORS autorisées |

---

## Ajouter une feature

```bash
make feature name=clients
```

Génère automatiquement dans `features/clients/` :

```
controller.py   service.py   schemas.py   tables.py
helpers.py      exceptions.py   piccolo_app.py
test_clients.py   templates/   migrations/
```

Ensuite :

1. **Implémenter** `features/clients/service.py`
2. **Enregistrer la table** dans `core/database.py` :
   ```python
   APP_REGISTRY = AppRegistry(apps=[
       "features.auth.piccolo_app",
       "features.clients.piccolo_app",  # ← ajouter
   ])
   ```
3. **Enregistrer le controller** dans `app.py` :
   ```python
   from features.clients.controller import ClientsController

   app = Litestar(
       route_handlers=[..., ClientsController],
   )
   ```
4. **Créer la migration** :
   ```bash
   make migration app=clients
   ```

---

## Commandes Makefile

| Commande | Description |
|---|---|
| `make up` | Lance tous les services Docker |
| `make down` | Arrête les services Docker |
| `make logs` | Affiche les logs de l'API |
| `make dev` | Serveur local avec hot-reload |
| `make install` | Installe les dépendances Python |
| `make migrate` | Applique toutes les migrations |
| `make migration app=xxx` | Génère une migration pour la feature `xxx` |
| `make feature name=xxx` | Génère le squelette d'une nouvelle feature |
| `make test` | Lance tous les tests Pytest |

---

## Auth — endpoints inclus

| Méthode | Route | Description |
|---|---|---|
| `POST` | `/auth/register` | Créer un compte |
| `POST` | `/auth/login` | Connexion (retourne un cookie JWT) |
| `GET` | `/auth/me` | Profil de l'utilisateur connecté |
| `DELETE` | `/auth/logout` | Déconnexion (supprime le cookie) |
| `POST` | `/auth/forgot-password` | Envoie un email de réinitialisation |
| `POST` | `/auth/reset-password` | Réinitialise le mot de passe |
| `PATCH` | `/users/me` | Mettre à jour le profil |
| `PATCH` | `/users/me/password` | Changer le mot de passe |
| `POST` | `/users/me/avatar` | Upload photo de profil |

> La logique de ces routes est dans `features/auth/service.py` — les méthodes sont des stubs `NotImplementedError` à implémenter.

---

## Protéger une route

```python
from core.guards import auth_guard

class MyController(Controller):
    guards = [auth_guard]  # toutes les routes du controller
```

ou sur une route spécifique :

```python
@get("/secret", guards=[auth_guard])
async def secret(self) -> dict:
    ...
```

---

## Envoyer un email

Ajouter un template HTML dans `features/ma_feature/templates/`, puis dans `helpers.py` :

```python
async def send_welcome_email(to_email: str, name: str) -> None:
    await send_email(
        to=to_email,
        subject=f"Bienvenue — {settings.APP_NAME}",
        text=f"Bonjour {name}",
        html=_render("welcome.html", name=name),
    )
```
