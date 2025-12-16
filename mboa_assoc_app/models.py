"""
Modèles de données pour la plateforme de gestion des associations camerounaises.
Gère les membres, cotisations, paiements Mobile Money et abonnements.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MinLengthValidator
from decimal import Decimal
from PIL import Image
import os


# ============================================================================
# ÉNUMÉRATIONS - Choix prédéfinis pour les champs
# ============================================================================

class Role(models.TextChoices):
    """Rôles des membres dans une association"""
    PRESIDENT = 'PRESIDENT', 'Président'
    TRESORIER = 'TRESORIER', 'Trésorier'
    ADMIN = 'ADMIN', 'Administrateur'
    MEMBRE = 'MEMBRE', 'Membre'


class TypePlan(models.TextChoices):
    """Types de plans tarifaires disponibles"""
    PRO = 'PRO', 'Pro'
    ENTREPRISE = 'ENTREPRISE', 'Entreprise'


class MethodePaiement(models.TextChoices):
    """Méthodes de paiement acceptées"""
    CASH = 'CASH', 'Cash'
    MOMO = 'MOMO', 'Mobile Money'  # MTN Mobile Money
    OM = 'OM', 'Orange Money'


class Statut(models.TextChoices):
    """Statut d'un membre par rapport à ses cotisations"""
    A_JOUR = 'A_JOUR', 'À jour'
    EN_RETARD = 'EN_RETARD', 'En retard'
    SUSPENDU = 'SUSPENDU', 'Suspendu'


class PaiementStatut(models.TextChoices):
    """Statut d'un paiement"""
    EN_ATTENTE = 'EN_ATTENTE', 'En attente'
    VALIDE = 'VALIDE', 'Validé'
    ECHOUE = 'ECHOUE', 'Échoué'


class TypeNotification(models.TextChoices):
    """Types de notifications"""
    RAPPEL_COTISATION = 'RAPPEL_COTISATION', 'Rappel de cotisation'
    PAIEMENT_RECU = 'PAIEMENT_RECU', 'Paiement reçu'
    PAIEMENT_ECHOUE = 'PAIEMENT_ECHOUE', 'Paiement échoué'
    NOUVEAU_MEMBRE = 'NOUVEAU_MEMBRE', 'Nouveau membre'
    RETARD_PAIEMENT = 'RETARD_PAIEMENT', 'Retard de paiement'
    INFO_GENERALE = 'INFO_GENERALE', 'Information générale'


# ============================================================================
# MODÈLES PRINCIPAUX
# ============================================================================

#-----------------------------------------------------------------#
#                          MEMBRES (USER)                         #
#-----------------------------------------------------------------#

class Membre(AbstractUser):
    """
    Modèle personnalisé de membre héritant de AbstractUser.
    Représente un membre d'une association avec authentification intégrée.
    Champs hérités: username, password, email, first_name, last_name, is_active, date_joined
    """
    # Utiliser le téléphone comme identifiant unique pour l'authentification
    USERNAME_FIELD = 'telephone'
    REQUIRED_FIELDS = ['username', 'email']  # Champs requis en plus de telephone et password
    
    # Champs personnalisés
    telephone = models.CharField(
        max_length=20, 
        unique=True,
        help_text="Numéro de téléphone pour Mobile Money et notifications SMS"
    )
    photo_profil = models.ImageField(
        upload_to='profils/', 
        blank=True, 
        null=True,
        help_text="Photo de profil du membre"
    )
    adresse = models.TextField(blank=True, help_text="Adresse physique")
    ville = models.CharField(max_length=100, blank=True)
    quartier = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Quartier de résidence"
    )
    date_naissance = models.DateField(null=True, blank=True)
    profession = models.CharField(max_length=100, blank=True)
    
    # Champs OTP
    telephone_verifie = models.BooleanField(
        default=False,
        help_text="Indique si le numéro de téléphone a été vérifié par OTP"
    )
    date_verification_telephone = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="Date de vérification du téléphone"
    )
    
    # Statut du membre
    statut = models.CharField(
        max_length=20,
        choices=Statut.choices,
        default=Statut.A_JOUR,
        help_text="Statut par rapport aux cotisations"
    )
    
    # Préférences de notification
    notification_sms = models.BooleanField(
        default=True,
        help_text="Recevoir les notifications par SMS"
    )
    notification_email = models.BooleanField(
        default=True,
        help_text="Recevoir les notifications par email"
    )
    
    # Métadonnées
    date_inscription = models.DateTimeField(auto_now_add=True)
    derniere_connexion = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Membre'
        verbose_name_plural = 'Membres'
        ordering = ['-date_inscription']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.username})"
    
    def get_associations(self):
        """Retourne toutes les associations du membre"""
        return Association.objects.filter(adhesions__membre=self, adhesions__is_active=True)
    
    def est_a_jour(self):
        """Vérifie si le membre est à jour dans ses cotisations"""
        return self.statut == Statut.A_JOUR


