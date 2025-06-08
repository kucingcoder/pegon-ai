import string
from typing import Counter
from flask import Blueprint, render_template

from models.history import History

visualization_bp = Blueprint('visualization', __name__)

@visualization_bp.route('/transliteration/<id>', methods=['GET'])
def report(id):
    history = History.objects(id=id).first()
    if not history:
        return "Fail to analyze", 200

    doc = history.to_mongo().to_dict()
    text = doc.get("text")

    text_clean = text.lower().translate(str.maketrans("", "", string.punctuation))
    words = text_clean.split()
    chars = list(text_clean.replace(" ", "").replace("\n", ""))

    word_counts = Counter(words)
    char_counts = Counter(chars)
    vowel_counts = {v: char_counts.get(v, 0) for v in "aeiou"}

    top_words = word_counts.most_common(5)
    top_chars = char_counts.most_common(10)

    return render_template(
        'report.html',
        top_words_labels=[w[0] for w in top_words],
        top_words_counts=[w[1] for w in top_words],
        top_chars_labels=[c[0] for c in top_chars],
        top_chars_counts=[c[1] for c in top_chars],
        vowels=vowel_counts
    )