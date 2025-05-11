import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction # Для атомарных операций

from users.models import Profile
from posts.models import Post
from interactions.models import Follow, PostLike, Comment

# Константы для генерации данных
NUM_REGULAR_USERS = 50
NUM_POSTS_PER_TRAINER = 10

# Когда я создал данный скрипт
TODAY = timezone.datetime(2025, 5, 11, tzinfo=timezone.get_current_timezone()) # Установим "сегодня" для консистентности примера
# TODAY = timezone.now() # Используйте это для реальной текущей даты

class Command(BaseCommand):
    help = 'Populates the database with test data for trainers, users, posts, and interactions.'

    def _create_users(self):
        self.stdout.write("Creating regular users...")
        users = []
        for i in range(1, NUM_REGULAR_USERS + 1):
            username = f'user{i}'
            email = f'user{i}@example.com'
            if User.objects.filter(username=username).exists():
                user = User.objects.get(username=username)
            else:
                user = User.objects.create_user(username=username, email=email, password='password123')
            users.append(user)
        self.regular_users = users
        self.stdout.write(self.style.SUCCESS(f"Created/retrieved {len(users)} regular users."))

        self.stdout.write("Creating trainer users...")
        # Популярный тренер
        if User.objects.filter(username='popular_trainer').exists():
            self.popular_trainer_user = User.objects.get(username='popular_trainer')
        else:
            self.popular_trainer_user = User.objects.create_user('popular_trainer', 'popular@example.com', 'password123')
        self.popular_trainer_user.profile.role = Profile.Role.TRAINER
        self.popular_trainer_user.profile.bio = "I'm a very popular fitness trainer with lots of advice!"
        self.popular_trainer_user.profile.can_monetize_posts = True # Предположим, он может
        self.popular_trainer_user.profile.save()

        # Средне-популярный тренер
        if User.objects.filter(username='moderate_trainer').exists():
            self.moderate_trainer_user = User.objects.get(username='moderate_trainer')
        else:
            self.moderate_trainer_user = User.objects.create_user('moderate_trainer', 'moderate@example.com', 'password123')
        self.moderate_trainer_user.profile.role = Profile.Role.TRAINER
        self.moderate_trainer_user.profile.bio = "I'm a moderately popular trainer, sharing my journey."
        self.moderate_trainer_user.profile.can_monetize_posts = False # Предположим, он пока не может
        self.moderate_trainer_user.profile.save()
        self.stdout.write(self.style.SUCCESS("Created/retrieved trainer users."))

        self.all_trainers = [self.popular_trainer_user, self.moderate_trainer_user]

    def _create_posts(self):
        self.stdout.write("Creating posts...")
        self.all_posts_map = {trainer.id: [] for trainer in self.all_trainers}

        # Даты для постов: Март и Апрель 2025
        # 5 постов в марте, 5 в апреле для каждого
        days_in_march = [random.randint(1, 31) for _ in range(NUM_POSTS_PER_TRAINER // 2)]
        days_in_april = [random.randint(1, 30) for _ in range(NUM_POSTS_PER_TRAINER - (NUM_POSTS_PER_TRAINER // 2))]

        march_dates = [TODAY.replace(month=3, day=d) for d in days_in_march]
        april_dates = [TODAY.replace(month=4, day=d) for d in days_in_april]
        post_dates = sorted(march_dates + april_dates)


        for trainer in self.all_trainers:
            for i in range(NUM_POSTS_PER_TRAINER):
                content = f"This is post number {i+1} by {trainer.username}. Some great fitness advice here about topic {random.randint(1,100)}."
                # Устанавливаем дату создания поста явно
                # Мы не можем напрямую установить auto_now_add, поэтому создаем и потом обновляем
                post = Post.objects.create(author=trainer, content=content)
                # Устанавливаем кастомную дату created_at (и updated_at для консистентности)
                # Это нужно делать осторожно, обычно auto_now_add/auto_now лучше не трогать
                # но для генерации исторических данных это необходимо.
                custom_date = post_dates[i]
                Post.objects.filter(id=post.id).update(created_at=custom_date, updated_at=custom_date)
                post.refresh_from_db() # Обновить объект из БД
                self.all_posts_map[trainer.id].append(post)
        self.stdout.write(self.style.SUCCESS(f"Created {NUM_POSTS_PER_TRAINER * len(self.all_trainers)} posts."))

    def _create_follows(self):
            self.stdout.write("Creating follows...")
            
            # Скорректируем цели для 50 пользователей, или увеличьте NUM_REGULAR_USERS
            # Популярный тренер
            # Общее кол-во: например, 40. Из них 15 за последние 30 дней.
            num_recent_follows_pt = 15 
            num_older_follows_pt = 25
            
            # Средний тренер
            # Общее кол-во: например, 20. Из них 5 за последние 30 дней.
            num_recent_follows_mpt = 5
            num_older_follows_mpt = 15

            # Подписчики для популярного тренера
            # Позволяем пользователям быть подписанными на обоих тренеров, если выборка это позволит
            followers_pt_sample_size = min(len(self.regular_users), num_recent_follows_pt + num_older_follows_pt)
            followers_pt = random.sample(self.regular_users, followers_pt_sample_size)
            
            for i, user in enumerate(followers_pt):
                days_ago = random.randint(1, 29) if i < num_recent_follows_pt else random.randint(30, 365)
                follow_date = TODAY - timedelta(days=days_ago)
                # Устанавливаем кастомную дату created_at для Follow
                Follow.objects.update_or_create(
                    follower=user, 
                    followed=self.popular_trainer_user, 
                    defaults={'created_at': follow_date}
                )


            # Подписчики для среднего тренера
            followers_mpt_sample_size = min(len(self.regular_users), num_recent_follows_mpt + num_older_follows_mpt)
            followers_mpt = random.sample(self.regular_users, followers_mpt_sample_size)

            for i, user in enumerate(followers_mpt):
                days_ago = random.randint(1, 29) if i < num_recent_follows_mpt else random.randint(30, 365)
                follow_date = TODAY - timedelta(days=days_ago)
                Follow.objects.update_or_create(
                    follower=user, 
                    followed=self.moderate_trainer_user, 
                    defaults={'created_at': follow_date}
                )
            self.stdout.write(self.style.SUCCESS("Created or updated follows."))
            
    def _create_likes_and_comments(self):
            self.stdout.write("Creating likes and comments...")
            for trainer_id, posts in self.all_posts_map.items():
                trainer = User.objects.get(id=trainer_id)
                for post in posts:
                    # Лайки (эта часть кода, похоже, была в порядке)
                    num_likes = random.randint(20, 50) if trainer == self.popular_trainer_user else random.randint(5, 15)
                    likers = random.sample(self.regular_users, min(len(self.regular_users), num_likes))
                    for liker in likers:
                        max_days_offset = (TODAY - post.created_at).days
                        if max_days_offset <= 0: 
                            max_days_offset = 1
                        days_after_post = random.randint(0, max_days_offset -1 if max_days_offset > 0 else 0)
                        like_date = post.created_at + timedelta(days=days_after_post)
                        if (TODAY - like_date).days > 365:
                           like_date = TODAY - timedelta(days=random.randint(30, 365))
                        like_date = max(like_date, post.created_at)
                        PostLike.objects.get_or_create(user=liker, post=post, defaults={'created_at': like_date})

                    # Комментарии
                    num_comments = random.randint(5, 15) if trainer == self.popular_trainer_user else random.randint(1, 5)
                    commenters = random.sample(self.regular_users, min(len(self.regular_users), num_comments))
                    for commenter in commenters:
                        max_days_offset_comment = (TODAY - post.created_at).days
                        if max_days_offset_comment <= 0:
                            max_days_offset_comment = 1
                        days_after_post_comment = random.randint(0, max_days_offset_comment -1 if max_days_offset_comment > 0 else 0)
                        comment_date = post.created_at + timedelta(days=days_after_post_comment)
                        if (TODAY - comment_date).days > 365:
                           comment_date = TODAY - timedelta(days=random.randint(30, 365))
                        comment_date = max(comment_date, post.created_at)

                        Comment.objects.get_or_create(
                            author=commenter, # <--- ИСПРАВЛЕНО ЗДЕСЬ (было user=commenter)
                            post=post,
                            defaults={
                                'content': f"Great comment by {commenter.username} on post {post.id}!",
                                'created_at': comment_date
                            }
                        )
            self.stdout.write(self.style.SUCCESS("Created likes and comments."))

    @transaction.atomic # Выполнять все в одной транзакции
    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Starting data population script... This may take a moment.'))

        # Опционально: Очистка старых данных (будьте ОСТОРОЖНЫ на "prod")
        # Post.objects.all().delete()
        # Follow.objects.all().delete() # и т.д.
        # User.objects.filter(is_superuser=False, is_staff=False).exclude(username__in=['popular_trainer', 'moderate_trainer']).delete()

        self._create_users()
        self._create_posts()
        self._create_follows()
        self._create_likes_and_comments()

        self.stdout.write(self.style.SUCCESS('Successfully populated test data!'))