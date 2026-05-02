import schedule
import time
from core.voice import speak


def set_reminder(task, reminder_time):

    def job():
        speak(f"Reminder: {task}")

    schedule.every().day.at(reminder_time).do(job)


def run_scheduler():

    while True:
        schedule.run_pending()
        time.sleep(1)