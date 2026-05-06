"""
Unit Tests for Afaan Oromo Spell Checker
Tests cover:
- Spell checking accuracy
- Grammar checking
- User feedback system
- Performance caching
- Edge cases
"""

import unittest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from spell_checker_ml import MLEnhancedSpellChecker
from grammar_checker import AfaanOromoGrammarChecker


class TestSpellChecker(unittest.TestCase):
    """Test spell checker functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Initialize spell checker once for all tests"""
        cls.checker = MLEnhancedSpellChecker(
            corpus_path='oromo_corpus.txt',
            use_ml=False  # Disable ML for faster tests
        )
    
    def test_vocabulary_loaded(self):
        """Test that vocabulary is loaded"""
        self.assertGreater(len(self.checker.words_db), 1000)
    
    def test_correct_word_simple(self):
        """Test simple word correction"""
        # Test common typos
        result = self.checker.correct_word('fedh')
        self.assertEqual(result, 'fedha')
    
    def test_correct_word_already_correct(self):
        """Test that correct words are not changed"""
        result = self.checker.correct_word('bishaan')
        self.assertEqual(result, 'bishaan')
    
    def test_correct_sentence_context(self):
        """Test sentence correction with context"""
        sentence = "Ani bishaan dhuguu fedh"
        corrected, corrections = self.checker.correct_sentence_with_context(sentence)
        
        self.assertEqual(len(corrections), 1)
        self.assertEqual(corrections[0]['original'], 'fedh')
        self.assertEqual(corrections[0]['corrected'], 'fedha')
    
    def test_incomplete_sentence_handling(self):
        """Test handling of incomplete sentences"""
        # Incomplete sentence should have higher confidence threshold
        sentence = "Ani bishaan"
        corrected, corrections = self.checker.correct_sentence_with_context(sentence)
        
        # Should not over-correct incomplete sentences
        self.assertIsInstance(corrected, str)
    
    def test_get_word_suggestions(self):
        """Test word suggestions"""
        suggestions = self.checker.get_word_suggestions('bishan', top_n=5)
        
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        # Should suggest 'bishaan'
        self.assertIn('bishaan', suggestions)
    
    def test_phonetic_similarity(self):
        """Test phonetic similarity calculation"""
        # Similar words should have high similarity
        sim1 = self.checker._phonetic_similarity('bishaan', 'bishaan')
        self.assertAlmostEqual(sim1, 1.0, places=1)
        
        # Different words should have lower similarity
        sim2 = self.checker._phonetic_similarity('bishaan', 'mana')
        self.assertLess(sim2, 0.5)
    
    def test_edit_distance(self):
        """Test edit distance calculation"""
        dist1 = self.checker._calculate_edit_distance('fedha', 'fedh')
        self.assertEqual(dist1, 1)
        
        dist2 = self.checker._calculate_edit_distance('bishaan', 'bishaan')
        self.assertEqual(dist2, 0)
        
        dist3 = self.checker._calculate_edit_distance('ani', 'inni')
        self.assertEqual(dist3, 1)
    
    def test_cache_performance(self):
        """Test caching mechanism"""
        # First call (cache miss)
        result1 = self.checker.correct_word('fedh')
        initial_misses = self.checker.cache_misses
        
        # Second call (cache hit)
        result2 = self.checker.correct_word('fedh')
        final_hits = self.checker.cache_hits
        
        self.assertEqual(result1, result2)
        self.assertGreater(final_hits, 0)
    
    def test_user_feedback_recording(self):
        """Test user feedback recording"""
        self.checker.record_user_feedback('fedh', 'fedha', True)
        
        # Check that feedback was recorded
        self.assertGreater(len(self.checker.correction_history), 0)
        self.assertIn('fedh->fedha', dict(self.checker.user_feedback_db))
    
    def test_common_words_priority(self):
        """Test that common words have high priority"""
        common_words = ['afaan', 'oromoo', 'bishaan', 'mana']
        
        for word in common_words:
            self.assertIn(word, self.checker.words_db)
            self.assertGreater(self.checker.words_db[word], 5000)
    
    def test_afan_oromo_patterns(self):
        """Test Afaan Oromo specific patterns"""
        # Test subject-verb patterns
        sentence = "Inni gara mana deeme"
        corrected, corrections = self.checker.correct_sentence_with_context(sentence)
        
        # Should recognize correct sentence
        self.assertEqual(len(corrections), 0)
    
    def test_hudhaa_apostrophe_handling(self):
        """Test handling of hudhaa (apostrophe)"""
        # Words with apostrophe should be handled
        word_with_apostrophe = "ba'ee"
        self.checker.correct_word(word_with_apostrophe)
    
    def test_empty_sentence(self):
        """Test handling of empty input"""
        corrected, corrections = self.checker.correct_sentence_with_context("")
        self.assertEqual(corrected, "")
        self.assertEqual(len(corrections), 0)
    
    def test_single_word_sentence(self):
        """Test single word sentence"""
        corrected, corrections = self.checker.correct_sentence_with_context("bishaan")
        self.assertEqual(corrected, "bishaan")
        self.assertEqual(len(corrections), 0)