#-----------------------------------------------------------------#
#                          ASSOCIATIONS                           #
#-----------------------------------------------------------------#

class Association(models.Model):
    """
    Modèle représentant une association, tontine ou syndicat.
    """
    TYPE_CHOICES = [
        ('association', 'Association'),
        ('tontine', 'Tontine'),
        ('syndicat', 'Syndicat'),
    ]
    
    # Informations de base
    name = models.CharField(
        max_length=200, 
        validators=[MinLengthValidator(3)],
        verbose_name="Nom de l'association"
    )
    type = models.CharField(
        max_length=20, 
        choices=TYPE_CHOICES,
        default='association',
        verbose_name="Type"
    )
    description = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Description"
    )
    
    # Informations légales
    registration_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
        verbose_name="Numéro d'enregistrement"
    )
    legal_status = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Statut juridique"
    )
    creation_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Date de création officielle"
    )
    
    # Paramètres
    currency = models.CharField(
        max_length=10,
        default='FCFA',
        editable=False,
        verbose_name="Devise"
    )
    logo = models.ImageField(
        upload_to='associations/logos/',
        blank=True,
        null=True,
        verbose_name="Logo"
    )
    
    # Métadonnées
    created_by = models.ForeignKey(
        Membre,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_associations',
        verbose_name="Créé par"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Créé le"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Modifié le"
    )
    
    # Statut
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active"
    )
    is_archived = models.BooleanField(
        default=False,
        verbose_name="Archivée"
    )
    archived_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name="Archivée le"
    )
    
    class Meta:
        verbose_name = "Association"
        verbose_name_plural = "Associations"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_active', 'is_archived']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"
    
    def save(self, *args, **kwargs):
        """
        Surcharge de la méthode save pour redimensionner le logo
        """
        super().save(*args, **kwargs)
        
        # Redimensionner le logo si présent
        if self.logo:
            self._resize_logo()
    
    def _resize_logo(self):
        """
        Redimensionne le logo à 300x300 pixels en conservant les proportions
        """
        img = Image.open(self.logo.path)
        
        # Convertir en RGB si nécessaire (pour les PNG avec transparence)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Définir la taille maximale
        max_size = (300, 300)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Sauvegarder l'image redimensionnée
        img.save(self.logo.path, quality=95, optimize=True)
    
    def get_president(self):
        """
        Retourne le président de l'association
        """
        try:
            return self.adhesions.get(role=Role.PRESIDENT, is_active=True).membre
        except Adhesion.DoesNotExist:
            return None
    
    def get_treasurer(self):
        """
        Retourne le trésorier de l'association
        """
        try:
            return self.adhesions.get(role=Role.TRESORIER, is_active=True).membre
        except Adhesion.DoesNotExist:
            return None
    
    def get_all_members(self):
        """
        Retourne tous les membres actifs
        """
        return self.adhesions.filter(is_active=True).select_related('membre')
    
    def get_member_count(self):
        """
        Retourne le nombre de membres actifs
        """
        return self.adhesions.filter(is_active=True).count()


