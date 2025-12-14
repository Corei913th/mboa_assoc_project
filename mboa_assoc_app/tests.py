"""
Tests pour l'application mboa_assoc_app
"""
from django.test import TestCase, override_settings
from unittest.mock import patch, MagicMock
from mboa_assoc_app.services.twilio_service import TwilioService
from twilio.base.exceptions import TwilioRestException


class TwilioServiceTestCase(TestCase):
    """Tests pour le service Twilio"""
    
    def setUp(self):
        """Configuration initiale pour chaque test"""
        self.service = TwilioService()
    
    @override_settings(DEBUG=True)
    def test_send_sms_debug_mode(self):
        """Test: En mode développement, le SMS est affiché dans les logs"""
        service = TwilioService()
        telephone = "+237683793777"
        message = "Votre code OTP est: 123456"
        
        # En mode debug, l'envoi doit réussir sans appeler Twilio
        result = service.send_sms(telephone, message)
        self.assertTrue(result)
    
    @override_settings(
        DEBUG=False,
        TWILIO_ACCOUNT_SID='test_sid',
        TWILIO_AUTH_TOKEN='test_token',
        TWILIO_PHONE_NUMBER='+237600000000'
    )
    @patch('mboa_assoc_app.services.twilio_service.Client')
    def test_send_sms_success(self, mock_client_class):
        """Test: Envoi SMS réussi via Twilio"""
        # Mock du client Twilio
        mock_client = MagicMock()
        mock_message = MagicMock()
        mock_message.sid = 'SM123456'
        mock_client.messages.create.return_value = mock_message
        mock_client_class.return_value = mock_client
        
        service = TwilioService()
        telephone = "+237683793777"
        message = "Votre code OTP est: 123456"
        
        result = service.send_sms(telephone, message)
        
        self.assertTrue(result)
        mock_client.messages.create.assert_called_once_with(
            body=message,
            from_='+237600000000',
            to=telephone
        )
    
    @override_settings(
        DEBUG=False,
        TWILIO_ACCOUNT_SID='test_sid',
        TWILIO_AUTH_TOKEN='test_token',
        TWILIO_PHONE_NUMBER='+237600000000'
    )
    @patch('mboa_assoc_app.services.twilio_service.Client')
    def test_send_sms_twilio_error(self, mock_client_class):
        """Test: Gestion d'erreur Twilio lors de l'envoi"""
        # Mock du client Twilio qui lève une exception
        mock_client = MagicMock()
        mock_client.messages.create.side_effect = TwilioRestException(
            status=400,
            uri='/Messages',
            msg='Invalid phone number',
            code=21211
        )
        mock_client_class.return_value = mock_client
        
        service = TwilioService()
        telephone = "+237683793777"
        message = "Votre code OTP est: 123456"
        
        result = service.send_sms(telephone, message)
        
        self.assertFalse(result)
    
    @override_settings(
        DEBUG=False,
        TWILIO_ACCOUNT_SID=None,
        TWILIO_AUTH_TOKEN=None,
        TWILIO_PHONE_NUMBER=None
    )
    def test_send_sms_missing_credentials(self):
        """Test: Échec si les identifiants Twilio ne sont pas configurés"""
        service = TwilioService()
        telephone = "+237683793777"
        message = "Votre code OTP est: 123456"
        
        result = service.send_sms(telephone, message)
        
        self.assertFalse(result)
    
    @override_settings(
        DEBUG=False,
        TWILIO_ACCOUNT_SID='test_sid',
        TWILIO_AUTH_TOKEN='test_token',
        TWILIO_PHONE_NUMBER='+237600000000'
    )
    def test_get_client(self):
        """Test: Création du client Twilio"""
        with patch('mboa_assoc_app.services.twilio_service.Client') as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value = mock_client
            
            service = TwilioService()
            client = service.get_client()
            
            self.assertIsNotNone(client)
            mock_client_class.assert_called_once_with('test_sid', 'test_token')



