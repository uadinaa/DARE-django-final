# users/management/commands/calculate_trainer_levels.py

import math
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from users.models import Profile # Модель профиля
from posts.models import Post   # Модель постов для подсчета их количества
from interactions.models import Follow, PostLike, Comment # Модели для метрик

class Command(BaseCommand):
    help = 'Calculates and updates trainer level scores based on various metrics.'

    def get_level_from_formula(self, current_value, base_A, factor_B):
        """
        Рассчитывает уровень n по формуле Value = A * (B^(n-1)).
        Если current_value < A (т.е. меньше порога для 1-го уровня), возвращает 0.
        Иначе, n = floor(log_B(current_value / A)) + 1.
        """
        if current_value < base_A:
            return 0
        if base_A <= 0 or factor_B <= 1 or current_value < 0: # Проверка корректности аргументов
            return 0

        # Рассчитываем (n-1)
        # current_value / base_A = factor_B ^ (n-1)
        # log_factor_B (current_value / base_A) = n-1
        try:
            n_minus_1 = math.log(current_value / base_A, factor_B)
            level = math.floor(n_minus_1) + 1
            return max(1, level) # Уровень не может быть меньше 1, если порог A достигнут
        except ValueError: # Например, логарифм от отрицательного числа или нуля
            return 0


    def get_average_engagement_score(self, trainer_user):
        """
        Рассчитывает компонентный балл за среднее вовлечение на пост за все время.
        """
        total_posts = Post.objects.filter(author=trainer_user).count()
        if total_posts == 0:
            return 0

        total_likes = PostLike.objects.filter(post__author=trainer_user).count()
        total_comments = Comment.objects.filter(post__author=trainer_user).count()

        average_engagement = (total_likes + total_comments) / total_posts

        # Простая система баллов на основе среднего вовлечения (можно настроить)
        if average_engagement >= 20:
            return 5 # Максимальный балл/уровень за этот компонент
        elif average_engagement >= 10:
            return 3
        elif average_engagement >= 5:
            return 2
        elif average_engagement >= 1: # Хотя бы какое-то вовлечение
            return 1
        else:
            return 0

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting trainer level calculation...'))

        thirty_days_ago = timezone.now() - timedelta(days=30)

        # Получаем только профили тренеров
        trainer_profiles = Profile.objects.filter(role=Profile.Role.TRAINER).select_related('user')

        for profile in trainer_profiles:
            trainer = profile.user
            self.stdout.write(f"Calculating levels for trainer: {trainer.username} (ID: {trainer.id})")

            component_levels = []

            # 1. Уровень по общему количеству подписчиков
            # S(n) = 100 * 3^(n-1)
            total_subscribers = Follow.objects.filter(followed=trainer).count()
            total_subscriber_level = self.get_level_from_formula(total_subscribers, 100, 3)
            component_levels.append(total_subscriber_level)
            self.stdout.write(f"  Total subscribers: {total_subscribers}, Level component: {total_subscriber_level}")

            # 2. Балл за среднее вовлечение на пост (за все время)
            avg_engagement_score = self.get_average_engagement_score(trainer)
            component_levels.append(avg_engagement_score)
            self.stdout.write(f"  Average engagement score: {avg_engagement_score}")

            # 3. Уровень по приросту подписчиков за последние 30 дней
            # S_30(n) = 10 * (2.5)^(n-1)
            recent_subscribers_gain = Follow.objects.filter(
                followed=trainer, 
                created_at__gte=thirty_days_ago
            ).count()
            recent_subscriber_gain_level = self.get_level_from_formula(recent_subscribers_gain, 10, 2.5)
            component_levels.append(recent_subscriber_gain_level)
            self.stdout.write(f"  Recent subscribers gain: {recent_subscribers_gain}, Level component: {recent_subscriber_gain_level}")

            # 4. Уровень по общему вовлечению за последние 30 дней
            # Используем формулу S(n) = 100 * 3^(n-1)
            recent_likes = PostLike.objects.filter(
                post__author=trainer,
                created_at__gte=thirty_days_ago
            ).count()
            recent_comments = Comment.objects.filter(
                post__author=trainer,
                created_at__gte=thirty_days_ago
            ).count()
            total_recent_engagement = recent_likes + recent_comments
            recent_engagement_level = self.get_level_from_formula(total_recent_engagement, 100, 3)
            component_levels.append(recent_engagement_level)
            self.stdout.write(f"  Recent engagement (likes: {recent_likes}, comments: {recent_comments}): {total_recent_engagement}, Level component: {recent_engagement_level}")

            # Суммируем все компонентные уровни/очки
            final_level_score = sum(component_levels)

            profile.level_score = final_level_score
            profile.levels_last_calculated_at = timezone.now()
            profile.save()

            self.stdout.write(self.style.SUCCESS(f"  Trainer {trainer.username} new level_score: {final_level_score}"))

        self.stdout.write(self.style.SUCCESS('Trainer level calculation finished.'))