#-----------------------------------------------------------------#
#                    ADHESIONS (Membres <-> Associations)         #
#-----------------------------------------------------------------#

class Adhesion(models.Model):
    """
    Lie un membre à une association avec son rôle.
    Un membre peut appartenir à plusieurs associations.
    Version étendue avec gestion des rôles président/trésorier.
    """
    membre = models.ForeignKey(
        Membre, 
        on_delete=models.CASCADE, 
        related_name='adhesions',
        verbose_name="Membre"
    )
    association = models.ForeignKey(
        Association, 
        on_delete=models.CASCADE, 
        related_name='adhesions',
        verbose_name="Association"
    )
    date = models.DateField(
        auto_now_add=True,
        verbose_name="Date d'adhésion"
    )
    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.MEMBRE,
        verbose_name="Rôle"
    )
    
    # Statut
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )
    
    class Meta:
        verbose_name = "Adhésion"
        verbose_name_plural = "Adhésions"
        unique_together = ['membre', 'association']
        ordering = ['role', 'date']
        indexes = [
            models.Index(fields=['association', 'role']),
            models.Index(fields=['membre', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.membre.get_full_name() or self.membre.username} - {self.get_role_display()} ({self.association.name})"
    
    def is_president(self):
        """Vérifie si le membre est président"""
        return self.role == Role.PRESIDENT and self.is_active
    
    def is_treasurer(self):
        """Vérifie si le membre est trésorier"""
        return self.role == Role.TRESORIER and self.is_active
    
    def can_manage_members(self):
        """Vérifie si le membre peut gérer d'autres membres"""
        return self.role in [Role.PRESIDENT, Role.TRESORIER] and self.is_active


# models.py - Ajouter après le modèle Adhesion
#-----------------------------------------------------------------#
#                          ABONNEMENTS                            #
#-----------------------------------------------------------------#

class Fonctionnalite(models.Model):
    """
    Représente une fonctionnalité disponible sur la plateforme.
    Les fonctionnalités sont liées aux plans tarifaires.
    """
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Code unique de la fonctionnalité (ex: MOBILE_MONEY, SMS_NOTIFICATIONS)"
    )
    nom = models.CharField(max_length=100, help_text="Nom de la fonctionnalité")
    description = models.TextField(help_text="Description détaillée de la fonctionnalité")
    icone = models.CharField(
        max_length=50,
        blank=True,
        help_text="Classe CSS de l'icône (ex: fa-mobile, fa-bell)"
    )
    active = models.BooleanField(
        default=True,
        help_text="Fonctionnalité active sur la plateforme"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Fonctionnalité'
        verbose_name_plural = 'Fonctionnalités'
        ordering = ['nom']
    
    def __str__(self):
        return self.nom

class Invitation(models.Model):
    """
    Gère les invitations à rejoindre une association.
    """
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Code unique d'invitation"
    )
    association = models.ForeignKey(
        Association,
        on_delete=models.CASCADE,
        related_name='invitations'
    )
    telephone_invite = models.CharField(
        max_length=20,
        help_text="Numéro de téléphone invité"
    )
    createur = models.ForeignKey(
        Membre,
        on_delete=models.CASCADE,
        related_name='invitations_envoyees'
    )
    
    # Statuts possibles
    class StatutInvitation(models.TextChoices):
        EN_ATTENTE = 'EN_ATTENTE', 'En attente'
        ACCEPTEE = 'ACCEPTEE', 'Acceptée'
        REFUSEE = 'REFUSEE', 'Refusée'
        EXPIREE = 'EXPIREE', 'Expirée'
    
    statut = models.CharField(
        max_length=20,
        choices=StatutInvitation.choices,
        default=StatutInvitation.EN_ATTENTE
    )
    
    date_creation = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateTimeField(
        help_text="Date d'expiration de l'invitation (7 jours)"
    )
    date_reponse = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Invitation'
        verbose_name_plural = 'Invitations'
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['telephone_invite', 'statut']),
        ]
    
    def __str__(self):
        return f"Invitation {self.code} pour {self.telephone_invite}"
    
    def est_valide(self):
        """Vérifie si l'invitation est encore valide"""
        from django.utils import timezone
        return (
            self.statut == self.StatutInvitation.EN_ATTENTE and 
            timezone.now() < self.date_expiration
        )

