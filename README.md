# basic script to work with the [Novel Coronavirus (COVID-19) cases dataset provided by JHU CSSE](https://systems.jhu.edu/research/public-health/ncov/)

Produce images like ![ like this one](/doc/coronavirus.png)

## install requirements
```
pip install -U requirements.txt
```

## run
```
$ python ./covid.py --help


  Command to download and plot Johns Hopkins SARS-nCOV-2 dataset

Options:
  --help  Show this message and exit.

Commands:
  download  download Johns Hopkins SARS-nCOV-2 dataset
  plot      Plot dataset

```
#### sample commands
```
# just download csv files
$ python ./covid.py download


$ python ./covid.python plot --help
Usage: covid.py plot [OPTIONS]

  Plot dataset

Options:
  --draw / --no-draw  plot on screen
  --save              save as PNG
  --help              Show this message and exit.
```
