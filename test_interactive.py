"""
Quick Test - Show Real-World Accuracy
Test with YOUR actual failing cases
"""

from spell_checker_ml import MLEnhancedSpellChecker

print("="*70)
print("🧪 Interactive Spell Checker Test")
print("="*70)

# Initialize
checker = MLEnhancedSpellChecker(corpus_path='oromo_corpus.txt', use_ml=False)

print("\n📝 Enter sentences to test (or 'quit' to exit)\n")

while True:
    sentence = input("Input: ").strip()
    
    if sentence.lower() in ['quit', 'exit', 'q']:
        print("\n👋 Goodbye!")
        break
    
    if not sentence:
        continue
    
    # Get correction
    corrected, corrections = checker.correct_sentence_with_context(sentence)
    
    print(f"\n✅ Output: {corrected}")
    
    if corrections:
        print(f"\n📝 Changes made: {len(corrections)}")
        for c in corrections:
            print(f"  • {c['original']} → {c['corrected']} (confidence: {c['confidence']}%)")
    else:
        print("\n✓ No changes (sentence is correct)")
    
    # Word analysis
    print("\n📊 Word analysis:")
    words = sentence.split()
    for word in words:
        clean = word.lower()
        in_vocab = clean in checker.words_db
        freq = checker.words_db.get(clean, 0)
        status = "✓" if in_vocab else "✗"
        print(f"  {status} {clean:<20} freq: {freq:>6,}")
    
    print("\n" + "-"*70 + "\n")
