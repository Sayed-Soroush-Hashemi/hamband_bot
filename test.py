__author__ = 'soroush'

import telegram
from sqlalchemy import create_engine
import time

if __name__ == '__main__':

    engine = create_engine('sqlite:///./temp.db')
    con = engine.connect()

    con.execute(
        """
        CREATE TABLE IF NOT EXISTS chat (
          "id" INTEGER PRIMARY KEY,
          "type" VARCHAR(50) NOT NULL,
          "title" VARCHAR(500) NULL,
          "username" VARCHAR(500) NULL,
          "first_name" VARCHAR(500) NULL,
          "last_name" VARCHAR(500) NULL
        );
        """
    )
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS "user" (
          "id" INTEGER  PRIMARY KEY,
          "username" VARCHAR(500) NULL,
          "first_name" VARCHAR(500) NULL,
          "last_name" VARCHAR(500) NULL
        );
        """
    )

    token = open('config/token.txt', 'r').read()
    bot = telegram.Bot(token=token)
    while True:
        a = bot.get_updates()
        for u in a:
            chat_id = u.message.chat.id
            chat_type = u.message.chat.type
            title = u.message.chat.title
            username = u.message.chat.username
            first_name = u.message.chat.first_name
            last_name = u.message.chat.last_name

            chat_id = chat_id if chat_id != '' else None
            chat_type = chat_type if chat_type != '' else None
            username = username if username != '' else None
            title = title if title != '' else title
            first_name = first_name if first_name != '' else None
            last_name = last_name if last_name != '' else None

            con.execute(
                """
                BEGIN
                    IF NOT EXISTS ( SELECT id FROM chat WHERE id={0} )
                    BEGIN
                        INSERT INTO chat("id", "type", "username", "first_name", "last_name")
                        VALUES({0}, "{1}", "{2}", "{3}", "{4}");
                    END
                END
                """.format(
                    chat_id, chat_type, username, title, first_name, last_name
                )
            )
        time.sleep(0.1)