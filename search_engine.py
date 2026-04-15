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

    best_match, best_score, best_idx = results[0]

   
    results_wr = process.extract(
        query, questions,
        scorer=fuzz.WRatio,
        limit=3
    )
    if results_wr and results_wr[0][1] > best_score:
        best_match, best_score, best_idx = results_wr[0]

    if best_score >= SIMILARITY_THRESHOLD:
        return qa_pairs[best_idx]["answer"], best_score

    return None, best_score
