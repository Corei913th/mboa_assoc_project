# Admin pour la gestion des associations

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Association, 
    Adhesion, 
    Membre,
    Cotisation,
    Paiement,
    PlanTarifaire,
    Fonctionnalite,
    Abonnement,
    Notification
)


# ============================================================================
# ADMINISTRATION DES MEMBRES (USER PERSONNALISÉ)
# ============================================================================

@admin.register(Membre)
class MembreAdmin(UserAdmin):
    """
    Interface d'administration pour les membres (modèle User personnalisé)
    """
    # Champs à afficher dans la liste
    list_display = [
        'username',
        'email',
        'get_full_name',
        'telephone',
        'statut',
        'is_active',
        'date_inscription'
    ]
    
    # Filtres
    list_filter = [
        'statut',
        'is_active',
        'is_staff',
        'date_inscription',
        'ville'
    ]
    
    # Recherche
    search_fields = [
        'username',
        'email',
        'first_name',
        'last_name',
        'telephone'
    ]
    
    # Organisation des champs dans le formulaire
    fieldsets = (
        ('Authentification', {
            'fields': ('username', 'password')
        }),
        ('Informations personnelles', {
            'fields': ('first_name', 'last_name', 'email', 'telephone', 'date_naissance')
        }),
        ('Adresse', {
            'fields': ('adresse', 'ville'),
            'classes': ('collapse',)
        }),
        ('Profil', {
            'fields': ('photo_profil', 'profession', 'statut')
        }),
        ('Notifications', {
            'fields': ('notification_sms', 'notification_email'),
            'classes': ('collapse',)
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Dates importantes', {
            'fields': ('date_inscription', 'derniere_connexion', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    # Champs en lecture seule
    readonly_fields = ['date_inscription', 'derniere_connexion', 'last_login']
    
    # Ordre par défaut
    ordering = ['-date_inscription']


# ============================================================================
# ADMINISTRATION DES ASSOCIATIONS
# ============================================================================

@admin.register(Association)
class AssociationAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour les associations
    """
    list_display = [
        'name', 
        'type', 
        'get_member_count',
        'get_president_name',
        'is_active', 
        'is_archived',
        'created_at'
    ]
    
    list_filter = [
        'type', 
        'is_active', 
        'is_archived',
        'created_at'
    ]
    
    search_fields = [
        'name', 
        'description', 
        'registration_number'
    ]
    
    readonly_fields = [
        'created_at', 
        'updated_at', 
        'archived_at'
    ]
    
    fieldsets = (
        ('Informations de base', {
            'fields': ('name', 'type', 'description')
        }),
        ('Informations légales', {
            'fields': ('registration_number', 'legal_status', 'creation_date'),
            'classes': ('collapse',)
        }),
        ('Paramètres', {
            'fields': ('currency', 'logo')
        }),
        ('Métadonnées', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Statut', {
            'fields': ('is_active', 'is_archived', 'archived_at')
        }),
    )
    
    def get_member_count(self, obj):
        """Affiche le nombre de membres"""
        return obj.get_member_count()
    get_member_count.short_description = 'Membres'
    
    def get_president_name(self, obj):
        """Affiche le nom du président"""
        president = obj.get_president()
        if president:
            return president.get_full_name() or president.username
        return "Aucun président"
    get_president_name.short_description = 'Président'


# ============================================================================
# ADMINISTRATION DES ADHÉSIONS (Liaison Membre-Association)
# ============================================================================

@admin.register(Adhesion)
class AdhesionAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour les adhésions (membres dans les associations)
    """
    list_display = [
        'get_membre_name',
        'association', 
        'role', 
        'is_active',
        'date'
    ]
    
    list_filter = [
        'role', 
        'is_active', 
        'date',
        'association__type'
    ]
    
    search_fields = [
        'membre__username',
        'membre__email',
        'membre__first_name',
        'membre__last_name',
        'association__name'
    ]
    
    readonly_fields = ['date']
    
    fieldsets = (
        ('Appartenance', {
            'fields': ('association', 'membre', 'role')
        }),
        ('Statut', {
            'fields': ('is_active', 'date')
        }),
    )
    
    # Actions personnalisées
    actions = ['activer_membres', 'desactiver_membres', 'promouvoir_tresorier']
    
    def get_membre_name(self, obj):
        """Affiche le nom complet du membre"""
        return obj.membre.get_full_name() or obj.membre.username
    get_membre_name.short_description = 'Membre'
    
    def activer_membres(self, request, queryset):
        """Active les membres sélectionnés"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} membre(s) activé(s).")
    activer_membres.short_description = "Activer les membres sélectionnés"
    
    def desactiver_membres(self, request, queryset):
        """Désactive les membres sélectionnés"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} membre(s) désactivé(s).")
    desactiver_membres.short_description = "Désactiver les membres sélectionnés"
    
    def promouvoir_tresorier(self, request, queryset):
        """Promouvoir en trésorier"""
        from .models import Role
        updated = queryset.update(role=Role.TRESORIER)
        self.message_user(request, f"{updated} membre(s) promu(s) trésorier.")
    promouvoir_tresorier.short_description = "Promouvoir en trésorier"


# ============================================================================
# ADMINISTRATION DES COTISATIONS ET PAIEMENTS
# ============================================================================

@admin.register(Cotisation)
class CotisationAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour les cotisations
    """
    list_display = [
        'association',
        'type_cotisation',
        'montant',
        'date_echeance',
        'date_paiement'
    ]
    
    list_filter = [
        'type_cotisation',
        'date_echeance',
        'association'
    ]
    
    search_fields = [
        'association__name',
        'type_cotisation'
    ]
    
    date_hierarchy = 'date_echeance'


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour les paiements
    """
    list_display = [
        'reference',
        'membre',
        'cotisation',
        'montant',
        'date_paiement',
        'statut',
        'methode'
    ]
    
    list_filter = [
        'statut',
        'methode',
        'date_paiement'
    ]
    
    search_fields = [
        'reference',
        'membre__username',
        'membre__email'
    ]
    
    readonly_fields = ['reference', 'date_paiement']
    
    date_hierarchy = 'date_paiement'


# ============================================================================
# ADMINISTRATION DES PLANS ET ABONNEMENTS
# ============================================================================

@admin.register(Fonctionnalite)
class FonctionnaliteAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour les fonctionnalités
    """
    list_display = [
        'nom',
        'code',
        'active',
        'date_creation'
    ]
    
    list_filter = ['active', 'date_creation']
    
    search_fields = ['nom', 'code', 'description']
    
    readonly_fields = ['date_creation']


@admin.register(PlanTarifaire)
class PlanTarifaireAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour les plans tarifaires
    """
    list_display = [
        'nom',
        'type_plan',
        'prix_mensuel',
        'limite_membres',
        'actif',
        'date_creation'
    ]
    
    list_filter = [
        'type_plan',
        'actif',
        'date_creation'
    ]
    
    search_fields = ['nom']
    
    readonly_fields = ['date_creation']
    
    #filter_horizontal = ['fonctionnalites']


@admin.register(Abonnement)
class AbonnementAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour les abonnements
    """
    list_display = [
        'association',
        'plan',
        'date_debut',
        'date_fin',
        'statut',
        'auto_renouvellement'
    ]
    
    list_filter = [
        'statut',
        'auto_renouvellement',
        'date_debut',
        'date_fin'
    ]
    
    search_fields = [
        'association__name'
    ]
    
    date_hierarchy = 'date_debut'


# ============================================================================
# ADMINISTRATION DES NOTIFICATIONS
# ============================================================================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour les notifications
    """
    list_display = [
        'membre',
        'type_notification',
        'titre',
        'lu',
        'envoye_sms',
        'envoye_email',
        'date_creation'
    ]
    
    list_filter = [
        'type_notification',
        'lu',
        'envoye_sms',
        'envoye_email',
        'date_creation'
    ]
    
    search_fields = [
        'membre__username',
        'membre__email',
        'titre',
        'message'
    ]
    
    readonly_fields = [
        'date_creation',
        'date_envoi',
        'date_lecture'
    ]
    
    date_hierarchy = 'date_creation'
    
    actions = ['marquer_comme_lu', 'marquer_comme_non_lu']
    
    def marquer_comme_lu(self, request, queryset):
        """Marque les notifications comme lues"""
        from django.utils import timezone
        updated = queryset.update(lu=True, date_lecture=timezone.now())
        self.message_user(request, f"{updated} notification(s) marquée(s) comme lue(s).")
    marquer_comme_lu.short_description = "Marquer comme lu"
    
    def marquer_comme_non_lu(self, request, queryset):
        """Marque les notifications comme non lues"""
        updated = queryset.update(lu=False, date_lecture=None)
        self.message_user(request, f"{updated} notification(s) marquée(s) comme non lue(s).")
    marquer_comme_non_lu.short_description = "Marquer comme non lu"
