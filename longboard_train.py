#!/usr/bin/python2.7
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
import tensorflow as tf
from keras.models import Sequential
from keras.layers import Dense, Dropout, Activation, Flatten,Input
from keras.layers import Conv2D, MaxPooling2D, GlobalAveragePooling2D
from keras.layers import Lambda, concatenate
from keras.layers.normalization import BatchNormalization
from keras.preprocessing.image import ImageDataGenerator
from keras.models import Model, load_model
from keras import optimizers
from keras.applications.inception_v3 import InceptionV3
from keras.utils import np_utils
from keras import backend as K
from keras.utils import multi_gpu_model
from keras.callbacks import ModelCheckpoint, LearningRateScheduler, CSVLogger, EarlyStopping, TensorBoard
from keras import Model
from keras.utils import multi_gpu_model

# config = tf.ConfigProto(log_device_placement=True)
# config.gpu_options.allocator_type = 'BFC'
# config.gpu_options.allow_growth = True
# sess = tf.Session(config = config)
# K.set_session(sess)



##Path to Data
basepath = "/home/ubuntu/efs/SLAV_Data/" 
Bulk_1571_Cerebellum = "1571_cereb_BT_40_L3"
Bulk_1571_Hippocampus = "1571_hippo_BT_41_L3"
Bulk_1846_Cerebellum = "1846_cereb_BT_13_L3"
Bulk_1846_Cortex = "1846_cortex_BT_71_L3"
Bulk_1846_Hippocampus = "1846_hippo_BT_19_L3"
Bulk_1846_Liver = "1846_liver_BT_22_L3"
Bulk_5125_Cortex = "5125_cortex_BT_122_L3"
Bulk_5125_Hippocampus = "5125_hippo_BT_139_L3"
Bulk_5125_Liver = "5125_liver_BT_164_L3"

SC_1571_Hippo = ["1571_hippo_SC_43_L3","1571_hippo_SC_45_L3","1571_hippo_SC_46_L3","1571_hippo_SC_47_L3","1571_hippo_SC_48_L3","1571_hippo_SC_50_L3","1571_hippo_SC_51_L3","1571_hippo_SC_52_L3","1571_hippo_SC_53_L3","1571_hippo_SC_55_L3","1571_hippo_SC_56_L3","1571_hippo_SC_57_L3","1571_hippo_SC_58_L3","1571_hippo_SC_59_L3","1571_hippo_SC_61_L3","1571_hippo_SC_62_L3","1571_hippo_SC_63_L3","1571_hippo_SC_64_L3"]
SC_1846_Cortex = ["1846_cortex_SC_72_L3","1846_cortex_SC_73_L3","1846_cortex_SC_74_L3","1846_cortex_SC_75_L3","1846_cortex_SC_78_L3","1846_cortex_SC_79_L3","1846_cortex_SC_80_L3","1846_cortex_SC_81_L3","1846_cortex_SC_82_L3","1846_cortex_SC_83_L3","1846_cortex_SC_84_L3","1846_cortex_SC_85_L3","1846_cortex_SC_86_L3"]
SC_1846_Hippo = ["1846_hippo_SC_100_L3","1846_hippo_SC_101_L3","1846_hippo_SC_102_L3","1846_hippo_SC_103_L3","1846_hippo_SC_104_L3","1846_hippo_SC_105_L3","1846_hippo_SC_106_L3","1846_hippo_SC_107_L3","1846_hippo_SC_108_L3","1846_hippo_SC_109_L3","1846_hippo_SC_110_L3","1846_hippo_SC_111_L3","1846_hippo_SC_112_L3","1846_hippo_SC_113_L3","1846_hippo_SC_88_L3","1846_hippo_SC_89_L3","1846_hippo_SC_90_L3","1846_hippo_SC_91_L3","1846_hippo_SC_92_L3","1846_hippo_SC_93_L3","1846_hippo_SC_94_L3","1846_hippo_SC_95_L3","1846_hippo_SC_99_L3"]
SC_5125_Cortex = ["5125_cortex_SC_125_L3","5125_cortex_SC_126_L3","5125_cortex_SC_127_L3","5125_cortex_SC_128_L3","5125_cortex_SC_129_L3","5125_cortex_SC_130_L3","5125_cortex_SC_131_L3","5125_cortex_SC_132_L3","5125_cortex_SC_133_L3","5125_cortex_SC_134_L3","5125_cortex_SC_135_L3","5125_cortex_SC_136_L3","5125_cortex_SC_138_L3"]
SC_5125_Hippo = ["5125_hippo_SC_140_L3","5125_hippo_SC_141_L3","5125_hippo_SC_142_L3","5125_hippo_SC_143_L3","5125_hippo_SC_144_L3","5125_hippo_SC_145_L3","5125_hippo_SC_147_L3","5125_hippo_SC_149_L3","5125_hippo_SC_150_L3","5125_hippo_SC_151_L3","5125_hippo_SC_152_L3","5125_hippo_SC_153_L3","5125_hippo_SC_154_L3","5125_hippo_SC_155_L3","5125_hippo_SC_156_L3","5125_hippo_SC_157_L3","5125_hippo_SC_158_L3","5125_hippo_SC_159_L3","5125_hippo_SC_160_L3","5125_hippo_SC_161_L3","5125_hippo_SC_162_L3","5125_hippo_SC_163_L3"]


