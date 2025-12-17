# Service d'intégration Mobile Money (MTN, Orange)
"""
Service de simulation de paiements Mobile Money.
Simule les processus MTN Mobile Money et Orange Money pour le MVP.
En production, ce service sera remplacé par les vraies API MTN/Orange.
"""

import uuid
import logging
from decimal import Decimal
from typing import Dict, Tuple
from django.utils import timezone

logger = logging.getLogger(__name__)


class MobileMoneyService:
    """
    Service de simulation de paiements Mobile Money.
    Simule MTN Mobile Money et Orange Money avec des scénarios réalistes.
    """
    
    # Opérateurs supportés
    OPERATEUR_MTN = 'MOMO'
    OPERATEUR_ORANGE = 'OM'
    
    # Statuts de transaction
    STATUT_SUCCES = 'SUCCESS'
    STATUT_ECHEC = 'FAILED'
    STATUT_EN_ATTENTE = 'PENDING'
    STATUT_ANNULE = 'CANCELLED'
    
    @staticmethod
    def generer_reference_transaction(operateur: str) -> str:
        """
        Génère une référence unique de transaction.
        
        Args:
            operateur: Code opérateur (MOMO ou OM)
            
        Returns:
            str: Référence unique (ex: MTN-20231217-ABC123)
        """
        prefix = 'MTN' if operateur == MobileMoneyService.OPERATEUR_MTN else 'OM'
        date_str = timezone.now().strftime('%Y%m%d')
        unique_id = uuid.uuid4().hex[:8].upper()
        
        return f"{prefix}-{date_str}-{unique_id}"
    
    @staticmethod
    def simuler_paiement(
        telephone: str,
        montant: Decimal,
        operateur: str,
        scenario: str = 'succes'
    ) -> Tuple[bool, Dict]:
        """
        Simule un paiement Mobile Money.
        
        Args:
            telephone: Numéro de téléphone du payeur
            montant: Montant à payer
            operateur: MOMO ou OM
            scenario: 'succes', 'echec', 'annule', 'en_attente'
            
        Returns:
            Tuple[bool, Dict]: (succès, détails_transaction)
        """
        reference = MobileMoneyService.generer_reference_transaction(operateur)
        
        # Simulation selon le scénario
        if scenario == 'succes':
            logger.info(
                f"[SIMULATION] Paiement réussi | Ref: {reference} | "
                f"Montant: {montant} FCFA | Opérateur: {operateur}"
            )
            return True, {
                'reference': reference,
                'statut': MobileMoneyService.STATUT_SUCCES,
                'montant': montant,
                'operateur': operateur,
                'telephone': telephone,
                'date_transaction': timezone.now(),
                'message': 'Paiement effectué avec succès',
                'frais': MobileMoneyService._calculer_frais(montant, operateur)
            }
        
        elif scenario == 'echec':
            logger.warning(
                f"[SIMULATION] Paiement échoué | Ref: {reference} | "
                f"Montant: {montant} FCFA | Opérateur: {operateur}"
            )
            return False, {
                'reference': reference,
                'statut': MobileMoneyService.STATUT_ECHEC,
                'montant': montant,
                'operateur': operateur,
                'telephone': telephone,
                'date_transaction': timezone.now(),
                'message': 'Solde insuffisant ou code PIN incorrect',
                'code_erreur': 'INSUFFICIENT_BALANCE'
            }
        
        elif scenario == 'annule':
            logger.info(
                f"[SIMULATION] Paiement annulé | Ref: {reference} | "
                f"Montant: {montant} FCFA | Opérateur: {operateur}"
            )
            return False, {
                'reference': reference,
                'statut': MobileMoneyService.STATUT_ANNULE,
                'montant': montant,
                'operateur': operateur,
                'telephone': telephone,
                'date_transaction': timezone.now(),
                'message': 'Transaction annulée par l\'utilisateur',
                'code_erreur': 'USER_CANCELLED'
            }
        
        else:  # en_attente
            logger.info(
                f"[SIMULATION] Paiement en attente | Ref: {reference} | "
                f"Montant: {montant} FCFA | Opérateur: {operateur}"
            )
            return False, {
                'reference': reference,
                'statut': MobileMoneyService.STATUT_EN_ATTENTE,
                'montant': montant,
                'operateur': operateur,
                'telephone': telephone,
                'date_transaction': timezone.now(),
                'message': 'En attente de confirmation par l\'utilisateur',
                'code_erreur': 'PENDING_CONFIRMATION'
            }
    
    @staticmethod
    def _calculer_frais(montant: Decimal, operateur: str) -> Decimal:
        """
        Calcule les frais de transaction Mobile Money.
        Simulation basée sur les grilles tarifaires réelles MTN/Orange Cameroun.
        
        Args:
            montant: Montant de la transaction
            operateur: MOMO ou OM
            
        Returns:
            Decimal: Frais de transaction
        """
        # Grille simplifiée (à ajuster selon les tarifs réels)
        if montant <= 1000:
            return Decimal('50')
        elif montant <= 5000:
            return Decimal('100')
        elif montant <= 10000:
            return Decimal('200')
        elif montant <= 25000:
            return Decimal('500')
        elif montant <= 50000:
            return Decimal('1000')
        else:
            # 2% pour les montants élevés
            return montant * Decimal('0.02')
    
    @staticmethod
    def verifier_statut_transaction(reference: str) -> Dict:
        """
        Vérifie le statut d'une transaction.
        En simulation, retourne toujours un statut validé.
        
        Args:
            reference: Référence de la transaction
            
        Returns:
            Dict: Détails de la transaction
        """
        logger.info(f"[SIMULATION] Vérification statut transaction: {reference}")
        
        return {
            'reference': reference,
            'statut': MobileMoneyService.STATUT_SUCCES,
            'message': 'Transaction validée',
            'date_verification': timezone.now()
        }
    
    @staticmethod
    def generer_recu(transaction: Dict) -> str:
        """
        Génère un reçu de transaction au format texte.
        
        Args:
            transaction: Détails de la transaction
            
        Returns:
            str: Reçu formaté
        """
        operateur_nom = 'MTN Mobile Money' if transaction['operateur'] == 'MOMO' else 'Orange Money'
        
        recu = f"""
╔══════════════════════════════════════╗
║         REÇU DE PAIEMENT             ║
║         MBOA ASSOC                   ║
╚══════════════════════════════════════╝

Opérateur: {operateur_nom}
Référence: {transaction['reference']}
Date: {transaction['date_transaction'].strftime('%d/%m/%Y %H:%M')}

Montant: {transaction['montant']} FCFA
Frais: {transaction.get('frais', 0)} FCFA
Total: {transaction['montant'] + transaction.get('frais', 0)} FCFA

Téléphone: {transaction['telephone']}
Statut: {transaction['statut']}

Message: {transaction['message']}

╔══════════════════════════════════════╗
║  Merci d'utiliser Mboa Assoc         ║
╚══════════════════════════════════════╝
        """
        
        return recu.strip()
    
    @staticmethod
    def valider_numero_mobile_money(telephone: str, operateur: str) -> Tuple[bool, str]:
        """
        Valide qu'un numéro de téléphone est compatible avec l'opérateur.
        
        Args:
            telephone: Numéro de téléphone
            operateur: MOMO ou OM
            
        Returns:
            Tuple[bool, str]: (valide, message)
        """
        # Retirer le préfixe +237 ou 237
        numero = telephone.replace('+237', '').replace('237', '')
        
        if operateur == MobileMoneyService.OPERATEUR_MTN:
            # MTN: commence par 67, 650-654, 680-683
            prefixes_mtn = ['67', '650', '651', '652', '653', '654', '680', '681', '682', '683']
            if any(numero.startswith(p) for p in prefixes_mtn):
                return True, "Numéro MTN valide"
            return False, "Ce numéro n'est pas un numéro MTN Mobile Money"
        
        elif operateur == MobileMoneyService.OPERATEUR_ORANGE:
            # Orange: commence par 69, 655-659
            prefixes_orange = ['69', '655', '656', '657', '658', '659']
            if any(numero.startswith(p) for p in prefixes_orange):
                return True, "Numéro Orange valide"
            return False, "Ce numéro n'est pas un numéro Orange Money"
        
        return False, "Opérateur non reconnu"


# Instance unique du service
mobile_money_service = MobileMoneyService()
