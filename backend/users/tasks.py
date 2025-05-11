from celery import shared_task
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

@shared_task(name="calculate_all_trainer_levels")
def calculate_all_trainer_levels_task():
    """
    Celery задача для запуска calculate_trainer_levels.
    """
    try:
        logger.info("Starting scheduled calculation of trainer levels...")
        # Вызываем management command. Вывод команды пойдет в логи Celery worker'а.
        call_command('calculate_trainer_levels')
        logger.info("Successfully finished calculation of trainer levels.")
    except Exception as e:
        logger.error(f"Error during scheduled calculation of trainer levels: {e}", exc_info=True)
        
@shared_task(name="generate_daily_user_activity")
def generate_daily_activity_task():
    """
    Celery задача для запуска generate_daily_activity.
    """
    try:
        logger.info("Starting scheduled daily activity generation...")
        call_command('generate_daily_activity')
        logger.info("Successfully finished daily activity generation.")
    except Exception as e:
        logger.error(f"Error during scheduled daily activity generation: {e}", exc_info=True)