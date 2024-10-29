from flask import Flask, render_template, request, jsonify
import string
import re
from collections import Counter
import numpy as np

app = Flask(__name__)
def read_corpus(filename):
    with open(filename,'r',encoding='utf-8') as file:
        lines=file.readlines()
        
        words=[]
        for word in lines:
            words += re.findall(r'\w+',word.lower())
    return words

corpus=read_corpus(r'big.txt')


vocab = set(corpus)
word_count = Counter(corpus)
total_word_counts = float(sum(word_count.values()))
word_prob = {word: word_count[word] / total_word_counts for word in word_count.keys()}

# Spell-checking functions
def split(word):
    return [(word[:i], word[i:]) for i in range(len(word) + 1)]

def delete(word):
    return [left + right[1:] for left, right in split(word) if right]

def swap(word):
    return [left + right[1] + right[0] for left, right in split(word) if len(right) > 1]

def replace(word):
    return [left + center + right[1:] for left, right in split(word) if right for center in string.ascii_lowercase]

def insert(word):
    return [left + center + right for left, right in split(word) for center in string.ascii_lowercase]

def level_one_edits(word):
    return set(delete(word) + swap(word) + replace(word) + insert(word))

def level_two_edits(word):
    return [e2 for e1 in level_one_edits(word) for e2 in level_one_edits(e1)]

def correct_spelling_word(word):
    if word in vocab:
        return [(word, word_prob[word])]
    suggestions = level_one_edits(word) or level_two_edits(word) or [word]
    best_guess = [w for w in suggestions if w in vocab]
    return sorted([(w, word_prob[w]) for w in best_guess], key=lambda x: x[1], reverse=True)

# Route for the main page
@app.route('/')
def index():
    return render_template('index.html')

# API route for spell-checking
@app.route('/check', methods=['POST'])
def check_spelling():
    word = request.form['word'].lower()
    guesses = correct_spelling_word(word)
    return jsonify(guesses)

if __name__ == '__main__':
    app.run(debug=True)
