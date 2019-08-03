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
from MulticoreTSNE import MulticoreTSNE as TSNE
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
subject = "USD25" #sys.argv[1]  #subjectid
Cells = ["USD25A1_S65","USD25A2_S73","USD25A3_S198","USD25A5_S81","USD25A6_S89","USD25B1_S66","USD25B2_S74","USD25B3_S199","USD25B5_S82","USD25B6_S90","USD25C1_S67","USD25C2_S75","USD25C3_S200","USD25C5_S83","USD25C6_S91","USD25C8_S217","USD25D1_S68","USD25D2_S76","USD25D3_S201","USD25D4_S209","USD25D5_S84","USD25D6_S92","USD25D7_S214","USD25D8_S218","USD25E1_S69","USD25E2_S77","USD25E3_S202","USD25E5_S85","USD25E6_S93","USD25E7_S215","USD25E8_S219","USD25F1_S70","USD25F2_S78","USD25F3_S203","USD25F5_S86","USD25F6_S94","USD25G1_S71","USD25G2_S79","USD25G3_S204","USD25G5_S87","USD25G6_S95","USD25H1_S72","USD25H2_S80","USD25H3_S205","USD25H5_S88","USD25H6_S96"]

session = Session(aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
s3 = session.resource('s3') 
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
            Y = xyz['Y']
            Z = xyz['Z']
            count+=1
            length = len(Y)
            U = [cid] * length
        else:
            Y = np.append(Y,xyz['Y'], axis=0)
            Z = np.append(Z,xyz['Z'], axis=0)
            length = len(xyz['Y'])
            U = U + ([cid] * length)

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