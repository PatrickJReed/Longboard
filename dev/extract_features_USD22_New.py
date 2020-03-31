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
subject = "USD22"
Cells = ["USD22_A1_S118","USD22_A2_S126","USD22_A3_S134","USD22_A4_S142","USD22_A5_S150","USD22_A6_S158","USD22_A7_S166","USD22_A8_S173","USD22_B1_S119","USD22_B2_S127","USD22_B3_S135","USD22_B4_S143","USD22_B5_S151","USD22_B6_S159","USD22_B7_S167","USD22_B8_S174","USD22_C1_S120","USD22_C2_S128","USD22_C3_S136","USD22_C4_S144","USD22_C5_S152","USD22_C6_S160","USD22_C7_S168","USD22_C8_S175","USD22_D1_S121","USD22_D2_S129","USD22_D3_S137","USD22_D4_S145","USD22_D5_S153","USD22_D6_S161","USD22_D7_S169","USD22_D8_S176","USD22_E1_S122","USD22_E2_S130","USD22_E3_S138","USD22_E4_S146","USD22_E5_S154","USD22_E6_S162","USD22_E7_S170","USD22_E8_S177","USD22_F1_S123","USD22_F2_S131","USD22_F3_S139","USD22_F4_S147","USD22_F5_S155","USD22_F6_S163","USD22_F7_S171","USD22_F8_S178","USD22_G1_S124","USD22_G2_S132","USD22_G3_S140","USD22_G4_S148","USD22_G5_S156","USD22_G6_S164","USD22_G7_S172","USD22_G8_S179","USD22_H1_S125","USD22_H2_S133","USD22_H3_S141","USD22_H4_S149","USD22_H5_S157","USD22_H6_S165"]

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
            Z = feat_extractor.predict(X, batch_size = 128)
            count+=1
            length = len(Y)
            U = [cid] * length
        else:
            X = xyz['X']
            Y = np.append(Y,xyz['Y'], axis=0)
            z = feat_extractor.predict(X, batch_size = 128)
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