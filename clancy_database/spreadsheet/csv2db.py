import csv
import sqlite3
import os.path
import sys
import time
import logging
import unicodedata

FILE_DIR = os.path.dirname(os.path.realpath(__file__))

CSV_FIELD_NAMES = ['UniqueId', 'Russian', 'SecondRussian', 'POS', 'POS_Subtype', 'Animacy', 'Level', 'English', 'Rank', 'Count', 'Chapter', 'AdjAdvProp', 'Collocations', 'Domain', 'DomainTags', 'Strеssеd_Russiаn', 'Transliteration', 'Prefixes', 'Roots', 'Suffixes', 'Length', 'Classes', 'Location_Type', 'Notes', 'Notes_declension', 'Notes_conjugation', 'Inflected', 'Indeclinable', 'Stem', 'Hard_Soft', 'Word_Type', 'Stress_Pattern_SEMU', 'Inflected_Forms', 'Inflected_Stressed_Forms', 'Constructicon', 'Reverse_inflection', 'myKnown', 'myNew', 'myTarget', 'Drawing_Image', 'Photo_Image', 'Related_Words', 'Synonyms', 'Antonyms', 'Hyponyms', 'Co.Hyponyms', 'Hyperonyms', 'Example1', 'Example2', 'Example3', 'Gender_Counterparts', 'NOMsg_stressed', 'ACCsg_stressed', 'GENsg_stressed', 'LOCsg_stressed', 'DATsg_stressed', 'INSTsg_stressed', 'INSTaltsg_stressed', 'NOMpl_stressed', 'ACCpl_stressed', 'GENpl_stressed', 'LOCpl_stressed', 'DATpl_stressed', 'INSTpl_stressed', 'GEN2sg_stressed', 'LOC2sg_stressed', 'VOCsg_stressed', 'GEN3sg_stressed', 'Gender', 'Details', 'Declension', 'NOMsg', 'ACCsg', 'GENsg', 'LOCsg', 'DATsg', 'INSTsg', 'INSTaltsg', 'NOMpl', 'ACCpl', 'GENpl', 'LOCpl', 'DATpl', 'INSTpl', 'GEN2sg', 'LOC2sg', 'VOCsg', 'GEN3sg', 'Freq_NOMsg', 'Freq_ACCsg', 'Freq_GENsg', 'Freq_LOCsg', 'Freq_DATsg', 'Freq_INSTsg', 'Freq_INSTaltsg', 'Freq_NOMpl', 'Freq_ACCpl', 'Freq_GENpl', 'Freq_LOCpl', 'Freq_DATpl', 'Freq_INSTpl', 'Freq_GEN2sg', 'Freq_LOC2sg', 'Freq_VOCsg', 'Freq_GEN3sg', 'Infinitive_stressed', 'sg1_stressed', 'sg2_stressed', 'sg3_stressed', 'pl1_stressed', 'pl2_stressed', 'pl3_stressed', 'Mpast_stressed', 'Fpast_stressed', 'Npast_stressed', 'Ppast_stressed', 'Imper_sg_stressed', 'Imper_pl_stressed', 'future_stressed', 'PrAP_stressed', 'PrAP_forms_stressed', 'PAP_stressed', 'PAP_forms_stressed', 'PrPP_stressed', 'PrPP_forms_stressed', 'PPP_stressed', 'PPP_forms_stressed', 'VbAdv1_stressed', 'VbAdv2_stressed', 'Aspect', 'Transitivity', 'Impersonal', 'Reflexive', 'Verb_Details', 'Aspectual_Grouping', 'Aspectual_Counterpart', 'Infinitive', 'sg1', 'sg2', 'sg3', 'pl1', 'pl2', 'pl3', 'Mpast', 'Fpast', 'Npast', 'Ppast', 'Imper_sg', 'Imper_pl', 'future', 'PrAP', 'PrAP_forms', 'PAP', 'PAP_forms', 'PrPP', 'PrPP_forms', 'PPP', 'PPP_forms', 'VbAdv1', 'VbAdv2', 'Freq_Infinitive', 'Freq_sg1', 'Freq_sg2', 'Freq_sg3', 'Freq_pl1', 'Freq_pl2', 'Freq_pl3', 'Freq_Mpast', 'Freq_Fpast', 'Freq_Npast', 'Freq_Ppast', 'Freq_Imper_sg', 'Freq_Imper_pl', 'Freq_PrAP', 'Freq_PAP', 'Freq_PrPP', 'Freq_PPP', 'Freq_VbAdv1', 'Freq_VbAdv2', 'Lemma_Total', 'Forms_Total', 'Prop_Infinitive', 'Prop_sg1', 'Prop_sg2', 'Prop_sg3', 'Prop_pl1', 'Prop_pl2', 'Prop_pl3', 'Prop_Mpast', 'Prop_Fpast', 'Prop_Npast', 'Prop_Ppast', 'Prop_Imper_sg', 'Prop_Imper_pl', 'Prop_PrAP', 'Prop_PAP', 'Prop_PrPP', 'Prop_PPP', 'Prop_VbAdv1', 'Prop_VbAdv2', 'Prop_Check', 'mNOMsg_stressed', 'mACCsgAN_stressed', 'mACCsgIN_stressed', 'mGENsg_stressed', 'mLOCsg_stressed', 'mDATsg_stressed', 'mINSTsg_stressed', 'nNOMsg_stressed', 'nACCsg_stressed', 'nGENsg_stressed', 'nLOCsg_stressed', 'nDATsg_stressed', 'nINSTsg_stressed', 'fNOMsg_stressed', 'fACCsg_stressed', 'fGENsg_stressed', 'fLOCsg_stressed', 'fDATsg_stressed', 'fINSTsg_stressed', 'fINSTaltsg_stressed', 'plNOMpl_stressed', 'plACCplAN_stressed', 'plACCplIN_stressed', 'plGENpl_stressed', 'plLOCpl_stressed', 'plDATpl_stressed', 'plINSTpl_stressed', 'mshort_stressed', 'nshort_stressed', 'fshort_stressed', 'plshort_stressed', 'comparative_stressed', 'extracomparatives_stressed', 'stem', 'ending', 'mNOMsg', 'mACCsgAN', 'mACCsgIN', 'mGENsg', 'mLOCsg', 'mDATsg', 'mINSTsg', 'nNOMsg', 'nACCsg', 'nGENsg', 'nLOCsg', 'nDATsg', 'nINSTsg', 'fNOMsg', 'fACCsg', 'fGENsg', 'fLOCsg', 'fDATsg', 'fINSTsg', 'fINSTaltsg', 'plNOMpl', 'plACCplAN', 'plACCplIN', 'plGENpl', 'plLOCpl', 'plDATpl', 'plINSTpl', 'mshort', 'nshort', 'fshort', 'plshort', 'comparative', 'extracomparatives', 'mNOMsgFreq', 'mACCsgANFreq', 'mACCsgINFreq', 'mGENsgFreq', 'mLOCsgFreq', 'mDATsgFreq', 'mINSTsgFreq', 'nNOMsgFreq', 'nACCsgFreq', 'nGENsgFreq', 'nLOCsgFreq', 'nDATsgFreq', 'nINSTsgFreq', 'fNOMsgFreq', 'fACCsgFreq', 'fGENsgFreq', 'fLOCsgFreq', 'fDATsgFreq', 'fINSTsgFreq', 'fINSTaltsgFreq', 'plNOMplFreq', 'plACCplANFreq', 'plACCplINFreq', 'plGENplFreq', 'plLOCplFreq', 'plDATplFreq', 'plINSTplFreq', 'mshortFreq', 'nshortFreq', 'fshortFreq', 'plshortFreq', 'comparativeFreq', 'extracomparativesFreq', 'FinalColumn']

