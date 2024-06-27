import pickle
import re
from collections import Counter
import requests
import streamlit as st
import string
c='corpus.pkl'
st.title("Auto Correct Suggestion")

corpus=pickle.load(open(c,'rb'))
word_count=Counter(corpus)
vocab=set(corpus)
total_word_counts=float(sum(word_count.values()))
word_prob={word:word_count[word]/total_word_counts for word in word_count.keys()}

# Split Operation

def split(word):
    return [(word[:i],word[i:]) for i in range(len(word)+1)]

# Delete Operation

def delete(word):
    return [left+right[1:] for left,right in split(word) if right]

# Swap Operation
def swap(word):
    return [left + right[1] + right[0] for left,right in split(word) if len(right)>1]

# Repalce Operation
def replace(word):
    return [left+center+right[1:] for left,right in split(word) if right for center in string.ascii_lowercase]

# Insert Operation
def insert(word):
    return [left+center+right[1:] for left,right in split(word) for center in string.ascii_lowercase]

# Find Minimum distance

def level_one_edits(word):
    return set(delete(word)+swap(word)+replace(word)+insert(word))

def level_two_edits(word):
    return [e2 for e1 in level_one_edits(word) for e2 in level_one_edits(e1)]

# AutoCorrect Suggestion

def correct_spelling_word(word,vocab,word_prob):
    if word in vocab:
        return f"{word} is correctly spelled"
    suggestions=level_one_edits(word) or level_two_edits(word) or [word]
    best_guess=[w for w in suggestions if w in vocab]
    if not best_guess:
        return f"Sorry no suggestions found for {word}"
    suggestions_with_prob= [(w,word_prob[w]) for w in best_guess if w in word_prob]
    suggestions_with_prob.sort(key=lambda x:x[1],reverse=True)
    return f"Suggestions for {word}: " + ', '.join([f"{w} ({prob:.4%})" for w,prob in suggestions_with_prob[:10]])
w=st.text_input("Search Here")
button = st.button("Check")
if button:
    guess = correct_spelling_word(w, vocab, word_prob)
    st.write(guess)
