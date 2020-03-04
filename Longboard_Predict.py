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

basepath = "/home/ubuntu/"

batch_size = 256
# dimensions of our images.
img_width, img_height = 512, 512

from keras.models import load_model
model = load_model(os.path.join(basepath,'LongBoard_Train_AllImages_BN.h5'))

from keras.utils import multi_gpu_model
parallel_model = multi_gpu_model(model, gpus=8)

test_datagen = ImageDataGenerator(rescale=1./255)

test_generator = test_datagen.flow_from_directory(
        os.path.join(basepath,"All_Images"),
        target_size=(512, 512),
        color_mode="rgb",
        shuffle = False,
        class_mode=None,
        batch_size=256)

STEP_SIZE_TEST=test_generator.n//test_generator.batch_size
test_generator.reset()
pred=parallel_model.predict_generator(test_generator,steps=STEP_SIZE_TEST+1,verbose=1)

hf = h5py.File('Longboard_Predict.h5', 'w')
hf.create_dataset('pred', data=pred)
hf.close()                

s3.meta.client.upload_file(os.path.join('Longboard_Predict.h5'),'bsmn-data',os.path.join('Longboard_Predict.h5'))