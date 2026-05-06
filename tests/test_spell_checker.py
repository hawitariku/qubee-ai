"""
Comprehensive test suite for Qubee AI spell checker
Tests accuracy, grammar checking, and edge cases
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from spell_checker_ml import MLEnhancedSpellChecker
from grammar_checker import AfaanOromoGrammarChecker


class TestSpellCheckerAccuracy(unittest.TestCase):
    """Test spell checking accuracy"""
    
    @classmethod
    def setUpClass(cls):
        """Initialize spell checker once for all tests"""
        cls.checker = MLEnhancedSpellChecker(corpus_path='oromo_corpus.txt', use_ml=False)
    
    def test_vowel_length_correction(self):
        """Test correction of vowel length (a -> aa)"""
        result = self.checker.correct_word('bishan')
        self.assertEqual(result, 'bishaan', "Should correct 'bishan' to 'bishaan'")
    
    def test_missing_verb_ending(self):
        """Test adding missing verb endings"""
        result = self.checker.correct_word('fedh')
        self.assertEqual(result, 'fedha', "Should add missing 'a' to 'fedh'")
    
    def test_geminate_consonant(self):
        """Test geminate consonant correction (y -> yy)"""
        result = self.checker.correct_word('Waaqayo')
        self.assertEqual(result, 'Waaqayyo', "Should correct 'Waaqayo' to 'Waaqayyo'")
    
    def test_correct_word_unchanged(self):
        """Test that correct words are not changed"""
        correct_words = ['bishaan', 'mana', 'deeme', 'fedha', 'Oromoo']
        for word in correct_words:
            result = self.checker.correct_word(word)
            self.assertEqual(result, word, f"Correct word '{word}' should not be changed")
    
    def test_capitalization_correction(self):
        """Test capitalization handling"""
        result = self.checker.correct_word('Ani')
        self.assertIn(result.lower(), ['ani'], "Should handle capitalization")
    
    def test_pronoun_correction(self):
        """Test pronoun spelling corrections"""
        test_cases = {
            'nutii': 'nuti',
            'isaan': 'isaan',  # already correct
        }
        for input_word, expected in test_cases.items():
            result = self.checker.correct_word(input_word)
            self.assertEqual(result, expected, f"Should correct '{input_word}' to '{expected}'")


class TestSentenceCorrection(unittest.TestCase):
    """Test full sentence corrections"""
    
    @classmethod
    def setUpClass(cls):
        cls.checker = MLEnhancedSpellChecker(corpus_path='oromo_corpus.txt', use_ml=False)
    
    def test_simple_sentence_correction(self):
        """Test correction of simple sentence"""
        input_text = "Ani bishan dhuguu fedh"
        result = self.checker.correct_sentence(input_text)
        # Should correct: bishan->bishaan, fedh->fedha, Ani->ani
        self.assertIn('bishaan', result.lower())
        self.assertIn('fedha', result.lower())
    
    def test_correct_sentence_unchanged(self):
        """Test that correct sentences remain unchanged"""
        correct_sentence = "inni gara mana barumsaa deeme"
        result = self.checker.correct_sentence(correct_sentence)
        # Should not introduce false corrections
        self.assertIn('inni', result.lower())
        self.assertIn('deeme', result.lower())
    
    def test_multiple_errors_in_sentence(self):
        """Test correction of multiple errors"""
        input_text = "Isheen mana deeme"  # Should be 'deemte' for feminine
        result = self.checker.correct_sentence(input_text)
        # Basic spell check (grammar is separate)
        self.assertIsNotNone(result)


class TestGrammarChecker(unittest.TestCase):
    """Test grammar checking functionality"""
    
    @classmethod
    def setUpClass(cls):
        cls.grammar_checker = AfaanOromoGrammarChecker()
    
    def test_capitalization_check(self):
        """Test capitalization rule"""
        issues = self.grammar_checker.check_grammar("ani bishaan dhuga")
        cap_issues = [i for i in issues if i['type'] == 'capitalization']
        self.assertGreater(len(cap_issues), 0, "Should detect missing capitalization")
    
    def test_sentence_ending_punctuation(self):
        """Test sentence ending punctuation"""
        issues = self.grammar_checker.check_grammar("Ani bishaan dhuga")
        punct_issues = [i for i in issues if i['type'] == 'missing_punctuation']
        self.assertGreater(len(punct_issues), 0, "Should detect missing punctuation")
    
    def test_question_mark_detection(self):
        """Test question mark requirement"""
        issues = self.grammar_checker.check_grammar("Maal taata")
        question_issues = [i for i in issues if 'question' in i['type']]
        self.assertGreater(len(question_issues), 0, "Should detect missing question mark")
    
    def test_repetitive_words(self):
        """Test detection of repetitive words"""
        issues = self.grammar_checker.check_grammar("Ani ani bishaan dhuga.")
        rep_issues = [i for i in issues if i['type'] == 'repetitive_word']
        self.assertGreater(len(rep_issues), 0, "Should detect repetitive words")
    
    def test_correct_grammar_no_issues(self):
        """Test that correct grammar produces no errors"""
        issues = self.grammar_checker.check_grammar("Inni gara mana barumsaa deeme.")
        # May have some warnings but should not have critical errors
        errors = [i for i in issues if i['severity'] == 'error']
        self.assertEqual(len(errors), 0, "Correct sentence should have no errors")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling"""
    
    @classmethod
    def setUpClass(cls):
        cls.checker = MLEnhancedSpellChecker(corpus_path='oromo_corpus.txt', use_ml=False)
    
    def test_empty_string(self):
        """Test handling of empty string"""
        result = self.checker.correct_sentence("")
        self.assertEqual(result, "", "Empty string should return empty string")
    
    def test_single_character(self):
        """Test handling of single character"""
        result = self.checker.correct_word("a")
        self.assertIsNotNone(result)
    
    def test_very_long_word(self):
        """Test handling of very long words"""
        long_word = "a" * 100
        result = self.checker.correct_word(long_word)
        self.assertIsNotNone(result)
    
    def test_special_characters(self):
        """Test handling of special characters"""
        result = self.checker.correct_sentence("Ani bishaan dhuga!")
        self.assertIn('bishaan', result.lower())
    
    def test_numbers_in_text(self):
        """Test handling of numbers"""
        result = self.checker.correct_sentence("Ani waggaa 25 dha")
        self.assertIn('25', result)
    
    def test_apostrophe_handling(self):
        """Test handling of apostrophes (hudhaa)"""
        result = self.checker.correct_sentence("Isheen ba'ee deemte")
        self.assertIn("'", result)  # Should preserve apostrophe


