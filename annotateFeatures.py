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
import matplotlib.pyplot as plt

##Path to Data
basepath = "/home/ubuntu/"

with open(os.path.join(basepath,"config.txt")) as f:
    config = [line.rstrip() for line in f]    
print config[0]
print config[1]


CompleteOverlap = "/home/ubuntu/Longboard/hs37d5_15K_Windows_CompleteFinal.txt"
AnyOverlap = "/home/ubuntu/Longboard/hs37d5_15K_Windows_AnyFinal.txt"

session = Session(aws_access_key_id=config[0],aws_secret_access_key=config[1])
s3 = session.resource('s3')
s3.meta.client.download_file('bsmn-data',os.path.join('Training_af.h5'),os.path.join(basepath,'Training_af.h5'))
hf = h5py.File(os.path.join(basepath,'Training_af.h5'), 'r')
Train_Y = hf['Y'][()]
Train_Z = hf['Z'][()]

Ref_Complete = {}
with open(CompleteOverlap) as fin1:
    rows = ( line.strip().split('\t') for line in fin1 )
    for row in rows:
        Ref_Complete[row[0]] = {}
        Ref_Complete[row[0]]['L1HS'] = row[1]
        Ref_Complete[row[0]]['L1PA2'] = row[2]
        Ref_Complete[row[0]]['L1PA3'] = row[3]
        Ref_Complete[row[0]]['L1PA4'] = row[4]
        Ref_Complete[row[0]]['L1PA5'] = row[5]
        Ref_Complete[row[0]]['L1Other'] = row[6]
        Ref_Complete[row[0]]['eul1db_mrip'] = row[7]
Ref_Any = {}
with open(AnyOverlap) as fin2:
    rows = ( line.strip().split('\t') for line in fin2 )
    for row in rows:
        Ref_Any[row[0]] = {}
        Ref_Any[row[0]]['L1HS'] = row[1]
        Ref_Any[row[0]]['L1PA2'] = row[2]
        Ref_Any[row[0]]['L1PA3'] = row[3]
        Ref_Any[row[0]]['L1PA4'] = row[4]
        Ref_Any[row[0]]['L1PA5'] = row[5]
        Ref_Any[row[0]]['L1Other'] = row[6]
        Ref_Any[row[0]]['eul1db_mrip'] = row[7]

L = len(Train_Z)
print(L)
T={}
for i in range(0, L):
    position_key = Train_Y[i].decode('utf8').strip().split('-')[1].split('_mod')[0]
    if position_key not in T:
        cell_id = Train_Y[i].decode('utf8').strip().split('-')[0]
        Features = Train_Z[i]
        T[position_key] = {}
        T[position_key]['Ref_Partial'] = {}
        T[position_key]['Ref_Complete'] = {}      
        T[position_key]['Ref_Partial']['L1HS'] = '0'
        if int(Ref_Any[position_key]['L1HS']) > int(Ref_Complete[position_key]['L1HS']):
            T[position_key]['Ref_Partial']['L1HS'] = '1'
        T[position_key]['Ref_Complete']['L1HS'] = '0'
        if int(Ref_Complete[position_key]['L1HS']) != 0:
            T[position_key]['Ref_Complete']['L1HS'] = '1'                  
        T[position_key]['Ref_Partial']['L1PA2'] = '0'
        if int(Ref_Any[position_key]['L1PA2']) > int(Ref_Complete[position_key]['L1PA2']):
            T[position_key]['Ref_Partial']['L1PA2'] = '1'
        T[position_key]['Ref_Complete']['L1PA2'] = '0'
        if int(Ref_Complete[position_key]['L1PA2']) != 0:
            T[position_key]['Ref_Complete']['L1PA2'] = '1'    
        T[position_key]['Ref_Partial']['eul1db_mrip'] = '0'
        if int(Ref_Any[position_key]['eul1db_mrip']) != 0:
            T[position_key]['Ref_Partial']['eul1db_mrip'] = '1'
        T[position_key]['Ref_Complete']['eul1db_mrip'] = '0'
        if int(Ref_Complete[position_key]['eul1db_mrip']) != 0:
            T[position_key]['Ref_Complete']['eul1db_mrip'] = '1'    
    if i == 0:
        Labs = T[position_key]['Ref_Partial']['L1HS']+"_"+T[position_key]['Ref_Complete']['L1HS']+"_"+T[position_key]['Ref_Partial']['L1PA2']+"_"+T[position_key]['Ref_Complete']['L1PA2']+"_"+T[position_key]['Ref_Partial']['eul1db_mrip']+"_"+T[position_key]['Ref_Complete']['eul1db_mrip']
    else:
        Labs = np.vstack((Labs,T[position_key]['Ref_Partial']['L1HS']+"_"+T[position_key]['Ref_Complete']['L1HS']+"_"+T[position_key]['Ref_Partial']['L1PA2']+"_"+T[position_key]['Ref_Complete']['L1PA2']+"_"+T[position_key]['Ref_Partial']['eul1db_mrip']+"_"+T[position_key]['Ref_Complete']['eul1db_mrip']
))        
print(len(Labs)) 

Train_d = dict([(y,x+1) for x,y in enumerate(sorted(set(Labs[:,0])))])
Train_C = [Train_d[x] for x in Labs[:,0]]

hf = h5py.File('Training_Annotated.h5', 'w')
hf.create_dataset('Y', data=Train_Y)
hf.create_dataset('Z', data=Train_Z)
hf.create_dataset('L', data=Labs)
hf.create_dataset('C', data=Train_C)
hf.close()                

s3.meta.client.upload_file(os.path.join('Training_Annotated.h5'),'bsmn-data',os.path.join('Training_Annotated.h5'))