EMPTY_VALS = ('', 'NA', '-', '—')

POS = {
    'inflected': {
        'adj': 'adjective',
        'adjpron': 'adjective pronoun',
        'noun': 'noun',
        'num': 'numeral',
        'pron': 'pronoun',
        'ord': 'ordinal',
    },
    'noninflected': {
        'adv': 'adverb',
        'adjadv': 'adjectival adverb',
        'conj': 'conjunction',
        'disc': 'discourse',
        'func': 'function',
        'misc': 'miscellaneous',
        'phrase': 'phrase',
        'prefix': 'prefix',
        'prep': 'preposition',
    },
}

DECLENSIONS = [
    # Singular.
    ('NOMsg', 'NOMsg'),
    ('ACCsg', 'ACCsg'),
    ('GENsg', 'GENsg'),
    ('GEN2sg', 'GEN2sg'),
    ('GEN3sg', 'GEN3sg'),
    ('LOCsg', 'LOCsg'),
    ('LOC2sg', 'LOC2sg'),
    ('DATsg', 'DATsg'),
    ('INSTsg', 'INSTsg'),
    ('INSTaltsg', 'INSTaltsg'),
    ('VOCsg', 'VOCsg'),

    # Plural for nouns, pronouns, etc.
    ('NOMpl', 'NOMpl'),
    ('ACCpl', 'ACCpl'),
    ('GENpl', 'GENpl'),
    ('LOCpl', 'LOCpl'),
    ('DATpl', 'DATpl'),
    ('INSTpl', 'INSTpl'),

    # Plural of adjectives.
    ('plNOMpl', 'plNOMpl'),
    ('plACCplAN', 'plACCplAN'),
    ('plACCplIN', 'plACCplIN'),
    ('plGENpl', 'plGENpl'),
    ('plLOCpl', 'plLOCpl'),
    ('plDATpl', 'plDATpl'),
    ('plINSTpl', 'plINSTpl'),

    # Masculine forms.
    ('mNOMsg', 'mNOMsg'),
    ('mACCsgAN', 'mACCsgAN'),
    ('mACCsgIN', 'mACCsgIN'),
    ('mGENsg', 'mGENsg'),
    ('mLOCsg', 'mLOCsg'),
    ('mDATsg', 'mDATsg'),
    ('mINSTsg', 'mINSTsg'),

    # Neuter forms.
    ('nNOMsg', 'nNOMsg'),
    ('nACCsg', 'nACCsg'),
    ('nGENsg', 'nGENsg'),
    ('nLOCsg', 'nLOCsg'),
    ('nDATsg', 'nDATsg'),
    ('nINSTsg', 'nINSTsg'),

    # Feminine forms.
    ('fNOMsg', 'fNOMsg'),
    ('fACCsg', 'fACCsg'),
    ('fGENsg', 'fGENsg'),
    ('fLOCsg', 'fLOCsg'),
    ('fDATsg', 'fDATsg'),
    ('fINSTsg', 'fINSTsg'),
    ('fINSTaltsg', 'fINSTaltsg'),

    # Short forms of adjectives
    ('mshort', 'mshort'),
    ('nshort', 'nshort'),
    ('fshort', 'fshort'),
    ('plshort', 'plshort'),

    # Comparatives
    ('comparative', 'comparative'),
    ('extracomparatives', 'comparative'),
]
VERB_CONJUGATIONS = [
    ('sg1', 'sg1'),
    ('sg2', 'sg2'),
    ('sg3', 'sg3'),
    ('pl1', 'pl1'),
    ('pl2', 'pl2'),
    ('pl3', 'pl3'),
    ('Mpast', 'Mpast'),
    ('Fpast', 'Fpast'),
    ('Npast', 'Npast'),
    ('Ppast', 'Ppast'),
    ('Imper_sg', 'Imper_sg'),
    ('Imper_pl', 'Imper_pl'),
    ('PrAP', 'PrAP'),
    ('PrAP_forms', 'PrAP'),
    ('PAP', 'PAP'),
    ('PAP_forms', 'PAP'),
    ('PrPP', 'PrPP'),
    ('PrPP_forms', 'PrPP'),
    ('PPP', 'PPP'),
    ('PPP_forms', 'PPP'),
    ('VbAdv1', 'VbAdv1'),
    ('VbAdv2', 'VbAdv2'),
    ('Infinitive', 'Infinitive'),
]