class TestPerformance(unittest.TestCase):
    """Test performance characteristics"""
    
    @classmethod
    def setUpClass(cls):
        cls.checker = MLEnhancedSpellChecker(corpus_path='oromo_corpus.txt', use_ml=False)
    
    def test_correction_speed(self):
        """Test that corrections complete in reasonable time"""
        import time
        start = time.time()
        self.checker.correct_sentence("Ani bishaan dhuguu fedha")
        duration = time.time() - start
        self.assertLess(duration, 5.0, "Correction should complete within 5 seconds")
    
    def test_cache_effectiveness(self):
        """Test that caching improves performance"""
        import time
        
        # First call (uncached)
        start1 = time.time()
        self.checker.correct_sentence("Ani bishaan dhuguu fedha")
        duration1 = time.time() - start1
        
        # Second call (cached)
        start2 = time.time()
        self.checker.correct_sentence("Ani bishaan dhuguu fedha")
        duration2 = time.time() - start2
        
        # Cached should be faster (or at least not slower)
        self.assertLessEqual(duration2, duration1 * 1.5, "Cached call should be faster")


class TestVocabularySize(unittest.TestCase):
    """Test vocabulary and corpus"""
    
    @classmethod
    def setUpClass(cls):
        cls.checker = MLEnhancedSpellChecker(corpus_path='oromo_corpus.txt', use_ml=False)
    
    def test_vocabulary_loaded(self):
        """Test that vocabulary is loaded"""
        vocab_size = len(cls.checker.words_db)
        self.assertGreater(vocab_size, 1000, "Should have substantial vocabulary")
    
    def test_common_words_present(self):
        """Test that common Afaan Oromo words are in vocabulary"""
        common_words = ['ani', 'ati', 'inni', 'isheen', 'nuti', 'bishaan', 'mana', 'deeme']
        for word in common_words:
            self.assertIn(word, cls.checker.words_db, f"Common word '{word}' should be in vocabulary")
    
    def test_bigrams_loaded(self):
        """Test that bigrams are loaded"""
        bigram_count = len(cls.checker.bigrams)
        self.assertGreater(bigram_count, 100, "Should have bigrams loaded")


def run_tests():
    """Run all tests and print results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSpellCheckerAccuracy))
    suite.addTests(loader.loadTestsFromTestCase(TestSentenceCorrection))
    suite.addTests(loader.loadTestsFromTestCase(TestGrammarChecker))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    suite.addTests(loader.loadTestsFromTestCase(TestVocabularySize))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
