import json
from lxml import etree as ET
import nltk
from nltk.stem import WordNetLemmatizer
import os
import re


# given the name of a framenet fulltext file,
# finds each instance of expletive 'there' (marked with POS 'ex' or 'EX0'*),
# find the last verb in that clause (the next verb that isn't followed by another verb, adverbs notwithstanding)
# *here, expletive 'there' is equivalent to these POS tags; expletive 'it' is marked with 'PP'.
# TODO the method used herein detects the first main verb after the expletive. this is an issue for raising verbs.
def detect_in_fulltext(fname, save_counts=False, save_text=False):
    v_count_dct = {}
    text_list = []

    # namespace prefix my beloathed
    ns = '{http://framenet.icsi.berkeley.edu}'
    # open + parse xml file
    parser = ET.XMLParser(remove_blank_text=True)
    try:
        tree = ET.parse(fname, parser)
    except ET.XMLSyntaxError:
        return None
    # tree = ET.parse(fname)
    root = tree.getroot()
    expl_there_sents = {}

    # get all tree nodes labeled "sentence"
    sents = root.findall('.//*[@sentNo]')
    reg = re.compile('V(B|H|D|V|M)(D|Z|P|N)?')
    for s in sents:
        # get sentence text, then tokenize it
        sent_text = s.find('./' + ns + 'text').text
        # sent_words = nltk.word_tokenize(sent_text)

        # get first annotation set, marked UNANN; this contains POS markings (of which there should only be one set)
        pos_annot = s.findall('.//*[@status="UNANN"]')[0][0]  # <-- the indices get us the layer, which contains labels
        labels = pos_annot.findall('.//*[@name]')  # all of the pos labels
        # print(labels)
        need_v = False
        # last_v_index = 0
        for i in range(len(labels)):
            l = labels[i]
            name = l.get('name')
            if need_v:
                # detect if verb
                if reg.match(name) or name == 'vb' or name == 'vbp':
                    last_v_index = i
                elif name == 'rb' or name.startswith('AV') or name == 'md' or name.startswith('VM'):  # adverbs & modals are transparent
                    continue
                else:
                    need_v = False
                    try:
                        try:
                            last_v_label = labels[last_v_index]
                            last_v_start = int(last_v_label.get('start'))
                            last_v_end = int(last_v_label.get('end')) + 1
                            last_v = sent_text[last_v_start:last_v_end]
                            # last_v = sent_words[last_v_index]  # get last verb using its index
                            # ^ not using lemmatizer for now to avoid mistakes by simplifying
                            # print('word: ' + last_v)
                            sent_id = s.get('ID')
                            expl_there_sents[sent_id] = (sent_text, last_v)  # add to dictionary
                            # text_list.append(sent_id + ': ' + sent_text + ' verb: ' + last_v)
                        except IndexError:
                            continue
                        if last_v in v_count_dct.keys():
                            v_count_dct[last_v] += 1
                        else:
                            v_count_dct[last_v] = 1
                    except UnboundLocalError:  # no last_v_index bc no expletive in the sentence
                        continue
            if name == 'ex' or name == 'EX0':
                # print(sent_text)
                need_v = True
                last_v_index = i + 1

    if (save_counts or save_text) and len(v_count_dct) > 0:
        cwd = os.getcwd()
        os.chdir(os.path.join(cwd, 'data'))
        dump_fname = fname.replace('.', '_')
        if save_counts:  # save counts as json file
            with open(dump_fname + '.json', 'w') as f:
                json.dump(v_count_dct, f)
        if save_text:
            with open(dump_fname + '.txt', 'w') as f:
                for sent in text_list:
                    try:
                        f.write(sent + '\n')
                    except UnicodeEncodeError:
                        continue
        parent = os.path.dirname(os.getcwd())  # go back up to fulltext directory so we can read more files
        os.chdir(parent)
    return expl_there_sents


# get sentences containing expletive "there" in fulltext documents
def all_fulltext(num_docs=107, save=True):
    cwd = os.getcwd()
    os.chdir(os.path.join(cwd, 'fndata-1.7', 'fulltext'))
    all_files = [f for f in os.listdir() if f.endswith('.xml')]  # starting off with 5 files to test the waters
    # print(len(all_files))
    all_files = all_files[:num_docs]
    # ^ get all lexical unit files in directory
    lu_counts = {}
    for f in all_files:
        f_v_counts = detect_in_fulltext(f, save_text=True)
        for lu in f_v_counts:  # for each verb in the file's verb count dict, add to main verb count dict
            if lu in lu_counts.keys():
                lu_counts[lu] += f_v_counts[lu]
            else:
                lu_counts[lu] = f_v_counts[lu]
    if save:
        with open(os.path.join(cwd, 'data', 'expletive_verb_counts.json'), 'w') as f:
            json.dump(lu_counts, f)
    return lu_counts


# get sentences containing expletive "there" in lexical unit documents
def all_lu(num_docs=-1, save=True):
    cwd = os.getcwd()
    os.chdir(os.path.join(cwd, 'fndata-1.7', 'lu'))
    all_files = [f for f in os.listdir() if f.endswith('.xml')]
    # print(len(all_files))
    all_files = all_files[:num_docs]
    all_instances = {}
    for f in all_files:
        f_sents = detect_in_fulltext(f, save_text=True)
        if f_sents is not None:
            for s in f_sents.keys():  # for each verb in the file's verb count dict, add to main verb count dict
                if s is not None:
                    all_instances[s] = f_sents[s]
    if save:
        with open(os.path.join('data', 'expletive_verb_counts_lu.json'), 'w') as f:
            json.dump(all_instances, f)
    return all_instances


def consolidate():
    full_lines = {}
    cwd = os.getcwd()
    os.chdir(os.path.join(cwd, 'data'))
    all_files = [f for f in os.listdir() if f.endswith('.txt')]
    for fi in all_files:
        f = open(fi, 'r')
        lines = f.readlines()
        f.close()
        for l in lines:
            l_id = l.split(':')[0]
            full_lines[l_id] = l  # put sentence in dict, identified by id; doesn't matter if id already in there
            # putting them in a dict is the most efficient way to avoid duplicates
    with open('all_sents.txt', 'w') as f:
        for k in full_lines.keys():
            f.write(full_lines[k])


def process(fname, save=True):
    with open(fname, 'r') as f:
        data_dct = json.load(f)
    instances_by_v = {}
    for k in data_dct.keys():
        sent, v = data_dct[k]
        if v in instances_by_v.keys():
            instances_by_v[v][k] = (sent, v)
        else:
            instances_by_v[v] = {k: (sent, v)}
    if save:
        with open('expletive_instances_by_verb.json', 'w') as f:
            json.dump(instances_by_v, f)
    return instances_by_v


def rewrite(fname):
    with open(fname, 'r') as f:
        data = json.load(f)
    new = {}
    lemm = WordNetLemmatizer()
    for k in data.keys():
        sent, v = data[k]
        lemmatized = lemm.lemmatize(v, pos='v')
        if lemmatized == 'wa' or lemmatized == '\'s':
            lemmatized = 'be'
        new[k] = (sent, lemmatized)
    with open('expletive_instances.json', 'w') as f:
        json.dump(new, f)


def investigation():
    with open('expletive_instances_by_verb.json', 'r') as f:
        data = json.load(f)
    del data['be']
    with open('expletive_instances_minus_be.json', 'w') as f:
        json.dump(data, f)


if __name__ == '__main__':
    # rewrite('expletive_instances.json')
    # process('expletive_instances.json')
    investigation()
