#!/usr/bin/env python3

''' Telegram bot wrapper for Disneyland Reservation Checker
'''

import logging
import disneyland_reservation_checker as drc
import util
import config
from telegram import Update
from telegram.ext import (
    Updater,
    CallbackContext,
    CommandHandler,
)


def start(update: Update, context: CallbackContext) -> None:
    ''' Sends explanation on how to use the bot'''
    message = 'Hi, use /check <yyyy-mm-dd> to check reservations at' \
        + 'Disneyland or California Adventure.'
    update.message.reply_text(message)


def check(update: Update, context: CallbackContext) -> None:
    ''' Check given date for reservation availability'''

    logger = util.get_logger()
    check_date = ' '.join(context.args)
    calendar = drc.DisneylandReservationChecker(logger, check_date)
    calendar.refresh()
    calendar.validate()
    message = str(calendar)
    update.message.reply_text(message)


def main():
    ''' Run the bot'''

    # Configure logging
    logger = util.get_logger()

    # Create the updater and pass it bot token
    TOKEN = config.TOKEN
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('check', check))

    updater.start_polling()
    updater.idle()


if __name__ ==  '__main__':
    main()
