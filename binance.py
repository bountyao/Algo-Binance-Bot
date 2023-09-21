import requests
from datetime import datetime
import urllib.parse
import json

urlTicker24Hr = "https://api.binance.com/api/v3/ticker/24hr"


class BinanceAPI:
    listOfTop20 = []

    fiatCoins = ["BUSD", "USDC", "FDUSD", "TUSD"]

    def updateTop20List(self):
        self.getTop20Volume()

    def getUSDTPairs(self):
        response = requests.get(urlTicker24Hr)
        usdtPairs = []

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            exchange_info = response.json()

            for pair in exchange_info:
                if pair["symbol"].endswith("USDT") and not pair["symbol"].endswith("UPUSDT") and not pair[
                    "symbol"].endswith("DOWNUSDT"):
                    usdtPairs.append(pair)
            return usdtPairs
        else:
            return []

    def getTop20Volume(self):
        listOfPairsInVolume = []
        usdtPairs = self.getUSDTPairs()

        usdtPairs = sorted(
            usdtPairs,
            key=lambda x: float(x["quoteVolume"]),
            reverse=True
        )

        i = 0
        counter = 0
        while counter < 20:
            symbol = usdtPairs[i]['symbol']
            # Check if any fiat coin is in the symbol
            if any(fiat in symbol for fiat in self.fiatCoins):
                i += 1  # Move to the next symbol without processing
                continue

            # If no fiat coin found in the symbol, process it
            listOfPairsInVolume.append(
                str(counter + 1) + ") " + symbol + ": " + str(
                    round(float(usdtPairs[i]['quoteVolume']), 3)) + " USDT")
            self.listOfTop20.append(symbol)  # Append top 20 coins to list
            i += 1  # Move to the next symbol
            counter += 1

        return listOfPairsInVolume

    def getTop20Performing(self, isReversed=True):
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
                str(i + 1) + ") " + usdtPairs[i]['symbol'] + ": " + polarity + usdtPairs[i]['priceChangePercent'] + "%")

        return listOfPairsInBestPerforming

    def getRecentTrades(self):
        setOfCoinsWithTop3Trades = {}

        if not len(self.listOfTop20) > 0:
            self.getTop20Volume()

        limiter = 0
        for symbol in self.listOfTop20:

            if limiter == 10:
                break

            response = requests.get(f"https://api.binance.com/api/v3/trades?symbol={symbol}")

            tradeInfo = response.json()
            setOfCoinsWithTop3Trades[symbol] = self.getTop3Trades(tradeInfo)

            limiter = limiter + 1

        return setOfCoinsWithTop3Trades

    def getTop3Trades(self, arr):
        sortedTradesAndTop3Picks = sorted(arr, key=lambda x: float(x["quoteQty"]), reverse=True)[:3]

        sanitizedList = []

        for tradeInfo in sortedTradesAndTop3Picks:
            sanitizedList.append({
                'price': tradeInfo['price'],
                'qty': tradeInfo['qty'],
                'quoteQty': tradeInfo['quoteQty'],
                'time': sanitizeTimestamp(tradeInfo['time']),
                'isBuyer': not tradeInfo['isBuyerMaker'],
            })

        return sanitizedList


def sanitizeTimestamp(timestamp):
    # Convert milliseconds to seconds
    timestampSeconds = timestamp / 1000

    # Convert the timestamp to a datetime object
    dt = datetime.fromtimestamp(timestampSeconds)

    # Format the datetime object as a string
    readableTime = dt.strftime("%Y-%m-%d %H:%M:%S")

    return readableTime


if __name__ == "__main__":
    binance = BinanceAPI()

    print(binance.getRecentTrades())
