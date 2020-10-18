from django.core.mail import send_mail
from celery.decorators import task
from celery.utils.log import get_task_logger
from worker.worker import app

logger = get_task_logger(__name__)



@task(queue='send_email')
def send_email(email, content):
    """
    sends email to the client
    """
    logger.info("sending email to - " + email)

    return send_mail(
        "Here's your Magic Link!",
        content,
        'sajal.4591@gmail.com',
        [email],
        fail_silently=False
    )
