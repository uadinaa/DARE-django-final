# users/management/commands/generate_daily_activity.py
import random
from datetime import date
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from users.models import Profile
from posts.models import Post
from interactions.models import Follow, PostLike

NUM_NEW_USERS_DAILY = 50
SUBS_FOR_POPULAR_TRAINER = 40

LIKES_PER_ACTIVE_USER_MIN = 1
LIKES_PER_ACTIVE_USER_MAX = 3

POPULAR_TRAINER_USERNAME = 'popular_trainer'
MODERATE_TRAINER_USERNAME = 'moderate_trainer'

class Command(BaseCommand):
    help = 'Generates daily new users, subscriptions, and likes for specified trainers.'

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting daily activity generation...'))

        today_str = timezone.now().strftime("%Y%m%d")

        try:
            popular_trainer = User.objects.get(username=POPULAR_TRAINER_USERNAME)
            moderate_trainer = User.objects.get(username=MODERATE_TRAINER_USERNAME)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Trainers {POPULAR_TRAINER_USERNAME} or {MODERATE_TRAINER_USERNAME} not found. Skipping activity generation."))
            return

        new_users_created_today = []
        for i in range(NUM_NEW_USERS_DAILY):
            username = f'dailyuser_{today_str}_{i:02d}'
            email = f'dailyuser_{today_str}_{i:02d}@example.com'

            if User.objects.filter(username=username).exists():
                self.stdout.write(f"User {username} already exists, skipping.")
                try:
                    user = User.objects.get(username=username) # Получаем существующего для добавления в список
                    new_users_created_today.append(user)
                except User.DoesNotExist:
                    pass
                continue

            user = User.objects.create_user(username=username, email=email, password='password123')
            new_users_created_today.append(user)

        if not new_users_created_today:
            self.stdout.write(self.style.WARNING("No new users were effectively created or retrieved for today's activity."))
            self.stdout.write(self.style.SUCCESS('Daily activity generation finished (no new users).'))
            return

        self.stdout.write(self.style.SUCCESS(f"Created/retrieved {len(new_users_created_today)} users for today's activity."))

        # Распределяем подписчиков
        random.shuffle(new_users_created_today) # Перемешиваем, чтобы выборка была случайной

        users_for_popular = new_users_created_today[:SUBS_FOR_POPULAR_TRAINER]
        users_for_moderate = new_users_created_today[SUBS_FOR_POPULAR_TRAINER:]

        # Подписки и лайки для популярного тренера
        self._generate_activity_for_trainer(users_for_popular, popular_trainer, "popular")

        # Подписки и лайки для умеренного тренера
        self._generate_activity_for_trainer(users_for_moderate, moderate_trainer, "moderate")

        self.stdout.write(self.style.SUCCESS('Daily activity generation finished successfully!'))

    def _generate_activity_for_trainer(self, users_to_activate, trainer_to_follow, trainer_type_log):
        if not users_to_activate:
            self.stdout.write(f"No users assigned to generate activity for {trainer_type_log} trainer.")
            return

        self.stdout.write(f"Generating activity for {trainer_to_follow.username} from {len(users_to_activate)} users...")
        trainer_posts = list(Post.objects.filter(author=trainer_to_follow)) # Получаем список постов

        if not trainer_posts:
            self.stdout.write(self.style.WARNING(f"Trainer {trainer_to_follow.username} has no posts. Skipping likes for them."))
            # Подписки все равно создаем
            for user in users_to_activate:
                Follow.objects.get_or_create(follower=user, followed=trainer_to_follow)
            self.stdout.write(f"  Created {len(users_to_activate)} follows for {trainer_to_follow.username}.")
            return

        follows_created = 0
        likes_created = 0
        for user in users_to_activate:
            # Подписка
            _, created = Follow.objects.get_or_create(follower=user, followed=trainer_to_follow)
            if created:
                follows_created += 1

            # Лайки
            num_likes_to_give = random.randint(LIKES_PER_ACTIVE_USER_MIN, LIKES_PER_ACTIVE_USER_MAX)
            posts_to_like = random.sample(trainer_posts, min(len(trainer_posts), num_likes_to_give))

            for post in posts_to_like:
                _, created_like = PostLike.objects.get_or_create(user=user, post=post)
                if created_like:
                    likes_created +=1

        self.stdout.write(f"  For {trainer_to_follow.username}: Created {follows_created} new follows, {likes_created} new likes.")