class TestGrammarChecker(unittest.TestCase):
    """Test grammar checker functionality"""
    
    def setUp(self):
        """Initialize grammar checker"""
        self.checker = AfaanOromoGrammarChecker()
    
    def test_capitalization_check(self):
        """Test capitalization checking"""
        issues = self.checker._check_capitalization("ani bishaan dhuga")
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]['type'], 'capitalization')
    
    def test_sentence_ending_check(self):
        """Test sentence ending punctuation"""
        issues = self.checker._check_sentence_ending("Ani bishaan dhuga")
        self.assertGreater(len(issues), 0)
        self.assertEqual(issues[0]['type'], 'missing_punctuation')
    
    def test_question_formation(self):
        """Test question mark checking"""
        issues = self.checker._check_question_formation("Maal fedhta")
        self.assertGreater(len(issues), 0)
    
    def test_repetitive_words(self):
        """Test repetitive word detection"""
        issues = self.checker._check_repetitive_words("Ani ani bishaan dhuga")
        self.assertGreater(len(issues), 0)
        self.assertEqual(issues[0]['type'], 'repetitive_word')
    
    def test_vowel_length(self):
        """Test excessive vowel length detection"""
        issues = self.checker._check_vowel_length("Ani bishaaaan dhuga")
        self.assertGreater(len(issues), 0)
        self.assertEqual(issues[0]['type'], 'excessive_vowel')
    
    def test_comprehensive_grammar_check(self):
        """Test comprehensive grammar checking"""
        sentence = "ani bishaan dhuga"
        issues = self.checker.check_grammar(sentence)
        
        self.assertIsInstance(issues, list)
        # Should catch capitalization and missing punctuation at least
        self.assertGreaterEqual(len(issues), 2)
    
    def test_grammar_summary(self):
        """Test grammar summary generation"""
        issues = [
            {'severity': 'error', 'type': 'test1'},
            {'severity': 'warning', 'type': 'test2'},
            {'severity': 'warning', 'type': 'test3'},
        ]
        
        summary = self.checker.get_grammar_summary(issues)
        
        self.assertEqual(summary['total_issues'], 3)
        self.assertEqual(summary['errors'], 1)
        self.assertEqual(summary['warnings'], 2)
    
    def test_valid_sentence(self):
        """Test that valid sentences pass checks"""
        sentence = "Ani bishaan dhuguu fedha."
        issues = self.checker.check_grammar(sentence)
        
        # Should have minimal or no issues
        error_issues = [i for i in issues if i['severity'] == 'error']
        self.assertEqual(len(error_issues), 0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    @classmethod
    def setUpClass(cls):
        cls.checker = MLEnhancedSpellChecker(
            corpus_path='oromo_corpus.txt',
            use_ml=False
        )
    
    def test_very_long_sentence(self):
        """Test handling of very long sentences"""
        long_sentence = "Ani " * 1000
        corrected, corrections = self.checker.correct_sentence_with_context(long_sentence)
        
        self.assertIsInstance(corrected, str)
        self.assertGreater(len(corrected), 0)
    
    def test_special_characters(self):
        """Test handling of special characters"""
        sentence = "Ani bishaan dhuguu fedha! Isheen nyaata nyaatte?"
        corrected, corrections = self.checker.correct_sentence_with_context(sentence)
        
        self.assertIsInstance(corrected, str)
    
    def test_mixed_case(self):
        """Test handling of mixed case"""
        sentence = "AnI BiShAaN dHuGuU fEdHa"
        corrected, corrections = self.checker.correct_sentence_with_context(sentence)
        
        # Should normalize to lowercase
        self.assertIsInstance(corrected, str)
    
    def test_numbers_in_text(self):
        """Test handling of numbers"""
        sentence = "Ani barataa 1 dha"
        corrected, corrections = self.checker.correct_sentence_with_context(sentence)
        
        self.assertIsInstance(corrected, str)
    
    def test_unicode_characters(self):
        """Test handling of Unicode characters"""
        sentence = "Afaan Oromoo barreessuu"
        corrected, corrections = self.checker.correct_sentence_with_context(sentence)
        
        self.assertIsInstance(corrected, str)


class TestPerformance(unittest.TestCase):
    """Test performance characteristics"""
    
    @classmethod
    def setUpClass(cls):
        cls.checker = MLEnhancedSpellChecker(
            corpus_path='oromo_corpus.txt',
            use_ml=False
        )
    
    def test_cache_hit_rate(self):
        """Test that caching improves performance"""
        # Make repeated calls
        for _ in range(10):
            self.checker.correct_word('fedh')
        
        stats = self.checker.get_cache_stats()
        hit_rate = float(stats['hit_rate'].rstrip('%'))
        
        # Should have high hit rate for repeated calls
        self.assertGreater(hit_rate, 50.0)
    
    def test_vocabulary_size(self):
        """Test that vocabulary is adequately sized"""
        vocab_size = len(self.checker.words_db)
        
        # Should have at least 10,000 words
        self.assertGreater(vocab_size, 10000)
    
    def test_bigram_count(self):
        """Test that bigrams are loaded"""
        bigram_count = len(self.checker.bigrams)
        
        # Should have substantial bigrams
        self.assertGreater(bigram_count, 1000)


def run_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 Running Afaan Oromo Spell Checker Tests")
    print("="*60 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSpellChecker))
    suite.addTests(loader.loadTestsFromTestCase(TestGrammarChecker))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("📊 Test Summary")
    print("="*60)
    print(f"✅ Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"❌ Failed: {len(result.failures)}")
    print(f"💥 Errors: {len(result.errors)}")
    print(f"📝 Total: {result.testsRun}")
    print("="*60 + "\n")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