class OTPServiceTestCase(TestCase):
    """Tests pour le service OTP"""
    
    def setUp(self):
        """Configuration initiale pour chaque test"""
        from mboa_assoc_app.services.otp_service import OTPService
        from mboa_assoc_app.models import OTPCode
        self.service = OTPService
        self.telephone = "+237683793777"
        # Nettoyer les codes OTP existants
        OTPCode.objects.all().delete()
    
    @override_settings(OTP_EXPIRATION_MINUTES=10)
    def test_generate_otp_creates_6_digit_code(self):
        """Test: Génération d'un code OTP à 6 chiffres (Property 2)"""
        otp = self.service.generate_otp(self.telephone)
        
        self.assertEqual(len(otp.code), 6)
        self.assertTrue(otp.code.isdigit())
    
    @override_settings(OTP_EXPIRATION_MINUTES=10)
    def test_generate_otp_expiration_10_minutes(self):
        """Test: Expiration OTP à 10 minutes (Property 3)"""
        from datetime import timedelta
        from django.utils import timezone
        
        otp = self.service.generate_otp(self.telephone)
        
        # Vérifier que l'expiration est exactement 10 minutes après la création
        expected_expiration = otp.created_at + timedelta(minutes=10)
        
        # Comparer avec une tolérance de 1 seconde pour éviter les problèmes de timing
        time_diff = abs((otp.expires_at - expected_expiration).total_seconds())
        self.assertLess(time_diff, 1)
    
    @override_settings(OTP_EXPIRATION_MINUTES=10, OTP_MAX_ATTEMPTS=3)
    def test_validate_otp_correct_code(self):
        """Test: Validation réussie avec code correct (Property 4)"""
        otp = self.service.generate_otp(self.telephone)
        
        success, message = self.service.validate_otp(self.telephone, otp.code)
        
        self.assertTrue(success)
        self.assertEqual(message, "Code validé avec succès")
        
        # Vérifier que le code est marqué comme validé
        otp.refresh_from_db()
        self.assertTrue(otp.is_validated)
    
    @override_settings(OTP_EXPIRATION_MINUTES=10, OTP_MAX_ATTEMPTS=3)
    def test_validate_otp_incorrect_code(self):
        """Test: Validation échouée avec code incorrect (Property 7)"""
        otp = self.service.generate_otp(self.telephone)
        initial_attempts = otp.attempts
        
        success, message = self.service.validate_otp(self.telephone, "000000")
        
        self.assertFalse(success)
        self.assertIn("Code incorrect", message)
        
        # Vérifier que le compteur de tentatives a été incrémenté
        otp.refresh_from_db()
        self.assertEqual(otp.attempts, initial_attempts + 1)
    
    @override_settings(OTP_EXPIRATION_MINUTES=10, OTP_MAX_ATTEMPTS=3)
    def test_validate_otp_expired_code(self):
        """Test: Validation échouée avec code expiré (Property 5)"""
        from django.utils import timezone
        from datetime import timedelta
        
        otp = self.service.generate_otp(self.telephone)
        
        # Forcer l'expiration en modifiant expires_at
        otp.expires_at = timezone.now() - timedelta(minutes=1)
        otp.save()
        
        success, message = self.service.validate_otp(self.telephone, otp.code)
        
        self.assertFalse(success)
        self.assertIn("expiré", message.lower())
        
        # Vérifier que le code est marqué comme expiré
        otp.refresh_from_db()
        self.assertTrue(otp.is_expired)
    
    @override_settings(OTP_EXPIRATION_MINUTES=10, OTP_MAX_ATTEMPTS=3)
    def test_validate_otp_max_attempts_reached(self):
        """Test: Invalidation après 3 tentatives échouées (Requirement 2.5)"""
        otp = self.service.generate_otp(self.telephone)
        
        # Effectuer 3 tentatives échouées
        for i in range(3):
            success, message = self.service.validate_otp(self.telephone, "000000")
            self.assertFalse(success)
        
        # Vérifier que le code est invalidé
        otp.refresh_from_db()
        self.assertTrue(otp.is_expired)
        self.assertEqual(otp.attempts, 3)
    
    @override_settings(OTP_EXPIRATION_MINUTES=10)
    def test_is_expired_returns_true_for_expired_code(self):
        """Test: is_expired retourne True pour un code expiré"""
        from django.utils import timezone
        from datetime import timedelta
        
        otp = self.service.generate_otp(self.telephone)
        otp.expires_at = timezone.now() - timedelta(minutes=1)
        otp.save()
        
        self.assertTrue(self.service.is_expired(otp))
    
    @override_settings(OTP_EXPIRATION_MINUTES=10)
    def test_is_expired_returns_false_for_valid_code(self):
        """Test: is_expired retourne False pour un code valide"""
        otp = self.service.generate_otp(self.telephone)
        
        self.assertFalse(self.service.is_expired(otp))
    
    def test_invalidate_otp_marks_as_expired(self):
        """Test: invalidate_otp marque le code comme expiré"""
        otp = self.service.generate_otp(self.telephone)
        
        self.service.invalidate_otp(otp)
        
        otp.refresh_from_db()
        self.assertTrue(otp.is_expired)
    
    @override_settings(OTP_EXPIRATION_MINUTES=10, OTP_MAX_ATTEMPTS=3)
    def test_validate_otp_no_active_code(self):
        """Test: Validation échouée si aucun code actif"""
        success, message = self.service.validate_otp(self.telephone, "123456")
        
        self.assertFalse(success)
        self.assertIn("Aucun code OTP actif", message)
    
    @override_settings(OTP_EXPIRATION_MINUTES=10, OTP_MAX_ATTEMPTS=3)
    def test_validate_otp_uses_latest_code(self):
        """Test: Validation utilise le dernier code généré (Property 4)"""
        # Générer deux codes
        otp1 = self.service.generate_otp(self.telephone)
        otp2 = self.service.generate_otp(self.telephone)
        
        # Valider avec le code le plus récent
        success, message = self.service.validate_otp(self.telephone, otp2.code)
        
        self.assertTrue(success)
        
        # Vérifier que c'est bien otp2 qui est validé
        otp2.refresh_from_db()
        self.assertTrue(otp2.is_validated)


