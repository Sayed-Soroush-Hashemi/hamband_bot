#!/usr/bin/env bash

case "${1}" in
    setup )
        echo 'installing prerequisites . . .'
        sudo apt-get install postgresql
        sudo apt-get install postgresql-client
        sudo apt-get install postgresql-server-dev-all
        sudo pip3 install sqlalchemy
        sudo pip3 install python-telegram-bot
        sudo pip3 install psycopg2

        echo 'creating db role . . .'
        sudo -u postgres createuser hamband_bot
        sudo -u postgres psql -c "ALTER USER hamband_bot WITH PASSWORD '`cat 'config/db_password.txt'`'"

        echo 'creating db . . .'
        sudo -u postgres createdb --owner=hamband_bot hamband_bot_db

        echo 'initializing bot . . .'
#        if [ -e 'mydb.db' ] ; then
#            rm -f 'mydb.db'
#        fi
        python3 manage.py setup
        exit 0
        ;;
    start )
        echo 'starting bot . . .'
        python3 manage.py start &>> 'unexpected_log.txt' &
        echo $! > 'config/ps_id.txt'
        echo 'bot started successfully.'
        echo 'to stop it run ./manage.py start'
        exit 0
        ;;
    stop )
        echo 'stopping bot ...'
        ps_id=`cat 'config/ps_id.txt'`
        kill ${ps_id}
        rm 'config/ps_id.txt'
        echo 'bot stopped successfully.'
        echo 'to start it again run ./manage.py start'
        exit 0
        ;;
    restart )
        $0 stop
        $0 start
        exit 0
        ;;
    refresh )
        echo 'deleting db . . .'
        sudo -u postgres dropdb hamband_bot_db
        echo 'deleting role . . .'
        sudo -u postgres dropuser hamband_bot
        exit 0
        ;;
    debug )
        echo 'starting bot . . .'
        python3 manage.py start
        ;;
esac
