import requests

urlTicker24Hr = "https://api.binance.com/api/v3/ticker/24hr"

class BinanceAPI:

    def getUSDTPairs(self):
        response = requests.get(urlTicker24Hr)
        usdtPairs = []

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Print the response content
            exchange_info = response.json()

            for pair in exchange_info:
                if pair["symbol"].endswith("USDT") and not pair["symbol"].endswith("UPUSDT") and not pair["symbol"].endswith("DOWNUSDT"):
                    usdtPairs.append(pair)
            return usdtPairs
        else:
            return usdtPairs

    def getTop20Volume(self):
        listOfPairsInVolume = []
        usdtPairs = self.getUSDTPairs()

        usdtPairs = sorted(
            usdtPairs,
            key=lambda x: float(x["quoteVolume"]),
            reverse=True
        )

        for i in range(20):
            listOfPairsInVolume.append(
                str(i+1) + ") " + usdtPairs[i]['symbol'] + ": " + str(round(float(usdtPairs[i]['quoteVolume']), 3)) + " USDT")

        return listOfPairsInVolume

    def getTop20Performing(self, isReversed = True):
        listOfPairsInBestPerforming = []
        usdtPairs = self.getUSDTPairs()

        if isReversed:
            polarity = '+'
        else:
            polarity = ''

        usdtPairs = sorted(
            usdtPairs,
            key=lambda x: float(x["priceChangePercent"]),
            reverse=isReversed
        )

        for i in range(20):
            listOfPairsInBestPerforming.append(
                str(i+1) + ") " + usdtPairs[i]['symbol'] + ": " + polarity + usdtPairs[i]['priceChangePercent'] + "%")

        return listOfPairsInBestPerforming

    def getRecentTrades(self):
        symbol = "BTCUSDT"
        response = requests.get(f"https://api.binance.com/api/v3/trades?symbol={symbol}")
        trades_info = []

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Print the response content
            trades_info = response.json()

            return trades_info
        else:
            return trades_info

if __name__ == "__main__":
    binance = BinanceAPI()

    print(binance.getRecentTrades())
