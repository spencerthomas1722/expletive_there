import nltk
from nltk.corpus import brown, treebank
from nltk.stem import WordNetLemmatizer


# extract verbs paired with expletive 'there' from a given corpus/category
# designed for use with the brown corpus
def get_verbs_from_sents(c):
    verb_counts = {}
    sents = brown.tagged_sents(categories=c)
    for s in sents:
        for i in range(len(s)):
            if s[i][1] == 'EX':  # if the pos is expletive there
                next_pos = s[i+1]
                if next_pos.startswith('VB'):
                    if s[i+1] in verb_counts.keys():  # if verb already encountered
                        verb_counts[s[i]] += 1
                    else:
                        verb_counts[s[i]] = 1
                elif next_pos == 'RB':  # there followed by adverb
                    next_next_pos = s[i+1]
                    if next_next_pos.startswith('VB'):
                        if s[i+2][0] in verb_counts.keys():  # if verb already encountered
                            verb_counts[s[i+2][0]] += 1
                        else:
                            verb_counts[s[i+2][0]] = 1
    return verb_counts


def exp_clause(tr):
    # print(tr[0].label)
    try:
        return tr.label() == 'S' and tr[0][0].label() == 'EX'
    except AttributeError:
        pass


def lowest_vp(tr):
    child_labels = []
    num_children = len(tr)
    for i in range(num_children):
        child = tr[i]
        if isinstance(tr[i], nltk.Tree):
            child_labels.append(tr[i].label())
            # print(child_labels)
    # child_labels = [tr[i].label() for i in range(len(tr)) in tr if isinstance(tr[i], nltk.Tree)]  # direct children
    return tr.label() == 'VP' and 'VP' not in child_labels


def verbs_from_file_trees(filename):
    vs = {}
    lemmatizer = WordNetLemmatizer()
    trees = treebank.parsed_sents(filename)
    # print(trees)
    for t in trees:
        # print sentence if one of the words is 'there'; sanity check
        # leaves = t.leaves()
        # if 'there' in leaves:
        #     print(filename)
        #     print(leaves)
        # extract clauses whose subject is expletive there
        exp_clauses = t.subtrees(exp_clause)
        for exp in exp_clauses:
            print(exp.leaves())
            vp = exp.subtrees(lowest_vp)  # get the lowest vp in the clause
            for p in vp:
                v = p[0].leaves()[0]  # head verb
                v = lemmatizer.lemmatize(v, pos='v')
                # print(v)
                if v in vs.keys():  # if v already seen with expletive there in this file
                    vs[v] += 1
                else:
                    vs[v] = 1
                break  # only use v from highest clause
    return vs


def all_files():
    filenames = treebank.fileids()
    there_verb_counts = {}
    for fname in filenames:
        v_counts = verbs_from_file_trees(fname)
        for v in v_counts.keys():
            if v in there_verb_counts.keys():
                there_verb_counts[v] += v_counts[v]
            else:
                there_verb_counts[v] = v_counts[v]
    print(there_verb_counts)


if __name__ == '__main__':
    all_files()
