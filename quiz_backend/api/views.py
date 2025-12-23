from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Quiz, QuizSession, Team, ScoreEvent
from .serializers import QuizSerializer, QuizSessionSerializer, TeamSerializer

# PUBLIC_INTERFACE
@api_view(['GET'])
def health(request):
    """Health endpoint
    Returns:
      200 with {"message": "Server is up!"}
    """
    return Response({"message": "Server is up!"})


def _ensure_session_teams(session: QuizSession):
    # Ensure Team A and Team B exist for a session
    existing = {t.name: t for t in session.teams.all()}
    changed = False
    if 'Team A' not in existing:
        Team.objects.create(session=session, name='Team A', score=0)
        changed = True
    if 'Team B' not in existing:
        Team.objects.create(session=session, name='Team B', score=0)
        changed = True
    if changed:
        session.refresh_from_db()


# PUBLIC_INTERFACE
@api_view(['GET'])
def quizzes(request):
    """List all quizzes with questions."""
    qs = Quiz.objects.prefetch_related('questions').all()
    return Response(QuizSerializer(qs, many=True).data)


# PUBLIC_INTERFACE
@api_view(['GET'])
def quiz_detail(request, quiz_id: int):
    """Get quiz detail by id, including questions."""
    quiz = get_object_or_404(Quiz.objects.prefetch_related('questions'), pk=quiz_id)
    return Response(QuizSerializer(quiz).data)


def _get_or_create_session(quiz_id: int) -> QuizSession:
    quiz = get_object_or_404(Quiz, pk=quiz_id)
    session, _created = QuizSession.objects.get_or_create(
        quiz=quiz,
        is_active=True,
        defaults={'started_at': timezone.now()}
    )
    _ensure_session_teams(session)
    return session


# PUBLIC_INTERFACE
@api_view(['POST'])
def session_start(request, quiz_id: int):
    """Start or get current active session for a quiz."""
    session = _get_or_create_session(quiz_id)
    session.is_active = True
    if not session.started_at:
        session.started_at = timezone.now()
    session.save()
    return Response(QuizSessionSerializer(session).data, status=status.HTTP_201_CREATED)


# PUBLIC_INTERFACE
@api_view(['GET'])
def session_state(request, quiz_id: int):
    """Get current session state for a quiz (includes current question and timer)."""
    session = _get_or_create_session(quiz_id)
    # update remaining in-memory view
    return Response(QuizSessionSerializer(session).data)


def _move_question(session: QuizSession, delta: int) -> QuizSession:
    total = session.quiz.questions.count()
    if total == 0:
        return session
    new_index = session.current_question_index + delta
    new_index = max(0, min(total - 1, new_index))
    session.current_question_index = new_index
    # Reset reveal for new current question
    q = session.get_current_question()
    if q:
        q.reveal_answer = False
        q.save()
    session.save()
    return session


# PUBLIC_INTERFACE
@api_view(['POST'])
def next_question(request, quiz_id: int):
    """Move to the next question."""
    session = _get_or_create_session(quiz_id)
    _move_question(session, 1)
    return Response(QuizSessionSerializer(session).data)


# PUBLIC_INTERFACE
@api_view(['POST'])
def prev_question(request, quiz_id: int):
    """Move to the previous question."""
    session = _get_or_create_session(quiz_id)
    _move_question(session, -1)
    return Response(QuizSessionSerializer(session).data)


# PUBLIC_INTERFACE
@api_view(['POST'])
def reveal_answer(request, quiz_id: int):
    """Toggle reveal answer for the current question."""
    session = _get_or_create_session(quiz_id)
    q = session.get_current_question()
    if not q:
        return Response({"detail": "No current question."}, status=400)
    reveal = request.data.get('reveal', True)
    q.reveal_answer = bool(reveal)
    q.save()
    return Response({"reveal_answer": q.reveal_answer})


# Timer controls
# PUBLIC_INTERFACE
@api_view(['POST'])
def timer_configure(request, quiz_id: int):
    """Set timer total seconds and mode, and reset it."""
    session = _get_or_create_session(quiz_id)
    total = int(request.data.get('total_seconds', 0))
    mode = request.data.get('mode', 'question')
    session.set_timer(total, mode)
    session.save()
    return Response(QuizSessionSerializer(session).data)


# PUBLIC_INTERFACE
@api_view(['POST'])
def timer_start(request, quiz_id: int):
    """Start or resume timer."""
    session = _get_or_create_session(quiz_id)
    session.start_timer()
    session.save()
    return Response(QuizSessionSerializer(session).data)


# PUBLIC_INTERFACE
@api_view(['POST'])
def timer_pause(request, quiz_id: int):
    """Pause timer and snapshot remaining."""
    session = _get_or_create_session(quiz_id)
    session.pause_timer()
    session.save()
    return Response(QuizSessionSerializer(session).data)


# PUBLIC_INTERFACE
@api_view(['POST'])
def timer_reset(request, quiz_id: int):
    """Reset timer to total and stop."""
    session = _get_or_create_session(quiz_id)
    session.reset_timer()
    session.save()
    return Response(QuizSessionSerializer(session).data)


def _score_delta(session: QuizSession, team_name: str, delta: int, reason: str = '') -> Team:
    _ensure_session_teams(session)
    team = get_object_or_404(Team, session=session, name=team_name)
    with transaction.atomic():
        team.score = team.score + int(delta)
        team.save()
        ScoreEvent.objects.create(session=session, team=team, delta=delta, reason=reason or '')
    return team


# PUBLIC_INTERFACE
@api_view(['POST'])
def score_team_a(request, quiz_id: int):
    """Add/subtract score for Team A.
    Body: { "delta": 1, "reason": "correct" }
    """
    session = _get_or_create_session(quiz_id)
    delta = int(request.data.get('delta', 1))
    reason = request.data.get('reason', '')
    team = _score_delta(session, 'Team A', delta, reason)
    return Response(TeamSerializer(team).data)


# PUBLIC_INTERFACE
@api_view(['POST'])
def score_team_b(request, quiz_id: int):
    """Add/subtract score for Team B.
    Body: { "delta": 1, "reason": "correct" }
    """
    session = _get_or_create_session(quiz_id)
    delta = int(request.data.get('delta', 1))
    reason = request.data.get('reason', '')
    team = _score_delta(session, 'Team B', delta, reason)
    return Response(TeamSerializer(team).data)
