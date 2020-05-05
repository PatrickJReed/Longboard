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
genome_regions = "hs37d5_15K_Windows.bed"
L1HS_bam = "-L1HS_mapped.bam"
L1HS_bam_bai = "-L1HS_mapped.bam.bai"
L1HS = "/home/ubuntu/Longboard/rmask_L1HS_Correct.bed"
L1HScoverage = ".L1HScoverage"
L1HScoverage_gt100 = ".L1HScoverage_gt100"
bam = "-ready.bam"
bai = "-ready.bam.bai"
bed = ".bed"
loci = ".loci"


with open(os.path.join(basepath,"config.txt")) as f:
    config = [line.rstrip() for line in f]    

session = Session(aws_access_key_id=config[0],aws_secret_access_key=config[1])
s3 = session.resource('s3') 
s3.meta.client.download_file('bsmn-data',os.path.join('Training_All_Labeled.h5'),os.path.join('Training_All_Labeled.h5'))
hf = h5py.File(os.path.join('Training_All_Labeled.h5'), 'r')
Train_Z = hf['Z'][()] 
Train_C = hf['C'][()]
Train_Y = hf['Y'][()]
Labs = hf['L'][()]

Train_d = dict([(y,x+1) for x,y in enumerate(sorted(set(Labs[:,0])))])
Train_C = [Train_d[x] for x in Labs[:,0]]

embedding_unsupervised = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Train_Z[1:1500000,:])

hf = h5py.File('Training_Unsupervised_All.h5', 'w')
hf.create_dataset('Y', data=Train_Y[1:1500000])
hf.create_dataset('Z', data=Train_Z[1:1500000,:])
hf.create_dataset('C', data=Train_C[1:1500000])
hf.create_dataset('embedding_unsupervised', data=embedding_unsupervised)
hf.close()                
s3.meta.client.upload_file(os.path.join('Training_Unsupervised_All.h5'),'bsmn-data',os.path.join('Training_Unsupervised_All.h5'))


embedding_partialsupervised = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Train_Z[1:1500000,:], y=Train_C[1:1500000])

hf = h5py.File('Training_partialsupervised_All.h5', 'w')
hf.create_dataset('Y', data=Train_Y[1:1500000])
hf.create_dataset('Z', data=Train_Z[1:1500000,:])
hf.create_dataset('C', data=Train_C[1:1500000])
hf.create_dataset('embedding_partialsupervised', data=embedding_partialsupervised)
hf.close()                
s3.meta.client.upload_file(os.path.join('Training_partialsupervised_All.h5'),'bsmn-data',os.path.join('Training_partialsupervised_All.h5'))

C = np.asarray(Train_C)

Z_Class_12 = Train_Z[C==12]
C_Class_12 = C[C==12]
Y_Class_12 = Train_Y[C==12]
L_Class_12 = Labs[C==12]
umap_Class_12 = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Z_Class_12)
hf = h5py.File('Training_Class_12.h5', 'w')
hf.create_dataset('Y_12', data=Y_Class_12)
hf.create_dataset('Z_12', data=Z_Class_12)
hf.create_dataset('Umap_12', data=umap_Class_12)
hf.close()                
s3.meta.client.upload_file(os.path.join('Training_Class_12.h5'),'bsmn-data',os.path.join('Training_Class_12.h5'))

Z_Class_21 = Train_Z[C==21]
C_Class_21 = C[C==21]
Y_Class_21 = Train_Y[C==21]
L_Class_21 = Labs[C==21]
umap_Class_21 = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Z_Class_21)
hf = h5py.File('Training_Class_21.h5', 'w')
hf.create_dataset('Y_21', data=Y_Class_21)
hf.create_dataset('Z_21', data=Z_Class_21)
hf.create_dataset('Umap_21', data=umap_Class_21)
hf.close()                
s3.meta.client.upload_file(os.path.join('Training_Class_21.h5'),'bsmn-data',os.path.join('Training_Class_21.h5'))

Z_Class_1 = Train_Z[C==1]
C_Class_1 = C[C==1]
Y_Class_1 = Train_Y[C==1]
L_Class_1 = Labs[C==1]
umap_Class_1 = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Z_Class_1)
hf = h5py.File('Training_Class_1.h5', 'w')
hf.create_dataset('Y_1', data=Y_Class_1)
hf.create_dataset('Z_1', data=Z_Class_1)
hf.create_dataset('Umap_1', data=umap_Class_1)
hf.close()                
s3.meta.client.upload_file(os.path.join('Training_Class_1.h5'),'bsmn-data',os.path.join('Training_Class_1.h5'))

