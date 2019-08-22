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

Train_embedding_partialsupervised = umap.UMAP(n_neighbors=25, n_components=2, min_dist=0.0).fit_transform(Train_Z, y=Train_C)

Train_labels = hdbscan.HDBSCAN(min_samples=13,min_cluster_size=5000).fit_predict(Train_embedding_partialsupervised)

hf = h5py.File('Training_All_Final.h5', 'w')
hf.create_dataset('Y', data=Train_Y)
hf.create_dataset('Z', data=Train_Z)
hf.create_dataset('U', data=Train_U)
hf.create_dataset('C', data=Train_C)
hf.create_dataset('Umap_Partial', data=Train_embedding_partialsupervised)
hf.create_dataset('HDB', data=Train_labels)
hf.close()                

s3.meta.client.upload_file(os.path.join('Training_All_Final.h5'),'bsmn-data',os.path.join('Training_All_Final.h5'))

call(['sudo', 'shutdown', '-h', 'now'])