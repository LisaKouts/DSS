# -*- coding: utf-8 -*-
"""Final_script.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Gz7ss08-cPw5vKmqBWmCohjbsL45qJ5X

### <b>Deep Learning Assignment </b>

<b>Tilburg University</b><br>
<b>Master Data Science and Society</b>

<b>Team 33</b><br>
Agapi Broupi 2048389<br>
Hyun Seon Park 2036947 <br>
Lisa Koutsoviti Koumeri 2048041<br>


CodaLab account name: TiU_MSc_DSS_DL_Group_33<br>
Team name: KRxGR

October 5, 2020
"""

# Commented out IPython magic to ensure Python compatibility.
## Libraries ##

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import confusion_matrix, accuracy_score
from sklearn.model_selection import train_test_split

from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import *
from keras.utils.np_utils import to_categorical
from keras.initializers import Constant
from keras.layers import Bidirectional
from keras.layers import LSTM
import re

import matplotlib.pyplot as plt
# %matplotlib inline

"""## 1. Pre-proccessing"""

from google.colab import drive
drive.mount("/content/drive")

## LOADING DATA ##
X_train=pd.read_csv('/content/drive/My Drive/DL assignment/X_data.txt', header=None)
y_train=pd.read_csv('/content/drive/My Drive/DL assignment/y_data.txt', header=None)
X_test=pd.read_csv('/content/drive/My Drive/DL assignment/X_test.txt', header=None)

## Cleaning the input sentences

replace_puncts = {'`': "'", '′': "'", '“':'"', '”': '"', '‘': "'"}

strip_chars = [',', '.', '"', ':', ')', '(', '-', '|', ';', "'", '[', ']', '>', '=', '+', '\\', '•',  '~', '@', 
 '·', '_', '{', '}', '©', '^', '®', '`',  '<', '→', '°', '€', '™', '›',  '♥', '←', '×', '§', '″', '′', 'Â', '█', '½', 'à', '…', 
 '“', '★', '”', '–', '●', 'â', '►', '−', '¢', '²', '¬', '░', '¶', '↑', '±', '¿', '▾', '═', '¦', '║', '―', '¥', '▓', '—', '‹', '─', 
 '▒', '：', '¼', '⊕', '▼', '▪', '†', '■', '’', '▀', '¨', '▄', '♫', '☆', 'é', '¯', '♦', '¤', '▲', 'è', '¸', '¾', 'Ã', '⋅', '‘', '∞', 
 '∙', '）', '↓', '、', '│', '（', '»', '，', '♪', '╩', '╚', '³', '・', '╦', '╣', '╔', '╗', '▬', '❤', 'ï', 'Ø', '¹', '≤', '‡', '√', ]

puncts = ['!', '?', '$', '&', '/', '%', '#', '*','£']

def clean_str(x):
    x = str(x)
    
    x = x.lower()
    
    for k, v in replace_puncts.items():
        x = x.replace(k, f' {v} ')
        
    for punct in strip_chars:
        x = x.replace(punct, ' ') 
    
    for punct in puncts:
        x = x.replace(punct, f' {punct} ')
        
    x = x.replace(" '", " ")
    x = x.replace("' ", " ")
        
    return x


X_train[0] = X_train[0].apply(clean_str)

## Inspecting sentece length

X_train['l'] = X_train[0].apply(lambda x: len(str(x).split(' ')))
print("mean length of sentence: " + str(X_train.l.mean()))
print("max length of sentence: " + str(X_train.l.max()))
print("std dev length of sentence: " + str(X_train.l.std()))

## Creating a copy of X_train
sentences = X_train

"""### 1.1 Pre-preprocessing for Naive Bayes & Logistic regression classifiers"""

from sklearn import model_selection
sentences_train, sentences_test, y_train_NB, y_test_NB = model_selection.train_test_split(X_train, y_train,test_size=0.1,random_state=1000)

from sklearn import model_selection, preprocessing
encoder = preprocessing.LabelEncoder()
train_y_NB = encoder.fit_transform(np.array(y_train_NB[0]))
valid_y_NB = encoder.fit_transform(np.array(y_test_NB[0]))

