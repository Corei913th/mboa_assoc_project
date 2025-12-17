"""
Script de seed pour générer des données de test complètes.
Crée un workflow complet avec utilisateurs, associations, cotisations, paiements, invitations, etc.
"""

import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mboa_assoc.settings')
django.setup()

from django.utils import timezone
from mboa_assoc_app.models import (
    Membre, Association, Adhesion, Cotisation, Paiement,
    MethodePaiementModel, PaiementStatutModel, Invitation,
    Notification, Role, PaiementStatut, MethodePaiement,
    TypeNotification, Statut
)


def clear_data():
    """Supprime toutes les données existantes"""
    print("🗑️  Suppression des données existantes...")
    Notification.objects.all().delete()
    Paiement.objects.all().delete()
    Cotisation.objects.all().delete()
    Invitation.objects.all().delete()
    Adhesion.objects.all().delete()
    Association.objects.all().delete()
    Membre.objects.all().delete()
    MethodePaiementModel.objects.all().delete()
    PaiementStatutModel.objects.all().delete()
    print("✅ Données supprimées\n")


def create_payment_methods():
    """Crée les méthodes de paiement"""
    print("💳 Création des méthodes de paiement...")
    methods = []
    for method in MethodePaiement.choices:
        m, created = MethodePaiementModel.objects.get_or_create(libelle=method[0])
        methods.append(m)
        if created:
            print(f"   ✓ {method[1]}")
    return methods


def create_payment_statuses():
    """Crée les statuts de paiement"""
    print("\n📊 Création des statuts de paiement...")
    statuses = []
    for status in PaiementStatut.choices:
        s, created = PaiementStatutModel.objects.get_or_create(statut=status[0])
        statuses.append(s)
        if created:
            print(f"   ✓ {status[1]}")
    return statuses


def create_members():
    """Crée des membres de test"""
    print("\n👥 Création des membres...")
    
    members_data = [
        {
            'username': 'freddy',
            'telephone': '+237683793777',
            'first_name': 'Freddy',
            'last_name': 'Bogning',
            'email': 'freddy@example.com',
            'ville': 'Yaoundé',
            'quartier': 'Bastos',
            'telephone_verifie': True,
            'statut': Statut.A_JOUR
        },
        {
            'username': 'marie',
            'telephone': '+237690123456',
            'first_name': 'Marie',
            'last_name': 'Kamga',
            'email': 'marie@example.com',
            'ville': 'Douala',
            'quartier': 'Akwa',
            'telephone_verifie': True,
            'statut': Statut.A_JOUR
        },
        {
            'username': 'paul',
            'telephone': '+237677654321',
            'first_name': 'Paul',
            'last_name': 'Nkomo',
            'email': 'paul@example.com',
            'ville': 'Yaoundé',
            'quartier': 'Mvan',
            'telephone_verifie': True,
            'statut': Statut.EN_RETARD
        },
        {
            'username': 'sophie',
            'telephone': '+237698765432',
            'first_name': 'Sophie',
            'last_name': 'Mballa',
            'email': 'sophie@example.com',
            'ville': 'Douala',
            'quartier': 'Bonanjo',
            'telephone_verifie': True,
            'statut': Statut.A_JOUR
        },
        {
            'username': 'jean',
            'telephone': '+237655443322',
            'first_name': 'Jean',
            'last_name': 'Fotso',
            'email': 'jean@example.com',
            'ville': 'Bafoussam',
            'quartier': 'Centre',
            'telephone_verifie': False,
            'statut': Statut.A_JOUR
        },
        {
            'username': 'alice',
            'telephone': '+237699887766',
            'first_name': 'Alice',
            'last_name': 'Tchoua',
            'email': 'alice@example.com',
            'ville': 'Yaoundé',
            'quartier': 'Essos',
            'telephone_verifie': True,
            'statut': Statut.A_JOUR
        },
        {
            'username': 'david',
            'telephone': '+237688776655',
            'first_name': 'David',
            'last_name': 'Njoya',
            'email': 'david@example.com',
            'ville': 'Douala',
            'quartier': 'Bali',
            'telephone_verifie': True,
            'statut': Statut.EN_RETARD
        },
        {
            'username': 'claire',
            'telephone': '+237677889900',
            'first_name': 'Claire',
            'last_name': 'Biya',
            'email': 'claire@example.com',
            'ville': 'Yaoundé',
            'quartier': 'Nlongkak',
            'telephone_verifie': True,
            'statut': Statut.A_JOUR
        }
    ]
    
    members = []
    for data in members_data:
        member = Membre.objects.create_user(
            username=data['username'],
            telephone=data['telephone'],
            password='password123',
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            ville=data['ville'],
            quartier=data['quartier'],
            telephone_verifie=data['telephone_verifie'],
            statut=data['statut']
        )
        members.append(member)
        print(f"   ✓ {member.get_full_name()} ({member.telephone})")
    
    return members


