#!/home/ubuntu/miniconda2/bin/python

from __future__ import print_function
import glob, os, gc, sys
import os.path
import csv
import numpy as np
np.random.seed(1337)  # for reproducibility
from time import time
from subprocess import (call, Popen, PIPE)
from itertools import product
from IPython.display import display
from PIL import Image
from IPython.display import Image as IPImage
import shutil
import re
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten,Input
from keras.layers import Conv2D, MaxPooling2D, GlobalAveragePooling2D
from keras.layers import Lambda, concatenate
from keras.layers.normalization import BatchNormalization
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Model
from keras import optimizers
from keras.applications.inception_v3 import InceptionV3
from keras.utils import np_utils
from keras import backend as K
from keras.utils import multi_gpu_model
from keras.callbacks import ModelCheckpoint, LearningRateScheduler, CSVLogger, EarlyStopping, TensorBoard
from keras import Model
from keras.utils import multi_gpu_model
from keras.models import load_model
import uuid
import pickle
from boto3.session import Session
import boto3
import h5py
from keras import applications

basepath = "/home/ubuntu/"

# dimensions of our images.
img_width, img_height = 512, 512

top_model_weights_path = os.path.join(basepath,'bottleneck_fc_model_weights.h5')
epochs = 50
batch_size = 32
logs_base_dir = "./logs"
checkpoint = ModelCheckpoint("bottleneck_fc_model.h5", monitor='loss', verbose=1, save_best_only=True, save_weights_only=False, mode='auto', period=1)
early = EarlyStopping(monitor='loss', patience=10, verbose=1, mode='auto')
csv_logger = CSVLogger('bottleneck_fc_model.log', append=True, separator=';')


data_generator = ImageDataGenerator(rescale=1./255, validation_split=0.33)

# build the VGG16 network
model = applications.InceptionV3(include_top=False, weights='imagenet')

train_generator = data_generator.flow_from_directory(
    os.path.join(basepath,"Images_10K"),
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode=None,
    shuffle=False,
    seed=13,
    subset="training")
bottleneck_features_train = model.predict_generator(
    train_generator, train_generator.n//train_generator.batch_size)
np.save(open('bottleneck_features_train.npy', 'w'),bottleneck_features_train)

validation_generator = data_generator.flow_from_directory(
    os.path.join(basepath,"Images_10K"),
    target_size=(img_width, img_height),
    batch_size=batch_size,
    class_mode=None,
    shuffle=False,
    seed=13,
    subset="validation")
bottleneck_features_validation = model.predict_generator(
    validation_generator, validation_generator.n//validation_generator.batch_size)
np.save(open('bottleneck_features_validation.npy', 'w'),bottleneck_features_validation)

from keras.utils.np_utils import to_categorical

train_data = np.load(open('bottleneck_features_train.npy'))
train_labels = np.array(
    [0] * (len(train_data) / 2) + [1] * (len(train_data) / 2))

validation_data = np.load(open('bottleneck_features_validation.npy'))
validation_labels = np.array(
    [0] * (len(validation_data) / 2) + [1] * (len(validation_data) / 2))

model = Sequential()
model.add(Flatten(input_shape=train_data.shape[1:]))
model.add(Dense(256, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(4, activation='softmax'))

model.compile(optimizer='rmsprop',
              loss='categorical_crossentropy', metrics=['accuracy'])

model.fit(train_data, to_categorical(train_labels),
          callbacks = [early,checkpoint,csv_logger],
          epochs=epochs,
          batch_size=batch_size,
          validation_data=(validation_data, to_categorical(validation_labels)))
model.save_weights(top_model_weights_path)

call(['sudo', 'shutdown', '-h', 'now'])