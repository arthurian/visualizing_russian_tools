# -*- coding: utf-8 -*-
import string
import unicodedata
import re

# Alphabet
RUS_ALPHABET_LIST = (
    '\u0410', '\u0430', # Аа
    '\u0411', '\u0431', # Бб
    '\u0412', '\u0432', # Вв
    '\u0413', '\u0433', # Гг
    '\u0414', '\u0434', # Дд
    '\u0415', '\u0435', # Ее
    '\u0401', '\u0451', # Ёё
    '\u0416', '\u0436', # Жж
    '\u0417', '\u0437', # Зз
    '\u0418', '\u0438', # Ии
    '\u0419', '\u0439', # Йй
    '\u041A', '\u043A', # Кк
    '\u041B', '\u043B', # Лл
    '\u041C', '\u043C', # Мм
    '\u041D', '\u043D', # Нн
    '\u041E', '\u043E', # Оо
    '\u041F', '\u043F', # Пп
    '\u0420', '\u0440', # Рр
    '\u0421', '\u0441', # Сс
    '\u0422', '\u0442', # Тт
    '\u0423', '\u0443', # Уу
    '\u0424', '\u0444', # Фф
    '\u0425', '\u0445', # Хх
    '\u0426', '\u0446', # Цц
    '\u0427', '\u0447', # Чч
    '\u0428', '\u0448', # Шш
    '\u0429', '\u0449', # Щщ
    '\u042A', '\u044A', # Ъъ
    '\u042B', '\u044B', # Ыы
    '\u042C', '\u044C', # Ьь
    '\u042D', '\u044D', # Ээ
    '\u042E', '\u044E', # Юю
    '\u042F', '\u044F', # Яя
)
RUS_ALPHABET_SET = set(RUS_ALPHABET_LIST)
RUS_ALPHABET_STR = ''.join(RUS_ALPHABET_LIST)

# Hyphens and dashes
HYPHEN_CHAR = '\u002D'  # Punctuation used to join components of a word
EN_DASH_CHAR = '\u2013' # May be used interchangeably with hyphen or em-dash depending on context
EM_DASH_CHAR = '\u2014' # Punctuation used to separate words in a sentence

# Quotation marks
QUOTE_ANGLE_LEFT = '\u00AB'
QUOTE_ANGLE_RIGHT = '\u00BB'
QUOTE_RAISED_LEFT = '\u201e'
QUOTE_RAISED_RIGHT = '\u201c'

# Punctuation list
RUS_PUNCT = string.punctuation + QUOTE_ANGLE_LEFT + QUOTE_ANGLE_RIGHT + QUOTE_RAISED_LEFT + QUOTE_RAISED_RIGHT + EN_DASH_CHAR + EM_DASH_CHAR

# Diacritics
COMBINING_ACCENT_CHAR = '\u0301'   # Diacritic used to mark stress on russian words
COMBINING_DIURESIS_CHAR = '\u0308' # Diacritic used with the seventh letter of the russian alphabet (ё)
COMBINING_BREVE_CHAR = '\u0306'    # Diacritic used with the eleventh letter of the russian alphabet (й)

# Special cases where hyphenated words that should not be split up
# Word beginning with по- should also be privileged.
HYPHENATED_WORDS = (
    'всё-таки',
    'все-таки',
    'из-за',
    'из-под',
)

# Multi-word expressions
MWES = (
    'потому, что',
    ', потому что',
    'потому что',
    'несмотря на то, что',
    'несмотря на',
    'после того как',
    'после того, как',
    'до того как',
    'до того, как',
    'перед тем как',
    'перед тем, как',
    'в течение',
)

# Translators
TRANSLATOR_PUNCT_REMOVE = str.maketrans('', '', RUS_PUNCT)
TRANSLATOR_DIACRITICS_REMOVE = str.maketrans('', '', COMBINING_ACCENT_CHAR)

# Regular expressions
RE_MATCH_DIGITS_ONLY = re.compile(r'^\d+$')
RE_MATCH_WHITESPACE_ONLY = re.compile(r'^\s+$')

def tokenize(text, whitespace=True):
    """
    Returns a list of tokens.

    >>> tokenize("«Ко двору, — думает он. — Ко двору!»")
    ['«Ко', ' ', 'двору,', ' ', '—', ' ', 'думает', ' ', 'он.', ' ', '—', ' ', 'Ко', ' ', 'двору!»']
    >>> tokenize("«Ко двору, — думает он. — Ко двору!»", whitespace=False)
    ['«Ко', 'двору,', '—', 'думает', 'он.', '—', 'Ко', 'двору!»']
    >>> tokenize("В не́которых ру́сских деревня́х по э́той техноло́гии вручну́ю де́лают матрёшек и сего́дня.")
    ['В', ' ', 'не́которых', ' ', 'ру́сских', ' ', 'деревня́х', ' ', 'по', ' ', 'э́той', ' ', 'техноло́гии', ' ', 'вручну́ю', ' ', 'де́лают', ' ', 'матрёшек', ' ', 'и', ' ', 'сего́дня.']
    """
    pattern = r'(\s+)' if whitespace else r'\s+'
    tokens = re.split(pattern, normalize_hyphens(text))
    tokens = split_hyphenated(tokens)
    tokens = merge_multiwordexpr(tokens)
    return tokens

