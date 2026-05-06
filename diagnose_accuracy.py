"""
Diagnostic Script - Identify Accuracy Issues
Run this to see exactly what's being corrected wrong
"""

from spell_checker_ml import MLEnhancedSpellChecker
import json

def diagnose_accuracy():
    print("="*70)
    print("🔍 Afaan Oromo Spell Checker - Accuracy Diagnostic")
    print("="*70)
    
    # Initialize checker
    print("\n📊 Loading spell checker...")
    checker = MLEnhancedSpellChecker(corpus_path='oromo_corpus.txt', use_ml=False)
    
    print(f"\n✅ Loaded {len(checker.words_db):,} words")
    print(f"✅ {len(checker.bigrams):,} bigrams")
    print(f"✅ {len(checker.trigrams):,} trigrams")
    
    # Test sentences
    test_sentences = [
        "Ani bishaan dhuguu fedh",
        "Inni gara mana deeme",
        "Isheen barattuu dha",
        "Ani kitaaba bar",
        "Nuti hojii hojj",
        "Inni finfinnee deeme",
        "Isheen bishaan dhugde",
        "Ani nyaata nyaadha",
    ]
    
    print("\n" + "="*70)
    print("📝 Testing Corrections")
    print("="*70 + "\n")
    
    all_results = []
    
    for sentence in test_sentences:
        print(f"Input: {sentence}")
        
        # Get correction
        corrected, corrections = checker.correct_sentence_with_context(sentence)
        
        print(f"Output: {corrected}")
        
        if corrections:
            print(f"Changes: {len(corrections)}")
            for c in corrections:
                original_clean = c['original'].strip()
                corrected_clean = c['corrected'].strip()
                confidence = c['confidence']
                
                print(f"  • {original_clean} → {corrected_clean} (confidence: {confidence}%)")
                
                # Check if this correction seems wrong
                edit_dist = checker._calculate_edit_distance(original_clean.lower(), corrected_clean.lower())
                phonetic = checker._phonetic_similarity(original_clean.lower(), corrected_clean.lower())
                
                print(f"    - Edit distance: {edit_dist}")
                print(f"    - Phonetic similarity: {phonetic:.2f}")
                print(f"    - Original in vocab: {original_clean.lower() in checker.words_db}")
                print(f"    - Corrected in vocab: {corrected_clean.lower() in checker.words_db}")
                
                if original_clean.lower() in checker.words_db:
                    print(f"    - ⚠️ WARNING: Original word was already correct!")
                
                # Check frequency
                orig_freq = checker.words_db.get(original_clean.lower(), 0)
                corr_freq = checker.words_db.get(corrected_clean.lower(), 0)
                print(f"    - Original frequency: {orig_freq}")
                print(f"    - Corrected frequency: {corr_freq}")
                
                if corr_freq > orig_freq * 10:
                    print(f"    - ⚠️ WARNING: Frequency difference might be causing bias!")
        else:
            print("Changes: None (sentence deemed correct)")
        
        # Detailed word analysis
        print("\n  Word-by-word analysis:")
        words = sentence.split()
        for word in words:
            clean = word.lower()
            in_vocab = clean in checker.words_db
            freq = checker.words_db.get(clean, 0)
            status = "✓" if in_vocab else "✗"
            print(f"    {status} {clean:<15} freq: {freq:>6,}  {'in vocab' if in_vocab else 'NOT in vocab'}")
        
        print("\n" + "-"*70 + "\n")
        
        all_results.append({
            'input': sentence,
            'output': corrected,
            'corrections': corrections
        })
    
    # Summary
    print("="*70)
    print("📊 SUMMARY")
    print("="*70)
    
    total_words = 0
    corrected_words = 0
    false_corrections = 0
    
    for result in all_results:
        words = result['input'].split()
        total_words += len(words)
        corrected_words += len(result['corrections'])
        
        for c in result['corrections']:
            original = c['original'].strip().lower()
            if original in checker.words_db:
                false_corrections += 1
    
    print(f"\nTotal words analyzed: {total_words}")
    print(f"Words corrected: {corrected_words}")
    print(f"False corrections (correct words changed): {false_corrections}")
    
    if corrected_words > 0:
        false_rate = (false_corrections / corrected_words * 100)
        print(f"\nFalse correction rate: {false_rate:.1f}%")
        
        if false_rate > 30:
            print("\n❌ HIGH FALSE CORRECTION RATE!")
            print("   Problem: System is over-correcting")
            print("   Solution: Increase confidence threshold, reduce frequency weight")
        elif false_rate > 15:
            print("\n⚠️  MODERATE FALSE CORRECTION RATE")
            print("   Problem: Some over-correction happening")
            print("   Solution: Adjust scoring balance")
        else:
            print("\n✅ False correction rate is acceptable")
    
    # Save results
    with open('diagnostic_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Detailed results saved to: diagnostic_results.json")
    print("="*70)

if __name__ == '__main__':
    diagnose_accuracy()
