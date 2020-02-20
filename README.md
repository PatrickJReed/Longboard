# longboard

<img src="https://surferart.com/wp-content/uploads/2013/05/Longboard-5.jpg" align="right"
     title="longboard" width="256" height="195">
Fun in the sun

Longboard is an scalable, cloud based deep learning pipeline for the detection of somatic LINE-1 retrotransposition events from SLAV-Seq datasets.  Longboard takes SLAV-Seq (ref) bam file(s) as input and identifies      

## Getting Started

These instructions will get you longboard up and running on AWS testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

Longboard has been developed to work entirely on AWS and has not been tested on any other system.
```
Give examples
```

### Installing

1: Launch AWS isntance using Longboard AMI (link).  Instance size depends on scale of data to be processed. Minimum metrics are (), show plot of run time vs instance type.

2:  Clone Longboard Repo from github (link)

3: Run make_images.py (path to bam in s3)

4: Run get_predicitons.py (path to bam in s3)

Output looks like:

End with an example of getting some data out of the system or using it for a little demo


### Usage

make_SC_Images.py
extract_Features.py
agregate_Features.py
analyze_features-8Class.ipynb
analyze_features_All.py
analyze_features_Post_UMAP.ipynb
longboard_train_model.ipynb
```
Give an example
```

## Authors

* **Patrick J Reed** - *Complete* -

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration DEEP VARIANT
* etc
