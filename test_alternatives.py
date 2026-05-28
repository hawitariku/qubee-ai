from spell_checker_ml import MLEnhancedSpellChecker

checker = MLEnhancedSpellChecker('oromo_corpus.txt', use_ml=False)
result = checker.get_detailed_corrections('akam')

print('Main correction:', result['corrections'][0]['corrected'])
print('Alternatives (by frequency):', result['corrections'][0]['alternatives'])
print()
print('Checking frequencies:')
for alt in result['corrections'][0]['alternatives']:
    print(f'  {alt}: {checker.words_db.get(alt, 0):,}')
