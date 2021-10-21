#!/usr/bin/env python3

''' Telegram bot wrapper for Disneyland Reservation Checker
'''

import sys
import argparse
import yaml
import logging.config
from math import floor
import bot_config
import disneyland_reservation_checker as drc
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    Updater,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
)


DOC = {'CHECK': {'SYNTAX': '/check `<yyyy-mm-dd>`',
                 'DESC': 'Check for reservations every 30 seconds\.'},
       # 'CHECK1': {'SYNTAX': '`/check1 <yyyy-mm-dd>`',
       #            'DESC': 'Isolated check for reservations at Disneyland ' \
       #                     'or California Adventure\.'},
       'LIST': {'SYNTAX': '/list',
                'DESC': 'List query queue\.'},
       'DEL': {'SYNTAX': '/del',
               'DESC': 'Remove job from query queue\.'},
       'HELP': {'SYNTAX': '/help',
                'DESC': 'Print this help message\.'}
       }


def print_help(update: Update, context: CallbackContext) -> None:
    ''' Sends explanation on how to use the bot'''

    logger = logging.getLogger(__name__)
    logger.info('Printing help message.')

    name = update.effective_user
    text = 'Disneyland Reservation Checker'
    url = 'https://github.com/jcspeegs/disneyland-reservation-checker'
    message = f'Hi {name.mention_markdown_v2()}, I am the ' \
              f'[{text}]({url})\n'
    for d in DOC.values():
        message += f'\n {d["SYNTAX"]}\n{d["DESC"]}'

    update.message.reply_markdown_v2(message, disable_web_page_preview=True)


def query(context: CallbackContext) -> None:
    ''' Query reservation availability and return results as a string'''

    # Parse context
    check_date = context.job.context['check_date']
    chat_id = context.job.context['chat_id']

    calendar = drc.DisneylandReservationChecker(check_date)
    calendar.refresh()
    calendar.validate()
    message = str(calendar)

    # Send results
    context.bot.send_message(chat_id, message)


def build_context(update: Update, context: CallbackContext, chat_id=False,
                  check_date=False):
    ''' Build context dictionary inteded to be passed to query'''

    logger = logging.getLogger(__name__)

    job_context = {}
    if chat_id:
        job_context['chat_id'] = update.message.chat_id
        logger.debug(f'chat_id:{job_context["chat_id"]}')
    if check_date:
        job_context['check_date'] = context.args[0]
        logger.debug(f'check_date:{job_context["check_date"]}')

    return job_context


def check1(update: Update, context: CallbackContext) -> None:
    ''' Check given date for reservation availability'''

    # Get logger
    logger = logging.getLogger(__name__)
    logger.info('Running Check1')

    # Build job context to pass to query function
    job_context = build_context(update, context, chat_id=True, check_date=True)
    logger.debug(f'job_context:{job_context}')
    context.job_queue.run_once(query, 0, context=job_context,
                               name=str(job_context['chat_id']))


def keep_checking(update: Update, context: CallbackContext) -> None:
    ''' Check for reservations every 30 seconds'''

    # Get logger
    logger = logging.getLogger(__name__)
    logger.info('Running keep_checking')

    # Build job context to pass to query function
    job_context = build_context(update, context, chat_id=True, check_date=True)
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
    job_context = build_context(update, context, chat_id=True)
    name = str(job_context['chat_id'])
    logger.debug(f'name:{name}:{type(name)}')
    jobs = get_active_jobs(context, name)
    job_count = len(jobs)
    logger.debug(f'active jobs:{len(jobs)}')

    # Print list of active jobs
    if job_count > 0:
        message = []
        for i, j in enumerate(jobs):
            desc = f'{i}) Checking {j.context["check_date"]}'
            message.append(desc)
        message = '\n'.join(message)
        parse_mode = None

    elif job_count == 0:
        syntax = DOC['CHECK']['SYNTAX']
        message = f'No dates to check\.\nAdd one with: {syntax}'
        parse_mode = 'MarkdownV2'

    context.bot.send_message(name, message, parse_mode=parse_mode)


def define_keyboard(jobs: tuple, columns: int) -> list:
    ''' Create inline keyboard structure.  Returns a list of lists where each
        internal list represents a row and each item in the interior list
        represents a column.
        e.g. [[r1c1, r1c2], [r2c1, r2c2]]
    '''

    jk = [InlineKeyboardButton(j.context['check_date'], callback_data=i)
          for i, j in enumerate(jobs)]
    job_keyboard = []
    for i, j in enumerate(jk):
        if i % columns == 0:
            job_keyboard.append([])
        job_keyboard[floor(i/columns)].append(j)

    return job_keyboard


def del_job(update: Update, context: CallbackContext) -> None:
    ''' Remove a date from being checked for reservation status'''

    # Get logger
    logger = logging.getLogger(__name__)
    logger.info('Deleting a job')

    # Get active jobs
    job_context = build_context(update, context, chat_id=True)
    name = str(job_context['chat_id'])
    logger.debug(f'name:{name}:{type(name)}')
    jobs = get_active_jobs(context, name)
    job_count = len(jobs)
    logger.debug(f'jobs:{jobs}')
    logger.debug(f'active jobs:{job_count}')

    # Get index of job to end
    if job_count > 0:
        keyboard = define_keyboard(jobs, columns=2)
        logger.debug(f'keyboard:{keyboard}')
        reply_markup = InlineKeyboardMarkup(keyboard)
        update.message.reply_text('Choose date to remove:',
                                  reply_markup=reply_markup)
    elif job_count == 0:
        update.message.reply_text('No jobs to remove')


def button_press(update: Update, context: CallbackContext) -> None:
    ''' Parse the CallbackQuery when inline keyboard button
        is pressed'''

    # Get logger
    logger = logging.getLogger(__name__)
    logger.info('Button Press')

    query = update.callback_query
    logger.debug(f'query:{query}')
    logger.debug(f'query.data:{query.data}:type:{type(query.data)}')
    query.answer(text=f'Stopping check {query.data}')
    # query.edit_message_text(text=f'Select options: {query.data}')

    name = str(query.message.chat.id)
    logger.debug(f'name:{name}')
    jobs = get_active_jobs(context, name)
    logger.debug(f'jobs:{jobs}')
    job = jobs[int(query.data)]
    logger.debug(f'job:{job}')
    logger.debug(f'Delete job:{job}')
    try:
        job.schedule_removal()
    except Exception:
        raise

    query.edit_message_text(text='Job removed')


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
    dispatcher.add_handler(CommandHandler('h', print_help))
    dispatcher.add_handler(CommandHandler('check1', check1))
    dispatcher.add_handler(CommandHandler('check', keep_checking))
    dispatcher.add_handler(CommandHandler('c', keep_checking))
    dispatcher.add_handler(CommandHandler('list', list_jobs))
    dispatcher.add_handler(CommandHandler('l', list_jobs))
    dispatcher.add_handler(CommandHandler('del', del_job))
    dispatcher.add_handler(CommandHandler('d', del_job))
    dispatcher.add_handler(CallbackQueryHandler(button_press))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
