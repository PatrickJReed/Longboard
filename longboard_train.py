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


##Path to Data
basepath = "/home/ubuntu/"
ACCESS_KEY = 'AKIAJNNOA6QMT7HXF6GA'
SECRET_KEY = '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'
session = Session(aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
s3 = session.resource('s3')

img_width, img_height = 512,512
nb_epochs = 500
batch_size = 64

K.get_session().run(tf.global_variables_initializer())
#TRAIN inception model on SLAV
data_generator = ImageDataGenerator(rescale=1./255, validation_split=0.33)
train_generator = data_generator.flow_from_directory(os.path.join(basepath,"Images"), shuffle=True, seed=13, class_mode='categorical', batch_size=batch_size, subset="training", target_size=(img_width, img_height))
validation_generator = data_generator.flow_from_directory(os.path.join(basepath,"Images"), shuffle=True, seed=13, class_mode='categorical', batch_size=batch_size, subset="validation", target_size=(img_width, img_height))

if K.image_data_format() == 'channels_first':
    input_shape = (3, img_width, img_height)
else:
    input_shape = (img_width, img_height, 3)

base_model = InceptionV3(input_shape=input_shape, weights=None, include_top=False)

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(512, activation="relu")(x)
x = Dropout(.5)(x)
predictions = Dense(4, activation='softmax')(x)

# this is the model we will train
model = Model(inputs=base_model.input, outputs=predictions)
logs_base_dir = "./logs"
checkpoint = ModelCheckpoint("Longboard_model.h5", monitor='loss', verbose=1, save_best_only=True, save_weights_only=False, mode='auto', period=1)
early = EarlyStopping(monitor='loss', patience=10, verbose=1, mode='auto')
csv_logger = CSVLogger('training_longboard.log', append=True, separator=';')

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['acc'])

from sklearn.utils.class_weight import compute_class_weight

class_weight_list = compute_class_weight('balanced', np.unique(train_generator.classes), train_generator.classes)
class_weight = dict(zip(np.unique(train_generator.classes), class_weight_list))

STEP_SIZE_TRAIN=train_generator.n//train_generator.batch_size
STEP_SIZE_VALID=validation_generator.n//validation_generator.batch_size
model.fit_generator(generator=train_generator,
                    steps_per_epoch=STEP_SIZE_TRAIN,
                    validation_data=validation_generator,
                    validation_steps=STEP_SIZE_VALID,
                    epochs=nb_epochs,
                    callbacks = [early,checkpoint,csv_logger], 
                    verbose = 1,
                    class_weight=class_weight)
model.save('Longboard_model.h5')