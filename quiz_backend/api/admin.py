from django.contrib import admin
from .models import Quiz, Question, QuizSession, Team, ScoreEvent


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at")
    search_fields = ("title",)
    ordering = ("-id",)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "quiz", "order", "text", "reveal_answer")
    list_filter = ("quiz",)
    search_fields = ("text",)
    ordering = ("quiz", "order")


@admin.register(QuizSession)
class QuizSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "quiz", "current_question_index", "is_active", "timer_mode", "timer_running")
    list_filter = ("quiz", "is_active", "timer_mode", "timer_running")
    ordering = ("-id",)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "name", "score")
    list_filter = ("session", "name")
    search_fields = ("name",)


@admin.register(ScoreEvent)
class ScoreEventAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "team", "delta", "reason", "created_at")
    list_filter = ("session", "team")
    search_fields = ("reason",)
    ordering = ("-created_at",)