class PlanTarifaire(models.Model):
    """
    Définit les plans tarifaires (Pro, Entreprise) avec leurs limites et fonctionnalités.
    Un abonnement peut avoir plusieurs plans dans son historique.
    """
    nom = models.CharField(max_length=100)
    type_plan = models.CharField(
        max_length=20,
        choices=TypePlan.choices,
        help_text="Type de plan tarifaire"
    )
    prix_mensuel = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    limite_membres = models.IntegerField()
    
    # Relation Many-to-Many avec Fonctionnalite
    fonctionnalites = models.ManyToManyField(
        Fonctionnalite,
        through='PlanFonctionnalite',
        related_name='plans',
        help_text="Fonctionnalités incluses dans ce plan"
    )
    
    actif = models.BooleanField(
        default=True,
        help_text="Plan disponible à la souscription"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Plan Tarifaire'
        verbose_name_plural = 'Plans Tarifaires'
        ordering = ['prix_mensuel']
    
    def __str__(self):
        return f"{self.nom} - {self.prix_mensuel} FCFA/mois"
    
    def get_fonctionnalites_actives(self):
        """Retourne les fonctionnalités actives du plan"""
        return self.fonctionnalites.filter(active=True)


class PlanFonctionnalite(models.Model):
    """
    Table d'association entre PlanTarifaire et Fonctionnalite.
    Permet de définir des paramètres spécifiques pour chaque fonctionnalité dans un plan.
    """
    plan = models.ForeignKey(
        PlanTarifaire,
        on_delete=models.CASCADE,
        related_name='plan_fonctionnalites'
    )
    fonctionnalite = models.ForeignKey(
        Fonctionnalite,
        on_delete=models.CASCADE,
        related_name='plan_fonctionnalites'
    )
    
    limite_utilisation = models.IntegerField(
        null=True,
        blank=True,
        help_text="Limite d'utilisation (ex: 100 SMS/mois, null = illimité)"
    )
    parametres = models.JSONField(
        default=dict,
        blank=True,
        help_text="Paramètres additionnels spécifiques (JSON)"
    )
    
    date_ajout = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Plan-Fonctionnalité'
        verbose_name_plural = 'Plans-Fonctionnalités'
        unique_together = ['plan', 'fonctionnalite']
        ordering = ['plan', 'fonctionnalite']
    
    def __str__(self):
        return f"{self.plan.nom} - {self.fonctionnalite.nom}"


class Abonnement(models.Model):
    """
    Gère l'abonnement d'une association à la plateforme.
    Relation 1-1 avec Association.
    """
    association = models.OneToOneField(
        Association, 
        on_delete=models.CASCADE, 
        related_name='abonnement'
    )
    plan = models.ForeignKey(
        PlanTarifaire,
        on_delete=models.PROTECT,
        related_name='abonnements',
        help_text="Plan tarifaire souscrit"
    )
    date_debut = models.DateField()
    date_fin = models.DateField()
    statut = models.CharField(
        max_length=20, 
        choices=[('ACTIF', 'Actif'), ('EXPIRE', 'Expiré'), ('SUSPENDU', 'Suspendu')]
    )
    auto_renouvellement = models.BooleanField(
        default=False,
        help_text="Renouvellement automatique de l'abonnement"
    )
    
    class Meta:
        verbose_name = 'Abonnement'
        verbose_name_plural = 'Abonnements'
    
    def __str__(self):
        return f"Abonnement {self.association.name} - {self.plan.nom}"
    
    def get_fonctionnalites(self):
        """Retourne les fonctionnalités disponibles pour cet abonnement"""
        return self.plan.get_fonctionnalites_actives()
    
    def a_acces_fonctionnalite(self, code_fonctionnalite):
        """Vérifie si l'abonnement a accès à une fonctionnalité"""
        return self.plan.fonctionnalites.filter(
            code=code_fonctionnalite,
            active=True
        ).exists()


#-----------------------------------------------------------------#
#                     COTISATIONS & PAIEMENTS                     #
#-----------------------------------------------------------------#

class Cotisation(models.Model):
    """
    Définit une cotisation pour une association.
    Peut être mensuelle, annuelle ou pour un événement spécifique.
    """
    association = models.ForeignKey(
        Association, 
        on_delete=models.CASCADE, 
        related_name='cotisations'
    )
    montant = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    date_echeance = models.DateField()
    date_paiement = models.DateField(null=True, blank=True)
    type_cotisation = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.type_cotisation} - {self.montant} FCFA"


