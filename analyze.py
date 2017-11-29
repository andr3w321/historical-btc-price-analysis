import requests
import requests_cache
import datetime
import matplotlib.pyplot as plt
from pytrends.request import TrendReq

requests_cache.install_cache(expire_after=43200) # 12 hours
#requests_cache.clear()

def get_historical_google_trends():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['bitcoin'])
    return pytrend.interest_over_time()

def get_historical_btc_price_data(end_date_str="{}-{}-{}".format(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day), start_date_str="2010-07-17"):
    url = "https://api.coindesk.com/v1/bpi/historical/close.json?start={}&end={}".format(start_date_str, end_date_str)
    print(url)
    return requests.get(url).json()


def graph_daily_per_change_and_price(filename="graph.png", end_date=datetime.date(2140,1,1), start_date=datetime.date(2008,12,31)):
    graph(filename, end_date, start_date, False)

def graph_google_trends_and_price(filename="graph.png", end_date=datetime.date(2140,1,1), start_date=datetime.date(2008,12,31)):
    graph(filename, end_date, start_date, True)

def graph(filename="graph.png", end_date=datetime.date(2140,1,1), start_date=datetime.date(2008,12,31), is_google_trends=False):
    res_price = get_historical_btc_price_data()
    sorted_dates = sorted(res_price["bpi"], key=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').date())
    if is_google_trends:
        res_trends = get_historical_google_trends()
    x,x2,y,y2 = [],[],[],[]
    for i in range(0, len(sorted_dates)):
        date_str = sorted_dates[i]
        if i == 0:
            yest_price = 0.08
        today_price = res_price["bpi"][date_str]
        percent_increase = (today_price - yest_price) / yest_price * 100
        yest_price = today_price
        print("{} {} {:.2f}%".format(date_str, today_price, percent_increase))
        dt = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
        if dt > start_date and dt < end_date:
            x2.append(dt)
            y2.append(today_price)
            if is_google_trends:
                trends_row = res_trends.loc[date_str:date_str]
                if len(trends_row.values) > 0:
                    x.append(dt)
                    y.append(trends_row.values[0][0])
            else:
                x.append(dt)
                y.append(percent_increase)

    fig, ax1 = plt.subplots()
    ax2 = ax1.twinx()
    ax1.plot_date(x, y, "-", color="blue")
    ax2.plot_date(x2, y2, "-", color="orange")
    ax1.set_xlabel("Date")
    if is_google_trends:
        plt.title("Google trends for 'bitcoin' and BTC Price vs Date")
        ax1.set_ylabel("Google trends for 'bitcoin'")
    else:
        plt.title("Daily % change in BTC price and BTC Price vs Date")
        ax1.set_ylabel("Daily % gain")
    ax2.set_ylabel("BTC Price")
    fig.autofmt_xdate()
    plt.savefig(filename)
    plt.show()

graph_daily_per_change_and_price("2013-11-bubble.png", datetime.date(2013,12,31), datetime.date(2013,11,1))
graph_daily_per_change_and_price("2017-11-bubble.png", datetime.date(2017,11,29), datetime.date(2017,11,1))
graph_google_trends_and_price("2013-11-google-trends.png", datetime.date(2013,12,31), datetime.date(2013,11,1))
graph_google_trends_and_price("2017-11-google-trends.png", datetime.date(2017,11,29), datetime.date(2017,11,1))
graph_google_trends_and_price("all-time-google-trends.png")
graph_google_trends_and_price("2013-google-trends.png", datetime.date(2013,12,31), datetime.date(2013,1,1))
graph_google_trends_and_price("2017-google-trends.png", datetime.date(2017,11,29), datetime.date(2017,1,1))
