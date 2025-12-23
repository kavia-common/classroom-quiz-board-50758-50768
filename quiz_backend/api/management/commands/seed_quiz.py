from django.core.management.base import BaseCommand
from api.models import Quiz, Question


class Command(BaseCommand):
    help = "Seed a sample quiz with questions"

    def handle(self, *args, **options):
        quiz, _ = Quiz.objects.get_or_create(title="Sample Quiz", defaults={"description": "Demo quiz"})
        if quiz.questions.exists():
            self.stdout.write(self.style.WARNING("Sample quiz already has questions."))
            return
        data = [
            ("What is 2 + 2?", "4"),
            ("Capital of France?", "Paris"),
            ("Primary color that mixed with blue makes green?", "Yellow"),
        ]
        for idx, (q, a) in enumerate(data):
            Question.objects.create(quiz=quiz, order=idx, text=q, answer=a)
        self.stdout.write(self.style.SUCCESS(f"Seeded quiz '{quiz.title}' with {len(data)} questions."))
