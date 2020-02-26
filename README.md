# Longboard

<img src="https://surferart.com/wp-content/uploads/2013/05/Longboard-5.jpg" align="right"
     title="longboard" width="256" height="195">
Fun in the sun

Longboard is an scalable, cloud based deep learning pipeline for the detection of somatic LINE-1 retrotransposition events from SLAV-Seq datasets.  Longboard takes SLAV-Seq bam file(s) aligned to Hs37d5 as input and returns a vcf formated file of predicted somatic insertions. 

https://www.nature.com/articles/nn.4388

## Getting Started

These instructions will let you deploy Longboard on AWS.

### Prerequisites

Longboard has been developed to work entirely on AWS and has not been tested on any other system. 

1: AWS access (EC2 & S3)


### Installing

1: Launch AWS isntance using Longboard AMI: ami-0dc5f293477ab4af9

```
aws ec2 run-instances \
    --image-id ami-0dc5f293477ab4af9 \
    --count 1 \
    --instance-type **
```
** Instance size depends on scale of data to be processed. Minimum metrics are (), show plot of run time vs instance type.

2:  Clone Longboard Repo from github.

```
git clone https://github.com/PatrickJReed/Longboard.git
```

Done.

### Usage

1: Load bam files(s) to S3

3: Run make_images.py (path to bam in s3)

4: Run get_predicitons.py (path to bam in s3)

Done.

```
End with an example of getting some data out of the system or using it for a little demo
```

## Authors

* **Patrick J Reed** - *Complete* -

See also the list of [contributors](https://github.com/PatrickJReed/Longboard/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* This work was inspired by Deep Variant https://github.com/google/deepvariant
