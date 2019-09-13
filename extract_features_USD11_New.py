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
subject = "USD11" #sys.argv[1]  #subjectid
Cells = ["USD11A1_S105","USD11A2_S169","USD11A3_S97","USD11A4_S161","USD11A5_S113","USD11A6_S121","USD11B1_S106","USD11B2_S170","USD11B3_S98","USD11B4_S162","USD11B5_S114","USD11B6_S122","USD11C1_S107","USD11C2_S171","USD11C3_S99","USD11C4_S163","USD11C5_S115","USD11C6_S123","USD11D1_S108","USD11D2_S172","USD11D3_S100","USD11D4_S164","USD11D5_S116","USD11D6_S124","USD11E1_S109","USD11E2_S173","USD11E3_S101","USD11E4_S165","USD11E5_S117","USD11E6_S125","USD11F1_S110","USD11F2_S174","USD11F3_S102","USD11F4_S166","USD11F5_S118","USD11F6_S126","USD11G1_S111","USD11G2_S175","USD11G3_S103","USD11G4_S167","USD11G5_S119","USD11G6_S127","USD11H1_S112","USD11H2_S176","USD11H3_S104","USD11H4_S168","USD11H5_S120","USD11H6_S128"]

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