def create_associations(members):
    """Crée des associations avec différents types"""
    print("\n🏢 Création des associations...")
    
    associations_data = [
        {
            'name': 'Association des Développeurs Camerounais',
            'type': 'association',
            'description': 'Regroupement des développeurs logiciels du Cameroun pour partager connaissances et opportunités.',
            'created_by': members[0]
        },
        {
            'name': 'Tontine Solidarité Yaoundé',
            'type': 'tontine',
            'description': 'Tontine mensuelle pour l\'entraide financière entre membres.',
            'created_by': members[1]
        },
        {
            'name': 'Syndicat des Commerçants de Douala',
            'type': 'syndicat',
            'description': 'Défense des intérêts des commerçants du marché central de Douala.',
            'created_by': members[3]
        },
        {
            'name': 'Association Sportive Bastos',
            'type': 'association',
            'description': 'Club de football amateur du quartier Bastos.',
            'created_by': members[0]
        },
        {
            'name': 'Tontine Femmes Entrepreneures',
            'type': 'tontine',
            'description': 'Soutien financier et mentorat pour femmes entrepreneures.',
            'created_by': members[5]
        }
    ]
    
    associations = []
    for data in associations_data:
        assoc = Association.objects.create(
            name=data['name'],
            type=data['type'],
            description=data['description'],
            created_by=data['created_by'],
            is_active=True
        )
        associations.append(assoc)
        print(f"   ✓ {assoc.name} ({assoc.get_type_display()})")
    
    return associations


def create_adhesions(members, associations):
    """Crée les adhésions avec différents rôles"""
    print("\n🤝 Création des adhésions...")
    
    adhesions_data = [
        # Association des Développeurs
        {'membre': members[0], 'association': associations[0], 'role': Role.PRESIDENT},
        {'membre': members[1], 'association': associations[0], 'role': Role.TRESORIER},
        {'membre': members[2], 'association': associations[0], 'role': Role.MEMBRE},
        {'membre': members[4], 'association': associations[0], 'role': Role.MEMBRE},
        {'membre': members[6], 'association': associations[0], 'role': Role.MEMBRE},
        
        # Tontine Solidarité
        {'membre': members[1], 'association': associations[1], 'role': Role.PRESIDENT},
        {'membre': members[0], 'association': associations[1], 'role': Role.MEMBRE},
        {'membre': members[2], 'association': associations[1], 'role': Role.TRESORIER},
        {'membre': members[5], 'association': associations[1], 'role': Role.MEMBRE},
        
        # Syndicat Commerçants
        {'membre': members[3], 'association': associations[2], 'role': Role.PRESIDENT},
        {'membre': members[6], 'association': associations[2], 'role': Role.TRESORIER},
        {'membre': members[7], 'association': associations[2], 'role': Role.MEMBRE},
        
        # Association Sportive
        {'membre': members[0], 'association': associations[3], 'role': Role.PRESIDENT},
        {'membre': members[4], 'association': associations[3], 'role': Role.TRESORIER},
        {'membre': members[2], 'association': associations[3], 'role': Role.MEMBRE},
        
        # Tontine Femmes
        {'membre': members[5], 'association': associations[4], 'role': Role.PRESIDENT},
        {'membre': members[1], 'association': associations[4], 'role': Role.TRESORIER},
        {'membre': members[3], 'association': associations[4], 'role': Role.MEMBRE},
        {'membre': members[7], 'association': associations[4], 'role': Role.MEMBRE},
    ]
    
    adhesions = []
    for data in adhesions_data:
        adhesion = Adhesion.objects.create(
            membre=data['membre'],
            association=data['association'],
            role=data['role'],
            is_active=True
        )
        adhesions.append(adhesion)
        print(f"   ✓ {adhesion.membre.get_full_name()} → {adhesion.association.name} ({adhesion.get_role_display()})")
    
    return adhesions


