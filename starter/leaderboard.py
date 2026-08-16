"""Pure Python helpers for leaderboard ordering and sanitization.

These functions mirror the browser-side leaderboard rules so they can be
validated in tests without depending on a browser or localStorage.
"""


def parse_completion_time(value):
    """Convert a displayed MM:SS value to seconds."""
    if value is None:
        return 0

    if isinstance(value, (int, float)):
        return int(value)

    text = str(value).strip()
    if not text:
        return 0

    if ':' in text:
        minutes, seconds = text.split(':', 1)
        return int(minutes) * 60 + int(seconds)

    return int(text)


def sort_leaderboard(entries):
    """Return leaderboard entries sorted by fastest completion time first."""
    cleaned = []
    for entry in entries or []:
        if not isinstance(entry, dict):
            continue
        cleaned.append({
            'playerName': str(entry.get('playerName', 'Player')).strip() or 'Player',
            'completionTime': str(entry.get('completionTime', '00:00')).strip() or '00:00',
            'difficulty': str(entry.get('difficulty', 'medium')).strip() or 'medium',
            'hintsUsed': int(entry.get('hintsUsed', 0) or 0),
        })

    return sorted(
        cleaned,
        key=lambda item: (
            parse_completion_time(item.get('completionTime', '00:00')),
            item.get('hintsUsed', 0),
            item.get('playerName', '').lower(),
        )
    )


def keep_top_ten(entries):
    """Trim a leaderboard to the first ten sorted entries."""
    return sort_leaderboard(entries)[:10]
