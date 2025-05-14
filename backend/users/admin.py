# backend/users/admin.py
from django.contrib import admin
from .models import Profile, User # Добавь User, если хочешь кастомизировать и его админку

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'verification_status', 'verification_requested_at')
    list_filter = ('role', 'verification_status')
    search_fields = ('user__username', 'user__email')
    actions = ['approve_selected_trainers', 'reject_selected_trainers']

    def approve_selected_trainers(self, request, queryset):
        for profile in queryset.filter(verification_status=Profile.VerificationStatus.PENDING):
            profile.role = Profile.Role.TRAINER
            profile.verification_status = Profile.VerificationStatus.APPROVED
            profile.save()
            # TODO: Уведомить пользователя
        self.message_user(request, "Выбранные заявки одобрены.")
    approve_selected_trainers.short_description = "Одобрить выбранных как тренеров"

    def reject_selected_trainers(self, request, queryset):
        for profile in queryset.filter(verification_status=Profile.VerificationStatus.PENDING):
            profile.verification_status = Profile.VerificationStatus.REJECTED
            # profile.rejection_reason = "Отклонено через админ-панель" # Пример
            profile.save()
            # TODO: Уведомить пользователя
        self.message_user(request, "Выбранные заявки отклонены.")
    reject_selected_trainers.short_description = "Отклонить выбранные заявки"

admin.site.register(Profile, ProfileAdmin)