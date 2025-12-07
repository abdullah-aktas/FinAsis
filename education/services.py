from .models import StudentAnalytics, ExamSubmission, Question
from decimal import Decimal
from typing import Dict, Any, Tuple


class AdaptiveLearningService:
    """
    Öğrencinin zayıf olduğu konulara göre kişiselleştirilmiş öneriler sunar.
    """

    def get_recommendations(self, student):
        # Son analitik kaydını al
        analytics = (
            StudentAnalytics.objects.filter(student=student).order_by("-date").first()
        )
        if not analytics or not analytics.weak_topics:
            return {
                "recommendations": [],
                "message": "Tebrikler! Zayıf konunuz bulunmuyor.",
            }
        # Zayıf konulara göre öneriler üret
        recommendations = []
        for topic in analytics.weak_topics:
            recommendations.append(
                {
                    "topic": topic,
                    "suggestion": f"'{topic}' konusunda ek alıştırmalar çözebilir veya öğretmeninizden yardım isteyebilirsiniz.",
                }
            )
        return {
            "recommendations": recommendations,
            "message": "Aşağıdaki konularda gelişim gösterebilirsiniz.",
        }


# --- Auto grading utilities ---


def _score_question(q: Question, student_answer: Any) -> Tuple[Decimal, Dict[str, Any]]:
    """Return (score, flags) for a single question.
    Supports:
    - mcq: exact match; choices index or value acceptable
    - bool: true/false; accepts true/false/1/0/'true'/'false'
    - text: 0 by default (manual grading needed)
    """
    flags: Dict[str, Any] = {}
    max_points = q.points or Decimal("0")

    if q.type == "mcq":
        correct = q.correct_answer
        # normalize: allow index or value
        is_correct = False
        try:
            if isinstance(student_answer, int):
                # index
                if isinstance(correct, int):
                    is_correct = student_answer == correct
                else:
                    # if correct is value, map index to value
                    if isinstance(q.choices, list) and 0 <= student_answer < len(
                        q.choices
                    ):
                        is_correct = q.choices[student_answer] == correct
            else:
                is_correct = student_answer == correct
        except Exception as e:
            flags["error"] = f"mcq-compare-failed: {e}"
            is_correct = False
        return (max_points if is_correct else Decimal("0")), flags

    if q.type == "bool":

        def to_bool(v):
            if isinstance(v, bool):
                return v
            if isinstance(v, (int, float)):
                return bool(v)
            if isinstance(v, str):
                return v.strip().lower() in ["1", "true", "t", "yes", "y"]
            return False

        try:
            is_correct = to_bool(student_answer) == to_bool(q.correct_answer)
        except Exception as e:
            flags["error"] = f"bool-compare-failed: {e}"
            is_correct = False
        return (max_points if is_correct else Decimal("0")), flags

    # text or unknown types need manual grading
    flags["manual_required"] = True
    return Decimal("0"), flags


def grade_submission(submission: ExamSubmission) -> Tuple[Decimal, Dict[str, Any]]:
    """Compute auto_score and flags for an ExamSubmission based on exam questions.
    Does not save; caller should assign and save.
    """
    if not submission.exam:
        return Decimal("0"), {"error": "missing-exam"}

    answers = submission.answers or {}
    total = Decimal("0")
    all_flags: Dict[str, Any] = {"per_question": {}}

    # fetch questions once
    questions = list(submission.exam.questions.all())
    for q in questions:
        ans = answers.get(str(q.id), answers.get(q.id))
        score, flags = _score_question(q, ans)
        all_flags["per_question"][str(q.id)] = flags
        total += score

    return total, all_flags