# ------------------------------------------------------------------
# Functions


def create_schema(cursor):
    with open(os.path.join(FILE_DIR, 'schema.sql'), 'r', encoding='utf-8') as f:
        schema = f.read()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.executescript(schema)


def process_data(cursor, filename, verbose=False):
    with open(filename, encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile, fieldnames=CSV_FIELD_NAMES)
        lemma_to_sheet_row = {}
        for rowid, row in enumerate(csvreader, start=1):
            if rowid == 1:
                continue
            if can_insert_lemma(row, verbose=verbose):
                lemma = insert_lemma(cursor, row, verbose=verbose)
                lemma_pk = lemma['id']
                lemma_to_sheet_row[lemma_pk] = row
                insert_inflections(cursor, lemma_pk, row, verbose=verbose)
        insert_aspect_pairs(cursor, verbose, lemma_to_sheet_row)


def insert_aspect_pairs(cursor, verbose=False, lemma_to_sheet_row=None):
    '''
    Inserts relations for imperfective/perfective aspect pairs for verbs
    (as identified by "SecondRussian" in the original spreadsheet).
    '''
    if lemma_to_sheet_row is None:
        lemma_to_sheet_row = {}

    # collect aspect pairs from existing lemma data
    imperfectives = {}
    query = "SELECT id, lemma, aspect FROM lemma WHERE aspect IS NOT NULL AND aspect = ?"
    cursor.execute(query, ['imperfective'])
    rows = cursor.fetchall()
    for row in rows:
        (lemma_id, lemma, aspect) = row
        sheet_row = lemma_to_sheet_row[lemma_id]
        second_russian = sheet_row['SecondRussian'].strip()
        if second_russian == "0" or second_russian == "" or lemma == second_russian:
            continue

        lemma = unicodedata.normalize('NFKC', unicodedata.normalize('NFKD', lemma))
        second_russian = unicodedata.normalize('NFKC', unicodedata.normalize('NFKD', second_russian))

        if ";" in second_russian:
            # TODO: handle motion verbs
            # For now, just take the first verb if there are multiple entries
            multiple_second_russian = [s.strip() for s in second_russian.split(";") if s.strip() != lemma]
            if len(multiple_second_russian) > 0:
                perfective_verb = multiple_second_russian[0]
        elif " " in second_russian:
            continue
        else:
            perfective_verb = second_russian

        imperfectives[lemma] = perfective_verb

    # insert into the aspect_pairs table
    pair_id = 0
    inserts = []
    for (imperfective_verb, perfective_verb) in imperfectives.items():
        aspect_pair = [imperfective_verb, perfective_verb]
        pair_id += 1
        pair_name = "-".join(aspect_pair)

        aspect_pair_inserts = []
        for verb in aspect_pair:
            cursor.execute("SELECT id, aspect, count FROM lemma WHERE lemma = ? AND aspect in ('imperfective', 'perfective')", [verb])
            row = cursor.fetchone()
            if row is None:
                # print("WARNING: verb %s not found in database for pair %s" % (verb, pair_name))
                continue
            (lemma_id, aspect, lemma_count) = row
            aspect_pair_inserts.append([pair_id, pair_name, aspect, lemma_id, verb, lemma_count])

        # for now, we are requiring pairs of verbs
        if len(aspect_pair_inserts) == 2:
            inserts.extend(aspect_pair_inserts)

    sql = "INSERT INTO aspect_pair (pair_id, pair_name, aspect, lemma_id, lemma_label, lemma_count) VALUES (?, ?, ?, ?, ?, ?)"
    for insert in inserts:
        try:
            if verbose:
                print("Insert aspect_pair: %s" % insert)
            cursor.execute(sql, insert)
        except sqlite3.Error as e:
            logging.exception("aspect_pair: %s" % insert)
            raise e


