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
subject = "USH12"
Cells = ["USH12_A1_S177","USH12_A2_S185","USH12_A3_S193","USH12_A4_S200","USH12_A5_S207","USH12_A6_S214","USH12_A7_S284","USH12_A8_S292","USH12_B1_S178","USH12_B2_S186","USH12_B3_S194","USH12_B4_S201","USH12_B5_S208","USH12_B6_S215","USH12_B7_S285","USH12_C1_S179","USH12_C2_S187","USH12_C3_S195","USH12_C4_S202","USH12_C5_S209","USH12_C6_S216","USH12_C7_S286","USH12_C8_S293","USH12_D1_S180","USH12_D2_S188","USH12_D3_S196","USH12_D4_S203","USH12_D5_S210","USH12_D6_S217","USH12_D7_S287","USH12_D8_S294","USH12_E1_S181","USH12_E2_S189","USH12_E3_S197","USH12_E4_S204","USH12_E5_S211","USH12_E6_S218","USH12_E7_S288","USH12_E8_S295","USH12_F1_S182","USH12_F2_S190","USH12_F3_S198","USH12_F4_S205","USH12_F5_S212","USH12_F6_S219","USH12_F7_S289","USH12_F8_S296","USH12_G1_S183","USH12_G2_S191","USH12_G3_S199","USH12_G4_S206","USH12_G6_S220","USH12_G7_S290","USH12_G8_S297","USH12_H1_S184","USH12_H2_S192","USH12_H5_S213","USH12_H6_S221","USH12_H7_S291","USH12_H8_S298"]

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