"""
Test script to verify accuracy improvements after fixing the scoring algorithm
"""

from spell_checker_ml import MLEnhancedSpellChecker
import time

def test_accuracy():
    """Test accuracy with various test cases"""
    
    print("="*70)
    print("ACCURACY FIX VERIFICATION TEST")
    print("="*70)
    print("\nInitializing spell checker...")
    
    checker = MLEnhancedSpellChecker(corpus_path='oromo_corpus.txt', use_ml=False)
    
    print(f"✓ Loaded vocabulary: {len(checker.words_db)} words\n")
    
    # Test cases: (input, expected_output, test_description)
    test_cases = [
        # Vowel length corrections
        ("bishan", "bishaan", "Vowel length (a -> aa)"),
        ("fedh", "fedha", "Missing verb ending"),
        ("Waaqayo", "Waaqayyo", "Geminate consonant (y -> yy)"),
        
        # Correct words should not change
        ("bishaan", "bishaan", "Correct word unchanged"),
        ("mana", "mana", "Correct word unchanged"),
        ("deeme", "deeme", "Correct word unchanged"),
        ("fedha", "fedha", "Correct word unchanged"),
        
        # Pronoun corrections
        ("nutii", "nuti", "Pronoun spelling"),
        
        # Common typos
        ("dhuga", "dhuga", "Correct word unchanged"),
        ("jira", "jira", "Correct word unchanged"),
        
        # Edge cases
        ("Oromoo", "Oromoo", "Correct word with geminate"),
        ("barumsaa", "barumsaa", "Correct word unchanged"),
    ]
    
    print("Running test cases...")
    print("-"*70)
    
    passed = 0
    failed = 0
    results = []
    
    for input_word, expected, description in test_cases:
        start_time = time.time()
        result = checker.correct_word(input_word)
        duration = time.time() - start_time
        
        # Normalize for comparison (case-insensitive)
        result_lower = result.lower()
        expected_lower = expected.lower()
        
        success = result_lower == expected_lower
        
        if success:
            passed += 1
            status = "✓ PASS"
        else:
            failed += 1
            status = "✗ FAIL"
        
        results.append({
            'input': input_word,
            'expected': expected,
            'actual': result,
            'success': success,
            'description': description,
            'duration': duration
        })
        
        print(f"{status} | {description:30s} | '{input_word}' -> '{result}' (expected: '{expected}') [{duration:.3f}s]")
    
    print("-"*70)
    print(f"\nRESULTS:")
    print(f"  Passed: {passed}/{len(test_cases)} ({passed/len(test_cases)*100:.1f}%)")
    print(f"  Failed: {failed}/{len(test_cases)} ({failed/len(test_cases)*100:.1f}%)")
    
    # Test full sentences
    print("\n" + "="*70)
    print("SENTENCE CORRECTION TESTS")
    print("="*70)
    
    sentence_tests = [
        ("Ani bishan dhuguu fedh", "ani bishaan dhuguu fedha", "Multiple corrections"),
        ("Inni gara mana barumsaa deeme", "inni gara mana barumsaa deeme", "Correct sentence"),
        ("Isheen mana deeme", "isheen mana deeme", "Basic sentence"),
    ]
    
    sentence_passed = 0
    sentence_failed = 0
    
    for input_sent, expected_sent, description in sentence_tests:
        start_time = time.time()
        result = checker.correct_sentence_with_context(input_sent)
        duration = time.time() - start_time
        
        # Check if key corrections are present
        success = True
        if "bishan" in input_sent and "bishaan" not in result.lower():
            success = False
        if "fedh" in input_sent and "fedha" not in result.lower():
            success = False
        
        if success:
            sentence_passed += 1
            status = "✓ PASS"
        else:
            sentence_failed += 1
            status = "✗ FAIL"
        
        print(f"{status} | {description:30s}")
        print(f"  Input:    '{input_sent}'")
        print(f"  Output:   '{result}'")
        print(f"  Expected: '{expected_sent}'")
        print(f"  Duration: {duration:.3f}s")
        print()
    
    print("-"*70)
    print(f"\nSENTENCE RESULTS:")
    print(f"  Passed: {sentence_passed}/{len(sentence_tests)} ({sentence_passed/len(sentence_tests)*100:.1f}%)")
    print(f"  Failed: {sentence_failed}/{len(sentence_tests)} ({sentence_failed/len(sentence_tests)*100:.1f}%)")
    
    # Cache statistics
    print("\n" + "="*70)
    print("CACHE STATISTICS")
    print("="*70)
    cache_stats = checker.get_cache_stats()
    print(f"  Cache hits: {cache_stats['hits']}")
    print(f"  Cache misses: {cache_stats['misses']}")
    print(f"  Hit rate: {cache_stats['hit_rate']:.1%}")
    
    # Overall assessment
    print("\n" + "="*70)
    print("OVERALL ASSESSMENT")
    print("="*70)
    
    total_tests = len(test_cases) + len(sentence_tests)
    total_passed = passed + sentence_passed
    total_failed = failed + sentence_failed
    accuracy = (total_passed / total_tests) * 100
    
    print(f"  Total tests: {total_tests}")
    print(f"  Total passed: {total_passed}")
    print(f"  Total failed: {total_failed}")
    print(f"  Accuracy: {accuracy:.1f}%")
    
    if accuracy >= 85:
        print("\n  ✓ EXCELLENT: Accuracy target (85%+) achieved!")
    elif accuracy >= 70:
        print("\n  ⚠ GOOD: Accuracy improved but below target (85%)")
    else:
        print("\n  ✗ NEEDS WORK: Accuracy still below acceptable threshold")
    
    print("="*70)
    
    return accuracy >= 85


if __name__ == '__main__':
    success = test_accuracy()
    exit(0 if success else 1)
