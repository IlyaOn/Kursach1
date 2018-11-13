import glob

import ngram
import numpy
from keras import Sequential
from keras.layers import LSTM, Dropout, Dense, Activation
from keras.utils import np_utils
from music21 import converter, instrument, note, chord, stream
from music21.ext import joblib
from sklearn.preprocessing import LabelBinarizer
from heapq import nlargest
import operator
from keras.models import load_model
from app.midiNN.music_controller import create_midi, get_msg
from app.midiNN import wild_card

CONTENT_FILENAME = "uploads/music.mid"

def lets_do_it(mode):
    notes = []
    print("Engage!")
    #for file in glob.glob("input/*.mid"):
    notes.extend(get_msg(CONTENT_FILENAME))

    create_midi(notes)

    print("Загрузка ngram, для поиска похожих нот...")
    G = joblib.load("app/encoders/{}/ngram.sav".format(mode))
    for i in range(len(notes)):
        notes[i] = G.find(notes[i])
    create_midi(notes)

    print("Берем из словаря коды для каждой ноты...")
    encoder = LabelBinarizer()
    encoder.fit(notes)
    encoder = joblib.load("app/encoders/{}/LabelBinarizer.sav".format(mode))
    data = encoder.transform(notes)

    print("Создаем датасет...")
    look_back = 2
    trainX, trainY = wild_card.create_dataset(data, look_back)

    print('Загружаем сеть...')
    model = load_model("app/encoders/{}/model.h5".format(mode))

    print("Магия...")
    Y = wild_card.extended_this(model=model, trainX=trainX, trainY=trainY, look_back=look_back,
                                multi=1, type="remake")

    print("Расшифруем полученые данные в мелодию...")
    new_notes = []
    text_labels = encoder.classes_
    for i in range(len(Y)):
        # Ищем индекс самой вероятной ноты
        pred = Y[i]
        top = nlargest(1, enumerate(pred), operator.itemgetter(1))
        top = top[0][0]
        # Загружаем из словаря по индексу ноту
        predicted_label = text_labels[top]
        new_notes.append(predicted_label)

    sequence_length = 100
    print("СОХРАНЯЕМ!")
    create_midi(new_notes)
