# Longboard

Longboard is an scalable, cloud based deep learning pipeline for the detection of somatic LINE-1 retrotransposition events from SLAV-Seq datasets.  Longboard takes SLAV-Seq bam file(s) aligned to Hs37d5 as input and returns a vcf formated file of predicted somatic insertions. 

https://www.nature.com/articles/nn.4388

## Getting Started

These instructions will let you deploy Longboard on AWS.

### Prerequisites

Longboard has been developed to work entirely on AWS and has not been tested on any other system. 

1: AWS access (EC2 & S3)

2: Bam files(s) aligned to Hs37d5 representing SLAV-Seq libraries


### Installing

1: Launch AWS isntance using Longboard AMI: ami-0a88621ce222ec106

```
aws ec2 run-instances \
    --image-id ami-0a88621ce222ec106 \
    --count 1 \
    --instance-type **
```
** Instance size depends on scale of data to be processed. At a minium, the m4.8xl instance should be used when calling makeImages.py.  At a minimum, the g3.8xl instance should be used when running getPredictions.py 

2:  Clone Longboard Repo from github.

```
git clone https://github.com/PatrickJReed/Longboard.git
```

Done.

### Usage

1: Load bam files(s) to S3

2: Transfer config file [config.txt] containing AWS access credentials in home directory (see example).

3: Run makeImages.py [S3 Bucket] [Sample ID] [bulk ID]

4: Run getPredicitons.py [S3 Bucket] [Sample ID]

Done.

```
nano config.txt [paste access key and seceret key]

aws configure

aws s3 ls s3://lonboard-test/

aws s3 cp s3://longboard-test/config.txt .

./Longboard/makeImages.py longboard-test sample1 gDNA_sample1

./Longboard/getPredictions.py longboard-test sample1

head sample1_longboard.vcf

```
### Method



## Authors

* **Patrick J Reed**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* This work was inspired by Deep Variant https://github.com/google/deepvariant
* This work was funded by 
