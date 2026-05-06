import re
import unicodedata
from dataclasses import dataclass, asdict
from typing import List, Tuple, Dict

try:
    from langdetect import detect, LangDetectException
except Exception:  # fallback when dependency is missing
    detect = None
    LangDetectException = Exception


@dataclass
class PipelineConfig:
    remove_artifacts: bool = True
    normalize_unicode: bool = True
    normalize_spaces: bool = True
    fix_line_breaks: bool = True
    rebuild_paragraphs: bool = True
    remove_repeated_headers_footers: bool = True
    normalize_punctuation: bool = True
    chunk_size: int = 1800
    chunk_overlap: int = 150


def normalize_unicode_text(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def remove_artifacts(text: str) -> str:
    # Remove control characters while preserving new lines and tabs.
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)
    # Remove common OCR/PDF extraction artifacts.
    text = text.replace("�", "")
    text = re.sub(r"[□■▪●◦]{2,}", " ", text)
    # Remove isolated repeated punctuation/noise, but keep normal punctuation.
    text = re.sub(r"([_\-=*#~])\1{2,}", r"\1", text)
    return text


def normalize_spaces(text: str) -> str:
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def normalize_punctuation(text: str) -> str:
    replacements = {
        "“": '"', "”": '"', "„": '"',
        "‘": "'", "’": "'",
        "…": "...",
        "–": "-", "—": "-",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Remove spaces before punctuation and ensure one after punctuation when useful.
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"([,.;:!?])([^\s\n])", r"\1 \2", text)
    return text


def remove_repeated_headers_footers(text: str) -> str:
    lines = text.splitlines()
    if len(lines) < 8:
        return text

    normalized = [re.sub(r"\d+", "#", line.strip().lower()) for line in lines if line.strip()]
    counts: Dict[str, int] = {}
    for line in normalized:
        if 4 <= len(line) <= 120:
            counts[line] = counts.get(line, 0) + 1

    repeated = {line for line, count in counts.items() if count >= 3}
    cleaned = []
    for original in lines:
        key = re.sub(r"\d+", "#", original.strip().lower())
        if key in repeated:
            continue
        cleaned.append(original)
    return "\n".join(cleaned)


def fix_line_breaks(text: str) -> str:
    lines = text.splitlines()
    output = []
    buffer = ""

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if buffer:
                output.append(buffer.strip())
                buffer = ""
            output.append("")
            continue

        if not buffer:
            buffer = stripped
            continue

        previous_ends_sentence = bool(re.search(r"[.!?:;)]$", buffer))
        current_starts_list = bool(re.match(r"^([\-•*]|\d+[.)])\s+", stripped))
        current_starts_heading = stripped.isupper() and len(stripped) < 80

        if previous_ends_sentence or current_starts_list or current_starts_heading:
            output.append(buffer.strip())
            buffer = stripped
        else:
            # Join broken lines from PDF/OCR extraction.
            if buffer.endswith("-"):
                buffer = buffer[:-1] + stripped
            else:
                buffer += " " + stripped

    if buffer:
        output.append(buffer.strip())

    return "\n".join(output)


def rebuild_paragraphs(text: str) -> str:
    # Keep list items separated, but group normal lines into paragraphs.
    blocks = re.split(r"\n\s*\n", text)
    rebuilt = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue
        if all(re.match(r"^([\-•*]|\d+[.)])\s+", line) for line in lines):
            rebuilt.append("\n".join(lines))
        else:
            rebuilt.append(" ".join(lines))
    return "\n\n".join(rebuilt)


def clean_text(raw_text: str, config: PipelineConfig) -> Tuple[str, List[str]]:
    text = raw_text or ""
    steps = []

    if config.normalize_unicode:
        text = normalize_unicode_text(text)
        steps.append("Normalização Unicode NFKC")
    if config.remove_artifacts:
        text = remove_artifacts(text)
        steps.append("Remoção de artefactos e caracteres inválidos")
    if config.remove_repeated_headers_footers:
        text = remove_repeated_headers_footers(text)
        steps.append("Remoção de cabeçalhos/rodapés repetidos")
    if config.fix_line_breaks:
        text = fix_line_breaks(text)
        steps.append("Correção de quebras de linha incorretas")
    if config.rebuild_paragraphs:
        text = rebuild_paragraphs(text)
        steps.append("Reconstrução de parágrafos")
    if config.normalize_punctuation:
        text = normalize_punctuation(text)
        steps.append("Normalização de pontuação")
    if config.normalize_spaces:
        text = normalize_spaces(text)
        steps.append("Normalização de espaços")

    return text, steps


def detect_language(text: str) -> str:
    if not text.strip():
        return "unknown"
    if detect is None:
        return "unknown"
    try:
        return detect(text[:3000])
    except LangDetectException:
        return "unknown"


def chunk_text(text: str, chunk_size: int = 1800, overlap: int = 150) -> List[str]:
    if not text:
        return []
    paragraphs = re.split(r"\n\s*\n", text)
    chunks: List[str] = []
    current = ""

    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue

        if len(paragraph) > chunk_size:
            # Split very large paragraphs by sentence.
            sentences = re.split(r"(?<=[.!?])\s+", paragraph)
            for sentence in sentences:
                if len(current) + len(sentence) + 1 <= chunk_size:
                    current = (current + " " + sentence).strip()
                else:
                    if current:
                        chunks.append(current)
                    current = sentence
            continue

        if len(current) + len(paragraph) + 2 <= chunk_size:
            current = (current + "\n\n" + paragraph).strip()
        else:
            if current:
                chunks.append(current)
                prefix = current[-overlap:] if overlap > 0 else ""
                current = (prefix + "\n\n" + paragraph).strip() if prefix else paragraph
            else:
                current = paragraph

    if current:
        chunks.append(current)
    return chunks


def create_prompt(chunk: str, language: str = "pt") -> str:
    language_hint = "português" if language == "pt" else language
    return f"""És um assistente especializado em normalização textual.

Tarefa:
- Normaliza o texto abaixo em {language_hint}.
- Corrige erros de extração, espaços, pontuação e quebras de linha.
- Mantém o significado original.
- Não inventes informação nova.
- Devolve apenas o texto normalizado em plain text.

Texto a normalizar:
{chunk}
"""


def pipeline_summary(config: PipelineConfig, steps: List[str], language: str, chunks: List[str]) -> Dict[str, object]:
    return {
        "configuracao": asdict(config),
        "etapas_executadas": steps,
        "idioma_detetado": language,
        "numero_de_chunks": len(chunks),
        "tamanho_dos_chunks": [len(chunk) for chunk in chunks],
    }
