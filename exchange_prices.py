import requests
import datetime
import matplotlib.pyplot as plt
import pandas as pd

folder = "./data/"

def download_data(filenames):
    for filename in filenames:
        if filename == "vwapHourlyBTCUSD.csv":
            # bitfinex data from bitcoincharts.com only goes back to Dec 2016
            # need to download recent bitfinex data manually
            base_url = "https://www.bfxdata.com/csv/"
        else:
            base_url = "http://api.bitcoincharts.com/v1/csv/"
        url = base_url + filename
        print(url)
        filename = folder + filename.replace("inactive_exchanges/","").replace("vwapHourlyBTCUSD.csv","bfxUSD.csv")
        with open(filename, "wb") as f:
            res = requests.get(url)
            f.write(res.content)

def graph_data(filenames, end_date, start_date, save_filename=None):
    colors = ['#3366CC','#DC3912','#FF9900','#109618','#990099','#3B3EAC','#0099C6','#DD4477','#66AA00','#B82E2E','#316395','#994499','#22AA99','#AAAA11','#6633CC','#E67300','#8B0707','#329262','#5574A6','#3B3EAC']
    i = 0
    plt.figure(figsize=(20,10))
    for filename in filenames:
        filename = filename.replace("inactive_exchanges/","")
        x,y = [],[]
        if filename == "bfxUSD.csv":
            df = pd.read_csv(folder + filename)
            price_idx = 2
        else:
            df = pd.read_csv(folder + filename, compression="gzip")
            price_idx = 1
        for row in df.values:
            dt = datetime.datetime.fromtimestamp(int(row[0]))
            if dt > start_date and dt < end_date:
                x.append(dt)
                y.append(row[price_idx])
        plt.plot_date(x,y, "-", color=colors[i], label=filename.split("USD")[0], linewidth=0.5)
        i += 1
    plt.legend()
    plt.xlabel("Date")
    plt.ylabel("Bitcoin Price")
    if save_filename:
        plt.title(save_filename.replace(".png","").replace("-"," ").split("/")[-1])
        plt.savefig(save_filename)
    else:
        plt.title("Bitcoin price at various exchanges over time")
    plt.show()

#filenames = ["bitfinexUSD.csv.gz","coinbaseUSD.csv.gz","bitstampUSD.csv.gz","krakenUSD.csv.gz","hitbtcUSD.csv.gz","itbitUSD.csv.gz","cexUSD.csv.gz","btceUSD.csv.gz","inactive_exchanges/mtgoxUSD.csv.gz","vwapHourlyBTCUSD.csv"]
#download_data(filenames)

graph_data(["inactive_exchanges/mtgoxUSD.csv.gz", "bitstampUSD.csv.gz", "btceUSD.csv.gz"], datetime.datetime(2014,5,1) ,datetime.datetime(2013,1,1), "./output/bitcoin-price-in-2013-runup-at-various-exchanges.png")

filenames = ["bfxUSD.csv","coinbaseUSD.csv.gz","bitstampUSD.csv.gz","krakenUSD.csv.gz"]
graph_data(filenames, datetime.datetime(2017,12,31) ,datetime.datetime(2017,1,1), "./output/bitcoin-price-in-2017-runup-at-various-exchanges.png")
graph_data(filenames, datetime.datetime(2017,7,1) ,datetime.datetime(2017,3,1), "./output/bitcoin-price-when-bfx-lost-banking-in-2017-at-various-exchanges.png")