# word vectors
vectorizer = CountVectorizer(min_df=3)
vectorizer.fit(np.array(sentences_train[0]))
X_train_NB = vectorizer.transform(np.array(sentences_train[0]))
X_test_NB  = vectorizer.transform(np.array(sentences_test[0]))

# word level tf-idf
tfidf_vect = TfidfVectorizer(analyzer='word', token_pattern=r'\w{1,}', max_features=5000)
tfidf_vect.fit(np.array(sentences[0]))
xtrain_tfidf =  tfidf_vect.transform(np.array(sentences_train[0]))
xvalid_tfidf =  tfidf_vect.transform(np.array(sentences_test[0]))

# word level trigrams
tfidf_vect_ngram = TfidfVectorizer(analyzer='word', token_pattern=r'\w{1,}', ngram_range=(2,3), max_features=5000)
tfidf_vect_ngram.fit(np.array(sentences[0]))
xtrain_tfidf_ngram =  tfidf_vect_ngram.transform(np.array(sentences_train[0]))
xvalid_tfidf_ngram =  tfidf_vect_ngram.transform(np.array(sentences_test[0]))
xtrain_tfidf_ngram.shape

"""### 1.2 Pre-preprocessing - for neural networks"""

sequence_length = 50

max_features = 20000 # this is the number of words we care about

tokenizer = Tokenizer(num_words=max_features, split=' ', oov_token='<unw>', filters=' ')
tokenizer.fit_on_texts(X_train[0].values)

# this takes our sentences and replaces each word with an integer
X = tokenizer.texts_to_sequences(X_train[0].values)

# we then pad the sequences so they're all the same length (sequence_length)
X = pad_sequences(X, sequence_length)

y = pd.get_dummies(y_train[0]).values

# lets keep a couple of thousand samples back as a test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1,random_state=1000)

print("test set size " + str(len(X_test)))

embeddings_index = {}
f = open('/content/drive/My Drive/DL assignment/glove.6B.300d.txt', encoding="utf-8")
for line in f:
    values = line.split()
    word = values[0]
    coefs = np.asarray(values[1:], dtype='float32')
    embeddings_index[word] = coefs
f.close()

print('Found %s word vectors.' % len(embeddings_index))

word_index = tokenizer.word_index
print('Found %s unique tokens.' % len(word_index))

num_words = min(max_features, len(word_index)) + 1
print(num_words)

embedding_dim = 300

# first create a matrix of zeros, this is our embedding matrix
embedding_matrix = np.zeros((num_words, embedding_dim))

# for each word in out tokenizer lets try to find that work in our w2v model
for word, i in word_index.items():
    if i > max_features:
        continue
    embedding_vector = embeddings_index.get(word)
    if embedding_vector is not None:
        # we found the word - add that words vector to the matrix
        embedding_matrix[i] = embedding_vector
    else:
        # doesn't exist, assign a random vector
        embedding_matrix[i] = np.random.randn(embedding_dim)

"""## 2. Machine learning models

### 2.1 Exploring Naive Bayes and Logistic Regression
"""

### Baseline model

from sklearn.linear_model import LogisticRegression

# Vector count input
classifier = LogisticRegression(max_iter = 1000)
classifier.fit(X_train_NB, train_y_NB)
score = classifier.score(X_test_NB, y_test_NB)

print("Accuracy:", score)

# Frequency count input
classifier = LogisticRegression(max_iter = 1000)
classifier.fit(xtrain_tfidf, train_y_NB)
score = classifier.score(xvalid_tfidf, valid_y_NB)

print("Accuracy:", score)

# Trigram input
classifier = LogisticRegression(max_iter = 1000)
classifier.fit(xtrain_tfidf_ngram, train_y_NB)
score = classifier.score(xvalid_tfidf_ngram, valid_y_NB)

print("Accuracy:", score)

from sklearn.naive_bayes import MultinomialNB

# Vector count input
classifier = MultinomialNB()
classifier.fit(X_train_NB, train_y_NB)
score = classifier.score(X_test_NB, valid_y_NB)

print("Accuracy:", score)

# Frequency count input
classifier = MultinomialNB()
classifier.fit(xtrain_tfidf, train_y_NB)
score = classifier.score(xvalid_tfidf, valid_y_NB)

