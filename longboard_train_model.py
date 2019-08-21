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
import xml.etree.ElementTree as ET
from sklearn.model_selection import train_test_split
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

##Path to Data

Data_Set_Train = []
Data_Set_Validate = []
Data_Set_Train.append([SC_1571_Hippo,Bulk_1571_Hippocampus,Bulk_1571_Cerebellum])
Data_Set_Train.append([SC_1846_Cortex,Bulk_1846_Cortex,Bulk_1846_Liver])
Data_Set_Train.append([SC_1846_Hippo,Bulk_1846_Hippocampus,Bulk_1846_Liver])
Data_Set_Train.append([SC_5125_Cortex,Bulk_5125_Cortex,Bulk_5125_Liver])
Data_Set_Validate.append([SC_5125_Hippo,Bulk_5125_Hippocampus,Bulk_5125_Liver])

#TRAIN inception model on SLAV

train_datagen = ImageDataGenerator(width_shift_range=0.2,height_shift_range=0.1,zoom_range=0.1,horizontal_flip=True)

validate_datagen = ImageDataGenerator()

img_width, img_height = 512,512

nb_epochs = 10
batch_size = 32

if K.image_data_format() == 'channels_first':
    input_shape = (3, img_width, img_height)
else:
    input_shape = (img_width, img_height, 3)


base_model = InceptionV3(input_shape=input_shape, weights=None, include_top=False)

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(1024, activation="relu")(x)
x = Dropout(.2)(x)
predictions = Dense(25, activation='sigmoid')(x)

# this is the model we will train
model = Model(inputs=base_model.input, outputs=predictions)

checkpoint = ModelCheckpoint("slav_incv3_scratch_25.h5", monitor='loss', verbose=1, save_best_only=True, save_weights_only=False, mode='auto', period=1)
early = EarlyStopping(monitor='loss', patience=10, verbose=1, mode='auto')
csv_logger = CSVLogger('training_scratch25.log', append=True, separator=';')
tensorboard = TensorBoard(log_dir='./logs_25', histogram_freq=0,
                          write_graph=True, write_images=False)

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

for e in range(nb_epochs):
    print("epoch %d" % e)
    for dset in Data_Set_Train:    
        for cell in dset[0]:
            print(cell)
            batches = 0
            if os.path.isfile(os.path.join(basepath, cell, cell+'_XY.npz')):
                try:
                    data = np.load(os.path.join(basepath, cell, cell+'_XY.npz'))
                    X = data['X']
                    Y = data['Y']
                    Y = Y[:,np.r_[0:21,33:37]]
                    X_train, X_validate, Y_train, Y_validate = train_test_split(X, Y, test_size=0.2, random_state=42)
                    data = None
                    X = None
                    Y = None
                    print("npz is OK")
                    model.fit_generator(train_datagen.flow(X_train, Y_train, batch_size=batch_size), callbacks = [early,checkpoint,csv_logger,tensorboard], verbose = 1, epochs=1, steps_per_epoch=len(X_train) / 32, validation_data=validate_datagen.flow(X_validate, Y_validate, batch_size=batch_size))
                except: 
                    print("npz is bad")
                    pass
model.save('inceptionV3_SLAV_Scratch_25.h5')  