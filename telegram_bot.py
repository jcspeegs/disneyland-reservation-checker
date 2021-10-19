#!/usr/bin/env python3

''' Telegram bot wrapper for Disneyland Reservation Checker
'''

import sys
import argparse
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
              f'[{text}]({url})' \
              f'\n``` /check <yyyy-mm-dd>```\nChecks for reservations at ' \
              r'Disneyland or California Adventure every 30 seconds\.' \
              f'\n``` /check1 <yyyy-mm-dd>```\nIsolated check for '\
              r'reservations at Disneyland or California Adventure\.' \
              f'\n``` /list```\nList query queue' r'\.' \
              f'\n``` /del <job-number>```\nRemove job from query queue' \
              r'\.' \
              f'\n``` /help```\nPrints this help message' r'\.'
    update.message.reply_markdown_v2(message, disable_web_page_preview=True)


def query(context: CallbackContext) -> None:
    ''' Query reservation availability and return results as a string'''

    # Parse context
    check_date = context.job.context['check_date']
    chat_id = context.job.context['chat_id']

    calendar = \
        drc.DisneylandReservationChecker(check_date)
    calendar.refresh()
    calendar.validate()
    message = str(calendar)

    # Send results
    context.bot.send_message(chat_id, message)


def build_context(update: Update, context: CallbackContext):
    ''' Build context dictionary inteded to be passed to query'''

    job_context = {}
    job_context['chat_id'] = update.message.chat_id
    job_context['check_date'] = context.args[0]

    return job_context


def check1(update: Update, context: CallbackContext) -> None:
    ''' Check given date for reservation availability'''

    # Get logger
    logger = logging.getLogger(__name__)

    # Build job context to pass to query function
    job_context = build_context(update, context)
    logger.debug(f'job_context:{job_context}')
    context.job_queue.run_once(query, 0, context=job_context,
                               name=str(job_context['chat_id']))


def keep_checking(update: Update, context: CallbackContext) -> None:
    ''' Check for reservations every 30 seconds'''

    # Get logger
    logger = logging.getLogger(__name__)

    # Build job context to pass to query function
    job_context = build_context(update, context)
    logger.debug(f'job_context:{job_context}')

    context.job_queue.run_repeating(query, interval=30, first=0.1,
                                    context=job_context,
                                    name=str(job_context['chat_id']))


def get_active_jobs(context: CallbackContext, name: str) -> tuple:
    ''' Returns a tuple of active jobs'''

    return context.job_queue.get_jobs_by_name(name)


def list_jobs(update: Update, context: CallbackContext) -> None:
    ''' List current reservation query date(s)'''

    # Get logger
    logger = logging.getLogger(__name__)
    logger.info('Listing jobs')

    # Get active jobs
    name = str(update.message.chat_id)
    logger.debug(f'name:{name}:{type(name)}')
    jobs = get_active_jobs(context, name)
    logger.debug(f'jobs:{jobs}')
    logger.debug(f'active jobs:{len(jobs)}')

    # Print list of active jobs
    message = []
    for i, j in enumerate(jobs):
        logger.debug(f'context:{j.context}')
        logger.debug(f'name:{j.name}')
        desc = f'{i}) Checking {j.context["check_date"]}'
        message.append(desc)
    message = '\n'.join(message)

    update.message.reply_text(message)


def del_job(update: Update, context: CallbackContext) -> None:
    ''' Remove a date from being checked for reservation status'''

    # Get logger
    logger = logging.getLogger(__name__)
    logger.info('Deleting a job')

    # Get index of job to end
    # Get active jobs
    name = str(update.message.chat_id)
    logger.debug(f'name:{name}:{type(name)}')
    jobs = get_active_jobs(context, name)
    logger.debug(f'jobs:{jobs}')
    logger.debug(f'active jobs:{len(jobs)}')
    job = jobs[int(context.args[0])]
    logger.debug(f'Delete job:{job}')
    try:
        job.schedule_removal()
    except Exception:
        raise


def parse_arguments(args):
    ''' Parse command line arguments'''

    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument('-v', '--verbose', action='count', default=0,
                        help='Print verbose output')

    return parser.parse_args(args)


def main():
    ''' Run the bot'''

    # Parse arguments
    args = parse_arguments(sys.argv[1:])

    # Configure logging
    log_conf = 'logging.yaml'
    with open(log_conf) as f:
        config = yaml.safe_load(f)

    if args.verbose == 1:
        config['handlers']['console']['level'] = 'INFO'
    elif args.verbose == 2:
        config['handlers']['console']['level'] = 'DEBUG'
    logging.config.dictConfig(config)

    # Create the updater and pass it bot token
    TOKEN = bot_config.TOKEN
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', print_help))
    dispatcher.add_handler(CommandHandler('help', print_help))
    dispatcher.add_handler(CommandHandler('check1', check1))
    dispatcher.add_handler(CommandHandler('check', keep_checking))
    dispatcher.add_handler(CommandHandler('list', list_jobs))
    dispatcher.add_handler(CommandHandler('del', del_job))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
