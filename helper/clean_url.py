import re


def sanitize_url(str):
    if str:
        return str.lower()\
            .replace('/', '')\
            .replace(', ', '-')\
            .replace(':', '-')\
            .replace('&', 'und')\
            .replace(' ', '-')\
            .replace('---', '-')\
            .replace('--', '-')\
            .replace('.', '')\
            .replace('ö', 'oe')\
            .replace('ä', 'ae')\
            .replace('ü', 'ue')
    return None


def clean_url(str):
    return sanitize_url(deEmojify(str)) if str else ''


def deEmojify(text):
    regrex_pattern = re.compile(pattern="["
                                u"\U0001F600-\U0001F64F"  # emoticons
                                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                "]+", flags=re.UNICODE)
    return regrex_pattern.sub(r'', text)

