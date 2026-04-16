import logging
import re
from thefuzz import fuzz, process
from database import get_all_questions

logger = logging.getLogger(__name__)
SIMILARITY_THRESHOLD = 65
CANDIDATE_LIMIT = 10

STOP_WORDS = {
    "ما", "هو", "هي", "في", "على", "عن", "من", "إلى", "مع", "كان", "هذا", "هذه",
    "شو", "شو هوي", "شو هي", "يعنني", "يعني", "بدي", "بدنا", "كيف", "وين", "ليش",
    "شنو", "ايش", "الترفع", "الإداري", "اداري", "ال", "لل", "يا"
}

def clean_arabic_text(text: str) -> str:
 
    if not text:
        return ""
    try:
      
        text = re.sub(r'[ًٌٍَُِْ]', '', text)
        text = re.sub(r'\bال', ' ', text)
        words = text.split()
      
        filtered_words = [w for w in words if w not in STOP_WORDS and len(w) > 1]
     
        cleaned = ' '.join(filtered_words)
        return cleaned.strip()
    except Exception:
        return text


async def find_best_answer(query: str) -> tuple[str | None, float]:
    try:
        if not query or not query.strip():
            return None, 0.0
 
        cleaned_query = clean_arabic_text(query)
        logger.info(f"سؤال المستخدم بعد التنظيف: '{cleaned_query}'")

        qa_pairs = await get_all_questions()
        if not qa_pairs:
            logger.warning("قاعدة البيانات فارغة")
            return None, 0.0
  
        cleaned_questions = [clean_arabic_text(pair["question"]) for pair in qa_pairs]
        original_questions = [pair["question"] for pair in qa_pairs]

        best_match_idx = -1
        best_score = 0.0
        best_match_cleaned = ""

        scorers = [fuzz.token_set_ratio, fuzz.partial_ratio, fuzz.WRatio]

        for scorer in scorers:
            results = process.extract(
                cleaned_query,
                cleaned_questions,
                scorer=scorer,
                limit=CANDIDATE_LIMIT
            )
            
            for item in results:
                if len(item) == 3:
                    match_text, score, idx = item
                elif len(item) == 2:
                    match_text, score = item
                    try:
                        idx = cleaned_questions.index(match_text)
                    except ValueError:
                        continue
                else:
                    continue

                query_words = set(cleaned_query.split())
                match_words = set(match_text.split())
                common_words = query_words.intersection(match_words)

              
                if score > 80:
                    if score > best_score:
                        best_score = score
                        best_match_idx = idx
                        best_match_cleaned = match_text
                elif score >= SIMILARITY_THRESHOLD and len(common_words) >= 2:
                    if score > best_score:
                        best_score = score
                        best_match_idx = idx
                        best_match_cleaned = match_text

        logger.info(f"أفضل تطابق: '{best_match_cleaned}' بدرجة {best_score}")

        if best_score < SIMILARITY_THRESHOLD or best_match_idx == -1:
            return None, best_score

        return qa_pairs[best_match_idx]["answer"], best_score

    except Exception as e:
        logger.error(f"خطأ في البحث: {e}", exc_info=True)
        return None, 0.0
