"""
kruti_to_unicode.py
===================
Convert Kruti Dev 010 (legacy Hindi font, stored as ASCII) text to proper
Unicode Devanagari. Government Hindi PDFs (GFR, Vigilance Manual, Store Purchase
Rules, etc.) are often typed in Kruti Dev — extracting their text layer yields
ASCII gibberish like "lkekU; foŸkh; fu;ekoyh" which must be converted to
"सामान्य वित्तीय नियमावली" before it can be embedded / searched.

Algorithm (the widely-used Kruti Dev -> Unicode approach):
  1. Apply a long ordered list of substring replacements (longest first).
  2. Move the short-i matra 'ि' to AFTER its consonant (it precedes in Kruti Dev).
  3. Re-order the reph 'र्' so it attaches after the following consonant cluster.
"""

import re

# Ordered (kruti, unicode) pairs. Longer/compound sequences MUST come first.
_MAP = [
    ("¢", "॰"),
    ("ñ", "171"), ("ò", "172"), ("ó", "173"), ("ô", "174"), ("ö", "176"),
    ("÷", "177"), ("ø", "178"), ("ù", "179"), ("ú", "180"),
    ("(", "("), (")", ")"),
    ("Q+", "फ़"), ("dY", "क्ल"), ("DY", "क्ल"),
    ("'k", "श"), ("\"k", "ष"), ("'", "ष"), ('"', "ष"),
    ("d", "क"), ("Q", "फ"), ("कW", "काँ"),
    ("ोa", "ौं"), ("ेa", "ैं"),
    ("ÅN", "ँ"), ("Å", "ॅ"),
    ("é", "ृ"), ("è", "ध"),
    ("ध;", "ध्य"),
    ("[k", "ख"), ("[+k", "ख़"), ("[", "ख"),
    ("DkW", "काँ"),
    ("x", "ग"), ("X", "ग्"), ("Xk", "ग"), ("?k", "घ"), ("³", "ङ"),
    ("pkS", "चौ"), ("p", "च"), ("P", "च्"), ("Pk", "च"),
    ("N", "छ"), ("t", "ज"), ("T", "ज्"), ("Tk", "ज"), (">", "झ"), ("÷", "झ"),
    ("÷k", "झ"), ("¥", "ट्ट"), ("ê", "ट्ठ"),
    ("V", "ट"), ("B", "ठ"), ("M+", "ड़"), ("<+", "ढ़"), ("M", "ड"), ("<", "ढ"),
    (".k", "ण"), ("M", "ड"),
    ("r", "त"), ("R", "त्"), ("Rk", "त"), ("Fk", "थ"), ("F", "थ्"),
    ("n", "द"), ("/k", "ध"), ("(k", "ध"), ("/", "ध्"), ("u", "न"), ("U", "न्"), ("Uk", "न"),
    ("Ik", "प"), ("I", "प्"), ("i", "प"), ("Q", "फ"), ("c", "ब"), ("C", "ब्"), ("Ck", "ब"),
    ("Hk", "भ"), ("H", "भ्"), ("e", "म"), ("E", "म्"), ("Ek", "म"),
    (";", "य"), ("¸", "य्"), ("j", "र"), ("y", "ल"), ("Y", "ल्"), ("Yk", "ल"),
    ("G", "ळ"), ("o", "व"), ("O", "व्"), ("Ok", "व"),
    ("'k", "श"), ("'", "श"), ("\"k", "ष"), ("\"", "ष"),
    ("l", "स"), ("L", "स्"), ("Lk", "स"), ("g", "ह"),
    ("{k", "क्ष"), ("{", "क्ष"), ("=", "त्र"), ("«", "त्र"), ("K", "ज्ञ"), ("K", "ज्ञ"),
    ("J", "श्र"), ("J", "श्र"),
    # vowels (independent)
    ("v", "अ"), ("vk", "आ"), ("b", "इ"), ("bZ", "ई"), ("Á", "ई"),
    ("m", "उ"), ("Q+", "ऊ"), ("Å", "ऊ"), ("_", "ऋ"),
    (",", "ए"), (",s", "ऐ"), ("vks", "ओ"), ("vkS", "औ"),
    ("Å¡", "ऊँ"),
    # matras
    ("k", "ा"), ("f", "ि"), ("h", "ी"), ("q", "ु"), ("w", "ू"),
    ("`", "ृ"), ("s", "े"), ("S", "ै"), ("ks", "ो"), ("kS", "ौ"),
    ("a", "ं"), ("¡", "ँ"), ("%", "ः"), ("•", "ं"),
    ("•", "॰"), ("@", "/"), ("‘", "‘"), ("’", "’"), ("“", "“"), ("”", "”"),
    ("&", "-"), ("&", "-"), ("·", "ऽ"), ("É", "द्द"),
    ("Ù", "रु"), ("Úk", "रू"), ("Ú", "रू"),
    ("™", "ट्र"), ("nz", "द्र"),
    ("í", "द्द"), ("Ì", "ट्ठ"), ("Î", "ड्ड"),
    ("ì", "क्र"),
    # digits (Kruti often keeps ASCII digits, but map the Devanagari-mapped ones)
    ("¼", "("), ("½", ")"), ("ƒ", "३"),
    ("”", '"'),
]

