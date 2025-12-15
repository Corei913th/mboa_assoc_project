"""
Modèles de données pour la plateforme de gestion des associations camerounaises.
Gère les membres, cotisations, paiements Mobile Money et abonnements.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator
from decimal import Decimal


# ============================================================================
# ÉNUMÉRATIONS - Choix prédéfinis pour les champs
# ============================================================================

class Role(models.TextChoices):
    """Rôles des membres dans une association"""
    TRESORIER = 'TRESORIER', 'Trésorier'
    ADMIN = 'ADMIN', 'Administrateur'
    MEMBRE = 'MEMBRE', 'Membre'
    PRESIDENT = 'PRESIDENT', 'Président'


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

class Association(models.Model):
    """
    Représente une association, tontine, coopérative ou syndicat.
    C'est l'entité principale qui regroupe les membres.
    """
    nom = models.CharField(max_length=200)  # Nom de l'association
    description = models.TextField(blank=True)  # Description optionnelle
    logo_url = models.URLField(blank=True)  # URL du logo
    statut_juridique = models.CharField(max_length=100)  # Ex: Association loi 1901, Coopérative, etc.
    date_creation = models.DateField()  # Date de création de l'association
    
    class Meta:
        verbose_name = 'Association'
        verbose_name_plural = 'Associations'
        ordering = ['nom']
    
    def __str__(self):
        return self.nom
    
    def get_fonctionnalites_disponibles(self):
        """Retourne les fonctionnalités disponibles selon l'abonnement"""
        try:
            return self.abonnement.get_fonctionnalites()
        except Abonnement.DoesNotExist:
            return Fonctionnalite.objects.none()
    
    def a_acces_fonctionnalite(self, code_fonctionnalite):
        """Vérifie si l'association a accès à une fonctionnalité"""
        try:
            return self.abonnement.a_acces_fonctionnalite(code_fonctionnalite)
        except Abonnement.DoesNotExist:
            return False


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
        'PlanTarifaire',
        on_delete=models.PROTECT,
        related_name='abonnements',
        help_text="Plan tarifaire souscrit"
    )
    date_debut = models.DateField()  # Date de début de l'abonnement
    date_fin = models.DateField()  # Date de fin de l'abonnement
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
        return f"Abonnement {self.association.nom} - {self.plan.nom}"
    
    def get_fonctionnalites(self):
        """Retourne les fonctionnalités disponibles pour cet abonnement"""
        return self.plan.get_fonctionnalites_actives()
    
    def a_acces_fonctionnalite(self, code_fonctionnalite):
        """Vérifie si l'abonnement a accès à une fonctionnalité"""
        return self.plan.fonctionnalites.filter(
            code=code_fonctionnalite,
            active=True
        ).exists()


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


class PlanTarifaire(models.Model):
    """
    Définit les plans tarifaires (Pro, Entreprise) avec leurs limites et fonctionnalités.
    Un abonnement peut avoir plusieurs plans dans son historique.
    """
    nom = models.CharField(max_length=100)  # Nom du plan (Pro, Entreprise)
    type_plan = models.CharField(
        max_length=20,
        choices=TypePlan.choices,
        help_text="Type de plan tarifaire"
    )
    prix_mensuel = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))]
    )  # Prix en FCFA
    limite_membres = models.IntegerField()  # Nombre maximum de membres autorisés
    
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
    
    # Paramètres optionnels spécifiques au plan
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
        return Association.objects.filter(adhesions__membre=self)
    
    def est_a_jour(self):
        """Vérifie si le membre est à jour dans ses cotisations"""
        return self.statut == Statut.A_JOUR





class Adhesion(models.Model):
    """
    Lie un membre à une association avec son rôle.
    Un membre peut appartenir à plusieurs associations.
    """
    membre = models.ForeignKey(
        Membre, 
        on_delete=models.CASCADE, 
        related_name='adhesions'
    )
    association = models.ForeignKey(
        Association, 
        on_delete=models.CASCADE, 
        related_name='adhesions'
    )
    date = models.DateField()  # Date d'adhésion
    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.MEMBRE
    )  # Rôle dans l'association
    
    class Meta:
        unique_together = ['membre', 'association']  # Un membre ne peut adhérer qu'une fois à une association
    
    def __str__(self):
        return f"{self.membre.nom_complet} - {self.association.nom}"


# models.py - Ajouter après le modèle Adhesion

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
    )  # Montant en FCFA
    date_echeance = models.DateField()  # Date limite de paiement
    date_paiement = models.DateField(null=True, blank=True)  # Date effective du paiement
    type_cotisation = models.CharField(max_length=50)  # Ex: Mensuelle, Annuelle, Événement
    
    def __str__(self):
        return f"{self.type_cotisation} - {self.montant} FCFA"


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
    )  # Montant payé en FCFA
    date_paiement = models.DateField(auto_now_add=True)  # Date du paiement
    reference = models.CharField(max_length=100, unique=True)  # Référence unique du paiement
    statut = models.ForeignKey(
        'PaiementStatutModel', 
        on_delete=models.PROTECT, 
        related_name='paiements'
    )
    methode = models.ForeignKey(
        'MethodePaiementModel', 
        on_delete=models.PROTECT, 
        related_name='paiements'
    )
    
    def __str__(self):
        return f"Paiement {self.reference} - {self.montant} FCFA"


class PaiementStatutModel(models.Model):
    """
    Modèle pour stocker le statut d'un paiement.
    Permet de suivre l'évolution du paiement (En attente, Validé, Échoué).
    """
    statut = models.CharField(max_length=20, choices=PaiementStatut.choices)
    
    def __str__(self):
        return self.get_statut_display()


class MethodePaiementModel(models.Model):
    """
    Modèle pour stocker la méthode de paiement utilisée.
    Supporte Cash, MTN Mobile Money et Orange Money.
    """
    libelle = models.CharField(max_length=20, choices=MethodePaiement.choices)
    
    def __str__(self):
        return self.get_libelle_display()


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
    )  # Montant de la commission en FCFA
    taux = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.00'))]
    )  # Taux de commission en pourcentage
    date_commission = models.DateField(auto_now_add=True)  # Date de calcul de la commission
    
    def __str__(self):
        return f"Commission {self.montant} FCFA ({self.taux}%)"


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
  