class MethodePaiementModel(models.Model):
    """
    Modèle pour stocker la méthode de paiement utilisée.
    Supporte Cash, MTN Mobile Money et Orange Money.
    """
    libelle = models.CharField(max_length=20, choices=MethodePaiement.choices)
    
    def __str__(self):
        return self.get_libelle_display()


class PaiementStatutModel(models.Model):
    """
    Modèle pour stocker le statut d'un paiement.
    Permet de suivre l'évolution du paiement (En attente, Validé, Échoué).
    """
    statut = models.CharField(max_length=20, choices=PaiementStatut.choices)
    
    def __str__(self):
        return self.get_statut_display()


class Paiement(models.Model):
    """
    Enregistre un paiement effectué par un membre pour une cotisation.
    Gère les paiements Mobile Money avec référence unique.
    """
    cotisation = models.ForeignKey(
        Cotisation, 
        on_delete=models.CASCADE, 
        related_name='paiements'
    )
    membre = models.ForeignKey(
        Membre, 
        on_delete=models.CASCADE, 
        related_name='paiements'
    )
    montant = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    date_paiement = models.DateField(auto_now_add=True)
    reference = models.CharField(max_length=100, unique=True)
    statut = models.ForeignKey(
        PaiementStatutModel, 
        on_delete=models.PROTECT, 
        related_name='paiements'
    )
    methode = models.ForeignKey(
        MethodePaiementModel, 
        on_delete=models.PROTECT, 
        related_name='paiements'
    )
    
    def __str__(self):
        return f"Paiement {self.reference} - {self.montant} FCFA"


class Commission(models.Model):
    """
    Calcule et enregistre la commission prélevée sur chaque paiement.
    Relation 1-1 avec Paiement.
    """
    paiement = models.OneToOneField(
        Paiement, 
        on_delete=models.CASCADE, 
        related_name='commission'
    )
    montant = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    taux = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    date_commission = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"Commission {self.montant} FCFA ({self.taux}%)"


#-----------------------------------------------------------------#
#                         NOTIFICATIONS                           #
#-----------------------------------------------------------------#

class Notification(models.Model):
    """
    Gère les notifications envoyées aux membres.
    Supporte les notifications SMS, Email et in-app.
    """
    membre = models.ForeignKey(
        Membre,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text="Destinataire de la notification"
    )
    type_notification = models.CharField(
        max_length=30,
        choices=TypeNotification.choices,
        help_text="Type de notification"
    )
    titre = models.CharField(max_length=200, help_text="Titre de la notification")
    message = models.TextField(help_text="Contenu du message")
    
    # Canaux d'envoi
    envoye_sms = models.BooleanField(default=False)
    envoye_email = models.BooleanField(default=False)
    
    # Statut
    lu = models.BooleanField(default=False, help_text="Notification lue par le membre")
    date_lecture = models.DateTimeField(null=True, blank=True)
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True)
    date_envoi = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['membre', '-date_creation']),
            models.Index(fields=['lu', 'membre']),
        ]
    
    def __str__(self):
        return f"{self.get_type_notification_display()} - {self.membre.username}"


