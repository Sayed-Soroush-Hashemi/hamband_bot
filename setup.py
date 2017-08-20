__author__ = 'soroush'

from sqlalchemy import create_engine
from config import settings


def setup_db():
    engine = create_engine('{0}://{1}:{2}@{3}:{4}/{5}'.format(
        settings.DB['DRIVER'], settings.DB['USER'], settings.DB['PASSWORD'], settings.DB['HOST'], settings.DB['PORT'], settings.DB['NAME']
    ))
    con = engine.connect()

    con.execute(
        """
        DROP TABLE IF EXISTS lesson;
        """
    )

    con.execute(
        """
        CREATE TABLE IF NOT EXISTS lesson (
          "id" VARCHAR(10) PRIMARY KEY,
          "en_name" VARCHAR(100) NULL,
          "fa_name" VARCHAR(100) NOT NULL,
          "type" VARCHAR(100) NULL,
          "class" VARCHAR(100) NULL,
          "unit" VARCHAR(10) NULL,
          "needs" VARCHAR(50) NULL,
          "prerequisite" VARCHAR(50) NULL,
          "last_offer" VARCHAR(100) NULL,
          "last_offer_prof" VARCHAR(200) NULL
        );
        """
    )

    lessons_file = open('config/lessons list.txt', 'r')
    lessons = lessons_file.read().split('\n')
    lessons_file.close()
    lessons = lessons[1:]
    count = 1
    for lesson in lessons:
        print('adding {0} . . .'.format(count))
        count += 1

        lesson = lesson.split('\t')
        con.execute(
            """
            INSERT INTO lesson("id", "en_name", "fa_name", "type", "class", "unit", "needs", "prerequisite", "last_offer", "last_offer_prof")
            VALUES('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}');
            """.format(
                lesson[0], lesson[1], lesson[2], lesson[3], lesson[4], lesson[5], lesson[6], lesson[7], lesson[8], lesson[9]
            )
        )


def setup():
    setup_db()


if __name__ == '__main__':
    setup_db()