# Extra ligatures / conjuncts seen in govt Kruti Dev docs.
_MAP += [
    ("Ÿ", "त्त"), ("ŸQ", "त्त"), ("Ø", "क्र"), ("ø", "क्र"),
    ("Œ", "त्त"), ("œ", "क्क"), ("Ý", "ट्ट"), ("Þ", "ट्ठ"),
    ("ç", "प्र"), ("Ç", "प्र"), ("æ", "द्व"), ("ð", "ड्ढ"),
    ("èk", "ध"),   # dha ligature absorbs following 'k'  (vfèkd -> अधिक)
    ("Ï", "ट्ट"), ("Ð", "ट्ठ"), ("Ñ", "ड्ड"), ("Ò", "ड्ढ"),
    ("Ó", "ङ्क"), ("Ô", "ङ्ग"), ("Õ", "श्च"), ("Ö", "स्त"),
    ("Ø", "क्र"), ("Ù", "रु"), ("Úk", "रू"), ("Ú", "रू"),
    ("¶", "ष्ट"), ("Ø", "क्र"), ("ª", "ार"),
    ("Ÿk", "त्त"), ("Ÿ", "त्त"),   # त्त ligature (absorbs following 'k')
    ("z", "्र"),                    # ra-phala (lower 'z')  e.g. iz -> प्र
    ("A", "।"),                     # danda / purna viram
    ("D", "क्"), ("|", "द्य"), ("}", "द्व"), ("~", "्"),
    ("‘", "‘"), ("’", "’"),
]

# halant
_HAL = "्"

# Apply longest source-strings first so compounds (vkS->औ) win over singles (v->अ).
_SORTED = sorted([kv for kv in _MAP if kv[0]], key=lambda kv: -len(kv[0]))


def _basic_replace(text: str) -> str:
    for k, v in _SORTED:
        text = text.replace(k, v)
    return text


def kruti_to_unicode(text: str) -> str:
    if not text:
        return text

    s = text

    # 1. Apply the base substitution table (longest match first).
    s = _basic_replace(s)

    cons = "कखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसहळक्ष"

    # 2. Reph: Kruti types the reph 'Z' AFTER the consonant it rides on; move
    #    "र्" to before that consonant. Scoped to the 'Z' marker only, so it does
    #    NOT corrupt legitimate त्र / प्र / क्र conjuncts.
    s = re.sub("([" + cons + "])Z", r"र्\1", s)
    s = s.replace("Z", "र्")  # any leftover lone reph

    # 3. Move the short-i matra 'ि' to AFTER its consonant cluster
    #    (Kruti types the 'f' -> ि BEFORE the consonant).
    s = re.sub("ि([" + cons + "](?:" + _HAL + "[" + cons + "])*)", r"\1ि", s)

    return s


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    samples = [
        "lkekU; foŸkh; fu;ekoyh 2017",
        "Hkkjr ljdkj",
        "foŸk ea=ky;] O;; foHkkx",
        "vuq'kklfud dk;Zokgh vkSj fuyacu",
        "lrdZrk fu;ekoyh",
    ]
    for s in samples:
        print(repr(s), "->", kruti_to_unicode(s))
