import logging
import re
from thefuzz import fuzz, process
from database import get_all_questions

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = 55
CANDIDATE_LIMIT = 10


def clean_arabic_text(text: str) -> str:
    
    if not text:
        return ""
   
    text = re.sub(r'\bال', ' ', text)
    text = re.sub(r'[ًٌٍَُِْ]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


async def find_best_answer(query: str) -> tuple[str | None, float]:
    if not query or not query.strip():
        return None, 0.0

    cleaned_query = clean_arabic_text(query)

    qa_pairs = await get_all_questions()
    if not qa_pairs:
        return None, 0.0

    cleaned_questions = [clean_arabic_text(pair["question"]) for pair in qa_pairs]
    original_questions = [pair["question"] for pair in qa_pairs]

    best_match_idx = -1
    best_score = 0.0

    scorers = [
        fuzz.token_set_ratio,    
        fuzz.partial_ratio,     
        fuzz.WRatio        
    ]

    for scorer in scorers:
        results = process.extract(
            cleaned_query,
            cleaned_questions,
            scorer=scorer,
            limit=CANDIDATE_LIMIT
        )
        for match_text, score, idx in results:
            if score > best_score:

                query_words = set(cleaned_query.split())
                match_words = set(match_text.split())
                common_words = query_words.intersection(match_words)
                
                if len(common_words) >= 2 or score > 75:
                    best_score = score
                    best_match_idx = idx
                
                elif score > best_score + 10:
                    best_score = score
                    best_match_idx = idx

    if best_score < SIMILARITY_THRESHOLD:
        logger.info(f"أفضل تطابق: {cleaned_questions[best_match_idx] if best_match_idx >=0 else 'لا شيء'} بدرجة {best_score}")
        return None, best_score

    if best_match_idx >= 0:
        return qa_pairs[best_match_idx]["answer"], best_score

    return None, 0.0
