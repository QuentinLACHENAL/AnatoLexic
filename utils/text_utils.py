import re
import random

def shuffle_preserving_punctuation(text):
    """
    Shuffles only alphabetic letters in 'text',
    while preserving punctuation, spaces and their positions.
    """
    pattern = re.compile(r'([a-zA-ZÀ-ÖÙ-Ýà-öù-ý]+|[^a-zA-ZÀ-ÖÙ-Ýà-öù-ý]+)')
    segments = pattern.findall(text)

    result_segments = []
    for seg in segments:
        if re.match(r'^[a-zA-ZÀ-ÖÙ-Ýà-öù-ý]+$', seg):
            seg_list = list(seg)
            random.shuffle(seg_list)
            result_segments.append("".join(seg_list))
        else:
            result_segments.append(seg)

    return "".join(result_segments)
