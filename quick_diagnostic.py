"""
Quick diagnostic - shows exactly what's happening
"""
from spell_checker_ml import MLEnhancedSpellChecker

print("="*70)
print("🔍 DIAGNOSTIC - What is the spell checker doing?")
print("="*70)

checker = MLEnhancedSpellChecker(corpus_path='oromo_corpus.txt', use_ml=False)

# Test the exact sentences from your logs
test_sentences = [
    "hiin",
    "hiin hinafin",
    "hiin inafin",
    "maal kuun",
    "mal kuun",
    "affan",
    "affann",
    "affan ko",
    "affan kotu",
    "orromo",
    "gaaraa",
    "hawin fokkistu dha",
]

for sentence in test_sentences:
    corrected, corrections = checker.correct_sentence_with_context(sentence)
    
    print(f"\n{'='*70}")
    print(f"Input:    '{sentence}'")
    print(f"Output:   '{corrected}'")
    
    if corrections:
        print(f"\nChanges made: {len(corrections)}")
        for c in corrections:
            print(f"  • '{c['original']}' → '{c['corrected']}' (confidence: {c['confidence']}%)")
            print(f"    - Edit distance: {checker._calculate_edit_distance(c['original'], c['corrected'])}")
            print(f"    - Phonetic similarity: {checker._phonetic_similarity(c['original'], c['corrected']):.2f}")
            print(f"    - Original in vocab: {c['original'].lower() in checker.words_db}")
            print(f"    - Corrected in vocab: {c['corrected'].lower() in checker.words_db}")
    else:
        print("\n✓ No changes (sentence considered correct)")
    
    # Show word analysis
    print(f"\nWord analysis:")
    for word in sentence.split():
        clean = word.lower()
        in_vocab = clean in checker.words_db
        freq = checker.words_db.get(clean, 0)
        status = "✓" if in_vocab else "✗"
        print(f"  {status} {clean:<20} freq: {freq:>6,}")

print(f"\n{'='*70}")
print("DIAGNOSTIC COMPLETE")
print(f"{'='*70}")