def split_hyphenated(tokens):
    new_tokens = []
    for token in tokens:
        # split hyphenated unless it's a special case like "по-" words (DB entries for those)
        if HYPHEN_CHAR in token and not token.startswith("по-") and token not in HYPHENATED_WORDS:
            for t in re.split(r'(-)', token):
                new_tokens.append(t)
        else:
            new_tokens.append(token)
    return new_tokens

def merge_multiwordexpr(tokens):
    # TODO: use trie data structure to detect and merge MWEs
    return tokens

def tag(tokens, taggers=None):
    """
    Tag tokens with additional information. 
    Optionally provide callable "taggers" that will be called on each token.
    Returns an array of tuples: [(token1, index1, offset1, ...), (token2, index2, offset2, ...)]

    >>> tag(['Ко', 'двору,'], taggers=[lambda token: token.lower(), lambda token: len(token)])
    [('Ко', 0, 0, 'ко', 2), ('двору,', 1, 2, 'двору,', 6)]
    """
    if taggers is None:
        taggers = []
    tagged = []
    offset = 0
    for idx, token in enumerate(tokens):
        tags = [tagger(token) for tagger in taggers]
        tagged.append( tuple([token, idx, offset] + tags) )
        offset += len(token)
    return tagged

def normalize_hyphens(token):
    """
    Normalizes hyphens.
    """
    return token.replace(EN_DASH_CHAR, HYPHEN_CHAR)

def unicode_decompose(token):
    """
    Decomposes the unicode string into NFKD form (e.g. separate combining accents, diacritics, etc).
    """
    return unicodedata.normalize('NFKD', token)

def unicode_compose(token):
    """
    Composes the unicode string so it is the canonical composition (eliminate combining characters).
    """
    return unicodedata.normalize('NFKC', token)

def strip_punctuation(token):
    """
    Removes punctuation from text.
    """
    return token.translate(TRANSLATOR_PUNCT_REMOVE)

def strip_diacritics(token):
    """
    Removes diacritics from text.

    >>> strip_diacritics("В не́которых ру́сских деревня́х по э́той техноло́гии вручну́ю де́лают матрёшек и сего́дня.")
    'В некоторых русских деревнях по этой технологии вручную делают матрёшек и сегодня.'
    """
    return token.translate(TRANSLATOR_DIACRITICS_REMOVE)

def canonical(token):
    """
    Returns the canonical text stripped of all punctuation and diacritics.
    This is intended to be used for doing lookups against the database.
    """
    # Strip diacritics
    token = unicode_compose(strip_diacritics(unicode_decompose(normalize_hyphens(token))))

    # Strip punctunation, handling some special cases where punctuation should be preserved
    if token.startswith("по-"):
        token = token[0:len("по-")] + strip_punctuation(token[len("по-"):])
    elif token not in HYPHENATED_WORDS:
        token = strip_punctuation(token)
    
    # Change to lowercase
    token = token.lower()

    return token


TOKEN_RUS = "RUS"
TOKEN_PUNCT = "PUNCT"
TOKEN_SPACE = "SPACE"
TOKEN_NUM = "NUM"

def tokentype(text):
    """
    Returns the type of text contained in a token:
        NUM: number
        PUNCT: punctuation
        RUS: russian
        SPACE: whitespace 

    >>> tokentype('«Ко')
    'RUS'
    >>> tokentype('—')
    'PUNCT'
    >>> tokentype("hello") is None
    True
    >>> tokentype("найти")
    'RUS'
    """
    tokentype = None
    if is_whitespace(text):
        tokentype = TOKEN_SPACE
    elif is_punctuation(text):
        tokentype = TOKEN_PUNCT
    else:
        canonical_text = canonical(text)
        if is_russian(canonical_text):
            tokentype = TOKEN_RUS
        elif is_numeric(canonical_text):
            tokentype = TOKEN_NUM
    return tokentype

def is_russian(token):
    """
    Returns true if the token contains only russian characters or punctuation, otherwise false.
    """
    return token[0] in RUS_ALPHABET_SET

def is_punctuation(token):
    return all([c in RUS_PUNCT for c in token])

def is_whitespace(token):
    return RE_MATCH_WHITESPACE_ONLY.match(token) is not None

def is_numeric(token):
    return token.isdigit()

def is_equal(text1, text2):
    return unicode_decompose(text1) == unicode_decompose(text2)