# ============================================================================
# MODÈLES OTP - Authentification par code SMS
# ============================================================================

class OTPCode(models.Model):
    """
    Stocke les codes OTP générés pour l'authentification par SMS.
    Un code OTP est valide pendant 10 minutes et limité à 3 tentatives.
    """
    telephone = models.CharField(
        max_length=20,
        help_text="Numéro de téléphone au format +237XXXXXXXXX"
    )
    code = models.CharField(
        max_length=6,
        help_text="Code OTP à 6 chiffres"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date et heure de création du code"
    )
    expires_at = models.DateTimeField(
        help_text="Date et heure d'expiration du code (10 minutes après création)"
    )
    is_validated = models.BooleanField(
        default=False,
        help_text="Indique si le code a été validé avec succès"
    )
    is_expired = models.BooleanField(
        default=False,
        help_text="Indique si le code a expiré ou été invalidé"
    )
    attempts = models.IntegerField(
        default=0,
        help_text="Nombre de tentatives de validation"
    )
    date_envoi = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date et heure d'envoi du SMS"
    )
    
    class Meta:
        verbose_name = 'Code OTP'
        verbose_name_plural = 'Codes OTP'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['telephone', '-created_at']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"OTP {self.code} pour {self.telephone}"


class OTPAttempt(models.Model):
    """
    Enregistre l'historique des tentatives de validation OTP.
    Permet de tracer les tentatives réussies et échouées pour la sécurité.
    """
    otp_code = models.ForeignKey(
        OTPCode,
        on_delete=models.CASCADE,
        related_name='tentatives',
        help_text="Code OTP concerné"
    )
    attempted_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date et heure de la tentative"
    )
    success = models.BooleanField(
        help_text="Indique si la tentative a réussi"
    )
    ip_address = models.GenericIPAddressField(
        help_text="Adresse IP de l'utilisateur"
    )
    
    class Meta:
        verbose_name = 'Tentative OTP'
        verbose_name_plural = 'Tentatives OTP'
        ordering = ['-attempted_at']
        indexes = [
            models.Index(fields=['otp_code', '-attempted_at']),
        ]
    
    def __str__(self):
        status = "Réussie" if self.success else "Échouée"
        return f"Tentative {status} - {self.otp_code.telephone} à {self.attempted_at}"


class PhoneBlock(models.Model):
    """
    Gère les blocages temporaires de numéros de téléphone.
    Un numéro est bloqué après 5 échecs de validation OTP pour 1 heure.
    """
    telephone = models.CharField(
        max_length=20,
        unique=True,
        help_text="Numéro de téléphone bloqué"
    )
    blocked_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Date et heure du blocage"
    )
    blocked_until = models.DateTimeField(
        help_text="Date et heure de fin du blocage"
    )
    total_failures = models.IntegerField(
        default=0,
        help_text="Nombre total d'échecs ayant conduit au blocage"
    )
    reason = models.CharField(
        max_length=100,
        help_text="Raison du blocage"
    )
    
    class Meta:
        verbose_name = 'Blocage de téléphone'
        verbose_name_plural = 'Blocages de téléphone'
        ordering = ['-blocked_at']
        indexes = [
            models.Index(fields=['telephone']),
            models.Index(fields=['blocked_until']),
        ]
    
    def __str__(self):
        return f"Blocage {self.telephone} jusqu'à {self.blocked_until}"
  
        return f"{self.get_type_notification_display()} - {self.membre.username}"
