#!/home/ubuntu/miniconda2/bin/python

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
basepath = "/home/ubuntu/"
ACCESS_KEY = 'AKIAJNNOA6QMT7HXF6GA'
SECRET_KEY = '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'
subject =  "USD37" #sys.argv[1]  #subjectid
Cells = ["USD37_A1_S44"] #sys.argv[2] #input
ACCESS_KEY = 'AKIAJNNOA6QMT7HXF6GA'
SECRET_KEY = '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'

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
#hf.create_dataset('U', data=U)
hf.close()

session = Session(aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
s3 = session.resource('s3')
s3.meta.client.upload_file(os.path.join(subject+'_new.h5'),'bsmn-data',os.path.join(subject, subject+'_new.h5'))



#call(['sudo', 'shutdown', '-h', 'now'])