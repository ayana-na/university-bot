import logging
from thefuzz import fuzz, process
from database import get_all_questions

logger = logging.getLogger(__name__)
SIMILARITY_THRESHOLD = 60

async def find_best_answer(query: str) -> tuple[str | None, float]:
    if not query.strip():
        return None, 0.0

    qa_pairs = await get_all_questions()
    if not qa_pairs:
        return None, 0.0

    questions = [pair["question"] for pair in qa_pairs]

    results = process.extract(
        query, questions,
        scorer=fuzz.token_set_ratio,
        limit=5
    )

    if not results:
        return None, 0.0

    first = results[0]
    if len(first) == 3:
        best_match, best_score, best_idx = first
    else:
        best_match, best_score = first
        try:
            best_idx = questions.index(best_match)
        except ValueError:
            best_idx = 0

    results_wr = process.extract(
        query, questions,
        scorer=fuzz.WRatio,
        limit=3
    )
    if results_wr:
        first_wr = results_wr[0]
        if len(first_wr) == 3:
            match_wr, score_wr, idx_wr = first_wr
        else:
            match_wr, score_wr = first_wr
            try:
                idx_wr = questions.index(match_wr)
            except ValueError:
                idx_wr = 0

        if score_wr > best_score:
            best_match, best_score, best_idx = match_wr, score_wr, idx_wr

    if best_score >= SIMILARITY_THRESHOLD:
        return qa_pairs[best_idx]["answer"], best_score

    return None, best_score