def can_insert_lemma(row, verbose=False):
    # Skip 6O lemmas since these should be omitted
    # as they don't fit in the schema right now (includes some MWEs, etc)
    if row['Level'].strip() == "6O":
        return False
    return True


def insert_lemma(cursor, row, verbose=False):
    data = {
        'external_id':         row['UniqueId'],
        'lemma':               row['Russian'].strip(),
        'stressed':            row['Strеssеd_Russiаn'].strip(),
        'translation':         row['English'].strip(),
        'pos':                 row['POS'].strip(),
        'pos_subtype':         row['POS_Subtype'].strip(),
        'rank':                row['Rank'].strip(),
        'count':               row['Count'].strip(),
        'level':               row['Level'].strip(),
        'gender':              row['Gender'].strip(),
        'animacy':             row['Animacy'].strip(),
        'stem':                row['stem'].strip(),
        'ending':              row['ending'].strip(),
        'domain':              row['Domain'].strip(),
        'aspect':              row['Aspect'].strip(),
        'transitivity':        row['Transitivity'].strip(),
        'stress_pattern_semu': row['Stress_Pattern_SEMU'].strip(),
    }
    items = data.items()
    fieldstr = ','.join(["'%s'" % k for k, v in items])
    valstr = ','.join(['?' for k, v in items])
    values = [v for k, v in items]
    sql = 'INSERT INTO lemma (%s) VALUES (%s)' % (fieldstr, valstr)
    try:
        cursor.execute(sql, values)
    except sqlite3.Error as e:
        logging.error(sql)
        logging.exception("lemma insert: %s" % values)
        raise e
    data['id'] = cursor.lastrowid
    return data


