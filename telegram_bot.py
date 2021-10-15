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


def print_help(update: Update, context: CallbackContext) -> None:
    ''' Sends explanation on how to use the bot'''
    name = update.effective_user
    text = 'Disneyland Reservation Checker'
    url = 'https://github.com/jcspeegs/disneyland-reservation-checker'
    message = f'Hi {name.mention_markdown_v2()}, I am the ' \
              f'{text}'\
              f'\n``` /check <yyyy-mm-dd>```\nchecks reservations at ' \
              f'Disneyland or California Adventure\.' \
              f'\n``` /help```\nprints this help message\.'
    update.message.reply_markdown_v2(message, disable_web_page_preview=False)


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

    dispatcher.add_handler(CommandHandler('start', print_help))
    dispatcher.add_handler(CommandHandler('help', print_help))
    dispatcher.add_handler(CommandHandler('check', check))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
