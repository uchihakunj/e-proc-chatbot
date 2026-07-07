"""
Krutidev → Unicode Devanagari converter.

Krutidev is a legacy Hindi font that stores characters using ASCII codepoints
with a proprietary mapping. PDFs that used Krutidev/DevLys/Chanakya fonts
produce garbled text when extracted by tools like PyMuPDF because the raw
codepoints are treated as ASCII.

This module converts that garbled text back to proper Unicode Devanagari.
"""

import re

# ---------------------------------------------------------------------------
# Krutidev → Unicode character map
# Each key is the ASCII character as it appears in Krutidev-encoded text.
# Values are the Unicode Devanagari equivalent.
# ---------------------------------------------------------------------------
_KRUTI_TO_UNI_CHAR: dict[str, str] = {
    # Vowels / matras
    'v': 'अ', 'vk': 'आ', 'b': 'इ', 'Z': 'र्', 'bZ': 'ई',
    'M~': 'ड़', '<+': 'ढ़', '+': 'ू',
    'q': 'ु', 'w': 'ू', 'k': 'ा', 'f': 'ि', 'h': 'ी',
    '^': 'ॉ', 'ks': 'ो', 'ksa': 'ों', 'ks a': 'ों',
    'S': 'ै', 'S a': 'ैं', ';s': 'ये',
    'W': 'ू', 'V': 'ट', 'B': 'ठ', 'M': 'ड', '<': 'ढ',
    'K': 'ज्ञ', 'N': 'छ', '}': 'द्व',
    # Consonants
    'D': 'क', 'Dk': 'का', 'Dh': 'की', 'Dq': 'कु', 'Dw': 'कू',
    'Dks': 'को', 'Ds': 'के',
    '[k': 'ख', 'x': 'ग', 'X': 'ग्', 'Xk': 'गा',
    '?k': 'घ', '^k': 'ङ',
    'p': 'च', 'pk': 'चा', 'ph': 'ची', 'Pk': 'चा',
    'N+': 'छ', 't': 'ज', 'tk': 'जा', 'th': 'जी',
    '¶k': 'फा', '¶': 'फ',
    'Q': 'फ', 'Qk': 'फा',
    'T': 'ज्', '>': 'झ',
    'V~': 'ट्', 'Vk': 'टा',
    '<~': 'ढ्',
    'P': 'च्', ';': 'य', 'j': 'र', 'jk': 'रा', 'jh': 'री',
    'y': 'ल', 'yk': 'ला', 'yh': 'ली',
    'o': 'व', 'ok': 'वा', 'oh': 'वी',
    '\"k': 'श', '\"kk': 'शा', 'k\"k': 'ाश',
    '\"k': 'श', 'k\"k': 'ाश',
    'l': 'स', 'lk': 'सा', 'lh': 'सी',
    'g': 'ह', 'gk': 'हा', 'gh': 'ही',
    'n': 'द', 'nk': 'दा', 'nh': 'दी',
    'Ë': 'ध', 'Ëk': 'धा',
    'Q': 'फ',
    'R': 'त्', 'r': 'त', 'rk': 'ता', 'rh': 'ती',
    'Fk': 'था', 'F': 'थ',
    'H': 'भ', 'Hk': 'भा', 'Hkh': 'भी',
    'e': 'म', 'ek': 'मा', 'eh': 'मी',
    'u': 'न', 'uk': 'ना', 'uh': 'नी',
    'U': 'न्',
    'i': 'प', 'ik': 'पा', 'ih': 'पी',
    'I': 'प्',
    'c': 'ब', 'ck': 'बा', 'ch': 'बी',
    'C': 'ब्',
    'dq': 'कु', 'dw': 'कू', 'ds': 'के', 'dks': 'को', 'dk': 'का',
    'dh': 'की', 'd': 'क',
    ';k': 'या', ';h': 'यी', ';s': 'ये',
    'jh': 'री', 'jk': 'रा', 'js': 'रे',
    'oh': 'वी', 'ok': 'वा', 'os': 'वे',
    'lq': 'सु', 'lw': 'सू', 'ls': 'से',
    'gq': 'हु', 'gw': 'हू', 'gs': 'हे',
    'nq': 'दु', 'nw': 'दू', 'ns': 'दे',
    'rq': 'तु', 'rw': 'तू', 'rs': 'ते',
    'eq': 'मु', 'ew': 'मू', 'es': 'मे',
    'uq': 'नु', 'uw': 'नू', 'us': 'ने',
    'iq': 'पु', 'iw': 'पू', 'is': 'पे',
    'cq': 'बु', 'cw': 'बू', 'cs': 'बे',
    'yq': 'लु', 'yw': 'लू', 'ys': 'ले',
    'xq': 'गु', 'xw': 'गू', 'xs': 'गे', 'xk': 'गा', 'xh': 'गी',
    'iq': 'पु',
    # Half forms / conjuncts
    'D[k': 'क्ख', 'Ddk': 'क्का', 'ddh': 'क्की',
    'Ë': 'ध',
    # Punctuation / special
    'A': '।', '&': '-', '¼': '(', '½': ')', ',': ',',
    '"': '"', '"': '"',
    '0': '०', '1': '१', '2': '२', '3': '३', '4': '४',
    '5': '५', '6': '६', '7': '७', '8': '८', '9': '९',
    # Anusvara, chandrabindu, visarga
    'a': 'ं', 'aa': 'ंं', 'W': 'ूँ', ':': 'ः',
    # Common digraphs
    'NRRkhlx<+': 'छत्तीसगढ़',
    'jkT;': 'राज्य',
    'cht': 'बीज',
    'Ñf"k': 'कृषि',
    'fyfeVsM': 'लिमिटेड',
    'LVsV': 'स्टेट',
    'b.MfLVª;y': 'इंडस्ट्रियल',
    'MsOgyiesaV': 'डेवलपमेंट',
    'dkiksZjs\'ku': 'कॉर्पोरेशन',
    'okj.kxj': 'वारंगल',
    'Hk.Mkj': 'भंडार',
}

