"""
Comprehensive Grammar Checker for Afaan Oromo
Implements advanced grammar rules including:
- Subject-verb agreement
- Tense consistency
- Case marking verification
- SOV word order validation
- Common grammar patterns
"""

import re
from typing import List, Dict


class AfaanOromoGrammarChecker:
    """Advanced grammar checker for Afaan Oromo language"""
    
    def __init__(self):
        # Subject pronouns and their properties
        self.pronouns = {
            'ani': {'person': '1st', 'number': 'singular', 'label': 'First person singular'},
            'ati': {'person': '2nd', 'number': 'singular', 'label': 'Second person singular'},
            'inni': {'person': '3rd', 'number': 'singular', 'gender': 'masculine', 'label': 'Third person singular (m)'},
            'isheen': {'person': '3rd', 'number': 'singular', 'gender': 'feminine', 'label': 'Third person singular (f)'},
            'nuti': {'person': '1st', 'number': 'plural', 'label': 'First person plural'},
            'isin': {'person': '2nd', 'number': 'plural', 'label': 'Second person plural'},
            'isaan': {'person': '3rd', 'number': 'plural', 'label': 'Third person plural'},
        }
        
        # Verb endings by subject
        self.verb_endings = {
            'ani': ['a', 'n', 'ffa', 'tta'],
            'ati': ['ta', 'tta', 'ffa'],
            'inni': ['e', 'a', 'eessa'],
            'isheen': ['te', 'tte', 'eetti'],
            'nuti': ['na', 'rra', 'anna', 'nna'],
            'isin': ['tu', 'ttu', 'ttan', 'tan'],
            'isaan': ['u', 'ru', 'lu', 'anu'],
        }
        
        # Common verb roots and their conjugations
        self.common_verbs = {
            'deem': {'meaning': 'go', 'present': 'deema', 'past': 'deeme', 'perfect': 'deemee'},
            'dhuf': {'meaning': 'come', 'present': 'dhufa', 'past': 'dhufe', 'perfect': 'dhufee'},
            'fedh': {'meaning': 'want', 'present': 'fedha', 'past': 'fedhe', 'perfect': 'fedhee'},
            'baar': {'meaning': 'learn', 'present': 'baara', 'past': 'baare', 'perfect': 'baaree'},
            'ny': {'meaning': 'eat', 'present': 'nyaata', 'past': 'nyaate', 'perfect': 'nyaatee'},
            'dhug': {'meaning': 'drink', 'present': 'dhuga', 'past': 'dhuge', 'perfect': 'dhugee'},
            'hojj': {'meaning': 'work', 'present': 'hojjeta', 'past': 'hojjete', 'perfect': 'hojjette'},
            'bar': {'meaning': 'know/learn', 'present': 'bara', 'past': 'bare', 'perfect': 'baree'},
            'beek': {'meaning': 'know', 'present': 'beeka', 'past': 'beeke', 'perfect': 'beekеe'},
            'jedh': {'meaning': 'say', 'present': 'jedha', 'past': 'jedhe', 'perfect': 'jedhee'},
        }
        
        # Tense markers
        self.tense_markers = {
            'present': ['a', 'aa', 'i', 'ii'],
            'past': ['e', 'ee', 'te', 'tte'],
            'future': ['da', 'du', 'f'],
            'perfect': ['ee', 'eessa', 'ttee'],
        }
        
        # Question words
        self.question_words = ['maal', 'eenyu', 'eessa', 'yoom', 'akkam', 'maaliif', 'maal', 'kam', 'enyu']
        
        # Common prepositions
        self.prepositions = ['gara', 'irraa', 'itti', 'waliin', 'keessa', 'biraa', 'jalaa', 'irratti', 'duuba']
        
        # Conjunctions
        self.conjunctions = ['fi', 'yookaan', 'garuu', 'ta\'uus', 'kan', 'akka']
        
        # Case markers
        self.case_markers = {
            'nominative': ['n', 'ni'],
            'genitive': ['aa', 'caa'],
            'dative': ['f', 'tti'],
            'locative': ['tti', 'rra', 'ssa'],
            'ablative': ['raa', 'raa'],
        }
        
        # Common grammar patterns
        self.sov_patterns = {
            'subject_object_verb': True,  # Afaan Oromo is SOV
        }

    def check_grammar(self, sentence: str) -> List[Dict]:
        """
        Comprehensive grammar checking
        Returns list of issues found
        """
        issues = []
        
        # Run all grammar checks
        issues.extend(self._check_capitalization(sentence))
        issues.extend(self._check_sentence_ending(sentence))
        issues.extend(self._check_subject_verb_agreement(sentence))
        issues.extend(self._check_tense_consistency(sentence))
        issues.extend(self._check_word_order(sentence))
        issues.extend(self._check_question_formation(sentence))
        issues.extend(self._check_preposition_usage(sentence))
        issues.extend(self._check_conjunction_usage(sentence))
        issues.extend(self._check_repetitive_words(sentence))
        issues.extend(self._check_vowel_length(sentence))
        issues.extend(self._check_common_patterns(sentence))
        issues.extend(self._check_case_marking(sentence))
        
        return issues

    def _check_capitalization(self, sentence: str) -> List[Dict]:
        """Check if sentence starts with capital letter"""
        issues = []
        words = sentence.split()
        
        if not words:
            return issues
        
        if words[0] and words[0][0].islower():
            issues.append({
                'type': 'capitalization',
                'severity': 'warning',
                'message': 'Jechi jalqabaa qubbaa guddaan jalqabuu qaba (First word should be capitalized)',
                'suggestion': words[0].capitalize(),
                'position': 0,
                'word': words[0]
            })
        
        return issues

    def _check_sentence_ending(self, sentence: str) -> List[Dict]:
        """Check if sentence ends with proper punctuation"""
        issues = []
        sentence = sentence.strip()
        
        if not sentence:
            return issues
        
        # Check if ends with proper punctuation
        if not sentence.endswith(('.', '!', '?', ':', ';')):
            # Check if it's a question
            words = sentence.split()
            is_question = any(w.lower() in self.question_words for w in words)
            
            if is_question:
                issues.append({
                    'type': 'missing_punctuation',
                    'severity': 'error',
                    'message': 'Gaaffiin qubbaa gaaffii (?) dhaan xumuramuu qaba (Question should end with ?)',
                    'suggestion': '?',
                    'position': len(words) - 1,
                    'word': words[-1] if words else ''
                })
            else:
                issues.append({
                    'type': 'missing_punctuation',
                    'severity': 'warning',
                    'message': 'Jumlaan tuqaa (.) dhaan xumuramuu qaba (Sentence should end with period)',
                    'suggestion': '.',
                    'position': len(words) - 1,
                    'word': words[-1] if words else ''
                })
        
        return issues

    def _check_subject_verb_agreement(self, sentence: str) -> List[Dict]:
        """Check subject-verb agreement"""
        issues = []
        words = sentence.split()
        
        if len(words) < 2:
            return issues
        
        # Find subject pronoun
        subject = None
        subject_pos = None
        for i, word in enumerate(words[:3]):  # Check first 3 words
            clean_word = re.sub(r'[^\w\']', '', word.lower())
            if clean_word in self.pronouns:
                subject = clean_word
                subject_pos = i
                break
        
        if not subject:
            return issues
        
        # Find verb (usually at the end in SOV)
        verb = None
        verb_pos = None
        for i in range(len(words) - 1, max(0, subject_pos), -1):
            clean_word = re.sub(r'[^\w\']', '', words[i].lower())
            if len(clean_word) > 2:
                verb = clean_word
                verb_pos = i
                break
        
        if not verb:
            return issues
        
        # Check if verb ending matches subject
        valid_endings = self.verb_endings.get(subject, [])
        if valid_endings:
            has_valid_ending = any(verb.endswith(ending) for ending in valid_endings)
            
            if not has_valid_ending and len(verb) > 3:
                issues.append({
                    'type': 'subject_verb_agreement',
                    'severity': 'error',
                    'message': f'Walii galtee mataa fi gochaa sirrii miti ({subject} → {verb})',
                    'suggestion': f'Use verb ending that matches {subject}',
                    'position': verb_pos,
                    'word': verb,
                    'details': {
                        'subject': subject,
                        'verb': verb,
                        'expected_endings': valid_endings
                    }
                })
        
        return issues

    def _check_tense_consistency(self, sentence: str) -> List[Dict]:
        """Check tense consistency in sentence"""
        issues = []
        words = sentence.split()
        
        if len(words) < 3:
            return issues
        
        # Identify tense markers in verbs
        tenses_found = []
        
        for i, word in enumerate(words):
            clean_word = re.sub(r'[^\w\']', '', word.lower())
            
            # Check if word is a verb
            for tense, markers in self.tense_markers.items():
                if any(clean_word.endswith(marker) for marker in markers):
                    tenses_found.append({
                        'word': clean_word,
                        'tense': tense,
                        'position': i
                    })
                    break
        
        # Check for mixed tenses
        if len(tenses_found) > 1:
            unique_tenses = set(t['tense'] for t in tenses_found)
            if len(unique_tenses) > 1:
                issues.append({
                    'type': 'tense_inconsistency',
                    'severity': 'warning',
                    'message': 'Yeroon walii galtee hin qabu (Inconsistent tense usage)',
                    'suggestion': f'Found tenses: {", ".join(unique_tenses)}',
                    'position': tenses_found[-1]['position'],
                    'word': tenses_found[-1]['word'],
                    'details': {
                        'tenses': tenses_found
                    }
                })
        
        return issues

    def _check_word_order(self, sentence: str) -> List[Dict]:
        """Check SOV (Subject-Object-Verb) word order"""
        issues = []
        words = sentence.split()
        
        if len(words) < 3:
            return issues
        
        # Find verb position (should be at the end)
        verb_positions = []
        for i, word in enumerate(words):
            clean_word = re.sub(r'[^\w\']', '', word.lower())
            # Check if it's likely a verb (ends with common verb endings)
            for endings in self.verb_endings.values():
                if any(clean_word.endswith(end) for end in endings):
                    verb_positions.append(i)
                    break
        
        # If verb is not at the end, warn
        if verb_positions and verb_positions[-1] < len(words) - 2:
            # Check if there are significant words after the verb
            remaining_words = words[verb_positions[-1] + 1:]
            meaningful_words = [w for w in remaining_words if len(re.sub(r'[^\w\']', '', w)) > 2]
            
            if meaningful_words:
                issues.append({
                    'type': 'word_order',
                    'severity': 'warning',
                    'message': 'Afaan Oromoo SOV (Mataa-Maamila-Gochaa) fayyadamuu qaba (Afaan Oromo uses SOV order)',
                    'suggestion': 'Move verb to the end of sentence',
                    'position': verb_positions[-1],
                    'word': words[verb_positions[-1]]
                })
        
        return issues

    def _check_question_formation(self, sentence: str) -> List[Dict]:
        """Check proper question formation"""
        issues = []
        words = sentence.split()
        
        if not words:
            return issues
        
        # Check if question word is used
        has_question_word = False
        question_word_pos = None
        
        for i, word in enumerate(words):
            if word.lower() in self.question_words:
                has_question_word = True
                question_word_pos = i
                break
        
        # If question word found, check for question mark
        if has_question_word and not sentence.rstrip().endswith('?'):
            issues.append({
                'type': 'question_mark_missing',
                'severity': 'error',
                'message': f'Gaaffii keessatti "{words[question_word_pos]}" jechi gaaffii akka jiru agarsiisa, "?" fayyadamuu qaba',
                'suggestion': '?',
                'position': len(words) - 1,
                'word': words[-1]
            })
        
        # Check if question word is in valid position (usually early in sentence)
        if has_question_word and question_word_pos > 2:
            issues.append({
                'type': 'question_word_position',
                'severity': 'info',
                'message': f'Jechi gaaffii "{words[question_word_pos]}" jalqaba jumlaa keessatti baay\'ee gaarii dha',
                'suggestion': f'Move "{words[question_word_pos]}" closer to beginning',
                'position': question_word_pos,
                'word': words[question_word_pos]
            })
        
        return issues

    def _check_preposition_usage(self, sentence: str) -> List[Dict]:
        """Check preposition usage"""
        issues = []
        words = sentence.split()
        
        for i, word in enumerate(words):
            clean_word = re.sub(r'[^\w\']', '', word.lower())
            
            if clean_word in self.prepositions:
                # Check if preposition is followed by appropriate word
                if i + 1 >= len(words):
                    issues.append({
                        'type': 'incomplete_preposition',
                        'severity': 'error',
                        'message': f'Jechi "{clean_word}" maamila hordofuu qaba',
                        'suggestion': 'Add noun after preposition',
                        'position': i,
                        'word': word
                    })
        
        return issues

    def _check_conjunction_usage(self, sentence: str) -> List[Dict]:
        """Check conjunction usage"""
        issues = []
        words = sentence.split()
        
        for i, word in enumerate(words):
            clean_word = re.sub(r'[^\w\']', '', word.lower())
            
            if clean_word in self.conjunctions:
                # Conjunction should not be first or last word
                if i == 0:
                    issues.append({
                        'type': 'conjunction_position',
                        'severity': 'warning',
                        'message': f'Jechi walqunnamsiisuu "{clean_word}" jalqaba jumlaa keessatti hin ta\'u',
                        'suggestion': 'Remove or reposition conjunction',
                        'position': i,
                        'word': word
                    })
                elif i == len(words) - 1:
                    issues.append({
                        'type': 'conjunction_position',
                        'severity': 'error',
                        'message': f'Jechi walqunnamsiisuu "{clean_word}" xumuruma jumlaa keessatti hin ta\'u',
                        'suggestion': 'Add element after conjunction',
                        'position': i,
                        'word': word
                    })
                else:
                    # Check if there are elements on both sides
                    has_before = i > 0 and len(re.sub(r'[^\w\']', '', words[i-1])) > 1
                    has_after = i < len(words) - 1 and len(re.sub(r'[^\w\']', '', words[i+1])) > 1
                    
                    if not has_before or not has_after:
                        issues.append({
                            'type': 'conjunction_usage',
                            'severity': 'warning',
                            'message': f'Jechi "{clean_word}" wantoota lama gidduutti ta\'uu qaba',
                            'suggestion': 'Ensure conjunction connects two elements',
                            'position': i,
                            'word': word
                        })
        
        return issues

    def _check_repetitive_words(self, sentence: str) -> List[Dict]:
        """Check for repetitive words"""
        issues = []
        words = sentence.split()
        
        for i in range(len(words) - 1):
            w1 = re.sub(r'[^\w\']', '', words[i].lower())
            w2 = re.sub(r'[^\w\']', '', words[i+1].lower())
            
            if w1 == w2 and len(w1) > 2:
                issues.append({
                    'type': 'repetitive_word',
                    'severity': 'warning',
                    'message': f'Jechi "{words[i]}" irra deddeebi\'ee dhufe',
                    'suggestion': words[i],
                    'position': i,
                    'word': words[i]
                })
        
        return issues

    def _check_vowel_length(self, sentence: str) -> List[Dict]:
        """Check for excessive vowel length"""
        issues = []
        words = sentence.split()
        
        for i, word in enumerate(words):
            clean = re.sub(r'[^a-z]', '', word.lower())
            if re.search(r'([aeiou])\1{2,}', clean):  # 3+ same vowels
                issues.append({
                    'type': 'excessive_vowel',
                    'severity': 'error',
                    'message': f'Vowwwel "{word}" keessatti baay\'ee dheerataa dha',
                    'suggestion': re.sub(r'([aeiou])\1+', r'\1\1', clean),
                    'position': i,
                    'word': word
                })
        
        return issues

    def _check_common_patterns(self, sentence: str) -> List[Dict]:
        """Check common Afaan Oromo grammar patterns"""
        issues = []
        words = sentence.split()
        
        if len(words) < 2:
            return issues
        
        # Check for common phrase patterns
        # Example: "gara ... deeme" (went to ...)
        for i, word in enumerate(words):
            clean_word = re.sub(r'[^\w\']', '', word.lower())
            
            if clean_word == 'gara' and i + 1 < len(words):
                # Check if followed by a destination and then a movement verb
                if i + 2 < len(words):
                    next_word = re.sub(r'[^\w\']', '', words[i+2].lower())
                    movement_verbs = ['deeme', 'dhufe', 'deema', 'dhufa', 'deemee', 'dhufee']
                    
                    if next_word not in movement_verbs:
                        # Check if there's a movement verb later
                        has_movement = any(
                            re.sub(r'[^\w\']', '', w.lower()) in movement_verbs
                            for w in words[i+1:]
                        )
                        
                        if not has_movement:
                            issues.append({
                                'type': 'missing_verb',
                                'severity': 'info',
                                'message': f'"gara" booda gocha sochii barbaachisa (Movement verb needed after "gara")',
                                'suggestion': 'Add movement verb (deeme/dhufe/etc.)',
                                'position': i,
                                'word': word
                            })
        
        return issues

    def _check_case_marking(self, sentence: str) -> List[Dict]:
        """Check case marking (basic)"""
        issues = []
        words = sentence.split()
        
        # This is a simplified check - full case marking requires deep linguistic analysis
        # For now, check common case marking errors
        
        for i, word in enumerate(words):
            clean_word = re.sub(r'[^\w\']', '', word.lower())
            
            # Check for common case marker misuse
            if clean_word.endswith('tti') and i > 0:
                # Locative case - should follow a noun
                prev_word = re.sub(r'[^\w\']', '', words[i-1].lower())
                if len(prev_word) < 2:
                    issues.append({
                        'type': 'case_marking',
                        'severity': 'info',
                        'message': f'Case marker "-tti" maamila hordofuu qaba',
                        'suggestion': 'Ensure "-tti" follows a noun',
                        'position': i,
                        'word': word
                    })
        
        return issues

    def get_grammar_summary(self, issues: List[Dict]) -> Dict:
        """Get summary of grammar issues by severity"""
        summary = {
            'total_issues': len(issues),
            'errors': len([i for i in issues if i['severity'] == 'error']),
            'warnings': len([i for i in issues if i['severity'] == 'warning']),
            'info': len([i for i in issues if i['severity'] == 'info']),
            'issues_by_type': {}
        }
        
        for issue in issues:
            issue_type = issue['type']
            if issue_type not in summary['issues_by_type']:
                summary['issues_by_type'][issue_type] = 0
            summary['issues_by_type'][issue_type] += 1
        
        return summary