def create_cotisations(associations):
    """Crée des cotisations variées (en attente, payées, en retard)"""
    print("\n💰 Création des cotisations...")
    
    today = timezone.now().date()
    
    cotisations_data = [
        # Association Développeurs - cotisations en attente
        {'association': associations[0], 'type': 'Cotisation mensuelle Janvier', 'montant': 5000, 'echeance': today - timedelta(days=5)},
        {'association': associations[0], 'type': 'Cotisation mensuelle Février', 'montant': 5000, 'echeance': today + timedelta(days=10)},
        {'association': associations[0], 'type': 'Formation Python', 'montant': 15000, 'echeance': today - timedelta(days=2)},
        
        # Tontine Solidarité - cotisations urgentes
        {'association': associations[1], 'type': 'Tontine Décembre', 'montant': 10000, 'echeance': today - timedelta(days=10)},
        {'association': associations[1], 'type': 'Tontine Janvier', 'montant': 10000, 'echeance': today - timedelta(days=3)},
        {'association': associations[1], 'type': 'Tontine Février', 'montant': 10000, 'echeance': today + timedelta(days=15)},
        
        # Syndicat Commerçants
        {'association': associations[2], 'type': 'Cotisation trimestrielle Q1', 'montant': 25000, 'echeance': today - timedelta(days=7)},
        {'association': associations[2], 'type': 'Fonds de solidarité', 'montant': 5000, 'echeance': today + timedelta(days=5)},
        
        # Association Sportive
        {'association': associations[3], 'type': 'Cotisation mensuelle', 'montant': 3000, 'echeance': today - timedelta(days=1)},
        {'association': associations[3], 'type': 'Achat maillots', 'montant': 20000, 'echeance': today + timedelta(days=20)},
        
        # Tontine Femmes
        {'association': associations[4], 'type': 'Tontine mensuelle', 'montant': 15000, 'echeance': today - timedelta(days=4)},
        {'association': associations[4], 'type': 'Fonds entrepreneuriat', 'montant': 50000, 'echeance': today + timedelta(days=30)},
    ]
    
    cotisations = []
    for data in cotisations_data:
        cotisation = Cotisation.objects.create(
            association=data['association'],
            type_cotisation=data['type'],
            montant=Decimal(str(data['montant'])),
            date_echeance=data['echeance']
        )
        cotisations.append(cotisation)
        status = "⚠️ EN RETARD" if data['echeance'] < today else "✓ À venir"
        print(f"   {status} {cotisation.type_cotisation} - {cotisation.montant} FCFA ({cotisation.association.name})")
    
    return cotisations