class SecurityServiceTestCase(TestCase):
    """Tests pour le service de sécurité"""
    
    def setUp(self):
        """Configuration initiale pour chaque test"""
        from mboa_assoc_app.services.security_service import SecurityService
        from mboa_assoc_app.models import PhoneBlock, OTPAttempt, OTPCode
        self.service = SecurityService
        self.telephone = "+237683793777"
        # Nettoyer les données existantes
        PhoneBlock.objects.all().delete()
        OTPAttempt.objects.all().delete()
        OTPCode.objects.all().delete()
    
    def test_check_phone_blocked_returns_false_when_not_blocked(self):
        """Test: check_phone_blocked retourne False si le téléphone n'est pas bloqué (Requirement 3.3)"""
        result = self.service.check_phone_blocked(self.telephone)
        self.assertFalse(result)
    
    @override_settings(PHONE_BLOCK_DURATION_HOURS=1)
    def test_check_phone_blocked_returns_true_when_blocked(self):
        """Test: check_phone_blocked retourne True si le téléphone est bloqué (Requirement 3.3)"""
        from django.utils import timezone
        from datetime import timedelta
        from mboa_assoc_app.models import PhoneBlock
        
        # Créer un blocage actif
        PhoneBlock.objects.create(
            telephone=self.telephone,
            blocked_until=timezone.now() + timedelta(hours=1),
            total_failures=5,
            reason="Test"
        )
        
        result = self.service.check_phone_blocked(self.telephone)
        self.assertTrue(result)
    
    @override_settings(PHONE_BLOCK_DURATION_HOURS=1)
    def test_check_phone_blocked_removes_expired_block(self):
        """Test: check_phone_blocked supprime les blocages expirés (Requirement 3.4)"""
        from django.utils import timezone
        from datetime import timedelta
        from mboa_assoc_app.models import PhoneBlock
        
        # Créer un blocage expiré
        PhoneBlock.objects.create(
            telephone=self.telephone,
            blocked_until=timezone.now() - timedelta(hours=1),
            total_failures=5,
            reason="Test"
        )
        
        result = self.service.check_phone_blocked(self.telephone)
        self.assertFalse(result)
        
        # Vérifier que le blocage a été supprimé
        self.assertFalse(PhoneBlock.objects.filter(telephone=self.telephone).exists())
    
    @override_settings(PHONE_MAX_FAILURES=5, PHONE_BLOCK_DURATION_HOURS=1)
    def test_increment_failure_blocks_after_max_failures(self):
        """Test: increment_failure bloque après 5 échecs (Requirement 3.2)"""
        from django.utils import timezone
        from mboa_assoc_app.models import OTPCode, OTPAttempt, PhoneBlock
        
        # Créer un code OTP
        otp = OTPCode.objects.create(
            telephone=self.telephone,
            code="123456",
            expires_at=timezone.now() + timezone.timedelta(minutes=10)
        )
        
        # Créer 5 tentatives échouées
        for i in range(5):
            OTPAttempt.objects.create(
                otp_code=otp,
                success=False,
                ip_address="127.0.0.1"
            )
        
        # Incrémenter les échecs (devrait bloquer)
        self.service.increment_failure(self.telephone)
        
        # Vérifier que le téléphone est bloqué
        self.assertTrue(PhoneBlock.objects.filter(telephone=self.telephone).exists())
    
    @override_settings(PHONE_BLOCK_DURATION_HOURS=1)
    def test_block_phone_creates_block(self):
        """Test: block_phone crée un blocage (Requirement 3.2)"""
        from django.utils import timezone
        from mboa_assoc_app.models import PhoneBlock
        
        self.service.block_phone(self.telephone, duration_hours=1)
        
        # Vérifier que le blocage existe
        block = PhoneBlock.objects.filter(telephone=self.telephone).first()
        self.assertIsNotNone(block)
        self.assertEqual(block.telephone, self.telephone)
        
        # Vérifier que blocked_until est dans le futur
        self.assertGreater(block.blocked_until, timezone.now())
    
    def test_unblock_expired_removes_expired_blocks(self):
        """Test: unblock_expired supprime les blocages expirés (Requirement 3.4)"""
        from django.utils import timezone
        from datetime import timedelta
        from mboa_assoc_app.models import PhoneBlock
        
        # Créer un blocage expiré
        PhoneBlock.objects.create(
            telephone=self.telephone,
            blocked_until=timezone.now() - timedelta(hours=1),
            total_failures=5,
            reason="Test"
        )
        
        # Créer un blocage actif
        PhoneBlock.objects.create(
            telephone="+237600000000",
            blocked_until=timezone.now() + timedelta(hours=1),
            total_failures=5,
            reason="Test"
        )
        
        # Débloquer les expirés
        count = self.service.unblock_expired()
        
        # Vérifier qu'un seul blocage a été supprimé
        self.assertEqual(count, 1)
        
        # Vérifier que le blocage expiré a été supprimé
        self.assertFalse(PhoneBlock.objects.filter(telephone=self.telephone).exists())
        
        # Vérifier que le blocage actif existe toujours
        self.assertTrue(PhoneBlock.objects.filter(telephone="+237600000000").exists())
