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


session = Session(aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
s3 = session.resource('s3') 

s3.meta.client.download_file('bsmn-data',os.path.join('Training_All_New.h5'),os.path.join('Training_All_New.h5'))
hf = h5py.File(os.path.join('Training_All_New.h5'), 'r')
Train_Z = hf['Z'][()] 
Train_C = hf['C'][()]
Train_Y = hf['Y'][()]
Train_U = hf['U'][()]
Labs = hf['L'][()]

#Subest each by Class

C = np.asarray(Train_C)

Z_Class_1 = Train_Z[C==1]
C_Class_1 = C[C==1]
Y_Class_1 = Train_Y[C==1]
U_Class_1 = Train_U[C==1]
L_Class_1 = Labs[C==1]

Z_Class_2 = Train_Z[C==2]
C_Class_2 = C[C==2]
Y_Class_2 = Train_Y[C==2]
U_Class_2 = Train_U[C==2]
L_Class_2 = Labs[C==2]

Z_Class_3 = Train_Z[C==3]
C_Class_3 = C[C==3]
Y_Class_3 = Train_Y[C==3]
U_Class_3 = Train_U[C==3]
L_Class_3 = Labs[C==3]

Z_Class_5 = Train_Z[C==5]
C_Class_5 = C[C==5]
Y_Class_5 = Train_Y[C==5]
U_Class_5 = Train_U[C==5]
L_Class_5 = Labs[C==5]

Z_Class_6 = Train_Z[C==6]
C_Class_6 = C[C==6]
Y_Class_6 = Train_Y[C==6]
U_Class_6 = Train_U[C==6]
L_Class_6 = Labs[C==6]
 
Z_Class_9 = Train_Z[C==9]
C_Class_9 = C[C==9]
Y_Class_9 = Train_Y[C==9]
U_Class_9 = Train_U[C==9]
L_Class_9 = Labs[C==9]

Z_Class_13 = Train_Z[C==13]
C_Class_13 = C[C==13]
Y_Class_13 = Train_Y[C==13]
U_Class_13 = Train_U[C==13]
L_Class_13 = Labs[C==13]




umap_Class_1 = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Z_Class_1)
umap_Class_2 = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Z_Class_2)
umap_Class_3 = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Z_Class_3)
umap_Class_5 = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Z_Class_5)
umap_Class_6 = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Z_Class_6)
umap_Class_9 = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Z_Class_9)
umap_Class_13 = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Z_Class_13)


#Train_labels = hdbscan.HDBSCAN(min_samples=13,min_cluster_size=5000).fit_predict(Train_embedding_partialsupervised)

hf = h5py.File('Training_All_Final.h5', 'w')
hf.create_dataset('Y_1', data=Y_Class_1)
hf.create_dataset('Z_1', data=Z_Class_1)
hf.create_dataset('U_1', data=U_Class_1)
hf.create_dataset('Y_2', data=Y_Class_2)
hf.create_dataset('Z_2', data=Z_Class_2)
hf.create_dataset('U_2', data=U_Class_2)
hf.create_dataset('Y_3', data=Y_Class_3)
hf.create_dataset('Z_3', data=Z_Class_3)
hf.create_dataset('U_3', data=U_Class_3)
hf.create_dataset('Y_5', data=Y_Class_5)
hf.create_dataset('Z_5', data=Z_Class_5)
hf.create_dataset('U_5', data=U_Class_5)
hf.create_dataset('Y_6', data=Y_Class_6)
hf.create_dataset('Z_6', data=Z_Class_6)
hf.create_dataset('U_6', data=U_Class_6)
hf.create_dataset('Y_9', data=Y_Class_9)
hf.create_dataset('Z_9', data=Z_Class_9)
hf.create_dataset('U_9', data=U_Class_9)
hf.create_dataset('Y_13', data=Y_Class_13)
hf.create_dataset('Z_13', data=Z_Class_13)
hf.create_dataset('U_13', data=U_Class_13)
hf.create_dataset('Umap_1', data=umap_Class_1)
hf.create_dataset('Umap_2', data=umap_Class_2)
hf.create_dataset('Umap_3', data=umap_Class_3)
hf.create_dataset('Umap_5', data=umap_Class_5)
hf.create_dataset('Umap_6', data=umap_Class_6)
hf.create_dataset('Umap_9', data=umap_Class_9)
hf.create_dataset('Umap_13', data=umap_Class_13)

hf.close()                

s3.meta.client.upload_file(os.path.join('Training_All_Final.h5'),'bsmn-data',os.path.join('Training_All_Final.h5'))

call(['sudo', 'shutdown', '-h', 'now'])