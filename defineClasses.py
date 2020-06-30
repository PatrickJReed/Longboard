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
import seaborn as sns



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

vals = np.arange(0,Train_Z.shape[0],1)
np.random.shuffle(vals)

set1 = vals[0:1592902]
set2 = vals[1592902:3185804]

print set1.shape
print set2.shape

Train_Z_1 = Train_Z[set1,:]
Train_C_1 = Train_C[set1]

Train_Z_2 = Train_Z[set2,:]
Train_C_2 = Train_C[set2]

print Train_Z_1.shape
print Train_Z_2.shape

print Train_C_1.shape
print Train_C_2.shape

embedding_partialsupervised_1 = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Train_Z_1, y=Train_C_1)
embedding_partialsupervised_2 = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Train_Z_2, y=Train_C_2)


hf = h5py.File('Training_UMAP_2Set.h5', 'w')
hf.create_dataset('Y', data=Train_Y)
hf.create_dataset('Z', data=Train_Z)
hf.create_dataset('C', data=Train_C)##just basic classes
hf.create_dataset('set1', data=set1)
hf.create_dataset('set2', data=set2)
hf.create_dataset('embedding_partialsupervised_1', data=embedding_partialsupervised_1)
hf.create_dataset('embedding_partialsupervised_2', data=embedding_partialsupervised_2)
hf.close()

session = Session(aws_access_key_id=config[0],aws_secret_access_key=config[1])
s3 = session.resource('s3')
s3.meta.client.upload_file(os.path.join('Training_UMAP_2Set.h5'),'bsmn-data',os.path.join('Training_UMAP_2Set.h5'))

HDB_1 = hdbscan.HDBSCAN(min_samples=14,min_cluster_size=5000,prediction_data=True).fit_predict(embedding_partialsupervised_1)
HDB_2 = hdbscan.HDBSCAN(min_samples=14,min_cluster_size=5000,prediction_data=True).fit_predict(embedding_partialsupervised_2)

session = Session(aws_access_key_id=config[0],aws_secret_access_key=config[1])
s3 = session.resource('s3')
hf = h5py.File('Training_UMAP_HDB_2Set.h5', 'w')
hf.create_dataset('Y', data=Train_Y)
hf.create_dataset('Z', data=Train_Z)
hf.create_dataset('C', data=Train_C)
hf.create_dataset('set1', data=set1)
hf.create_dataset('set2', data=set2)
hf.create_dataset('embedding_partialsupervised_1', data=embedding_partialsupervised_1)
hf.create_dataset('embedding_partialsupervised_2', data=embedding_partialsupervised_2)
hf.create_dataset('HDB_1', data=HDB_1)
hf.create_dataset('HDB_2', data=HDB_2)
hf.close()
s3.meta.client.upload_file(os.path.join('Training_UMAP_HDB_2Set.h5'),'bsmn-data',os.path.join('Training_UMAP_HDB_2Set.h5'))
