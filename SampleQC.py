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
from PIL import Image
import shutil
import re
import xml.etree.ElementTree as ET
from boto3.session import Session
import boto3
import h5py
import pybedtools
import pysam

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
subject = sys.argv[1]  #subjectid
gDNA = sys.argv[2]


with open(os.path.join(basepath,"config.txt")) as f:
    config = [line.rstrip() for line in f]    

##Load Ref Data
session = Session(aws_access_key_id=config[0],aws_secret_access_key=config[1])
s3 = session.resource('s3')
your_bucket = s3.Bucket('longboard-sc')
for s3_file in your_bucket.objects.all():
    s3 = boto3.client ('s3')
    s3.download_file('longboard-sc',s3_file.key,os.path.join(basepath,s3_file.key))

##Fetch file list
print os.path.join("/metadata", subject + ".txt")
print os.path.join(basepath,subject + ".txt")
s3 = boto3.client ('s3')
s3.download_file('for-ndar',os.path.join("metadata", subject + ".txt"),os.path.join(basepath,subject + ".txt"))
with open(subject + ".txt") as f:
    Cells = [line.rstrip() for line in f]

s3.download_file('for-ndar',os.path.join("SLAV-Seq/BulkSamples", gDNA + bam),os.path.join(basepath,gDNA + bam))

p0 = Popen(['samtools', 'index', os.path.join(basepath,gDNA + bam)])
p0.wait()

myoutput2 = open(os.path.join(basepath, gDNA + L1HScoverage), 'w')
p3 = Popen(['bedtools', 'multicov', '-bams', os.path.join(basepath,gDNA + bam), '-bed', os.path.join(basepath,L1HS)], stdout=myoutput2)
p3.wait()
myoutput2.close()

myinput3 = open(os.path.join(basepath, gDNA + L1HScoverage), 'r')
myoutput3 = open(os.path.join(basepath, gDNA + L1HScoverage_gt100), 'w')
awk_cmd = "{ if ($7 > 100) { print } }"
proc = Popen(['awk', awk_cmd], stdin=myinput3, stdout=myoutput3)
proc.wait()
myoutput3.flush()
a = pybedtools.BedTool(os.path.join(basepath, gDNA + L1HScoverage_gt100))
b = pybedtools.BedTool(L1HS)
output = "Percentage of reference L1HS with gt 100 reads in Bulk: " + str((len(a) / len(b))*100)
print output


for cell in Cells:
    session = Session(aws_access_key_id=config[0],aws_secret_access_key=config[1])
    s3 = session.resource('s3')
    s3 = boto3.client ('s3')
    s3.download_file('for-ndar',os.path.join("SLAV-Seq/",subject, cell + bam),os.path.join(basepath,cell + bam))
    
    p0 = Popen(['samtools', 'index', os.path.join(basepath, cell + bam)])
    p0.wait()
    
    name = os.path.join(basepath,cell)
    bamfile = os.path.join(basepath, cell+bam)
    a1 = pybedtools.BedTool(os.path.join(basepath, gDNA + L1HScoverage_gt100))
    L1HS_in_Cell_slop1K = a1.slop(b=1000, genome='hg19')
    
    a_bam = pysam.AlignmentFile(os.path.join(basepath, cell + bam), 'rb')
    bam_reads=0
    for read in a_bam.fetch(): bam_reads+=1
    output = "Total Aligned Reads: " + str(bam_reads)  
    print output
    
    L1HS_reads=0
    for interval in L1HS_in_Cell_slop1K:
        for read in a_bam.fetch(str(interval[0]), int(interval[1]), int(interval[2])): L1HS_reads+=1 
    output = "average aligned reads per L1HS: " + str((L1HS_reads / len(a1)))
    print output
    
    myoutput2 = open(os.path.join(basepath, cell + L1HScoverage), 'w')
    p3 = Popen(['bedtools', 'multicov', '-bams', os.path.join(basepath,cell + bam), '-bed', os.path.join(basepath,L1HS)],           stdout=myoutput2)
    p3.wait()
    myoutput2.close()
    
    myinput3 = open(os.path.join(basepath, cell + L1HScoverage), 'r')
    myoutput3 = open(os.path.join(basepath, cell + L1HScoverage_gt100), 'w')
    awk_cmd = "{ if ($7 > 100) { print } }"
    proc = Popen(['awk', awk_cmd], stdin=myinput3, stdout=myoutput3)
    proc.wait()
    myoutput3.flush()
    
    a2 = pybedtools.BedTool(os.path.join(basepath, cell + L1HScoverage_gt100))
    b2 = pybedtools.BedTool(L1HS)
    output = "Percentage of reference L1HS with gt 100 reads in Cell: " + str((len(a2) / len(b2))*100)
    print output
