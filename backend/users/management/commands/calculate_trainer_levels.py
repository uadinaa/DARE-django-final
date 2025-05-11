import math
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import timedelta
from django.db import transaction

from users.models import Profile
from interactions.models import Follow, PostLike, Comment
from posts.models import Post  # Import for actual post count

# === Configuration Constants ===
SUBSCRIBER_BASE_A = 10
SUBSCRIBER_FACTOR_B = 3.0

ENGAGEMENT_BASE_A = 4    # For mapping average engagement to level
ENGAGEMENT_FACTOR_B = 2.0

RECENT_SUB_BASE_A = 4
RECENT_SUB_FACTOR_B = 2.5

RECENT_ENG_BASE_A = 10
RECENT_ENG_FACTOR_B = 3.0

RECENT_DAYS = 30

class Command(BaseCommand):
    help = 'Calculates and updates trainer level scores based on various metrics.'

    def get_subscribers_for_level(self, level_n: int) -> int:
        if level_n < 1:
            return 0
        return int(SUBSCRIBER_BASE_A * (SUBSCRIBER_FACTOR_B ** (level_n - 1)))

    def get_level_from_formula(self, value: float, base_A: float, factor_B: float) -> int:
        if value < base_A or base_A <= 0 or factor_B <= 1:
            return 0
        try:
            n_minus_1 = math.log(value / base_A) / math.log(factor_B)
            return max(1, math.floor(n_minus_1) + 1)
        except (ValueError, ZeroDivisionError):
            return 0

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting trainer level calculation...'))

        now = timezone.now()
        recent_threshold = now - timedelta(days=RECENT_DAYS)

        trainers = Profile.objects.filter(role=Profile.Role.TRAINER).select_related('user')
        total = trainers.count()
        self.stdout.write(f'Found {total} trainers to process.')

        for idx, profile in enumerate(trainers, start=1):
            trainer = profile.user
            self.stdout.write(f'[{idx}/{total}] Processing: {trainer.username} (ID {trainer.id})')

            try:
                # 1) Level from total subscribers
                subs_total = Follow.objects.filter(followed=trainer).count()
                lvl_subs = self.get_level_from_formula(subs_total, SUBSCRIBER_BASE_A, SUBSCRIBER_FACTOR_B)

                # 2) Level from actual average engagement per post (all time)
                total_likes_all = PostLike.objects.filter(post__author=trainer).count()
                total_comments_all = Comment.objects.filter(post__author=trainer).count()
                total_engagement_all = total_likes_all + total_comments_all
                post_count = Post.objects.filter(author=trainer).count()
                avg_engagement = (total_engagement_all / post_count) if post_count > 0 else 0
                lvl_avg_eng = self.get_level_from_formula(avg_engagement, ENGAGEMENT_BASE_A, ENGAGEMENT_FACTOR_B)

                # 3) Level from recent subscriber gain
                subs_recent = Follow.objects.filter(
                    followed=trainer,
                    created_at__gte=recent_threshold
                ).count()
                lvl_recent_subs = self.get_level_from_formula(subs_recent, RECENT_SUB_BASE_A, RECENT_SUB_FACTOR_B)

                # 4) Level from recent total engagement
                likes_recent = PostLike.objects.filter(
                    post__author=trainer,
                    created_at__gte=recent_threshold
                ).count()
                comments_recent = Comment.objects.filter(
                    post__author=trainer,
                    created_at__gte=recent_threshold
                ).count()
                total_eng_recent = likes_recent + comments_recent
                lvl_recent_eng = self.get_level_from_formula(total_eng_recent, RECENT_ENG_BASE_A, RECENT_ENG_FACTOR_B)

                # Sum components for final score
                final_score = lvl_subs + lvl_avg_eng + lvl_recent_subs + lvl_recent_eng

                # Save atomically
                with transaction.atomic():
                    profile.level_score = final_score
                    profile.levels_last_calculated_at = now
                    profile.save(update_fields=['level_score', 'levels_last_calculated_at'])

                self.stdout.write(self.style.SUCCESS(
                    f"  -> subs_total={subs_total}(lvl {lvl_subs}), "
                    f"avg_engagement={avg_engagement:.2f}(lvl {lvl_avg_eng}), "
                    f"subs_recent={subs_recent}(lvl {lvl_recent_subs}), "
                    f"eng_recent={total_eng_recent}(lvl {lvl_recent_eng}) => score={final_score}"
                ))

            except Exception as e:
                raise CommandError(f"Error processing {trainer.username}: {e}")

        self.stdout.write(self.style.SUCCESS('Trainer level calculation finished.'))