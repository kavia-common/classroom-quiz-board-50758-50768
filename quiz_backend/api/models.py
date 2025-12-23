from django.db import models
from django.utils import timezone


class Quiz(models.Model):
    """Represents a quiz which contains ordered questions."""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.title


class Question(models.Model):
    """A single question belonging to a quiz"""
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0)
    text = models.TextField()
    answer = models.TextField(blank=True, default='')
    reveal_answer = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']
        unique_together = ('quiz', 'order')

    def __str__(self) -> str:
        return f"{self.quiz.title} - Q{self.order}"


class QuizSession(models.Model):
    """An instance of running a quiz, holds current state and timers."""
    quiz = models.ForeignKey(Quiz, related_name='sessions', on_delete=models.CASCADE)
    current_question_index = models.IntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=False)

    # Timer fields (backend-driven)
    # When timer is running: timer_running=True and timer_started_at is set.
    timer_running = models.BooleanField(default=False)
    timer_total_seconds = models.IntegerField(default=0)  # configured total length for question/quiz
    timer_remaining_seconds = models.IntegerField(default=0)  # snapshot when paused or last calc
    timer_started_at = models.DateTimeField(null=True, blank=True)

    # Mode distinguishes per-question vs full-quiz timer if needed by UI
    timer_mode = models.CharField(max_length=32, default='question')  # 'question' or 'quiz'

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def recalc_remaining(self) -> int:
        """Recalculate remaining seconds based on timer_started_at and running flag."""
        if not self.timer_running or not self.timer_started_at:
            return max(0, self.timer_remaining_seconds)
        elapsed = int((timezone.now() - self.timer_started_at).total_seconds())
        remaining = max(0, self.timer_total_seconds - elapsed)
        return remaining

    def set_timer(self, total_seconds: int, mode: str = 'question'):
        """Configure timer total and reset remaining to total."""
        self.timer_total_seconds = max(0, int(total_seconds))
        self.timer_remaining_seconds = self.timer_total_seconds
        self.timer_mode = mode
        self.timer_running = False
        self.timer_started_at = None

    def start_timer(self):
        """Start or resume timer based on remaining snapshot."""
        now = timezone.now()
        # If currently paused with remaining snapshot, convert to running with fresh started_at
        self.timer_running = True
        self.timer_started_at = now
        # If starting fresh (remaining 0) but total set, reset remaining to total
        if self.timer_remaining_seconds <= 0 and self.timer_total_seconds > 0:
            self.timer_remaining_seconds = self.timer_total_seconds

    def pause_timer(self):
        """Pause timer and persist remaining snapshot."""
        remaining = self.recalc_remaining()
        self.timer_remaining_seconds = remaining
        self.timer_running = False
        self.timer_started_at = None

    def reset_timer(self):
        """Reset timer to total and stop."""
        self.timer_running = False
        self.timer_remaining_seconds = self.timer_total_seconds
        self.timer_started_at = None

    def get_current_question(self):
        qs = self.quiz.questions.all()
        if 0 <= self.current_question_index < qs.count():
            return qs[self.current_question_index]
        return None


class Team(models.Model):
    """Teams in a given session (Team A/B)"""
    session = models.ForeignKey(QuizSession, related_name='teams', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    score = models.IntegerField(default=0)

    class Meta:
        unique_together = ('session', 'name')

    def __str__(self) -> str:
        return f"{self.session.id}:{self.name}({self.score})"


class ScoreEvent(models.Model):
    """Audit trail of scoring operations."""
    session = models.ForeignKey(QuizSession, related_name='score_events', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='events', on_delete=models.CASCADE)
    delta = models.IntegerField()
    reason = models.CharField(max_length=255, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        sign = '+' if self.delta >= 0 else ''
        return f"{self.team.name} {sign}{self.delta} @ {self.created_at.isoformat()}"
