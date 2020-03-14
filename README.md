# NSR Scraper

This script is meant to scrape the specialist database on [**The National Specialist Register Of The Malaysian Medical Council**](https://www.nsr.org.my) and create a CSV containing all the specialist data.

## Installation
Install dependencies:
```sh
pip install requests
pip install beautifulsoup4
pip install progressbar2
```

## Usage
Run the script by providing an input filename with a URLs of the specialists and output filename that you would like the data to be saved to. You can also get the usage help by using the `-h` flag:
```sh
$ python3 ./scraper.py -h
Welcome to this NSR scraper!!
usage: scraper.py [-h] [-i INPUT] [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input URL file
  -o OUTPUT, --output OUTPUT
                        Outut CSV file
```

### URL file format
The input file containing the URLs for the specialists needs tohave one URL per line:
```
https://www.nsr.org.my/list1viewdetails.asp?Account=N-0-289350
https://www.nsr.org.my/list1viewdetails.asp?Account=N-0-289351
https://www.nsr.org.my/list1viewdetails.asp?Account=N-0-289352
https://www.nsr.org.my/list1viewdetails.asp?Account=N-0-289356
https://www.nsr.org.my/list1viewdetails.asp?Account=N-0-289357
https://www.nsr.org.my/list1viewdetails.asp?Account=N-0-289358
https://www.nsr.org.my/list1viewdetails.asp?Account=N-0-289361
https://www.nsr.org.my/list1viewdetails.asp?Account=N-0-289366
https://www.nsr.org.my/list1viewdetails.asp?Account=N-0-289368
```
You can look at the `urls.csv` file for an example.

### Example
Assuming the file contatining the URLs is called `urls.csv`:
```sh
python3 ./scraper.py -i urls.csv -o doctors.csv
```
The output should look something like this:
```
$ python3 ./scraper.py -i urls.csv -o doctors.csv
Welcome to this NSR scraper!!

Loading URLs from urls.csv... done

Parsing doctor data from the URLs
 [Elapsed Time: 0:05:10] 100%|#######################################| (Time:  0:05:10) 

Saving to doctors.csv... done
```