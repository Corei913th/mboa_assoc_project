# 🗺️ Guide des Routes - Mboa Assoc

## 📍 Routes Publiques

| Route | URL | Description |
|-------|-----|-------------|
| Landing | `/` | Page d'accueil publique |
| Inscription | `/auth/register/` | Créer un compte avec téléphone |
| Vérification OTP | `/auth/verify-otp/` | Vérifier le code SMS |
| Connexion | `/auth/login/` | Se connecter |

## 🏠 Dashboard Utilisateur

| Route | URL | Description |
|-------|-----|-------------|
| Dashboard | `/dashboard/` | Tableau de bord principal |
| Profil | `/auth/profile/` | Modifier son profil |
| Déconnexion | `/auth/logout/` | Se déconnecter |
| Mes Associations | `/mes-associations/` | Liste de toutes mes associations |
| Mes Invitations | `/mes-invitations/` | Invitations en attente |

## 🏢 Gestion des Associations

| Route | URL | Description | Accès |
|-------|-----|-------------|-------|
| Créer | `/association/creer/` | Créer une nouvelle association | Connecté |
| Dashboard | `/association/{id}/dashboard/` | Dashboard de l'association | Membre |
| Détails | `/association/{id}/` | Voir les détails | Membre |
| Paramètres | `/association/{id}/parametres/` | Modifier les paramètres | Président |
| Archiver | `/association/{id}/archiver/` | Archiver l'association | Président |
| Supprimer | `/association/{id}/supprimer/` | Supprimer définitivement | Président |

## 👥 Gestion des Membres

| Route | URL | Description | Accès |
|-------|-----|-------------|-------|
| Liste | `/associations/{id}/membres/` | Liste des membres | Membre |
| Inviter | `/associations/{id}/inviter/` | Inviter par téléphone | Président/Trésorier |
| Accepter invitation | `/invitations/accepter/{code}/` | Accepter/Refuser | Invité |
| Détail membre | `/associations/{id}/membres/{membre_id}/detail/` | Voir profil membre | Membre |
| Changer rôle | `/associations/{id}/membres/{membre_id}/changer-role/` | Modifier le rôle | Président |
| Exclure | `/associations/{id}/membres/{membre_id}/exclure/` | Retirer un membre | Président |
| Export CSV | `/association/{id}/export-membres/` | Télécharger liste CSV | Président/Trésorier |

## 💰 Cotisations

| Route | URL | Description | Accès |
|-------|-----|-------------|-------|
| Liste | `/association/{id}/cotisations/` | Toutes les cotisations | Membre |
| Créer | `/association/{id}/cotisations/creer/` | Nouvelle cotisation | Président/Trésorier |

## 💳 Paiements

| Route | URL | Description | Accès |
|-------|-----|-------------|-------|
| Effectuer | `/cotisation/{id}/payer/` | Payer une cotisation | Membre |
| Historique | `/association/{id}/paiements/` | Historique des paiements | Membre |

---

## 🎯 Navigation Rapide depuis le Dashboard

### Depuis le Dashboard Principal (`/dashboard/`)
- ✅ Voir toutes mes associations
- ✅ Créer une nouvelle association
- ✅ Accéder à mes invitations
- ✅ Modifier mon profil
- ✅ Accès rapide au dashboard de chaque association

### Depuis le Dashboard Association (`/association/{id}/dashboard/`)
- ✅ Voir les statistiques (membres, collecte, échéances)
- ✅ Accéder aux cotisations
- ✅ Voir la liste des membres
- ✅ Inviter de nouveaux membres (si président/trésorier)
- ✅ Exporter la liste des membres en CSV
- ✅ Voir les derniers paiements
- ✅ Voir les membres récents

### Depuis la Sidebar (toujours visible)
- ✅ Dashboard principal
- ✅ Mon profil
- ✅ Mes associations
- ✅ Mes invitations (avec badge si nouvelles)
- ✅ Déconnexion

---

## 🔐 Niveaux d'Accès

### Public
- Landing page
- Inscription
- Connexion

### Connecté
- Dashboard
- Profil
- Créer association
- Voir invitations

### Membre
- Dashboard association
- Liste cotisations
- Liste membres
- Effectuer paiements
- Voir historique

### Trésorier
- Tout ce que Membre peut faire
- Créer cotisations
- Inviter membres
- Export CSV

### Président
- Tout ce que Trésorier peut faire
- Modifier paramètres association
- Changer rôles membres
- Exclure membres
- Archiver/Supprimer association

---

## 🎨 Structure des URLs

```
/                                   # Landing
├── auth/
│   ├── register/                   # Inscription
│   ├── verify-otp/                 # Vérification OTP
│   ├── login/                      # Connexion
│   ├── logout/                     # Déconnexion
│   └── profile/                    # Profil
│
├── dashboard/                      # Dashboard principal
│
├── mes-associations/               # Liste associations
├── mes-invitations/                # Liste invitations
│
├── association/
│   ├── creer/                      # Créer
│   └── {id}/
│       ├── dashboard/              # Dashboard association
│       ├── parametres/             # Paramètres
│       ├── membres/                # Gestion membres
│       ├── cotisations/            # Liste cotisations
│       │   └── creer/              # Créer cotisation
│       ├── paiements/              # Historique paiements
│       ├── export-membres/         # Export CSV
│       ├── archiver/               # Archiver
│       └── supprimer/              # Supprimer
│
├── associations/{id}/
│   ├── membres/                    # Liste membres
│   ├── inviter/                    # Inviter
│   └── membres/{membre_id}/
│       ├── detail/                 # Détail membre
│       ├── changer-role/           # Changer rôle
│       └── exclure/                # Exclure
│
├── invitations/
│   └── accepter/{code}/            # Accepter invitation
│
└── cotisation/{id}/
    └── payer/                      # Effectuer paiement
```

---

## 🚀 Flux Utilisateur Typique

### 1. Nouvel Utilisateur (Ali)
```
/ → /auth/register/ → /auth/verify-otp/ → /dashboard/
```

### 2. Créer Association
```
/dashboard/ → /association/creer/ → /association/{id}/dashboard/
```

### 3. Inviter Membre (Bob)
```
/association/{id}/dashboard/ → /associations/{id}/inviter/
```

### 4. Bob Accepte
```
/mes-invitations/ → /invitations/accepter/{code}/ → /association/{id}/dashboard/
```

### 5. Créer Cotisation
```
/association/{id}/dashboard/ → /association/{id}/cotisations/creer/
```

### 6. Bob Paie
```
/association/{id}/cotisations/ → /cotisation/{id}/payer/ → /association/{id}/paiements/
```

### 7. Voir Résultats
```
/association/{id}/dashboard/ (stats mises à jour)
```

---

## 📱 Navigation Mobile

Toutes les routes sont optimisées pour mobile avec:
- ✅ Menu hamburger responsive
- ✅ Cartes empilables
- ✅ Boutons tactiles larges
- ✅ Navigation simplifiée
- ✅ Sidebar collapsible

---

## 🎯 Points d'Entrée Principaux

Pour la démo, commencer par:
1. **Landing** (`/`) - Présenter la plateforme
2. **Dashboard** (`/dashboard/`) - Montrer l'interface utilisateur
3. **Association Dashboard** (`/association/{id}/dashboard/`) - Montrer les stats
4. **Cotisations** (`/association/{id}/cotisations/`) - Montrer les paiements

Ces 4 pages montrent l'essentiel de la plateforme! 🚀