print("Accuracy:", score)

# Trigram input
classifier = MultinomialNB()
classifier.fit(xtrain_tfidf_ngram, train_y_NB)
score = classifier.score(xvalid_tfidf_ngram, valid_y_NB)

print("Accuracy:", score)

"""### 2.3 Exploring deep learning approaches"""

## CNN - winner model
from keras import layers
from keras import optimizers
from keras import regularizers

embedding_dim = 300

model = Sequential()
model.add(layers.Embedding(num_words, embedding_dim, input_length=sequence_length))
model.add(layers.Conv1D(128, 4, activation='relu'))
model.add(layers.GlobalMaxPooling1D())
model.add(layers.Dense(10, activation='relu',)) 
model.add(layers.Dense(5, activation='relu',)) 
model.add(layers.Dense(2, activation='sigmoid'))
model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])
model.summary()

history = model.fit(X_train, y_train,
                    epochs=2,
                    validation_data=(X_test, y_test),
                    batch_size=128)

from keras.utils.vis_utils import plot_model
plot_model(model, to_file='model_plot.png', show_shapes=True, show_layer_names=True)

results = model.evaluate(X_test, y_test, batch_size=128)
print("test loss, test acc:", results)

results

## Simple RNN
import keras

def RNN():
    inputs = Input(name='inputs',shape=[sequence_length])
    layer = Embedding(num_words,50,input_length=num_words)(inputs)
    layer = LSTM(64)(layer)
    layer = Dense(256,name='FC1')(layer)
    layer = Activation('relu')(layer)
    layer = Dropout(0.5)(layer)
    layer = Dense(2,name='out_layer')(layer)
    layer = Activation('sigmoid')(layer)
    model = keras.Model(inputs=inputs,outputs=layer)
    return model

model_rnn = RNN()
model_rnn.summary()
model_rnn.compile(loss='binary_crossentropy',optimizer=optimizers.RMSprop(),metrics=['accuracy'])

model_rnn.fit(X_train,y_train,batch_size=128,epochs=5,
          validation_split=0.2,callbacks=[keras.callbacks.EarlyStopping(monitor='val_loss',min_delta=0.0001)])

accr = model_rnn.evaluate(X_test,y_test)

## Bi-directional RNN LSTM
model_lstm = Sequential()
model_lstm.add(Embedding(num_words,
                    embedding_dim,
                    embeddings_initializer=Constant(embedding_matrix),
                    input_length=sequence_length,
                    trainable=True))
model_lstm.add(SpatialDropout1D(0.2))
model_lstm.add(Bidirectional(LSTM(64, return_sequences=True)))
model_lstm.add(Bidirectional(LSTM(32)))
model_lstm.add(Dropout(0.25))
model_lstm.add(Dense(units=2, activation='softmax'))
model_lstm.compile(loss = 'categorical_crossentropy', optimizer='adam',metrics = ['accuracy'])
print(model_lstm.summary())

batch_size = 128
history_lstm = model_lstm.fit(X_train, y_train, epochs=5, batch_size=batch_size, verbose=1, validation_split=0.1)

plot_model(model_lstm, to_file='model_LSTMplot.png', show_shapes=True, show_layer_names=True)

"""### 3. Creating a text file with the predictions"""

y_hat = model.predict(X_test)
accuracy_score(list(map(lambda x: np.argmax(x), y_test)), list(map(lambda x: np.argmax(x), y_hat)))

test_sent = pd.read_csv('/content/drive/My Drive/DL assignment/X_test.txt', header=None) 
test_sent[0] = test_sent[0].apply(clean_str)

x = tokenizer.texts_to_sequences(test_sent[0].values)
x = pad_sequences(x, sequence_length)

pred = model.predict(x)

from itertools import chain
pred = pd.DataFrame(list(zip(test_sent[0].values, list(map(lambda x: np.argmax(x), pred)))), columns=['text', 'label'])
predlist=pred['label'].tolist()

# Creating text file
new_list = []
for i in predlist:
    new_list.append(str(i))

with open('answer.txt', mode='w', newline='\n') as myfile:
    myfile.write("\n".join(new_list))