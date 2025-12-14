# Admin pour la gestion des associations

from django.contrib import admin
from .models import *


@admin.register(OTPCode)
class OTPCodeAdmin(admin.ModelAdmin):
    list_display = ['telephone', 'code', 'created_at', 'expires_at', 'is_validated', 'is_expired', 'attempts']
    list_filter = ['is_validated', 'is_expired', 'created_at']
    search_fields = ['telephone', 'code']
    readonly_fields = ['created_at', 'date_envoi']
    ordering = ['-created_at']


@admin.register(OTPAttempt)
class OTPAttemptAdmin(admin.ModelAdmin):
    list_display = ['otp_code', 'attempted_at', 'success', 'ip_address']
    list_filter = ['success', 'attempted_at']
    search_fields = ['otp_code__telephone', 'ip_address']
    readonly_fields = ['attempted_at']
    ordering = ['-attempted_at']


@admin.register(PhoneBlock)
class PhoneBlockAdmin(admin.ModelAdmin):
    list_display = ['telephone', 'blocked_at', 'blocked_until', 'total_failures', 'reason']
    list_filter = ['blocked_at', 'blocked_until']
    search_fields = ['telephone']
    readonly_fields = ['blocked_at']
    ordering = ['-blocked_at']