Z_Class_3 = Train_Z[C==3]
C_Class_3 = C[C==3]
Y_Class_3 = Train_Y[C==3]
L_Class_3 = Labs[C==3]
umap_Class_3 = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Z_Class_3)
hf = h5py.File('Training_Class_3.h5', 'w')
hf.create_dataset('Y_3', data=Y_Class_3)
hf.create_dataset('Z_3', data=Z_Class_3)
hf.create_dataset('Umap_3', data=umap_Class_3)
hf.close()                
s3.meta.client.upload_file(os.path.join('Training_Class_3.h5'),'bsmn-data',os.path.join('Training_Class_3.h5'))

Z_Class_4 = Train_Z[C==4]
C_Class_4 = C[C==4]
Y_Class_4 = Train_Y[C==4]
L_Class_4 = Labs[C==4]
umap_Class_4 = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Z_Class_4)
hf = h5py.File('Training_Class_4.h5', 'w')
hf.create_dataset('Y_4', data=Y_Class_4)
hf.create_dataset('Z_4', data=Z_Class_4)
hf.create_dataset('Umap_4', data=umap_Class_4)
hf.close()                
s3.meta.client.upload_file(os.path.join('Training_Class_4.h5'),'bsmn-data',os.path.join('Training_Class_4.h5'))

Z_Class_10 = Train_Z[C==10]
C_Class_10 = C[C==10]
Y_Class_10 = Train_Y[C==10]
L_Class_10 = Labs[C==10]
umap_Class_10 = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Z_Class_10)
hf = h5py.File('Training_Class_10.h5', 'w')
hf.create_dataset('Y_10', data=Y_Class_10)
hf.create_dataset('Z_10', data=Z_Class_10)
hf.create_dataset('Umap_10', data=umap_Class_10)
hf.close()                
s3.meta.client.upload_file(os.path.join('Training_Class_10.h5'),'bsmn-data',os.path.join('Training_Class_10.h5'))


Z_Class_28 = Train_Z[C==28]
C_Class_28 = C[C==28]
Y_Class_28 = Train_Y[C==28]
L_Class_28 = Labs[C==28]
umap_Class_28 = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Z_Class_28)
hf = h5py.File('Training_Class_28.h5', 'w')
hf.create_dataset('Y_28', data=Y_Class_28)
hf.create_dataset('Z_28', data=Z_Class_28)
hf.create_dataset('Umap_28', data=umap_Class_28)
hf.close()                
s3.meta.client.upload_file(os.path.join('Training_Class_28.h5'),'bsmn-data',os.path.join('Training_Class_28.h5'))

Z_Class_14 = Train_Z[C==14]
C_Class_14 = C[C==14]
Y_Class_14 = Train_Y[C==14]
L_Class_14 = Labs[C==14]
umap_Class_14 = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Z_Class_14)
hf = h5py.File('Training_Class_14.h5', 'w')
hf.create_dataset('Y_14', data=Y_Class_14)
hf.create_dataset('Z_14', data=Z_Class_14)
hf.create_dataset('Umap_14', data=umap_Class_14)
hf.close()                
s3.meta.client.upload_file(os.path.join('Training_Class_14.h5'),'bsmn-data',os.path.join('Training_Class_14.h5'))

Z_Class_13 = Train_Z[C==13]
C_Class_13 = C[C==13]
Y_Class_13 = Train_Y[C==13]
L_Class_13 = Labs[C==13]
umap_Class_13 = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Z_Class_13)
hf = h5py.File('Training_Class_13.h5', 'w')
hf.create_dataset('Y_13', data=Y_Class_13)
hf.create_dataset('Z_13', data=Z_Class_13)
hf.create_dataset('Umap_13', data=umap_Class_13)
hf.close()                
s3.meta.client.upload_file(os.path.join('Training_Class_13.h5'),'bsmn-data',os.path.join('Training_Class_13.h5'))

