import requests
import requests_cache
import datetime
import matplotlib.pyplot as plt
from pytrends.request import TrendReq

def date_str_to_date(date_str):
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    
def print_yearly_returns():
    current_year = datetime.datetime.now().year
    for year in range(2011,current_year + 1):
        year_start_price = res_price["bpi"]["{}-01-01".format(year)]
        if year < current_year:
            next_year_start_price = res_price["bpi"]["{}-01-01".format(year + 1)]
        else:
            next_year_start_price = res_price["bpi"][sorted_dates[-1]]
        yearly_roi = float(next_year_start_price - year_start_price) / year_start_price * 100.0
        print("{} {} {:.2f}%".format(year, year_start_price, yearly_roi))

def get_historical_google_trends():
    pytrend = TrendReq()
    pytrend.build_payload(kw_list=['bitcoin'])
    return pytrend.interest_over_time()

def get_historical_btc_price_data(end_date_str="{}-{}-{}".format(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day), start_date_str="2010-07-17"):
    url = "https://api.coindesk.com/v1/bpi/historical/close.json?start={}&end={}".format(start_date_str, end_date_str)
    return requests.get(url).json()

def graph_daily_per_change_and_price(filename="./output/graph.png", end_date=datetime.date(2140,1,1), start_date=datetime.date(2008,12,31)):
    graph(filename, end_date, start_date, False)

def graph_google_trends_and_price(filename="./output/graph.png", end_date=datetime.date(2140,1,1), start_date=datetime.date(2008,12,31)):
    graph(filename, end_date, start_date, True)

def graph(filename="graph.png", end_date=datetime.date(2140,1,1), start_date=datetime.date(2008,12,31), is_google_trends=False):
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
        dt = date_str_to_date(date_str)
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

def calc_ma(i, ma_len):
    # calculate a moving average using the res_price and sorted_dates globals
    prev_prices = []
    stop_point = i - ma_len
    while(i > stop_point and i >=0):
        prev_prices.append(res_price["bpi"][sorted_dates[i]])
        i -= 1
    return sum(prev_prices) / len(prev_prices)

def print_bull_bear_trends(ma_len, trend_days_cutoff, roi_cutoff, filename=None):
    print("Bull Bear Trends for {} day moving average ignoring trends shorter than {} day or with ROI < {}%".format(ma_len, trend_days_cutoff, roi_cutoff))
    local_min_maxes = {} 
    pos_rois, neg_rois, pos_days, neg_days = [],[],[],[]
    for i in range(0, len(sorted_dates)):
        date_str = sorted_dates[i]
        today_price = res_price["bpi"][date_str]
        # make starting and ending dates a data point
        if i == 0 or i == len(sorted_dates) - 1:
            local_min_maxes[date_str_to_date(date_str)] = today_price
        elif i >= ma_len:
            yest_ma = calc_ma(i-1, ma_len)
            today_ma = calc_ma(i, ma_len)
            tom_ma = calc_ma(i+1, ma_len)

            if today_ma > yest_ma and today_ma > tom_ma or today_ma < yest_ma and today_ma < tom_ma:
                local_min_maxes[date_str_to_date(date_str)] = today_ma

    # graph moving averages
    x,y = [],[]
    sorted_local_min_maxes = list(sorted(local_min_maxes))
    for i in range(0, len(sorted_local_min_maxes)):
        dt = sorted_local_min_maxes[i]
        x.append(dt)
        y.append(local_min_maxes[dt])
        if i > 0:
            last_dt = sorted_local_min_maxes[i - 1]
            last_price = local_min_maxes[last_dt]
            today_price = local_min_maxes[dt]
            roi = float(today_price - last_price) / last_price * 100.0
            days_diff = (dt - last_dt).days
            if days_diff > trend_days_cutoff and abs(roi) > roi_cutoff:
                print("{} {:.2f} {:.2f}% in {} days".format(dt, today_price, roi, days_diff))
                if roi > 0:
                    pos_rois.append(roi)
                    pos_days.append(days_diff)
                else:
                    neg_rois.append(roi)
                    neg_days.append(days_diff)
                    
    print("Avg Bull Run: {:.2f}% over {:.1f} days".format(sum(pos_rois) / len(pos_rois), sum(pos_days) / len(pos_days)))
    print("Avg Bear Run: {:.2f}% over {:.1f} days".format(sum(neg_rois) / len(neg_rois), sum(neg_days) / len(neg_days)))

    # graph price
    x2,y2 = [],[]
    for i in range(0, len(sorted_dates)):
        date_str = sorted_dates[i]
        x2.append(date_str_to_date(date_str))
        y2.append(res_price["bpi"][date_str])

    plt.plot_date(x,y, "-", color="blue", label="{} day moving avg".format(ma_len))
    plt.plot_date(x2,y2, "-", color="orange", label="BTC Price")
    plt.legend()
    plt.xlabel("Date")
    plt.ylabel("BTC Price")
    plt.title("BTC Price and {} day moving avg vs date".format(ma_len))
    if filename:
        plt.savefig(filename)
    plt.show()
                
requests_cache.install_cache(expire_after=43200) # 12 hours
#requests_cache.clear()

res_price = get_historical_btc_price_data()
sorted_dates = sorted(res_price["bpi"], key=lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').date())

# graph_daily_per_change_and_price("./output/2013-11-bubble.png", datetime.date(2013,12,31), datetime.date(2013,11,1))
# graph_daily_per_change_and_price("./output/2017-11-bubble.png", datetime.date(2017,11,29), datetime.date(2017,11,1))
# graph_google_trends_and_price("./output/2013-11-google-trends.png", datetime.date(2013,12,31), datetime.date(2013,11,1))
# graph_google_trends_and_price("./output/2017-11-google-trends.png", datetime.date(2017,11,29), datetime.date(2017,11,1))
# graph_google_trends_and_price("./output/all-time-google-trends.png")
# graph_google_trends_and_price("./output/2013-google-trends.png", datetime.date(2013,12,31), datetime.date(2013,1,1))
# graph_google_trends_and_price("./output/2017-google-trends.png", datetime.date(2017,11,29), datetime.date(2017,1,1))
# print_yearly_returns()

print_bull_bear_trends(30, 10, 1, "./output/30-day-ma.png")
print_bull_bear_trends(200, 10, 1, "./output/200-day-ma.png")
