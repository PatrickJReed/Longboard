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

#Path to Data
basepath = "/home/ubuntu/"
genome_regions = "longboard/hs37d5_15K_Windows.bed"
L1HS = "/home/ubuntu/longboard/rmask_L1HS_Correct.bed"
ACCESS_KEY = 'AKIAJNNOA6QMT7HXF6GA'
SECRET_KEY = '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'
CompleteOverlap = "/home/ubuntu/longboard/hs37d5_15K_Windows_CompleteFinal.txt"
AnyOverlap = "/home/ubuntu/longboard/hs37d5_15K_Windows_AnyFinal.txt"
subject = "USD37" #sys.argv[1]  #subjectid
Cells = ["USD37_A1_S44","USD37_A2_S52","USD37_A3_S59","USD37_A4_S67","USD37_A5_S14","USD37_A6_S22","USD37_A7_S29","USD37_B1_S45","USD37_B2_S53","USD37_B3_S60","USD37_B4_S68","USD37_B5_S15","USD37_B6_S23","USD37_B7_S30","USD37_B8_S37","USD37_C1_S46","USD37_C2_S54","USD37_C3_S61","USD37_C4_S69","USD37_C5_S16","USD37_C6_S24","USD37_C7_S31","USD37_C8_S38","USD37_D1_S47","USD37_D2_S55","USD37_D3_S62","USD37_D4_S70","USD37_D5_S17","USD37_D6_S25","USD37_D7_S32","USD37_D8_S39","USD37_E1_S48","USD37_E2_S56","USD37_E3_S63","USD37_E4_S71","USD37_E5_S18","USD37_E6_S26","USD37_E7_S33","USD37_E8_S40","USD37_F1_S49","USD37_F2_S57","USD37_F3_S64","USD37_F4_S72","USD37_F5_S19","USD37_F6_S27","USD37_F7_S34","USD37_F8_S41","USD37_G1_S50","USD37_G3_S65","USD37_G4_S73","USD37_G5_S20","USD37_G7_S35","USD37_G8_S42","USD37_H1_S51","USD37_H2_S58","USD37_H3_S66","USD37_H4_S74","USD37_H5_S21","USD37_H6_S28","USD37_H7_S36","USD37_H8_S43"]

session = Session(aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
s3 = session.resource('s3') 
s3.meta.client.download_file('bsmn-data',os.path.join('feat_extractor.h5'),os.path.join(basepath,'feat_extractor.h5'))
feat_extractor = load_model(os.path.join(basepath,'feat_extractor.h5'))

count = 0
for cell in Cells:
    print(cell)
    cell_size=0
    cell_ids = []
    s3.meta.client.download_file('bsmn-data',os.path.join(subject, cell+'_IDs.h5'),os.path.join(basepath,cell+'_IDs.h5'))
    f = h5py.File(os.path.join(basepath,cell+'_IDs.h5'), 'r')
    cell_ids = f['ID']
    for cid in cell_ids:
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
            print Z.shape

hf = h5py.File(subject+'.h5', 'w')
hf.create_dataset('Y', data=Y)
hf.create_dataset('Z', data=Z)
hf.create_dataset('U', data=U)
hf.close()

session = Session(aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
s3 = session.resource('s3')
s3.meta.client.upload_file(os.path.join(subject+'.h5'),'bsmn-data',os.path.join(subject, subject+'.h5'))

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
        
L = len(Z)
T={}
for i in range(0, L):
    position_key = Y[i].strip().split('-')[1].split('_mod')[0]
    cell_id = Y[i].strip().split('-')[0]
    Features = Z[i]
    if position_key in T:
        T[position_key]['Cell_Data'][cell_id] = {}
        T[position_key]['count'] = T[position_key].get('count') + 1
        T[position_key]['Cell_Data'][cell_id]['Features'] = Features
        T[position_key]['Cell_Data'][cell_id]['cid'] = U[i]       
    else:
        T[position_key] = {}
        T[position_key]['count'] = 1
        T[position_key]['Ref_All'] = {}
        T[position_key]['Ref_Complete'] = {}
        T[position_key]['Ref_All']['L1HS'] = Ref_Any[position_key]['L1HS']
        T[position_key]['Ref_Complete']['L1HS'] = Ref_Complete[position_key]['L1HS']           
        
        T[position_key]['Ref_All']['L1PA2'] = Ref_Any[position_key]['L1PA2']
        T[position_key]['Ref_Complete']['L1PA2'] = '0'
        if int(Ref_Complete[position_key]['L1PA2']) != 0:
            T[position_key]['Ref_Complete']['L1PA2'] = '1'
        
        T[position_key]['Ref_All']['eul1db_mrip'] = Ref_Any[position_key]['eul1db_mrip']
        T[position_key]['Ref_Complete']['eul1db_mrip'] = '0'
        if int(Ref_Complete[position_key]['eul1db_mrip']) != 0:
            T[position_key]['Ref_Complete']['eul1db_mrip'] = '1'
            
        T[position_key]['Cell_Data'] = {}
        T[position_key]['Cell_Data'][cell_id] = {}
        T[position_key]['Cell_Data'][cell_id]['Features'] = Features
        T[position_key]['Cell_Data'][cell_id]['cid'] = U[i]
    if i == 0:
        Labs = T[position_key]['Ref_Complete']['L1HS']+"_"+T[position_key]['Ref_Complete']['L1PA2']+"_"+T[position_key]['Ref_Complete']['eul1db_mrip']
    else:
        Labs = np.vstack((Labs,T[position_key]['Ref_Complete']['L1HS']+"_"+T[position_key]['Ref_Complete']['L1PA2']+"_"+T[position_key]['Ref_Complete']['eul1db_mrip']))        
        
f = open(subject+".pkl","wb")
pickle.dump([T,Labs],f)
f.close()        

session = Session(aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
s3 = session.resource('s3')
s3.meta.client.upload_file(os.path.join(subject+".pkl"),'bsmn-data',os.path.join(subject, subject+".pkl"))

call(['sudo', 'shutdown', '-h', 'now'])