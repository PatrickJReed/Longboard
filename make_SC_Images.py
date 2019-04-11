#!/usr/bin/python
from __future__ import division
import sys
import glob, os, gc
import cottoncandy as cc
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

##Path to Data
basepath = "/home/ubuntu/"
genome_regions = "hs37d5_15K_Windows.bed"
L1HS_bam = "-L1HS_mapped.bam"
L1HS_bam_bai = "-L1HS_mapped.bam.bai"
L1HS = "/home/ubuntu/rmask_L1HS_Correct.bed"
bam = "-ready.bam"
bai = "-ready.bam.bai"
igv = "-igv.xml"
bed = ".bed"
coverage15k = ".coverage15k"
coverage15k_gt100 = ".coverage15kgt100"
loci = ".loci"
##IGV Template
IGV = "/home/ubuntu/longboard/IGV_template.xml"
subject = sys.argv[1]  #subjectid
cell = sys.argv[2] #input
ACCESS_KEY = 'AKIAJNNOA6QMT7HXF6GA'
SECRET_KEY = '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'
cci = cc.get_interface('bsmn-data', ACCESS_KEY=ACCESS_KEY, SECRET_KEY=SECRET_KEY, endpoint_url='https://s3-us-west-2.amazonaws.com')
print cell


##Load Data
session = Session(aws_access_key_id=ACCESS_KEY,aws_secret_access_key=SECRET_KEY)
s3 = session.resource('s3')
your_bucket = s3.Bucket('longboard-sc')
for s3_file in your_bucket.objects.all():
    s3 = boto3.client ('s3')
    s3.download_file('longboard-sc',s3_file.key,s3_file.key)
#Bam
s3.download_file('bsmn-data',os.path.join(subject, cell, cell + bam),os.path.join(basepath,cell + bam))
s3.download_file('bsmn-data',os.path.join(subject, cell, cell + bai),os.path.join(basepath,cell + bai))




myoutput = open(os.path.join(basepath, cell + L1HS_bam), 'w')
p1 = Popen(['java', '-jar', '/home/ubuntu/jvarkit/dist/samviewwithmate.jar', '-b', L1HS, '--samoutputformat', 'BAM', os.path.join(basepath, cell + bam)], stdout=myoutput)
p1.wait()
myoutput.close()

p2 = Popen(['samtools', 'index', os.path.join(basepath, cell + L1HS_bam)])
p2.wait()

myoutput2 = open(os.path.join(basepath, cell + coverage15k), 'w')
p3 = Popen(['bedtools', 'multicov', '-bams', os.path.join(basepath, cell + bam), '-bed', os.path.join(basepath,genome_regions)], stdout=myoutput2)
p3.wait()
myoutput2.close()

myinput3 = open(os.path.join(basepath, cell + coverage15k), 'r')
myoutput3 = open(os.path.join(basepath, cell + coverage15k_gt100), 'w')
awk_cmd = "{ if ($4 > 100) { print } }"
proc = Popen(['awk', awk_cmd], stdin=myinput3, stdout=myoutput3)
proc.wait()
myoutput3.flush()

tree = ET.parse(IGV)
root = tree.getroot()
root[0][0].set('path', os.path.join(basepath, cell + bam)) #sc bam
root[0][1].set('path', os.path.join(basepath, cell + L1HS_bam)) #L1HS bam
root[1][0].set('id', os.path.join(basepath, cell + bam)) #sc bam
root[2][0].set('id', os.path.join(basepath, cell + L1HS_bam)) #L1HS bam
tree.write(os.path.join(basepath, cell + igv))

myinput_loci = os.path.join(basepath, cell + coverage15k_gt100)
myoutput_loci = os.path.join(basepath, cell + loci)
with open(myoutput_loci, 'w') as outfile:
	with open(myinput_loci, 'r') as infile:
        	data = infile.readlines()
        	for region in data:
                	row = [str(region.strip().split('\t')[0]),":",str(region.strip().split('\t')[1]),"-",str(region.strip().split('\t')[2])]
                	outfile.write("".join(row)+'\n')
Popen(['split', '-l', '100', '-d', os.path.join(basepath, cell + loci), os.path.join(basepath, cell + ".locisplit")]).wait()

print cell
cell_ids = []
locifile = os.path.join(basepath, cell + loci)
worklist = glob.glob("*.locisplit*")
batchsize = 16
print len(worklist)
for i in xrange(0, len(worklist), batchsize):
    batch = worklist[i:i+batchsize]
    print i
    index = 1
    procs = []
    for file in batch:
        print file
        with open(os.path.join(basepath, file)) as f0:
            first = f0.readline()# Read the first line.
            for last in f0: pass
            firstpic = cell+"-"+"*"+first.strip().split(':')[0]+"_"+first.strip().split(':')[1].split('-')[0]+"_"+first.strip().split(':')[1].split('-')[1]+".png"
            lastpic = cell+"-"+"*"+last.strip().split(':')[0]+"_"+last.strip().split(':')[1].split('-')[0]+"_"+last.strip().split(':')[1].split('-')[1]+".png"
	    if not (glob.glob(os.path.join(basepath, firstpic)) or glob.glob(os.path.join(basepath, lastpic))):
                p = Popen(['igv_plotter', '-o', cell+"_", '-L', file, '-v', '--max-panel-height', '1000', '--igv-jar-path', '/home/ubuntu/IGV_2.4.10/igv.jar', '-m', '6G', '-g', 'hg19', os.path.join(path, cell + igv)])
                procs.append(p)
    for pp in procs:
        pp.wait()
    for file in glob.glob("*s*__*.png"):
        newfile = re.sub("_s\d+__", "-", file)
        shutil.move(file, newfile)
    for file in glob.glob("*.png"):
        if "mod" not in file:
            path = os.path.splitext(file)[0]
            basename = os.path.basename(path)
            outfile1 = basename + "_mod.png"
            if not os.path.isfile(os.path.join(basepath,outfile1)):
                img = Image.open(file)
                pixelMap = img.load()
                img2 = Image.new(img.mode, img.size)
                pixelsNew = img2.load()
                for i in range(img2.size[0]):
                    for j in range(img2.size[1]):
                        if 250 in pixelMap[i,j]:
                            pixelMap[i,j] = (0,0,0,0)
                        else:
                            pixelsNew[i,j] = pixelMap[i,j]
            	img2.crop((174,130,img.size[0]-22,img.size[1])).resize((512,512)).save(outfile1)
    filelist = glob.glob("*_mod.png")
    x = np.array([np.array(Image.open(fname)) for fname in filelist])
    y = np.array([np.array(fname).astype(str) for fname in filelist])
    uid = uuid.uuid4()
    cell_ids.append(uid.hex)
    s3_response1 = cci.upload_raw_array(subject+'/'+cell+'/'+cell+'_'+uid.hex+'_X.npy', x, gzip=True)
    s3_response2 = cci.upload_raw_array(subject+'/'+cell+'/'+cell+'_'+uid.hex+'_Y.npy', y, gzip=True)
    print s3_response1
    print s3_response2
    for file in glob.glob("*.png"):
        os.remove(file)
s3_response3 = cci.upload_raw_array(subject+'/'+cell+'/'+cell+'_IDs.npy', np.array(cell_ids))
print s3_response3
print "Done with Sample: "+cell
call(['sudo', 'shutdown', '-h', 'now'])