Data_Set_Train = []
Data_Set_Validate = []
Data_Set_Train.append([SC_1571_Hippo,Bulk_1571_Hippocampus,Bulk_1571_Cerebellum])
Data_Set_Train.append([SC_1846_Cortex,Bulk_1846_Cortex,Bulk_1846_Liver])
Data_Set_Train.append([SC_1846_Hippo,Bulk_1846_Hippocampus,Bulk_1846_Liver])
Data_Set_Train.append([SC_5125_Cortex,Bulk_5125_Cortex,Bulk_5125_Liver])
Data_Set_Validate.append([SC_5125_Hippo,Bulk_5125_Hippocampus,Bulk_5125_Liver])

#TRAIN inception model on SLAV


img_width, img_height = 512,512

nb_epochs = 2
batch_size = 32

if K.image_data_format() == 'channels_first':
    input_shape = (3, img_width, img_height)
else:
    input_shape = (img_width, img_height, 3)


base_model = InceptionV3(input_shape=input_shape, weights='imagenet', include_top=False)

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(1024, activation="relu")(x)
x = Dropout(.2)(x)
predictions = Dense(37, activation='sigmoid')(x)

# # this is the model we will train
model = Model(inputs=base_model.input, outputs=predictions)
for layer in base_model.layers:
    layer.trainable = False

checkpoint = ModelCheckpoint("slav_incv3.h5", monitor='loss', verbose=1, save_best_only=True, save_weights_only=False, mode='auto', period=1)

early = EarlyStopping(monitor='loss', patience=10, verbose=1, mode='auto')

csv_logger = CSVLogger('training.log', append=True, separator=';')

tensorboard = TensorBoard(log_dir='./logs2', histogram_freq=0,
                          write_graph=True, write_images=False)

model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# #parallel_model = multi_gpu_model(model, gpus=4)
# #parallel_model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

for e in range(nb_epochs):
    print("epoch %d" % e)
    for dset in Data_Set_Train:    
        for cell in dset[0]:
            print(cell)
            if os.path.isfile(os.path.join(basepath, cell, cell+'_XY.npz')):
                try:
                    data = np.load(os.path.join(basepath, cell, cell+'_XY.npz'))
                    X_train = data['X'] / 255
                    Y_train = data['Y']
                    print("npz is OK")
                    model.fit(X_train, Y_train, batch_size=batch_size, epochs=10, callbacks = [early,checkpoint,csv_logger,tensorboard], validation_split=.2, verbose = 1)
                except Exception as e: 
                    print(e) 
                    print("npz is bad")
                    pass
model.save('inceptionV3_SLAV_5_1.h5')


for layer in model.layers[:249]:
      layer.trainable = False
for layer in model.layers[249:]:
      layer.trainable = True

from keras.optimizers import SGD
model.compile(optimizer=SGD(lr=0.0001, momentum=0.9), loss='binary_crossentropy',metrics=['accuracy'])

for e in range(nb_epochs):
    print("epoch %d" % e)
    for dset in Data_Set_Train:
        for cell in dset[0]:
            print(cell)
            if os.path.isfile(os.path.join(basepath, cell,cell+'_XY.npz')):
                try:
                    data = np.load(os.path.join(basepath, cell, cell+'_XY.npz'))
                    X_train = data['X'] / 255
                    Y_train = data['Y']
                    print("npz is OK")
                    model.fit(X_train, Y_train, batch_size=batch_size, epochs=10, callbacks = [early,checkpoint,csv_logger,tensorboard], validation_split=.2, verbose = 1)
                except:
                    print("npz is bad")
                    pass
model.save('inceptionV3_SLAV_5_2.h5')
