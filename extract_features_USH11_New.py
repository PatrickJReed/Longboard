#!/usr/local/share/bcbio/anaconda/bin/python

from __future__ import division
import sys
import glob, os, gc
import uuid
import os.path
import csv
import numpy as np
from time import time
from subprocess import (call, Popen, PIPE)
from itertools import product
import shutil
import re
import pickle
from boto3.session import Session
import boto3
import h5py
import umap
import hdbscan
from keras.models import load_model
from keras.models import Model
from keras import backend as K

##Path to Data
basepath = "/raidixshare_log-g/longboard/"
ACCESS_KEY = 'AKIAJNNOA6QMT7HXF6GA'
SECRET_KEY = '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'
subject = "USH11" #sys.argv[1]  #subjectid
Cells = ["USH11_A1_S45","USH11_A2_S53","USH11_A3_S60","USH11_A4_S67","USH11_A5_S75","USH11_A6_S82","USH11_B1_S46","USH11_B2_S54","USH11_B3_S61","USH11_B4_S68","USH11_B5_S76","USH11_B6_S83","USH11_C1_S47","USH11_C2_S55","USH11_C3_S62","USH11_C4_S69","USH11_C5_S77","USH11_C6_S84","USH11_D1_S48","USH11_D2_S56","USH11_D3_S63","USH11_D4_S70","USH11_D5_S78","USH11_D6_S85","USH11_E1_S49","USH11_E2_S57","USH11_E4_S71","USH11_E5_S79","USH11_E6_S86","USH11_F1_S50","USH11_F4_S72","USH11_F6_S87","USH11_G1_S51","USH11_G2_S58","USH11_G3_S65","USH11_G4_S73","USH11_G5_S80","USH11_G6_S88","USH11_H1_S52","USH11_H2_S59","USH11_H4_S74","USH11_H5_S81"]

session = Session(aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
s3 = session.resource('s3') 
s3.meta.client.download_file('bsmn-data',os.path.join('Inception_Transfer_Model.h5'),os.path.join(basepath,'Inception_Transfer_Model.h5'))
feat_extractor = load_model(os.path.join(basepath,'Inception_Transfer_Model.h5'))

count = 0
for cell in Cells:
    print(cell)
    cell_size=0
    cell_ids = []
    s3.meta.client.download_file('bsmn-data',os.path.join(subject, cell+'_IDs.h5'),os.path.join(basepath,cell+'_IDs.h5'))
    f = h5py.File(os.path.join(basepath,cell+'_IDs.h5'), 'r')
    cell_ids = f['ID']
    for cid in cell_ids:
        cid = cid.decode('utf-8')
        s3.meta.client.download_file('bsmn-data',os.path.join(subject, cell+'_'+cid+'.h5'),os.path.join(basepath,cell+'_'+cid+'.h5'))
        xyz = h5py.File(os.path.join(basepath,cell+'_'+cid+'.h5'), 'r')
        os.remove(os.path.join(basepath,cell+'_'+cid+'.h5'))
        if count == 0:
            X = xyz['X']
            Y = xyz['Y']
            Z = feat_extractor.predict(X, batch_size = 16)
            count+=1
            length = len(Y)
            U = [cid] * length
        else:
            X = xyz['X']
            Y = np.append(Y,xyz['Y'], axis=0)
            z = feat_extractor.predict(X, batch_size = 16)
            Z = np.append(Z,z, axis=0)
            length = len(xyz['Y'])
            U = U + ([cid] * length)
            print(Z.shape)

hf = h5py.File(subject+'_new.h5', 'w')
hf.create_dataset('Y', data=Y)
hf.create_dataset('Z', data=Z)
hf.close()

session = Session(aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
s3 = session.resource('s3')
s3.meta.client.upload_file(os.path.join(subject+'_new.h5'),'bsmn-data',os.path.join(subject, subject+'_new.h5'))