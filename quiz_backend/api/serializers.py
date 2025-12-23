from rest_framework import serializers
from .models import Quiz, Question, QuizSession, Team, ScoreEvent


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'order', 'text', 'answer', 'reveal_answer']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'questions']


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name', 'score']


class ScoreEventSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)

    class Meta:
        model = ScoreEvent
        fields = ['id', 'team', 'delta', 'reason', 'created_at']


class QuizSessionSerializer(serializers.ModelSerializer):
    quiz = QuizSerializer(read_only=True)
    teams = TeamSerializer(many=True, read_only=True)
    current_question = serializers.SerializerMethodField()
    timer_remaining = serializers.SerializerMethodField()

    def get_current_question(self, obj: QuizSession):
        q = obj.get_current_question()
        return QuestionSerializer(q).data if q else None

    def get_timer_remaining(self, obj: QuizSession):
        return obj.recalc_remaining()

    class Meta:
        model = QuizSession
        fields = [
            'id', 'quiz', 'current_question_index', 'is_active',
            'timer_mode', 'timer_total_seconds', 'timer_remaining',
            'timer_running', 'started_at', 'teams', 'current_question',
            'created_at', 'updated_at'
        ]
