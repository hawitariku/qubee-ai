"""
Test Improved Scoring Algorithm
"""
from spell_checker_ml import MLEnhancedSpellChecker

print("="*70)
print("🧪 Testing Improved Scoring Algorithm")
print("="*70)

# Initialize
checker = MLEnhancedSpellChecker(corpus_path='oromo_corpus.txt', use_ml=False)

# Test cases
tests = [
    ("Ani bishaan dhuguu fedh", "Ani bishaan dhuguu fedha"),
    ("Inni gara mana deeme", "Inni gara mana deeme"),
    ("Isheen barattuu dha", "Isheen barattuu dha"),
    ("Ani kitaaba bar", "Ani kitaaba bara"),
    ("Nuti hojii hojj", "Nuti hojii hojjeta"),
    ("hawi", "hawi"),  # Should NOT change (dialect word)
    ("hiin", "hiin"),  # Should NOT change (vowel length)
    ("akkaam", "akkaam"),  # Should NOT change
]

passed = 0

for input_text, expected in tests:
    corrected, corrections = checker.correct_sentence_with_context(input_text)
    
    print(f"\nInput:    {input_text}")
    print(f"Expected: {expected}")
    print(f"Got:      {corrected}")
    
    if corrections:
        print(f"Changes:  {len(corrections)}")
        for c in corrections:
            print(f"  • {c['original']} → {c['corrected']} (confidence: {c['confidence']}%)")
    else:
        print("Changes:  None")
    
    if corrected == expected:
        print("✅ PASS")
        passed += 1
    else:
        print("❌ FAIL")

print(f"\n{'='*70}")
print(f"Accuracy: {passed}/{len(tests)} = {passed/len(tests)*100:.1f}%")
print(f"{'='*70}")
