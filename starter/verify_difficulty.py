#!/usr/bin/env python3
"""
Quick verification script for difficulty levels feature.
Tests that the /new route correctly handles difficulty parameters.
"""
import json
from app import app

def test_difficulty_feature():
    """Test that difficulty levels work correctly."""
    client = app.test_client()
    
    print("Testing Difficulty Levels Feature...\n")
    
    # Test Easy (45 clues)
    print("✓ Testing Easy (45 clues)...")
    response = client.get('/new?difficulty=easy')
    data = json.loads(response.data)
    puzzle = data['puzzle']
    easy_clues = sum(1 for row in puzzle for cell in row if cell != 0)
    print(f"  Generated: {easy_clues} clues (expected: 45)")
    assert easy_clues == 45, f"Easy: Expected 45 clues, got {easy_clues}"
    print("  ✅ PASS\n")
    
    # Test Medium (35 clues)
    print("✓ Testing Medium (35 clues)...")
    response = client.get('/new?difficulty=medium')
    data = json.loads(response.data)
    puzzle = data['puzzle']
    medium_clues = sum(1 for row in puzzle for cell in row if cell != 0)
    print(f"  Generated: {medium_clues} clues (expected: 35)")
    assert medium_clues == 35, f"Medium: Expected 35 clues, got {medium_clues}"
    print("  ✅ PASS\n")
    
    # Test Hard (25 clues)
    print("✓ Testing Hard (25 clues)...")
    response = client.get('/new?difficulty=hard')
    data = json.loads(response.data)
    puzzle = data['puzzle']
    hard_clues = sum(1 for row in puzzle for cell in row if cell != 0)
    print(f"  Generated: {hard_clues} clues (expected: 25)")
    assert hard_clues == 25, f"Hard: Expected 25 clues, got {hard_clues}"
    print("  ✅ PASS\n")
    
    # Test Default (no difficulty = medium = 35)
    print("✓ Testing Default (no difficulty parameter)...")
    response = client.get('/new')
    data = json.loads(response.data)
    puzzle = data['puzzle']
    default_clues = sum(1 for row in puzzle for cell in row if cell != 0)
    print(f"  Generated: {default_clues} clues (expected: 35)")
    assert default_clues == 35, f"Default: Expected 35 clues, got {default_clues}"
    print("  ✅ PASS\n")
    
    # Test clues parameter still works (backward compatibility)
    print("✓ Testing clues parameter (backward compatibility)...")
    response = client.get('/new?clues=50')
    data = json.loads(response.data)
    puzzle = data['puzzle']
    custom_clues = sum(1 for row in puzzle for cell in row if cell != 0)
    print(f"  Generated: {custom_clues} clues (expected: 50)")
    assert custom_clues == 50, f"Clues param: Expected 50 clues, got {custom_clues}"
    print("  ✅ PASS\n")
    
    # Test that clues parameter takes precedence
    print("✓ Testing clues precedence over difficulty...")
    response = client.get('/new?difficulty=easy&clues=30')
    data = json.loads(response.data)
    puzzle = data['puzzle']
    precedence_clues = sum(1 for row in puzzle for cell in row if cell != 0)
    print(f"  Generated: {precedence_clues} clues (expected: 30, not 45)")
    assert precedence_clues == 30, f"Precedence: Expected 30 clues, got {precedence_clues}"
    print("  ✅ PASS\n")
    
    print("=" * 50)
    print("✅ All difficulty tests PASSED!")
    print("=" * 50)

if __name__ == '__main__':
    test_difficulty_feature()