def create_paiements(cotisations, members, statuses, methods):
    """Crée des paiements (validés, en attente, échoués)"""
    print("\n💳 Création des paiements...")
    
    statut_valide = next(s for s in statuses if s.statut == PaiementStatut.VALIDE)
    statut_attente = next(s for s in statuses if s.statut == PaiementStatut.EN_ATTENTE)
    statut_echoue = next(s for s in statuses if s.statut == PaiementStatut.ECHOUE)
    
    methode_momo = next(m for m in methods if m.libelle == MethodePaiement.MOMO)
    methode_om = next(m for m in methods if m.libelle == MethodePaiement.OM)
    methode_cash = next(m for m in methods if m.libelle == MethodePaiement.CASH)
    
    paiements_data = [
        # Paiements validés
        {'cotisation': cotisations[0], 'membre': members[1], 'statut': statut_valide, 'methode': methode_momo},
        {'cotisation': cotisations[0], 'membre': members[4], 'statut': statut_valide, 'methode': methode_om},
        {'cotisation': cotisations[3], 'membre': members[1], 'statut': statut_valide, 'methode': methode_momo},
        {'cotisation': cotisations[6], 'membre': members[3], 'statut': statut_valide, 'methode': methode_cash},
        
        # Paiements en attente
        {'cotisation': cotisations[1], 'membre': members[2], 'statut': statut_attente, 'methode': methode_momo},
        {'cotisation': cotisations[4], 'membre': members[5], 'statut': statut_attente, 'methode': methode_om},
        
        # Paiements échoués
        {'cotisation': cotisations[2], 'membre': members[6], 'statut': statut_echoue, 'methode': methode_momo},
    ]
    
    paiements = []
    for i, data in enumerate(paiements_data, 1):
        paiement = Paiement.objects.create(
            cotisation=data['cotisation'],
            membre=data['membre'],
            montant=data['cotisation'].montant,
            reference=f"PAY{timezone.now().strftime('%Y%m%d')}{i:04d}",
            statut=data['statut'],
            methode=data['methode']
        )
        paiements.append(paiement)
        icon = "✅" if data['statut'].statut == PaiementStatut.VALIDE else "⏳" if data['statut'].statut == PaiementStatut.EN_ATTENTE else "❌"
        print(f"   {icon} {paiement.reference} - {paiement.montant} FCFA ({paiement.membre.get_full_name()}) - {data['methode'].get_libelle_display()}")
    
    return paiements


def create_invitations(associations, members):
    """Crée des invitations en attente"""
    print("\n📧 Création des invitations...")
    
    invitations_data = [
        {
            'association': associations[0],
            'telephone': '+237699112233',
            'createur': members[0],
            'code': 'INV001DEV',
            'jours_expiration': 5
        },
        {
            'association': associations[0],
            'telephone': '+237688223344',
            'createur': members[0],
            'code': 'INV002DEV',
            'jours_expiration': 3
        },
        {
            'association': associations[1],
            'telephone': '+237677334455',
            'createur': members[1],
            'code': 'INV001TON',
            'jours_expiration': 6
        },
        {
            'association': associations[2],
            'telephone': '+237666445566',
            'createur': members[3],
            'code': 'INV001SYN',
            'jours_expiration': 4
        },
        {
            'association': associations[4],
            'telephone': '+237655556677',
            'createur': members[5],
            'code': 'INV001FEM',
            'jours_expiration': 7
        },
    ]
    
    invitations = []
    for data in invitations_data:
        invitation = Invitation.objects.create(
            association=data['association'],
            telephone_invite=data['telephone'],
            createur=data['createur'],
            code=data['code'],
            statut=Invitation.StatutInvitation.EN_ATTENTE,
            date_expiration=timezone.now() + timedelta(days=data['jours_expiration'])
        )
        invitations.append(invitation)
        print(f"   ✓ {invitation.code} → {invitation.telephone_invite} ({invitation.association.name})")
    
    return invitations


