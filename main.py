__author__ = 'soroush'

import telegram
import json
from config import settings
import time
import re
import traceback
import _thread
import logging


def find_lesson(l_id=None, en_name=None, fa_name=None):
    if l_id:
        res = settings.con.execute(
            """
            SELECT * FROM lesson WHERE id = %s;
            """,
            l_id
        )
        keys = res.keys()
        rows = res.fetchall()
    elif en_name:
        en_name = en_name.lower()
        res = settings.con.execute(
            """
            SELECT * FROM lesson WHERE LOWER(en_name) = LOWER(%s);
            """,
            en_name
        )
        keys = res.keys()
        rows = res.fetchall()
        if len(rows) == 0:
            rows = []
            candidates = en_name.split(' ')

            for candidate in candidates:
                if len(candidate) < 3:
                    continue
                candidate_rows = settings.con.execute(
                    """
                    SELECT * FROM lesson WHERE LOWER(en_name) LIKE '%%{0}%%';
                    """.format(candidate)
                ).fetchall()
                rows.append(candidate_rows)
            rows = sorted(rows, key=lambda x: len(x))
            i = 0
            while i < len(rows) and len(rows[i]) == 0:
                i += 1
            if i == len(rows):
                rows = []
            else:
                rows = rows[i]
    elif fa_name:
        res = settings.con.execute(
            """
            SELECT * FROM lesson WHERE fa_name = %s;
            """,
            fa_name
        )
        keys = res.keys()
        rows = res.fetchall()
        if len(rows) == 0:
            rows = []
            candidates = fa_name.split()
            for candidate in candidates:
                if len(candidate) < 3:
                    continue
                candidate_rows = settings.con.execute(
                    """
                    SELECT * FROM lesson WHERE fa_name Like '%%{0}%%';
                    """.format(candidate)
                ).fetchall()
                rows.append(candidate_rows)
            rows = sorted(rows, key=lambda x: len(x))
            i = 0
            while i < len(rows) and len(rows[i]) == 0:
                i += 1
            if i == len(rows):
                rows = []
            else:
                rows = rows[i]

    else:
        keys = []
        rows = []
    lessons = []
    for row in rows:
        lesson = dict(zip(keys, row))
        lessons.append(lesson)
    return lessons


def lessons_to_text_long(lessons):
    resp_text = ''
    for lesson in lessons:
        lesson_text = '```\n{' + '\nشماره درس: {0}\nنام درس: {1}\nواحد: {2}\n'.format(
            lesson['id'], lesson['fa_name'], lesson['unit']
        )
        if len(lesson['prerequisite']) > 2:
            lesson_text += 'پیشنیاز: {0}\n'.format(lesson['prerequisite'])
        if len(lesson['needs']) > 2:
            lesson_text += 'همنیاز: {0}\n'.format(lesson['needs'])
        if len(lesson['type']) > 2:
            lesson_text += 'مقطع: {0}\n'.format(lesson['class'])
        if len(lesson['last_offer']) > 2:
            lesson_text += 'آخرین ارائه: {0}\n'.format(lesson['last_offer'])
        if len(lesson['last_offer_prof']) > 2:
            lesson_text += 'استاد آخرین ارائه: {0}\n'.format(lesson['last_offer_prof'])
        lesson_text += '}```\n'
        if len(lesson['prerequisite']) > 2:
            lesson_text += 'پیشنیازها:\n'
            pres = re.findall('\d+', lesson['prerequisite'])
            for pre in pres:
                pre_lesson = find_lesson(l_id=pre)
                if pre_lesson:
                    lesson_text += '/{0} {1}\n'.format(pre, pre_lesson[0]['fa_name'])
        if len(lesson['needs']) > 2:
            lesson_text += 'همنیاز:\n'
            pres = re.findall('\d+', lesson['needs'])
            for pre in pres:
                pre_lesson = find_lesson(l_id=pre)
                if pre_lesson:
                    lesson_text += '/{0} {1}\n'.format(pre, pre_lesson[0]['fa_name'])

        resp_text += lesson_text

    if resp_text == '':
        resp_text = 'معذرت می خوام. نفهمیدم چه درسی رو میگی'

    return resp_text


def lessons_to_text_short(lessons):
    resp_text = ''
    for lesson in lessons:
        resp_text += '/{0} {1}\n'.format(lesson['id'], lesson['fa_name'])
    return resp_text


