#!/usr/bin/env /usr/bin/python

import time
import sys
import psycopg2
from common import cspace # we use the config file reading function
from cspace_django_site import settings
from os import path

config = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), 'toolbox')

reload(sys)
sys.setdefaultencoding('utf-8')

timeoutcommand = "set statement_timeout to 240000; SET NAMES 'utf8';"
connect_string = config.get('connect', 'connect_string')

def getitems(table, num2ret, start_date, end_date, period):
    dbconn = psycopg2.connect(connect_string)
    items = dbconn.cursor()
    items.execute(timeoutcommand)
    if int(num2ret) > 1000: num2ret = 1000
    if int(num2ret) < 1:    num2ret = 1

    getitems = '''
select 

count(*) as n,
to_char(date_trunc('%s', cc.updatedat),'YYYY-MM-DD') as period

from %s_common xc
inner join collectionspace_core cc on xc.id=cc.id
where cc.updatedat >= '%s' and cc.updatedat <= '%s'
group by date_trunc('%s', cc.updatedat)
order by period
limit %s;
''' % (period, table, start_date, end_date, period, num2ret)

    items.execute(getitems)
    return [list(item) for item in items.fetchall()]
