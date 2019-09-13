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
subject = "USD01"
Cells = ["USD01A1_S246","USD01A2_S9","USD01A3_S222","USD01A4_S230","USD01A5_S238","USD01A6_S245","USD01A7_S1","USD01B1_S247","USD01B2_S10","USD01B3_S223","USD01B4_S231","USD01B5_S239","USD01B6_S243","USD01B7_S2","USD01C1_S248","USD01C2_S11","USD01C3_S224","USD01C4_S232","USD01C5_S240","USD01C6_S237","USD01C7_S3","USD01D1_S249","USD01D2_S12","USD01D3_S225","USD01D4_S233","USD01D5_S241","USD01D6_S17","USD01D7_S4","USD01E1_S250","USD01E2_S13","USD01E3_S226","USD01E4_S234","USD01E5_S242","USD01E6_S18","USD01F1_S251","USD01F2_S14","USD01F3_S227","USD01F4_S235","USD01F6_S6","USD01G1_S252","USD01G3_S228","USD01G4_S236","USD01G5_S244","USD01G6_S7","USD01H1_S253","USD01H2_S16","USD01H3_S229","USD01H5_S8"]

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

#call(['sudo', 'shutdown', '-h', 'now'])
