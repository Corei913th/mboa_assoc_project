# Plateforme de Gestion des Associations Camerounaises

Projet académique - Gestion des membres, cotisations et paiements Mobile Money.

## Stack Technique

- Django 5.1.4
- MySQL (PyMySQL)
- Tailwind CSS
- Django REST Framework

## Installation

### Prérequis
- Python 3.10+
- MySQL 8.0+
- Node.js 14+ (pour Tailwind)

### 1. Environnement

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 2. Base de données

```bash
mysql -u root -p
CREATE DATABASE mboa_assoc_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

Configurer `.env` :
```env
DB_NAME=mboa_assoc_db
DB_USER=root
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=3306
```

### 3. Migrations

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 4. Tailwind CSS

```bash
python manage.py tailwind init  # Nommer l'app: theme
python manage.py tailwind install
```

Ajouter dans `settings.py` :
```python
INSTALLED_APPS = [
    # ...
    'tailwind',
    'theme',
    'django_browser_reload',
]

MIDDLEWARE = [
    # ...
    'django_browser_reload.middleware.BrowserReloadMiddleware',
]

TAILWIND_APP_NAME = 'theme'
INTERNAL_IPS = ["127.0.0.1"]
```

Ajouter dans `urls.py` :
```python
path("__reload__/", include("django_browser_reload.urls")),
```

### 5. Lancer

Terminal 1 :
```bash
python manage.py tailwind start
```

Terminal 2 :
```bash
python manage.py runserver
```

## Structure

```
mboa_assoc_project/
├── mboa_assoc/              # Configuration
├── mboa_assoc_app/          # Application
│   ├── models.py            # Membre, Association, Cotisation, Paiement
│   ├── views.py
│   ├── urls.py
│   ├── templates/
│   ├── static/
│   └── services/            # Mobile Money, Notifications
├── theme/                   # Tailwind CSS
├── media/                   # Uploads
└── .env                     # Configuration
```

## Modèles Principaux

- **Membre** : Utilisateur avec authentification Django
- **Association** : Tontines, coopératives, syndicats
- **Cotisation** : Mensuelle, annuelle, événement
- **Paiement** : Mobile Money (MTN, Orange)
- **Notification** : SMS, Email, in-app
- **Fonctionnalite** : Gestion des fonctionnalités par plan

## API

- Documentation : http://localhost:8000/api/
- Admin : http://localhost:8000/admin

## Commandes Utiles

```bash
# Migrations
python manage.py makemigrations
python manage.py migrate

# Créer un admin
python manage.py createsuperuser

# Shell Django
python manage.py shell

# Tests
python manage.py test

# Compiler Tailwind pour production
python manage.py tailwind build
```

## MySQL avec PyMySQL

PyMySQL est configuré automatiquement dans `settings.py`. Pas besoin de compilation.

## Template Tailwind

```html
{% load static tailwind_tags %}
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Mboa Assoc</title>
    {% tailwind_css %}
</head>
<body class="bg-gray-100">
    <div class="container mx-auto px-4">
        <h1 class="text-3xl font-bold text-blue-600">
            Gestion des Associations
        </h1>
    </div>
</body>
</html>
```

## Fonctionnalités MVP

1. **Gestion des Membres** : Profils, statuts, historique
2. **Cotisations** : Configuration, échéanciers, rappels
3. **Paiements Mobile Money** : MTN, Orange, reçus automatiques
4. **Notifications** : SMS, Email pour rappels et confirmations
5. **Dashboard** : Vue d'ensemble des cotisations et paiements

## Dépannage

**Erreur PyMySQL** : Déjà configuré dans settings.py

**Erreur Pillow** : `pip install Pillow --only-binary :all:`

**Erreur Tailwind** : Vérifier Node.js installé (`node --version`)

## Licence

Projet académique - IUC CS2I
