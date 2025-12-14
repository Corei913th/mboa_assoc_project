import logging
from typing import Optional

from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

logger = logging.getLogger(__name__)


class SMSServiceError(Exception):
    """Erreur générique liée à l'envoi de SMS."""


class TwilioService:
    """
    Service d'envoi de SMS via Twilio.
    
    - En DEV : simulation contrôlée
    - En PROD : envoi réel obligatoire
    - Aucun faux succès autorisé
    """

    def __init__(self) -> None:
        self.account_sid: Optional[str] = getattr(settings, "TWILIO_ACCOUNT_SID", None)
        self.auth_token: Optional[str] = getattr(settings, "TWILIO_AUTH_TOKEN", None)
        self.phone_number: Optional[str] = getattr(settings, "TWILIO_PHONE_NUMBER", None)

        self.debug: bool = getattr(settings, "DEBUG", False)
        self.send_real_sms: bool = getattr(settings, "TWILIO_SEND_REAL_SMS", False)

        self._client: Optional[Client] = None

    # ---------- Private helpers ----------

    def _is_configured(self) -> bool:
        return all([self.account_sid, self.auth_token, self.phone_number])

    def _get_client(self) -> Client:
        if not self._is_configured():
            raise SMSServiceError(
                "Twilio n'est pas correctement configuré "
                "(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER)"
            )

        if self._client is None:
            self._client = Client(self.account_sid, self.auth_token)

        return self._client

    # ---------- Public API ----------

    def send_sms(self, telephone: str, message: str) -> bool:
        """
        Envoie un SMS.

        En DEV :
            - si TWILIO_SEND_REAL_SMS=False → simulation (log uniquement)

        En PROD :
            - envoi réel obligatoire
            - toute erreur est bloquante
            
        Returns:
            bool: True si l'envoi a réussi (ou simulé), False sinon
        """

        if not telephone.startswith("+"):
            raise ValueError("Le numéro de téléphone doit être au format international (E.164).")

        # ---------- MODE DEV ----------
        if self.debug and not self.send_real_sms:
            logger.info("[DEV][SMS SIMULÉ]")
            logger.info("→ Destinataire : %s", telephone)
            logger.info("→ Message      : %s", message)
            return True  # Retourner True pour indiquer le succès de la simulation

        # ---------- MODE PROD ----------
        try:
            client = self._get_client()

            sms = client.messages.create(
                body=message,
                from_=self.phone_number,
                to=telephone,
            )

            logger.info(
                "SMS envoyé avec succès | To=%s | SID=%s",
                telephone,
                sms.sid,
            )
            return True  # Retourner True pour indiquer le succès

        except TwilioRestException as e:
            logger.error(
                "Erreur Twilio | To=%s | Code=%s | Message=%s",
                telephone,
                e.code,
                e.msg,
            )
            raise SMSServiceError("Échec de l'envoi du SMS via Twilio.") from e

        except Exception as e:
            logger.exception("Erreur inattendue lors de l'envoi du SMS.")
            raise SMSServiceError("Erreur interne lors de l'envoi du SMS.") from e


# Instance unique (simple, contrôlée)
twilio_service = TwilioService()
