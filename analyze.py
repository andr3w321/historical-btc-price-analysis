import requests
import requests_cache
import datetime
import matplotlib.pyplot as plt

requests_cache.install_cache(expire_after=43200) # 12 hours

def get_historical_btc_price_data(end_date_str="{}-{}-{}".format(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day), start_date_str="2010-07-17"):
    url = "https://api.coindesk.com/v1/bpi/historical/close.json?start={}&end={}".format(start_date_str, end_date_str)
    print(url)
    return requests.get(url).json()

#requests_cache.clear()
res = get_historical_btc_price_data()
sorted_dates = sorted(res["bpi"], key=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').date())

def graph_daily_per_change_and_price(end_date=datetime.date(2140,1,1), start_date=datetime.date(2008,12,31), filename="graph.png"):
    x,y,y2 = [],[],[]
    for i in range(0, len(sorted_dates)):
        date_str = sorted_dates[i]
        if i == 0:
            yest_price = 0.08
        today_price = res["bpi"][date_str]
        percent_increase = (today_price - yest_price) / yest_price * 100
        yest_price = today_price
        print("{} {} {:.2f}%".format(date_str, today_price, percent_increase))
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        if dt > start_date and dt < end_date:
            x.append(dt)
            y.append(percent_increase)
            y2.append(today_price)

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.plot_date(x, y, "-", color="blue")
    ax2.plot_date(x, y2, "-", color="orange")
    plt.title("Daily % change in BTC price and BTC Price vs Date")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Daily % gain")
    ax2.set_ylabel("BTC Price")
    fig.autofmt_xdate()
    plt.savefig(filename)
    plt.show()

graph_daily_per_change_and_price(datetime.date(2013,12,31), datetime.date(2013,11,1), "2013-11-bubble.png")
graph_daily_per_change_and_price(datetime.date(2017,11,29), datetime.date(2017,11,1), "2017-11-bubble.png")