def insert_inflections(cursor, lemma_pk, row, verbose=False):
    sql = 'INSERT INTO inflection (lemma_id, form, stressed, type, frequency) VALUES (?, ?, ?, ?, ?)'
    inserts = []

    if row['POS'] in POS['inflected']:
        inserts = handle_inflected_forms(lemma_pk, row) # Nouns, Adjectives, Pronouns, Cardinal Numbers, etc
    elif row['POS'] in POS['noninflected']:
        inserts = handle_noninflected_forms(lemma_pk, row) # Adverbs, Conjunctions, Particles, etc
    elif row['POS'] == 'verb':
        inserts = handle_verb_forms(lemma_pk, row)
    else:
        raise Exception("Unhandled part of speech!")

    # If we did not generate any inserts, add a single word entry for the lemma
    if len(inserts) == 0:
        inserts = handle_lemma_forms(lemma_pk, row)

    if verbose:
        print("[%s:%s] %s => %d inserts (%s)\n" % (row['UniqueId'], row['POS'], row['Russian'], len(inserts), ",".join([insert[3] for insert in inserts])))

    for insert in inserts:
        try:
            cursor.execute(sql, insert)
        except sqlite3.Error as e:
            logging.exception("inflection: %s" % insert)
            raise e


def get_row_freq(row, colname):
    frequency = row.get('Freq_%s' % colname, '')
    if frequency in EMPTY_VALS:
        frequency = row.get('%sFreq' % colname, '')
    if frequency in EMPTY_VALS:
        frequency = None
    return frequency


def get_cell_multi_forms(form, stressed=''):
    forms_with_stressed = []
    if ';' in form:
        forms = [f for f in form.strip().split(';') if f not in EMPTY_VALS]
        stressed_forms = [s.strip() for s in stressed.strip().split(';') if s and s not in EMPTY_VALS]
        if len(stressed_forms) == len(forms):
            forms_with_stressed = list(zip(forms, stressed_forms))
        else:
            for index, form in enumerate(forms):
                try:
                    forms_with_stressed.append((form, stressed[index]))
                except IndexError:
                    forms_with_stressed.append((form, ''))
    elif form:
        forms_with_stressed.append((form, stressed))

    return forms_with_stressed


def has_second_russian(row):
    if row['POS'] in ('phrase', 'prefix', 'prep', 'num'):
        return True
    if row['POS'] == 'conj' and 'mwe' in row['POS_Subtype']:
        return True
    return False


