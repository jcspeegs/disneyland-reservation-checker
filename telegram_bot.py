#!/usr/bin/env python3

''' Telegram bot wrapper for Disneyland Reservation Checker
'''

import yaml
import logging.config
import bot_config
import disneyland_reservation_checker as drc
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
              f'[{text}]({url})'\
              f'\n``` /check1 <yyyy-mm-dd>```\nchecks reservations at ' \
              f'Disneyland or California Adventure\.' \
              f'\n``` /help```\nprints this help message\.'
    update.message.reply_markdown_v2(message, disable_web_page_preview=True)


def check1(update: Update, context: CallbackContext) -> None:
    ''' Check given date for reservation availability'''

    check_date = context.args[0]
    calendar = drc.DisneylandReservationChecker(check_date)
    calendar.refresh()
    calendar.validate()
    message = str(calendar)
    update.message.reply_text(message)

def keep_checking(update: Update,
                  context: CallbackContext) -> None:
    ''' Check for reservations every 30 seconds'''

    context.job_queue.run_repeating(check, interval=30,
                                    context=context)


def main():
    ''' Run the bot'''

    # Configure logging
    log_conf = 'logging.yaml'
    with open(log_conf) as f:
        config = yaml.safe_load(f)

    logging.config.dictConfig(config)

    # Create the updater and pass it bot token
    TOKEN = bot_config.TOKEN
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', print_help))
    dispatcher.add_handler(CommandHandler('help', print_help))
    dispatcher.add_handler(CommandHandler('check1', check1))
    dispatcher.add_handler(CommandHandler('check',
                                          keep_checking))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
