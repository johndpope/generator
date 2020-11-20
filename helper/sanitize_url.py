def sanitize_url(str):
    return str.lower().replace('/', '').replace(', ', '-').replace('&', 'und').replace(' ', '-')


def undo_sanitize(str: str):
    return str.title().replace('-', ' ').replace('und', '&')