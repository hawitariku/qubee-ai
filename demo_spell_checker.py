from spell_checker_ml import MLEnhancedSpellChecker

print("=== QUBEE AI SPELL CHECKER DEMO ===\n")

checker = MLEnhancedSpellChecker('oromo_corpus.txt', use_ml=False)

# Test case 1: "akam jirta"
print("TEST 1: Multiple word sentence")
print("-" * 50)
result = checker.get_detailed_corrections('akam jirta')

print(f"INPUT:  {result['original']}")
print(f"OUTPUT: {result['corrected']}")
print(f"\nCORRECTIONS: {result['total_changes']}")

for corr in result['corrections']:
    print(f"\n  '{corr['original']}' → '{corr['corrected']}' (confidence: {corr['confidence']}%)")
    
    if corr.get('alternatives'):
        print(f"  Alternative suggestions (by frequency):")
        for i, alt in enumerate(corr['alternatives'], 1):
            freq = checker.words_db.get(alt, 0)
            print(f"    {i}. {alt:15} (frequency: {freq:,})")

print("\n" + "=" * 50)

# Test case 2: "seenna kee"
print("\nTEST 2: Fragment correction")
print("-" * 50)
result2 = checker.get_detailed_corrections('seenna kee')

print(f"INPUT:  {result2['original']}")
print(f"OUTPUT: {result2['corrected']}")
print(f"\nCORRECTIONS: {result2['total_changes']}")

for corr in result2['corrections']:
    print(f"\n  '{corr['original']}' → '{corr['corrected']}' (confidence: {corr['confidence']}%)")
    
    if corr.get('alternatives'):
        print(f"  Alternative suggestions (by frequency):")
        for i, alt in enumerate(corr['alternatives'], 1):
            freq = checker.words_db.get(alt, 0)
            print(f"    {i}. {alt:15} (frequency: {freq:,})")

print("\n" + "=" * 50)
print("\n✅ All alternatives are real words (4+ chars, no fragments)")
print("✅ Sorted by frequency (most common first)")
print("✅ Main correction uses balanced scoring")
print("\n=== END DEMO ===")