# ---------------------------------------------------------------------------
# Full Krutidev→Unicode lookup table (standard mapping used by most converters)
# Source: widely documented public domain Krutidev→Unicode tables
# ---------------------------------------------------------------------------
_KD_TABLE: list[tuple[str, str]] = [
    # Multi-char sequences first (order matters — longest match wins)
    ("NRRkhlx<+", "छत्तीसगढ़"),
    ("jkT;", "राज्य"),
    ("iz'kklu", "प्रशासन"),
    ("foRr", "वित्त"),
    ("iz'u", "प्रश्न"),
    ("<+", "ढ़"),
    ("M+", "ड़"),
    ("M~;", "ड्य"),
    ("V~;", "ट्य"),
    ("Vî", "टि"),
    ("ï", "फ़"),
    ("ð", "य़"),
    # Vowel signs (matras) — must come before consonant singles
    ("vksa", "ओं"),
    ("vks", "ओ"),
    ("vkS", "औ"),
    ("vk", "आ"),
    ("b±", "इं"),
    ("bZ", "ई"),
    ("b", "इ"),
    ("m|", "उद्"),
    ("m", "उ"),
    ("Å", "ऊ"),
    (";s", "ये"),
    ("yw", "लू"),
    ("ys", "ले"),
    ("yq", "लु"),
    ("yh", "ली"),
    ("yk", "ला"),
    ("ySa", "लैं"),
    ("lkFk", "साथ"),
    ("lHkh", "सभी"),
    ("lHkk", "सभा"),
    # Chandrabindu, anusvara, visarga
    ("W", "ूँ"),
    ("a", "ं"),
    (":", "ः"),
    # Conjunct consonants
    ("D[k", "क्ख"),
    ("K", "ज्ञ"),
    ("=k", "त्र"),
    ("\"kz", "श्र"),
    ("J", "श्र"),
    ("Ø", "क्र"),
    ("Ñ", "कृ"),
    ("{k", "क्ष"),
    ("ç", "प्र"),
    ("iz", "प्र"),
    ("xz", "ग्र"),
    ("nz", "द्र"),
    ("rz", "त्र"),
    ("Hz", "भ्र"),
    ("oz", "व्र"),
    ("úk", "हृ"),
    ("}k", "द्वा"),
    ("}", "द्व"),
    # Half forms (halanth)
    ("D", "क्"), ("[k", "ख"), ("x", "ग"), ("X", "ग्"),
    ("?k", "घ"), ("Pk", "च"), ("N", "छ"), ("t", "ज"),
    ("T", "ज्"), (">", "झ"), ("V", "ट"), ("B", "ठ"),
    ("M", "ड"), ("<", "ढ"), ("P", "च्"), (";", "य"),
    ("j", "र"), ("y", "ल"), ("o", "व"), ("\"k", "श"),
    ("\"", "श"), ("\"k", "श"),
    ("\"", "श"), (";k", "या"),
    ("l", "स"), ("g", "ह"), ("n", "द"), ("Ë", "ध"),
    ("Q", "फ"), ("R", "त्"), ("r", "त"), ("F", "थ"),
    ("Fk", "था"),
    ("H", "भ"), ("e", "म"), ("u", "न"), ("U", "न्"),
    ("i", "प"), ("I", "प्"), ("c", "ब"), ("C", "ब्"),
    ("d", "क"), ("¶", "फ"),
    # Matras (vowel signs)
    ("k", "ा"), ("f", "ि"), ("h", "ी"),
    ("q", "ु"), ("w", "ू"),
    ("s", "े"), ("S", "ै"),
    ("ks", "ो"), ("kS", "ौ"),
    ("^", "ॉ"),
    # Punctuation
    ("A", "।"), ("&", "-"),
    ("¼", "("), ("½", ")"),
    # Numerals (Krutidev uses Devanagari numerals)
    ("0", "०"), ("1", "१"), ("2", "२"), ("3", "३"), ("4", "४"),
    ("5", "५"), ("6", "६"), ("7", "७"), ("8", "८"), ("9", "९"),
]


