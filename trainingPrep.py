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
import uuid
import pickle
from boto3.session import Session
import boto3
import h5py
basepath = "/home/ubuntu/"
subject = sys.argv[1]

with open(os.path.join(basepath,"config.txt")) as f:
    config = [line.rstrip() for line in f]    

session = Session(aws_access_key_id=config[0],aws_secret_access_key=config[1])
s3 = session.resource('s3') 
s3.meta.client.download_file('bsmn-data',os.path.join('Training_UMAP_HDB_Final.h5'),os.path.join(basepath,'Training_UMAP_HDB_Final.h5'))
hf = h5py.File(os.path.join(basepath,'Training_UMAP_HDB_Final.h5'),'r')
Train_Z = hf['Z'][()] 
Train_C = hf['C'][()]
Train_Y = hf['Y'][()]
embedding_partialsupervised_1 = hf['embedding_partialsupervised_1'][()]
embedding_partialsupervised_2 = hf['embedding_partialsupervised_2'][()]
HDB_1 = hf['HDB_1'][()]
HDB_2 = hf['HDB_2'][()]
set1 = hf['set1'][()]
set2 = hf['set2'][()]
New_1 = hf['New_1'][()]
New_2 = hf['New_2'][()]

T1={}
for i in range(0, 30):
    with open(os.path.join(basepath,'Dict_'+str(i)+'.pkl'), 'rb') as handle:
        T = pickle.load(handle)
    if i == 0:
        T1 = dict(T)
    else:
        T1.update(T)
 
        
print(subject)
session = Session(aws_access_key_id=config[0],aws_secret_access_key=config[1])
s3 = session.resource('s3')
s3 = boto3.client ('s3')
s3.download_file('for-ndar',os.path.join("metadata/", subject + ".txt"),os.path.join(basepath,subject + ".txt"))

with open(os.path.join(basepath,subject + ".txt")) as f:
    Cells = [line.rstrip() for line in f]
for cell in Cells:
    print(cell)
    cell_ids = []
    s3.download_file('bsmn-data',os.path.join(subject, cell+'_IDs.h5'),os.path.join(basepath,cell+'_IDs.h5'))
    f = h5py.File(os.path.join(basepath,cell+'_IDs.h5'), 'r')
    os.remove(os.path.join(basepath,cell+'_IDs.h5'))
    cell_ids = f['ID']
    count = 0
    X = []
    Y = []
    for cid in cell_ids:
        s3.download_file('bsmn-data',os.path.join(subject, cell+'_'+cid+'.h5'), os.path.join(basepath,cell+'_'+cid+'.h5'))
        xyz = h5py.File(os.path.join(basepath,cell+'_'+cid+'.h5'), 'r')
        os.remove(os.path.join(basepath,cell+'_'+cid+'.h5'))
        if count == 0:
            X = xyz['X'][()]
            Y = xyz['Y'][()]
            count+=1
        else:
            X = np.append(X,xyz['X'][()], axis=0)
            Y = np.append(Y,xyz['Y'][()], axis=0)
    print(X.shape)
    print(X.shape)
    Labels = [None] * len(Y)
    for i in range(0,len(Y)):
        if Y[i] in Train_Y[set1]:
            Labels[i] = T1[Y[i]]
        else:
            Labels[i] = "NotClassified"
    rm=[]
    for i in range(0,len(Labels)):
        if Labels[i] == "NotClassified":
            rm=np.append(rm,i)
    X = np.delete(X,rm,0)
    Labels = np.delete(Labels,rm,0)
    Y = np.delete(Y,rm,0)
    for l in Labels:
        if not os.path.exists(os.path.join(basepath,"Images",l)):
            os.makedirs(os.path.join(basepath,"Images",l),0755)
    for i in range(0,len(Labels)):
        im = Image.fromarray(np.uint8(X[i,:,:,:]*255),mode='RGB')
        im.save(os.path.join(basepath,"Images",Labels[i],Y[i]))
    del X
    del Y
    del Labels
