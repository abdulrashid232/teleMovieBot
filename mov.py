import sqlite3
import threading
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext
from dotenv import load_dotenv
import os
from omdb import OMDB
from netnaija import movie_link, movie_series_link

load_dotenv()

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

class MovieBot:
    CHOOSING, TYPING_MOVIE, TYPING_SERIES = range(3)

    def __init__(self, token, api_key):
        self.token = token
        self.api_key = api_key
        self.updater = Updater(self.token)
        self.dispatcher = self.updater.dispatcher
        self.omdb_client = OMDB(self.api_key)

        self.connection = sqlite3.connect("search_history.db", check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS search_history "
                            "(user_id INTEGER, search_query TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)")
        self.connection.commit()

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                self.CHOOSING: [MessageHandler(Filters.regex('^(Movie|Series)$'), self.choice)],
                self.TYPING_MOVIE: [MessageHandler(Filters.text & ~Filters.command, self.search_movie)],
                self.TYPING_SERIES: [MessageHandler(Filters.text & ~Filters.command, self.search_series)],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )

        self.dispatcher.add_handler(conv_handler)
        self.dispatcher.add_handler(CommandHandler("history", self.view_search_history))
        self.dispatcher.add_handler(CommandHandler("help", self.help))
        self.dispatcher.add_error_handler(self.error)

    def start(self, update: Update, context: CallbackContext) -> int:
        user_id = update.message.from_user.id
        context.user_data['search_type'] = None
        reply_buttons = [['Movie', 'Series'], ['/start', '/help'], ['/history']]
        reply_markup = ReplyKeyboardMarkup(reply_buttons, resize_keyboard=True)
        update.message.reply_text(
            "Please choose whether you want to search for a movie or a series:",
            reply_markup=reply_markup
        )
        return self.CHOOSING

    def choice(self, update: Update, context: CallbackContext) -> int:
        user_choice = update.message.text.lower()
        context.user_data['search_type'] = user_choice
        if user_choice == 'movie':
            update.message.reply_text("Great! Please enter the name of the movie.")
            return self.TYPING_MOVIE
        elif user_choice == 'series':
            update.message.reply_text("Sure! Please enter the name of the series.")
            return self.TYPING_SERIES

    def search_movie(self, update: Update, context: CallbackContext) -> int:
        user_id = update.message.from_user.id
        movie_name = update.message.text

        reply_buttons = [['/start', '/help'], ['/history']]
        reply_markup = ReplyKeyboardMarkup(reply_buttons, resize_keyboard=True)
        update.message.reply_text(
            "Please wait while the movie information is fetch for you...",
            reply_markup=None
        )

        movie_link_result = movie_link(movie_name)

        message = ""

        if movie_link_result:
            threading.Thread(target=self._store_search_history, args=(user_id, movie_name)).start()

            movie_info = self.omdb_client.movie_info(movie_name)

            if movie_info:
                rating_text = f"IMDb Rating: {movie_info['imdb_ratings']}\n"
                for rating in movie_info['ratings']:
                    rating_text += f"{rating['Source']}: {rating['Value']}\n"

                message += (f"{movie_info['title']}: \n\n" +
                           f"Plot:\n{movie_info['plot']}\n\n" +
                           f"Starring:\n{movie_info['actors']}\n\n" +
                           f"Ratings:\n{rating_text}" +
                           f"Download Link: {movie_link_result}\n" +
                           f"Poster:\n{movie_info['poster']}\n\n"
                           )
            else:
                message = f"Movie '{movie_name}' not found on the OMDb site. Please check your spelling errors and try again."

            update.message.reply_text(text=message, reply_markup=None)
        else:
            message = f"Download link for movie '{movie_name}' not found on NetNaija. Please check your spelling errors and try again."
            update.message.reply_text(message)

        return self.start(update, context)

    def search_series(self, update: Update, context: CallbackContext) -> int:
        user_id = update.message.from_user.id
        series_name = update.message.text

        reply_buttons = [['/start', '/help'], ['/history']]
        reply_markup = ReplyKeyboardMarkup(reply_buttons, resize_keyboard=True)
        update.message.reply_text(
            "Please wait while the series information is fetch for you...",
            reply_markup=None
        )

        series_links = movie_series_link(series_name)

        if series_links:
            threading.Thread(target=self._store_search_history, args=(user_id, series_name)).start()

            for link in series_links:
                message = f"Download Link for series '{series_name}':\n{link}"
                update.message.reply_text(message)
        else:
            message = f"Download links for series '{series_name}' not found on NetNaija. Please check your spelling errors and try again."
            update.message.reply_text(message)

        return self.start(update, context)

    def cancel(self, update: Update, context: CallbackContext) -> int:
        update.message.reply_text("Search canceled. Please choose 'Movie' or 'Series' again.")
        return self.start(update, context)
    
    def help(self, update: Update, context: CallbackContext) -> int:
        update.message.reply_text("Search movie/series by choosing between movie and series button\n\n And then type the movie/series name.\n\nNB: Start the bot first.")
        

    def _store_search_history(self, user_id, movie_name):
        self.cursor.execute("INSERT INTO search_history (user_id, search_query) VALUES (?, ?)",
                            (user_id, movie_name))
        self.connection.commit()

    def view_search_history(self, update: Update, context: CallbackContext):
        user_id = update.message.from_user.id
        self.cursor.execute("SELECT search_query, timestamp FROM search_history WHERE user_id=?", (user_id,))
        search_history = self.cursor.fetchall()

        if search_history:
            message = "Your search history:\n"
            for query, timestamp in search_history:
                message += f"- {query} ({timestamp})\n"
        else:
            message = "Your search history is empty."

        update.message.reply_text(message)

    def error(self, update: Update, context: CallbackContext):
        logging.error(f"An error occurred: {context.error}")
        update.message.reply_text("An error occurred. Please try again later.")

    def run(self):
        self.updater.start_polling()
        self.updater.idle()

    def __del__(self):
        self.connection.close()

def main():
    token = os.getenv("Token")
    api_key = os.getenv("Movie_api")
    movie_bot = MovieBot(token, api_key)
    movie_bot.run()

if __name__ == '__main__':
    main()
