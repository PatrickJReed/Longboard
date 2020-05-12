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


embedding_partialsupervised = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Train_Z, y=Train_C)

hf = h5py.File('Training_partialsupervised_All.h5', 'w')
hf.create_dataset('Y', data=Train_Y)
hf.create_dataset('Z', data=Train_Z)
hf.create_dataset('C', data=Train_C)
hf.create_dataset('embedding_partialsupervised', data=embedding_partialsupervised)
hf.close()                
s3.meta.client.upload_file(os.path.join('Training_partialsupervised_All.h5'),'bsmn-data',os.path.join('Training_partialsupervised_All.h5'))

unique, counts = np.unique(C, return_counts=True)
print dict(zip(unique, counts))

fig, ax = plt.subplots(1, figsize=(14, 10))
plt.scatter(embedding_partialsupervised[:,0],embedding_partialsupervised[:,1], s=0.3, alpha=1)
plt.setp(ax, xticks=[], yticks=[])
plt.savefig('fig0.pdf') 

fig, ax = plt.subplots(1, figsize=(14, 10))
plt.scatter(embedding_partialsupervised[:,0],embedding_partialsupervised[:,1], s=0.3, c=C, cmap='nipy_spectral', alpha=1)
plt.setp(ax, xticks=[], yticks=[])
cbar = plt.colorbar(boundaries=np.arange(max(C)))
cbar.set_ticks(np.arange(max(C)))
plt.savefig('fig1.pdf') 

f, ax = plt.subplots(figsize=(10, 10))
cmap = sns.cubehelix_palette(as_cmap=True, dark=0, light=1, reverse=True)
sns.kdeplot(embedding_partialsupervised[:,0], embedding_partialsupervised[:,1], cmap=cmap, n_levels=100, shade=True);
plt.savefig('fig2.pdf') 

HDB = hdbscan.HDBSCAN(min_samples=14,min_cluster_size=5000,prediction_data=True).fit_predict(embedding_partialsupervised)

vals = np.linspace(0,1,35)
np.random.shuffle(vals)
cmap = plt.cm.colors.ListedColormap(plt.cm.nipy_spectral(vals))

clustered = (HDB >= 0)
fig, ax = plt.subplots(1, figsize=(14, 10))
plt.scatter(embedding_partialsupervised[~clustered, 0],
            embedding_partialsupervised[~clustered, 1],
            c=(0.5, 0.5, 0.5),
            s=0.1,
            alpha=0)
plt.scatter(embedding_partialsupervised[clustered, 0],
            embedding_partialsupervised[clustered, 1],
            c=HDB[clustered],
            s=0.1,
            cmap=cmap);
cbar = plt.colorbar(boundaries=np.arange(0,max(HDB)))
cbar.set_ticks(np.arange(0,max(HDB)))
plt.savefig('fig3.pdf') 

clustered = (HDB >= 0)
fig, ax = plt.subplots(1, figsize=(14, 10))
plt.scatter(embedding_partialsupervised[~clustered, 0],
            embedding_partialsupervised[~clustered, 1],
            c=(0.5, 0.5, 0.5),
            s=0.1,
            alpha=0)
plt.scatter(embedding_partialsupervised[clustered, 0],
            embedding_partialsupervised[clustered, 1],
            c=C[clustered],
            s=0.1,
            cmap=cmap);
cbar = plt.colorbar(boundaries=np.arange(0,max(C2[clustered])))
cbar.set_ticks(np.arange(0,max(C[clustered])))
plt.savefig('fig4.pdf') 

session = Session(aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
s3 = session.resource('s3') 
hf = h5py.File('Training_UMAP_HDB.h5', 'w')
hf.create_dataset('Y', data=Y)
hf.create_dataset('Z', data=Z)
hf.create_dataset('C', data=C)##just basic classes
hf.create_dataset('HDB', data=HDB) 
hf.create_dataset('embedding_partialsupervised', data=embedding_partialsupervised)
hf.close()
s3.meta.client.upload_file(os.path.join('Training_UMAP_HDB.h5'),'bsmn-data',os.path.join('Training_UMAP_HDB.h5'))
