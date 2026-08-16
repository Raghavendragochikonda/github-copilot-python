"""Tests for browser-side leaderboard behavior."""

from leaderboard import sort_leaderboard, keep_top_ten


class TestLeaderboardOrdering:
    """Verify leaderboard sorting and trimming logic."""

    def test_sort_leaderboard_by_fastest_time(self):
        entries = [
            {'playerName': 'Bob', 'completionTime': '01:30', 'difficulty': 'medium', 'hintsUsed': 2},
            {'playerName': 'Alice', 'completionTime': '00:45', 'difficulty': 'easy', 'hintsUsed': 1},
            {'playerName': 'Cara', 'completionTime': '00:45', 'difficulty': 'hard', 'hintsUsed': 0},
        ]

        result = sort_leaderboard(entries)
        assert result[0]['playerName'] == 'Cara'
        assert result[1]['playerName'] == 'Alice'
        assert result[2]['playerName'] == 'Bob'

    def test_keep_top_ten_trims_entries(self):
        entries = [
            {'playerName': f'Player {i}', 'completionTime': f'00:{(i % 59):02d}', 'difficulty': 'easy', 'hintsUsed': i}
            for i in range(12)
        ]

        result = keep_top_ten(entries)
        assert len(result) == 10
        assert result[0]['playerName'] == 'Player 0'
        assert result[-1]['playerName'] == 'Player 9'
