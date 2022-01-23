# CardMap

A bit of code to turn emails with orders from [CardMarket] into a map where my [Magic: the Gathering] cards are 
ending up.

## Setting things up

To get a copy of the code, set up a virtual environment and install packages the commands below can be used.

```commandline
git clone https://github.com/4dcu-be/CardMap
cd CardMap
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

You will also need a Google API KEY that can be used to access Google's Geocoding API. You can get one [here](https://developers.google.com/maps/documentation/geocoding/requests-geocoding?hl=en).
This needs to be set as an environmental variable. In Linux you can use the command below.

```commandline
export API_KEY=<YOUR KEY>
```

In PyCharm you could set it in the run configuration options, or you could create a .env file in the root of the project
containing (python-dotenv is included in the script to support this)

```
API_KEY=<YOUR KEY>
```


## Running the scripts

The first script ```parse_folder.py``` take two arguments: a file with shipping orders and the folder with .eml files from
shipping request from CardMarket. If the shipping order file exists, new data from eml files will be appended, 
otherwise a new file will be created and completed.

```commandline
python parse_folder.py ./data/shipping_orders.csv ./eml_data
```

The output will look like this:
```csv
shipment_id,zip,city,country,card_value,card_count,shipping,order_date,lng,lat
1059724747,3207SB,Spijkenisse,Netherlands,3.0,1,2.21,"Tue, 12 Oct 2021 08:37:51 +0000",4.355078499999999,51.8344145
1059947217,29323,Wietze,Germany,67.5,2,11.9,"Thu, 14 Oct 2021 20:31:20 +0000",9.8377274,52.6478492
1060585262,8900,Zalaegerszeg,Hungary,4.0,5,2.21,"Sat, 23 Oct 2021 02:51:59 +0000",16.8498282,46.8379252
...
```

[CardMarket]: https://www.cardmarket.com/en
[Magic: the Gathering]: https://magic.wizards.com/en