#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import time


def get_history_urls():
    url = "www.wellsfargo.com/mortgage/rates/"
    cdx_url = 'http://web.archive.org/cdx/search/cdx?url={0}'.format(url)

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:13.0) Gecko/20100101 Firefox/13.0.1'}

    response = requests.get(cdx_url, headers=headers)
    cdx_page_content = response.content

    history_urls = list()
    for line in cdx_page_content.splitlines():
        preamble, timestamp, url, type, status, digest, size = line.split(" ")
        if status == "200" and timestamp >= "2017":
            history_url = "https://web.archive.org/web/{0}/{1}".format(timestamp, url)
            history_urls.append(history_url)

    return history_urls


def get_rate_list_from_url(history_url):

    rate_list = None
    try:
        pattern = re.compile('https://web.archive.org/web/([0-9]{14})/https://www.wellsfargo.com/mortgage/rates/')
        timestamp = int(pattern.search(history_url).group(1))

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:13.0) Gecko/20100101 Firefox/13.0.1'}

        response = requests.get(history_url, headers=headers)
        html = response.content

        soup = BeautifulSoup(html)
        purchase_rates_table = soup.find("table", {"id": "PurchaseRatesTable"})

        rate_list = list()
        for row in purchase_rates_table.find_all('tr'):
            mortgate_type = row.find("th").getText()
            if mortgate_type in ("30-Year Fixed Rate",
                                 "30-Year Fixed-Rate FHA",
                                 "30-Year Fixed-Rate VA",
                                 "15-Year Fixed Rate",
                                 "7/1 ARM",
                                 "5/1 ARM",
                                 "30-Year Fixed-Rate Jumbo",
                                 "15-Year Fixed-Rate Jumbo",
                                 "7/1 ARM Jumbo",
                                 "10/1 ARM Jumbo"):

                mortgate_rate = float(row.find("td").getText().replace("%", "")) / 100
                rate_dict = {"timestamp": timestamp, "rate": mortgate_rate, "type": mortgate_type}

                rate_list.append(rate_dict)
    except:
        pass

    return rate_list


def persist_rates_as_csv():
    history_urls = get_history_urls()
    for history_url in history_urls:
        rate_list = get_rate_list_from_url(history_url)
        if rate_list:
            rate_list_dataframe = pd.DataFrame(rate_list)
            rate_list_dataframe.to_csv("R/rate_history.csv", columns=['timestamp', 'type', 'rate'], index=False, mode='a', header=False)
        time.sleep(4)


if __name__ == "__main__":
    persist_rates_as_csv()
