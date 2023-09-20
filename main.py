from telegram import Update
from telegram.ext import *
from twitter import TwitterParser
from binance import BinanceAPI
from config import TELEGRAMTOKEN
import sys

class TelegramBot:
    """
    FT Telegram chatbot engine
    """

    isStarted = False
    TwitterParser = TwitterParser()
    binanceAPI = BinanceAPI()

    def __init__(self):
        """
        Initialize
        """
        TOKEN = TELEGRAMTOKEN
        application = ApplicationBuilder().token(TOKEN).build()
        application.add_handler(CommandHandler('startFT', self.startFT))
        application.add_handler(CommandHandler('helpFT', self.startFT))
        application.add_handler(CommandHandler('getTop20Volume', self.getTop20Volume))
        application.add_handler(CommandHandler('getTop20BestPerformingCoins', self.getTop20BestPerformingCoins))
        application.add_handler(CommandHandler('getTop20WorstPerformingCoins', self.getTop20WorstPerformingCoins))
        application.run_polling()

    async def startFT(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Start command of the bot
        """

        if not self.isStarted:
            self.isStarted = True
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

    async def getTop20Volume(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        listOfCoins = self.binanceAPI.getTop20Volume()
        await self.sendMessage(update, context, listOfCoins)

    async def getTop20BestPerformingCoins(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        listOfCoins = self.binanceAPI.getTop20Performing(True)
        await self.sendMessage(update, context, listOfCoins)

    async def getTop20WorstPerformingCoins(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        listOfCoins = self.binanceAPI.getTop20Performing(False)
        await self.sendMessage(update, context, listOfCoins)

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


if __name__ == '__main__':
    print("Telegram bot is running")
    TelegramBot()
