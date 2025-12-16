# Tailwind CSS - Mboa Association

## 🚀 Installation

```bash
cd theme/static_src
pnpm install
```

## 📦 Scripts Disponibles

### Développement (avec watch)
```bash
pnpm run dev
```
Compile Tailwind en mode développement et surveille les changements.

### Build Production
```bash
pnpm run build
```
Compile et minifie Tailwind pour la production.

### Démarrer
```bash
pnpm start
```
Alias pour `pnpm run dev`.

## 🎨 Configuration

### Couleurs du Thème
Les couleurs sont définies dans `tailwind.config.js` et correspondent à celles de `mboa_assoc_app/static/css/style.css`:

- **Primary**: Vert émeraude `rgb(16 185 129)`
- **Secondary**: Orange ambré `rgb(245 158 11)`
- **Success**: Vert `rgb(34 197 94)`
- **Warning**: Jaune `rgb(251 191 36)`
- **Error**: Rouge `rgb(239 68 68)`
- **Info**: Bleu `rgb(96 165 250)`

### Fichiers
- `tailwind.config.js` - Configuration Tailwind
- `src/styles.css` - Point d'entrée CSS
- `../static/css/dist/styles.css` - CSS compilé (généré)

## 📝 Utilisation dans les Templates

```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/dist/styles.css' %}">
```

## 🔄 Workflow

1. **Développement**: `pnpm run dev` (laisse tourner en arrière-plan)
2. **Modifier les templates** avec les classes Tailwind
3. **Le CSS se recompile automatiquement**
4. **Production**: `pnpm run build` avant de commit

## 📦 Dépendances

- `tailwindcss` - Framework CSS
- `@tailwindcss/forms` - Styles pour les formulaires
- `@tailwindcss/typography` - Styles typographiques
- `@tailwindcss/aspect-ratio` - Utilitaires aspect-ratio
- `postcss` - Transformations CSS
- `cross-env` - Variables d'environnement cross-platform
- `rimraf` - Nettoyage de dossiers

## 🎯 Classes Personnalisées

### Animations
- `animate-float` - Animation flottante
- `animate-pulse-slow` - Pulse lent
- `animate-slide-up` - Slide vers le haut

### Spacing
- `space-touch` - 44px (touch-friendly)

## ⚠️ Important

- **Ne pas commit** `node_modules/` et `pnpm-lock.yaml`
- **Commit** le CSS compilé `theme/static/css/dist/styles.css`
- **Toujours build** avant de push en production
