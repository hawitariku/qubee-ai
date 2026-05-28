# Utility Scripts

This folder contains utility scripts for corpus management, diagnostics, and data downloads.

## Corpus Management

### `corpus_expansion.py`
Expand the Afaan Oromo corpus with additional text sources.

```bash
python scripts/corpus_expansion.py
```

### `download_bible_corpus.py`
Download Afaan Oromo Bible text for corpus expansion.

```bash
python scripts/download_bible_corpus.py
```

### `download_complete_bible.py`
Download complete Bible corpus with all books.

```bash
python scripts/download_complete_bible.py
```

### `download_wikipedia_corpus.py`
Download Afaan Oromo Wikipedia articles for corpus.

```bash
python scripts/download_wikipedia_corpus.py
```

### `download_wikipedia_expansion.py`
Expand Wikipedia corpus with additional articles.

```bash
python scripts/download_wikipedia_expansion.py
```

### `download_more_wiki.py`
Download more Wikipedia content for vocabulary expansion.

```bash
python scripts/download_more_wiki.py
```

### `download_wiki_api.py`
Download Wikipedia content using the MediaWiki API.

```bash
python scripts/download_wiki_api.py
```

### `download_professional_vocab.py`
Download professional and technical vocabulary.

```bash
python scripts/download_professional_vocab.py
```

## Diagnostics

### `diagnose_accuracy.py`
Diagnose spell checker accuracy issues and generate reports.

```bash
python scripts/diagnose_accuracy.py
```

### `quick_diagnostic.py`
Quick diagnostic check for spell checker functionality.

```bash
python scripts/quick_diagnostic.py
```

## PDF Processing

### `check_available_pdfs.py`
Check which PDF files are available for text extraction.

```bash
python scripts/check_available_pdfs.py
```

### `check_pdf_words.py`
Analyze word count and vocabulary from PDF files.

```bash
python scripts/check_pdf_words.py
```

## Notes

- All scripts should be run from the project root directory
- Some scripts may require additional dependencies (see requirements.txt)
- Corpus files will be saved to the project root directory
- Check individual script files for specific usage instructions
