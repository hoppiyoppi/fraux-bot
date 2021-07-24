# -*- coding: utf-8 -*-
"""
Created on Tue Mar 23 15:58:33 2021

@author: mocha
"""

frauxText = ""
f = open("frauxText.txt", 'r')
frauxText+=f.read()
frauxText = frauxText.replace('\n',' ')
frauxText = frauxText.replace('\t',' ')
frauxText = frauxText.replace('“', ' " ')
frauxText = frauxText.replace('”', ' " ')
for spaced in ['.','-',',','!','?','(','—',')']:
    frauxText = frauxText.replace(spaced, ' {0} '.format(spaced))
print(len(frauxText))

corpus_words = frauxText.split(' ')
corpus_words= [word for word in corpus_words if word != '']
corpus_words # [...'a', 'wyvern', ',', 'two', 'of', 'the', 'thousand'...]
print(len(corpus_words)) # 2185920

distinct_words = list(set(corpus_words))
word_idx_dict = {word: i for i, word in enumerate(distinct_words)}
distinct_words_count = print(len(list(set(corpus_words))))
distinct_words_count # 32663

k = 2 # adjustable
sets_of_k_words = [ ' '.join(corpus_words[i:i+k]) for i, _ in enumerate(corpus_words[:-k]) ]

from scipy.sparse import dok_matrix

sets_count = len(list(set(sets_of_k_words)))
next_after_k_words_matrix = dok_matrix((sets_count, len(distinct_words)))

distinct_sets_of_k_words = list(set(sets_of_k_words))
k_words_idx_dict = {word: i for i, word in enumerate(distinct_sets_of_k_words)}

for i, word in enumerate(sets_of_k_words[:-k]):

    word_sequence_idx = k_words_idx_dict[word]
    next_word_idx = word_idx_dict[corpus_words[i+k]]
    next_after_k_words_matrix[word_sequence_idx, next_word_idx] +=1
    
def sample_next_word_after_sequence(word_sequence, alpha = 0):
    next_word_vector = next_after_k_words_matrix[k_words_idx_dict[word_sequence]] + alpha
    likelihoods = next_word_vector/next_word_vector.sum()
    
    return weighted_choice(distinct_words, likelihoods.toarray())
    
def stochastic_chain(seed, chain_length=15, seed_length=2):
    current_words = seed.split(' ')
    if len(current_words) != seed_length:
        raise ValueError(f'wrong number of words, expected {seed_length}')
    sentence = seed

    for _ in range(chain_length):
        sentence+=' '
        next_word = sample_next_word_after_sequence(' '.join(current_words))
        sentence+=next_word
        current_words = current_words[1:]+[next_word]
    return sentence
# example use    
stochastic_chain('the world')