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


##Path to Data
basepath = "/home/ubuntu/"
genome_regions = "longboard/hs37d5_15K_Windows.bed"
L1HS = "/home/ubuntu/longboard/rmask_L1HS_Correct.bed"
ACCESS_KEY = 'AKIAJNNOA6QMT7HXF6GA'
SECRET_KEY = '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'
CompleteOverlap = "/home/ubuntu/longboard/hs37d5_15K_Windows_CompleteFinal.txt"
AnyOverlap = "/home/ubuntu/longboard/hs37d5_15K_Windows_AnyFinal.txt"

Training = ["USD22", "USD01", "USD11","USD25","USD30","USD37", "USH12"]
Testing = ["USD3","USH11","USD41"]

session = Session(aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
s3 = session.resource('s3') 
count = 0
for subject in Training:
    print(subject)
    s3.meta.client.download_file('bsmn-data',os.path.join(subject, subject+'.h5'),os.path.join(basepath,subject+'.h5'))
    s3.meta.client.download_file('bsmn-data',os.path.join(subject, subject+'.pkl'),os.path.join(basepath,subject+'.pkl'))
    hf = h5py.File(os.path.join(basepath,subject+'.h5'), 'r')
    if count == 0:
        Train_Y = hf['Y']
        Train_Z = hf['Z']
        Train_U = hf['U']
        with open(os.path.join(basepath,subject+'.pkl'), 'rb') as f:
            Train_T, Train_Labs = pickle.load(f)
        count+=1
    else:
        Train_Y = np.append(Train_Y,hf['Y'], axis=0)
        Train_Z = np.append(Train_Z,hf['Z'], axis=0)
        Train_U = np.append(Train_U,hf['U'], axis=0)
        with open(os.path.join(basepath,subject+'.pkl'), 'rb') as f:
            T_tmp, Labs_tmp = pickle.load(f)
        Train_Labs = np.append(Train_Labs,Labs_tmp, axis=0)

count = 0
for subject in Testing:
    print(subject)
    s3.meta.client.download_file('bsmn-data',os.path.join(subject, subject+'.h5'),os.path.join(basepath,subject+'.h5'))
    s3.meta.client.download_file('bsmn-data',os.path.join(subject, subject+'.pkl'),os.path.join(basepath,subject+'.pkl'))
    hf = h5py.File(os.path.join(basepath,subject+'.h5'), 'r')
    if count == 0:
        Test_Y = hf['Y']
        Test_Z = hf['Z']
        Test_U = hf['U']
        with open(os.path.join(basepath,subject+'.pkl'), 'rb') as f:
            Test_T, Test_Labs = pickle.load(f)
        count+=1
    else:
        Test_Y = np.append(Test_Y,hf['Y'], axis=0)
        Test_Z = np.append(Test_Z,hf['Z'], axis=0)
        Test_U = np.append(Test_U,hf['U'], axis=0)
        with open(os.path.join(basepath,subject+'.pkl'), 'rb') as f:
            T_tmp, Labs_tmp = pickle.load(f)
        Test_Labs = np.append(Test_Labs,Labs_tmp, axis=0)        

Train_d = dict([(y,x+1) for x,y in enumerate(sorted(set(Train_Labs[:,0])))])
Train_C = [Train_d[x] for x in Train_Labs[:,0]]        
        
for i in range(len(Train_C)):
    if Train_C[i] not in (1,2,3,5,6,10):
        Train_C[i] = -1
        
Train_embedding_unsupervised = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Train_Z)

Train_embedding_partialsupervised = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Train_Z, y=Train_C)

Train_labels = hdbscan.HDBSCAN(min_samples=10,min_cluster_size=3000).fit_predict(Train_embedding_partialsupervised)

hf = h5py.File('Training.h5', 'w')
hf.create_dataset('Y', data=Train_Y)
hf.create_dataset('Z', data=Train_Z)
hf.create_dataset('U', data=Train_U)
hf.create_dataset('L', data=Train_Labs)
hf.create_dataset('C', data=Train_C)
hf.create_dataset('Umap_Partial', data=Train_embedding_partialsupervised)
hf.create_dataset('Umap_Unsupervised', data=Train_embedding_unsupervised)
hf.create_dataset('HDB', data=Train_labels)
hf.close()                

s3.meta.client.upload_file(os.path.join('Training.h5'),'bsmn-data',os.path.join('Training.h5'))

Test_d = dict([(y,x+1) for x,y in enumerate(sorted(set(Test_Labs[:,0])))])
Test_C = [Test_d[x] for x in Test_Labs[:,0]]        
        
for i in range(len(Test_C)):
    if Test_C[i] not in (1,2,3,5,6,10):
        Test_C[i] = -1

Test_embedding_unsupervised = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Test_Z)

Test_embedding_partialsupervised = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Test_Z, y=Test_C)

Test_labels = hdbscan.HDBSCAN(min_samples=10,min_cluster_size=3000).fit_predict(Test_embedding_partialsupervised)

hf = h5py.File('Test.h5', 'w')
hf.create_dataset('Y', data=Test_Y)
hf.create_dataset('Z', data=Test_Z)
hf.create_dataset('U', data=Test_U)
hf.create_dataset('L', data=Test_Labs)
hf.create_dataset('Umap_Partial', data=Test_embedding_partialsupervised)
hf.create_dataset('Umap_Unsupervised', data=Test_embedding_unsupervised)
hf.create_dataset('HDB', data=Test_labels)
hf.close()                

s3.meta.client.upload_file(os.path.join('Test.h5'),'bsmn-data',os.path.join('Test.h5'))


call(['sudo', 'shutdown', '-h', 'now'])