def create_notifications(members, associations):
    """Crée des notifications variées"""
    print("\n🔔 Création des notifications...")
    
    notifications_data = [
        # Rappels de cotisation
        {
            'membre': members[0],
            'type': TypeNotification.RAPPEL_COTISATION,
            'titre': 'Cotisation en retard',
            'message': f'Votre cotisation "Formation Python" pour {associations[0].name} est en retard. Montant: 15000 FCFA',
            'lu': False
        },
        {
            'membre': members[0],
            'type': TypeNotification.RAPPEL_COTISATION,
            'titre': 'Cotisation à venir',
            'message': f'Votre cotisation mensuelle pour {associations[3].name} arrive à échéance dans 3 jours. Montant: 3000 FCFA',
            'lu': False
        },
        {
            'membre': members[1],
            'type': TypeNotification.RAPPEL_COTISATION,
            'titre': 'Tontine en retard',
            'message': f'Votre tontine de Janvier pour {associations[1].name} est en retard. Montant: 10000 FCFA',
            'lu': False
        },
        
        # Paiements reçus
        {
            'membre': members[1],
            'type': TypeNotification.PAIEMENT_RECU,
            'titre': 'Paiement validé',
            'message': 'Votre paiement de 5000 FCFA a été validé avec succès.',
            'lu': True
        },
        {
            'membre': members[3],
            'type': TypeNotification.PAIEMENT_RECU,
            'titre': 'Paiement cash enregistré',
            'message': 'Votre paiement cash de 25000 FCFA a été enregistré.',
            'lu': True
        },
        
        # Nouveaux membres
        {
            'membre': members[0],
            'type': TypeNotification.NOUVEAU_MEMBRE,
            'titre': 'Nouveau membre',
            'message': f'David Njoya a rejoint {associations[0].name}',
            'lu': False
        },
        
        # Infos générales
        {
            'membre': members[0],
            'type': TypeNotification.INFO_GENERALE,
            'titre': 'Réunion mensuelle',
            'message': f'Réunion de {associations[0].name} prévue le 25 du mois à 18h.',
            'lu': False
        },
    ]
    
    notifications = []
    for data in notifications_data:
        notif = Notification.objects.create(
            membre=data['membre'],
            type_notification=data['type'],
            titre=data['titre'],
            message=data['message'],
            lu=data['lu'],
            envoye_sms=True,
            date_envoi=timezone.now()
        )
        if data['lu']:
            notif.date_lecture = timezone.now()
            notif.save()
        notifications.append(notif)
        icon = "📖" if data['lu'] else "🔔"
        print(f"   {icon} {notif.titre} → {notif.membre.get_full_name()}")
    
    return notifications


def print_summary(members, associations, cotisations, paiements, invitations, notifications):
    """Affiche un résumé des données créées"""
    print("\n" + "="*60)
    print("📊 RÉSUMÉ DES DONNÉES CRÉÉES")
    print("="*60)
    print(f"👥 Membres: {len(members)}")
    print(f"🏢 Associations: {len(associations)}")
    print(f"💰 Cotisations: {len(cotisations)}")
    print(f"💳 Paiements: {len(paiements)}")
    print(f"📧 Invitations: {len(invitations)}")
    print(f"🔔 Notifications: {len(notifications)}")
    print("="*60)
    
    print("\n🔑 COMPTES DE TEST:")
    print("-" * 60)
    for member in members[:3]:
        print(f"   Username: {member.username}")
        print(f"   Téléphone: {member.telephone}")
        print(f"   Password: password123")
        print(f"   Associations: {member.adhesions.count()}")
        print()


def main():
    """Fonction principale"""
    print("\n" + "="*60)
    print("🌱 SEED DATA - MBOA ASSOC")
    print("="*60 + "\n")
    
    # Confirmation
    response = input("⚠️  Cela va supprimer toutes les données existantes. Continuer? (oui/non): ")
    if response.lower() not in ['oui', 'o', 'yes', 'y']:
        print("❌ Opération annulée")
        return
    
    # Exécution
    clear_data()
    methods = create_payment_methods()
    statuses = create_payment_statuses()
    members = create_members()
    associations = create_associations(members)
    adhesions = create_adhesions(members, associations)
    cotisations = create_cotisations(associations)
    paiements = create_paiements(cotisations, members, statuses, methods)
    invitations = create_invitations(associations, members)
    notifications = create_notifications(members, associations)
    
    print_summary(members, associations, cotisations, paiements, invitations, notifications)
    
    print("\n✅ SEED TERMINÉ AVEC SUCCÈS!\n")


if __name__ == '__main__':
    main()