def handle_inflected_forms(pk, row):
    inserts = []
    uniq = {}
    for declension in DECLENSIONS:
        colname, inflection_type = declension
        form = row[colname].strip()
        if form in EMPTY_VALS:
            form = ''
        stressed = row.get('%s_stressed' % colname, '')
        frequency = get_row_freq(row, colname)
        forms_with_stressed = get_cell_multi_forms(form, stressed)
        if has_second_russian(row):
            secondary_forms_with_stressed = get_cell_multi_forms(row['SecondRussian'])
            forms_with_stressed.extend(secondary_forms_with_stressed)

        for form, stressed in forms_with_stressed:
            if form + inflection_type not in uniq:
                uniq[form + inflection_type] = True
                inserts.append([pk, form.strip(), stressed, inflection_type, frequency])
    return inserts


def handle_noninflected_forms(pk, row):
    noninflected = POS['noninflected']
    inserts = []
    uniq = {}
    inflection_type = noninflected[row['POS']]
    form = row['Russian'].strip()
    if form in EMPTY_VALS:
        form = ''
    stressed = row['Strеssеd_Russiаn']
    frequency = None
    forms_with_stressed = get_cell_multi_forms(form, stressed)
    if has_second_russian(row):
        secondary_forms_with_stressed = get_cell_multi_forms(row['SecondRussian'])
        forms_with_stressed.extend(secondary_forms_with_stressed)

    for form, stressed in forms_with_stressed:
        if form + inflection_type not in uniq:
            uniq[form + inflection_type] = True
            inserts.append([pk, form.strip(), stressed, inflection_type, frequency])
    return inserts


def handle_verb_forms(pk, row):
    inserts = []
    uniq = {}
    for conjugation in VERB_CONJUGATIONS:
        colname, inflection_type = conjugation
        form = row[colname].strip()
        if form in EMPTY_VALS:
            form = ''
        frequency = get_row_freq(row, colname)
        stressed = row.get('%s_stressed' % colname, '')
        forms_with_stressed = get_cell_multi_forms(form, stressed)
        for form, stressed in forms_with_stressed:
            if form + inflection_type not in uniq:
                uniq[form + inflection_type] = True
                inserts.append([pk, form.strip(), stressed, inflection_type, frequency])
    return inserts


def handle_lemma_forms(pk, row):
    inserts = []
    colname = POS['inflected'].get(row['POS']) or POS['noninflected'].get(row['POS']) or ''
    forms_with_stressed = get_cell_multi_forms(row['Russian'].strip(), row['Strеssеd_Russiаn'].strip())
    for form, stressed in forms_with_stressed:
        inserts.append([pk, form.strip(), stressed, colname, None])
    return inserts


def csv_get_fields(filename):
    """Returns a list of the column headers from the CSV file."""
    fields = []
    with open(filename, encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        count = 0
        for row in csvreader:
            count += 1
            if count == 2:
                fields = row.keys()
                break
    return fields


def main(csvfile, dbfile, verbose=False):
    """Main task runner -- expected to be called from a script passing in the required arguments."""
    CONN = sqlite3.connect(dbfile)
    cursor = CONN.cursor()
    create_schema(cursor)
    process_data(cursor, csvfile, verbose=verbose)
    CONN.commit()
    CONN.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="Name of the CSV file with russian spreadsheet data.", default="NewVisualizingRussian21January2019.csv")
    parser.add_argument("--output", help="Name of the SQLite database.", default="russian.sqlite3")
    parser.add_argument("-v", "--verbose", help="Increase output verbosity.", action="store_true")
    args = parser.parse_args()
    csvfile = args.input
    dbfile = args.output
    sys.stdout.write("=> Processing...\n")
    start = time.time()
    main(csvfile, dbfile, verbose=args.verbose)
    end = time.time()
    sys.stdout.write("=> Completed. Execution time: %f seconds\n" % (end - start))
    sys.stdout.write("=> Database saved to %s\n" % dbfile)