Z_Class_16 = Train_Z[C==16]
C_Class_16 = C[C==16]
Y_Class_16 = Train_Y[C==16]
L_Class_16 = Labs[C==16]
umap_Class_16 = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Z_Class_16)
hf = h5py.File('Training_Class_16.h5', 'w')
hf.create_dataset('Y_16', data=Y_Class_16)
hf.create_dataset('Z_16', data=Z_Class_16)
hf.create_dataset('Umap_16', data=umap_Class_16)
hf.close()                
s3.meta.client.upload_file(os.path.join('Training_Class_16.h5'),'bsmn-data',os.path.join('Training_Class_16.h5'))

Z_Class_20 = Train_Z[C==20]
C_Class_20 = C[C==20]
Y_Class_20 = Train_Y[C==20]
L_Class_20 = Labs[C==20]
umap_Class_20 = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Z_Class_20)
hf = h5py.File('Training_Class_20.h5', 'w')
hf.create_dataset('Y_20', data=Y_Class_20)
hf.create_dataset('Z_20', data=Z_Class_20)
hf.create_dataset('Umap_20', data=umap_Class_20)
hf.close()                
s3.meta.client.upload_file(os.path.join('Training_Class_20.h5'),'bsmn-data',os.path.join('Training_Class_20.h5'))

Z_Class_23 = Train_Z[C==23]
C_Class_23 = C[C==23]
Y_Class_23 = Train_Y[C==23]
L_Class_23 = Labs[C==23]
umap_Class_23 = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Z_Class_23)
hf = h5py.File('Training_Class_23.h5', 'w')
hf.create_dataset('Y_23', data=Y_Class_23)
hf.create_dataset('Z_23', data=Z_Class_23)
hf.create_dataset('Umap_23', data=umap_Class_23)
hf.close()                
s3.meta.client.upload_file(os.path.join('Training_Class_23.h5'),'bsmn-data',os.path.join('Training_Class_23.h5'))

Z_Class_7 = Train_Z[C==7]
C_Class_7 = C[C==7]
Y_Class_7 = Train_Y[C==7]
L_Class_7 = Labs[C==7]
umap_Class_7 = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Z_Class_7)
hf = h5py.File('Training_Class_7.h5', 'w')
hf.create_dataset('Y_7', data=Y_Class_7)
hf.create_dataset('Z_7', data=Z_Class_7)
hf.create_dataset('Umap_7', data=umap_Class_7)
hf.close()                
s3.meta.client.upload_file(os.path.join('Training_Class_7.h5'),'bsmn-data',os.path.join('Training_Class_7.h5'))

Z_Class_5 = Train_Z[C==5]
C_Class_5 = C[C==5]
Y_Class_5 = Train_Y[C==5]
L_Class_5 = Labs[C==5]
umap_Class_5 = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Z_Class_5)
hf = h5py.File('Training_Class_5.h5', 'w')
hf.create_dataset('Y_5', data=Y_Class_5)
hf.create_dataset('Z_5', data=Z_Class_5)
hf.create_dataset('Umap_5', data=umap_Class_5)
hf.close()                
s3.meta.client.upload_file(os.path.join('Training_Class_5.h5'),'bsmn-data',os.path.join('Training_Class_5.h5'))

Z_Class_6 = Train_Z[C==6]
C_Class_6 = C[C==6]
Y_Class_6 = Train_Y[C==6]
L_Class_6 = Labs[C==6]
umap_Class_6 = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Z_Class_6)
hf = h5py.File('Training_Class_6.h5', 'w')
hf.create_dataset('Y_6', data=Y_Class_6)
hf.create_dataset('Z_6', data=Z_Class_6)
hf.create_dataset('Umap_6', data=umap_Class_6)
hf.close()                
s3.meta.client.upload_file(os.path.join('Training_Class_6.h5'),'bsmn-data',os.path.join('Training_Class_6.h5'))
 
Z_Class_19 = Train_Z[C==19]
C_Class_19 = C[C==19]
Y_Class_19 = Train_Y[C==19]
L_Class_19 = Labs[C==19]
umap_Class_19 = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Z_Class_19)
hf = h5py.File('Training_Class_19.h5', 'w')
hf.create_dataset('Y_19', data=Y_Class_19)
hf.create_dataset('Z_19', data=Z_Class_19)
hf.create_dataset('Umap_19', data=umap_Class_19)
hf.close()                
s3.meta.client.upload_file(os.path.join('Training_Class_19.h5'),'bsmn-data',os.path.join('Training_Class_19.h5'))