def _looks_krutidev(text: str) -> bool:
    """Heuristic: return True if the text appears to be Krutidev-encoded.

    Krutidev text shows up as ASCII characters in patterns like:
      NRRkhlx<+, jkT;, cht, Ñf"k, etc.
    We check for combinations of ASCII that would never appear in normal
    English or proper Unicode text.
    """
    indicators = [
        r'[A-Za-z][+<>]',           # letter followed by < > +
        r'[a-z]{2,}[A-Z][a-z]',     # mixed case like "jkT;"
        r'NRRk',                      # छत्तीसगढ़ in Krutidev
        r'[a-z]=[a-z]',              # = in unexpected positions
        r'\bfk\b|\bDk\b|\bdk\b',     # common Krutidev syllables
        r'[A-Z][a-z]{1,2}[A-Z]',    # e.g. "Ñf" or "Dks"
        r'jkT;|cht|Ñf"|fyfeVsM',    # very specific Krutidev words
    ]
    for pattern in indicators:
        if re.search(pattern, text):
            return True
    return False


def krutidev_to_unicode(text: str) -> str:
    """Convert Krutidev-encoded text to Unicode Devanagari.

    If the text does not appear to be Krutidev-encoded, it is returned as-is.
    """
    if not _looks_krutidev(text):
        return text

    result = text
    for kruti, uni in _KD_TABLE:
        result = result.replace(kruti, uni)
    return result


def fix_text(text: str) -> str:
    """Apply Krutidev→Unicode conversion to a block of text.

    Works line-by-line so that lines without Krutidev pass through unchanged.
    """
    lines = text.split('\n')
    fixed = []
    for line in lines:
        fixed.append(krutidev_to_unicode(line))
    return '\n'.join(fixed)