def handle_lesson_request(bot, update):
    try:

        logging.getLogger('info').info('from_user: ' + update.message.from_user.to_json())
        logging.getLogger('info').info('chat: ' + update.message.chat.to_json())
        logging.getLogger('info').info('{0} : message: {1}'.format(update.message.chat_id, update.message.to_json()))

        update.message.text = re.sub('@hamband_bot', '', update.message.text)
        if update.message.text in ['/start', '/help', 'help', 'کمک']:
            help_file = open('config/help.txt', 'r')
            help_text = help_file.read()
            help_file.close()
            bot.send_message(
                chat_id=update.message.chat_id,
                reply_to_message_id=update.message.message_id,
                text=help_text
            )
            return
        if update.message.reply_to_message and update.message.reply_to_message.from_user.id != bot.getMe().id:
            return
        if update.message.text.startswith('/') or update.message.text.startswith('\\'):
            update.message.text = update.message.text[1:]

        text = update.message.text
        digits_fa_en = [
            ('۰', '0'),
            ('۱', '1'),
            ('۲', '2'),
            ('۳', '3'),
            ('۴', '4'),
            ('۵', '5'),
            ('۶', '6'),
            ('۷', '7'),
            ('۸', '8'),
            ('۹', '9'),
        ]
        for digit in digits_fa_en:
            text = re.sub(digit[0], digit[1], text)
        update.message.text = text.strip()

        if len(update.message.text) > 30:
            bot.send_message(
                chat_id=update.message.chat_id,
                reply_to_message_id=update.message.message_id,
                text='یه کم کمتر حرف بزن'
            )
            return

        if re.match('\d+', update.message.text):
            lessons = find_lesson(l_id=update.message.text)
        elif len(re.findall('(?i)[a-z]{2}', update.message.text)) > 0:
            lessons = find_lesson(en_name=update.message.text)
        else:
            lessons = find_lesson(fa_name=update.message.text)

        resp_text = ''
        if len(lessons) < 3:
            resp_text = lessons_to_text_long(lessons)
        else:
            resp_text = lessons_to_text_short(lessons)

        bot.send_message(
            chat_id=update.message.chat_id,
            reply_to_message_id=update.message.message_id,
            parse_mode='Markdown',
            text=resp_text
        )
    except Exception as e:
        # error_traceback = traceback.format_exc()
        # error_message = '\n*' + str(e) + '*\n' + error_traceback
        logging.getLogger('errors').exception('{0} : {1}'.format(update.update_id, getattr(e, 'message', 'exception object has no message')))
        bot.send_message(
            chat_id=update.message.chat_id,
            reply_to_message_id=update.message.message_id,
            text='شرمنده. یه مشکلی در حین اجرای دستورت پیش اومد. به تیمم می گم مشکل رو حل کنن.'
        )
    return


def handle_request(bot, update):
    if update.message.new_chat_member:
        new_member = update.message.new_chat_member
        if new_member.id == bot.getMe().id:
            name = update.message.from_user.first_name
            if not name:
                name = update.message.from_user.last_name
            bot.send_message(
                chat_id=update.message.chat_id,
                reply_to_message_id=update.message.message_id,
                text='سلام به همه. مرسی ' + name + ' که من رو ادد کردی. \nمی خواین بدونی من کی ام؟ \n /help'
            )
    elif update.message.text:
        return handle_lesson_request(bot, update)


def run_bot():
    bot = telegram.Bot(token=settings.TOKEN)
    last_update_id = 0

    logging.basicConfig(filename='log.txt', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_formatter = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    info_file_handler = logging.FileHandler(filename='info.txt', encoding='utf-8')
    error_file_handler = logging.FileHandler(filename='errors.txt', encoding='utf-8')
    info_file_handler.setFormatter(log_formatter)
    error_file_handler.setFormatter(log_formatter)
    logging.getLogger('info').addHandler(info_file_handler)
    logging.getLogger('errors').addHandler(error_file_handler)

    while True:
        try:
            updates = bot.get_updates(offset=last_update_id)
            for update in updates:
                if update.message is None:
                    update.message = update.edited_message
                _thread.start_new_thread(handle_request, (bot, update))
                last_update_id = max(last_update_id, update.update_id + 1)
    
            time.sleep(settings.POLLING_SLEEP_TIME)
        except:
            time.sleep(settings.POLLING_SLEEP_TIME*5)
            bot = telegram.Bot(token=settings.TOKEN)
