from django.urls import path
from .views import (
    health,
    quizzes,
    quiz_detail,
    session_start,
    session_state,
    next_question,
    prev_question,
    reveal_answer,
    timer_configure,
    timer_start,
    timer_pause,
    timer_reset,
    score_team_a,
    score_team_b,
)

urlpatterns = [
    path('health/', health, name='Health'),

    # Quiz resources
    path('quizzes/', quizzes, name='Quizzes'),
    path('quizzes/<int:quiz_id>/', quiz_detail, name='QuizDetail'),

    # Session control/state
    path('quizzes/<int:quiz_id>/session/start/', session_start, name='SessionStart'),
    path('quizzes/<int:quiz_id>/session/state/', session_state, name='SessionState'),

    # Navigation and reveal
    path('quizzes/<int:quiz_id>/session/next/', next_question, name='NextQuestion'),
    path('quizzes/<int:quiz_id>/session/prev/', prev_question, name='PrevQuestion'),
    path('quizzes/<int:quiz_id>/session/reveal/', reveal_answer, name='RevealAnswer'),

    # Timer controls
    path('quizzes/<int:quiz_id>/session/timer/configure/', timer_configure, name='TimerConfigure'),
    path('quizzes/<int:quiz_id>/session/timer/start/', timer_start, name='TimerStart'),
    path('quizzes/<int:quiz_id>/session/timer/pause/', timer_pause, name='TimerPause'),
    path('quizzes/<int:quiz_id>/session/timer/reset/', timer_reset, name='TimerReset'),

    # Scoring
    path('quizzes/<int:quiz_id>/session/score/teamA/', score_team_a, name='ScoreTeamA'),
    path('quizzes/<int:quiz_id>/session/score/teamB/', score_team_b, name='ScoreTeamB'),
]
