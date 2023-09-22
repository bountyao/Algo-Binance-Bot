from telegram import Update
from telegram.ext import *
from binance import BinanceAPI
from config import TELEGRAMTOKEN
from config import CHAT_ID
import sys
import requests
import signal
import time
import atexit

class TelegramBot:
    """
    FT Telegram chatbot engine
    """

    binanceAPI = BinanceAPI()

    def __init__(self):
        """
        Initialize
        """
        self.TOKEN = TELEGRAMTOKEN

        application = ApplicationBuilder().token(self.TOKEN).build()
        application.add_handler(CommandHandler('startFT', self.startFT))
        application.add_handler(CommandHandler('helpFT', self.startFT))
        application.add_handler(CommandHandler('getTop20Volume', self.getTop20Volume))
        application.add_handler(CommandHandler('getTop20BestPerformingCoins', self.getTop20BestPerformingCoins))
        application.add_handler(CommandHandler('getTop20WorstPerformingCoins', self.getTop20WorstPerformingCoins))
        application.add_handler(CommandHandler('getTop10Top3Trades', self.getTop10Top3Trades))
        application.add_handler(CommandHandler('devGetChatID', self.getChatID))

        self.sendAlert("GM, I am now online", self.TOKEN)
        atexit.register(self.exitHandler)
        application.run_polling()

    async def startFT(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Start command of the bot
        """
        text = self.main_menu()

        await context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    def main_menu(self):
        """
        Function of Main menu text when bot is Online
        """

        return "Hello\n\n" \
               "Available commands:\n\n" \
               "/helpFT: Get available commands\n\n" \
               "/getTop20Volume: Get top 20 coins on Binance based on volume\n" \
               "/getTop20BestPerformingCoins: Get top 20 best performing coins\n" \
               "/getTop20WorstPerformingCoins: Get top 20 worst performing coins\n" \
               "/getTop10Top3Trades: Get top 3 most recent trades of top 10 volume coins\n" \

    async def getTop20Volume(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        listOfCoins = self.binanceAPI.getTop20Volume()
        await self.sendMessage(update, context, listOfCoins)

    async def getTop20BestPerformingCoins(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        listOfCoins = self.binanceAPI.getTop20Performing(True)
        await self.sendMessage(update, context, listOfCoins)

    async def getTop20WorstPerformingCoins(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        listOfCoins = self.binanceAPI.getTop20Performing(False)
        await self.sendMessage(update, context, listOfCoins)

    async def getTop10Top3Trades(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        sanitizedListOfCoins = []

        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="WARNING: Expensive operation. Please wait.")

        setOfCoins = self.binanceAPI.getRecentTrades()

        for key, coinData in setOfCoins.items():
            sanitizedTrades = ""
            for tradeInfo in coinData:
                if tradeInfo["isBuyer"]:
                    orderType = "BUY \U0001F4C8"
                else:
                    orderType = "SELL \U0001F4C9"
                sanitizedTrades = sanitizedTrades + str(
                    "\nOrder Type: " + orderType +
                    "\nPrice: " + str(round(float(tradeInfo['price']), 3)) +
                    "\nAmount: " + str(round(float(tradeInfo['qty']), 3)) + " " + key.rstrip("USDT") +
                    "\nAmount(USDT): " + str(round(float(tradeInfo['quoteQty']), 3)) + " USDT" +
                    "\nTime: " + tradeInfo['time'] + "\n"
                )

            sanitizedListOfCoins.append(
                "\U0001FA99" + key + "\U0001FA99" + "\n" + sanitizedTrades + '\n'
            )

        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="\n".join(sanitizedListOfCoins))

    async def sendMessage(self, update, context, listOfCoins):
        if len(listOfCoins) > 0:

            # Use a list comprehension to reformat the list of coins
            reformattedListOfCoins = "\n".join(listOfCoins)

            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text=reformattedListOfCoins)

        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text="REQUEST LIMIT TO BINANCE REACHED. Shutting down telegram bot :)")
            sys.exit(1)

    async def getChatID(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        print(update.message.chat_id)

    def sendAlert(self, message, token):
        try:
            response = requests.post(f'https://api.telegram.org/bot{token}/sendMessage', json={'chat_id': CHAT_ID, 'text': message})
            print(response.text)
        except Exception as e:
            print(e)

    def exitHandler(self):
        self.sendAlert("Shutting down. . .", self.TOKEN)

if __name__ == '__main__':
    print("Telegram bot is running")

    TelegramBot()
