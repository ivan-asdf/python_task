from celery import shared_task


@shared_task
def add(x, y):
    print("TASK:", x, y)
    return x + y
