import re
import unicodedata
import string

from langdetect import detect
from spellchecker import SpellChecker

# Spellchecker

spell = SpellChecker(language='pt')

# Remover artefactos

def remove_artifacts(text):
    return re.sub(
        r"[^\x00-\x7FÀ-ÿ€\n\t ]+",
        "",
        text
    )

# Remover cabeçalhos / rodapés

def remove_headers_footers(text):
    lines = text.splitlines()
    repeated = {}
    cleaned_lines = []

    for line in lines:
        clean = line.strip()

        if len(clean) < 4:
            continue

        repeated[clean] = repeated.get(clean, 0) + 1

    for line in lines:
        clean = line.strip()

        if repeated.get(clean, 0) > 3:
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)

# Normalizar unicode

def normalize_unicode_text(text):
    return unicodedata.normalize("NFKC", text)

# Normalizar espaços

def normalize_spaces(text):
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()

# Corrigir linhas

def fix_line_breaks(text):
    return re.sub(
        r"(?<!\n)\n(?!\n)",
        " ",
        text
    )

# Deteção erros

def clean_word(word):
    return word.strip(
        string.punctuation + "«»“”‘’…"
    )


def detect_spelling_errors(text):
    words = text.split()
    cleaned_words = []
    original_map = {}

    for word in words:
        clean = clean_word(word)

        if not clean:
            continue

        cleaned_words.append(clean)
        original_map[clean] = word

    misspelled = spell.unknown(cleaned_words)
    errors = []

    for word in misspelled:
        suggestion = spell.correction(word)

        if suggestion is None:
            suggestion = "Sem sugestão"

        errors.append({
            "erro": original_map.get(word, word),
            "sugestao": suggestion
        })

    return errors

# Correção automática

def auto_correct_text(text):
    words = text.split()
    corrected_words = []

    for word in words:
        corrected = spell.correction(word)

        if corrected:
            corrected_words.append(corrected)
        else:
            corrected_words.append(word)

    return " ".join(corrected_words)

# Score qualidade

def calculate_quality_score(num_errors):
    score = max(
        0,
        100 - (num_errors * 5)
    )

    return score

# Chunking

def chunk_text(text, chunk_size=1200, overlap=200):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks

# Prompts

def create_prompt(chunk, language):
    return f"""

Analisa o seguinte texto em {language}.

Objetivos:
- resumir;
- identificar tópicos principais;
- melhorar clareza;
- normalizar o conteúdo.

Texto:
{chunk}

"""

# Clean text

def clean_text(text):
    steps = []

    text = remove_artifacts(text)
    steps.append("Remoção artefactos")

    text = remove_headers_footers(text)
    steps.append("Remoção cabeçalhos/rodapés")

    text = normalize_unicode_text(text)
    steps.append("Normalização Unicode")

    text = normalize_spaces(text)
    steps.append("Normalização espaços")

    text = fix_line_breaks(text)
    steps.append("Correção linhas")

    try:
        text = auto_correct_text(text)
    except:
        pass

    steps.append("Correção ortográfica")

    return text, steps

# Idioma

def detect_language(text):
    try:
        return detect(text)
    except:
        return "desconhecido"