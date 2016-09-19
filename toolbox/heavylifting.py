import re
import django_tables2 as tables
from constants import getAgencies, getHierarchies
import dbconnector
from toolbox import activity2db


def extractTerms(context, dict, requestedField):
    field = None
    position = None
    for fieldname in 'date location crate object authority taxon reason handler groupby culture concept activity'.split(' '):
        if '.start' in requestedField:
            position = 'start'
        if '.end' in requestedField:
            position = 'end'
        if fieldname in requestedField:
            field = fieldname
            break
    return [position, field, dict[requestedField], context['applayout'][requestedField]['label'], requestedField]


def getFields(request, context):
    search_terms = {}
    for formField in request.POST:
        if formField in 'csrfmiddlewaretoken submit start enumerate search update movecheck'.split(' '): continue
        if 'select-' in formField: continue  # skip select items that may be in form
        if 'item-' in formField: continue
        # if not requestObject[p]: continue # uh...looks like we can have empty items...let's skip 'em
        search_terms[formField] = extractTerms(context, request.POST, formField)
    return search_terms


def doQuery(query, fields):
    # this just returns 40 rows of data from the portal...
    import demodata

    data = demodata.sampledata()
    rows = []
    for d in data:
        row = {}
        for field in fields:
            if field in d:
                row[field] = d[field]
        rows.append(row)
    data = rows

    return data


def doSearch(context, request):
    context['checkitems'] = getFields(request, context)

    if 'items' in context: del context['items']
    context['action'] = 'enumerate'

    return context


def getData(context,request):
    context ={}
    for formField in request.GET:
        context[formField] = request.GET[formField]

    # import datelist
    # print getitems('collectionobjects', 100, '1999-01-01', '2015-05-01', 'month')
    # data = datelist.datelist

    num2ret = context['num2ret']
    period = context['period']
    table = context['activity']
    start = context['start']
    end = context['end']
    data = activity2db.getitems(table, num2ret, start, end, period)

    context['data'] = data
    context['numberofitems'] = len(data)
    return context


def doActivity(context, request):
    context['checkitems'] = getFields(request, context)

    forminput = getFields(request, context)
    if 'items' in context: del context['items']
    context['action'] = 'enumerate'

    # import datelist
    # daterange = datelist.datelist
    # getitems(table, num2ret, start_date, end_date, period)
    # print getitems('collectionobjects', 100, '1999-01-01', '2015-05-01', 'month')

    num2ret = 500
    period = forminput['period'][2]
    table = forminput['activity'][2]
    start = forminput['date.start'][2]
    end = forminput['date.end'][2]

    context['num2ret'] = num2ret
    context['period'] = period
    context['activity'] = table
    context['start'] = start
    context['end'] = end
    daterange = activity2db.getitems(table, num2ret, start, end, period)

    rows = []
    for d in daterange:
        row = {}
        for i,field in enumerate('count date'.split(' ')):
            row[field] = d[i]
        rows.append(row)
    data = rows

    class NameTable(tables.Table):

        count = tables.Column(verbose_name='count')
        date = tables.Column(verbose_name='date')

    table = NameTable(data)

    context['reviewitems'] = table
    context['numberofitems'] = len(data)

    context['action'] = 'end'

    return context


def doEnumerate(context, request):
    data = doQuery('query', 'objmusno_s objname_s objcount_s objfcpverbatim_s objfilecode_ss objassoccult_ss'.split(' '))

    class NameTable(tables.Table):

        def render_objassoccult_ss(self, value):
            if value is not None:
                return ', '.join(value)
            else:
                return ''

        objmusno_s = tables.Column(verbose_name='museum number')
        objname_s = tables.Column(verbose_name='object name')
        objcount_s = tables.Column(verbose_name='count')
        objfcpverbatim_s = tables.Column(verbose_name='field collection place')
        objassoccult_ss = tables.Column(verbose_name='culture')

    table = NameTable(data)

    context['enumerateditems'] = table
    context['numberofitems'] = len(data)

    # set next workflow state
    context['action'] = context['applayout']['enumerate']['parameter']

    return context


def doReview(context, request):
    # foo = tables.TemplateColumn('{{ record.bar }}')
    data = doQuery('query', 'objmusno_s objname_s objcount_s objfcpverbatim_s objfilecode_ss objassoccult_ss'.split(' '))

    class NameTable(tables.Table):

        def render_objassoccult_ss(self, value):
            if value is not None:
                return ', '.join(value)
            else:
                return ''

        objmusno_s = tables.Column(verbose_name='museum number')
        objname_s = tables.TemplateColumn('<input type ="text" value="{{ record.objname_s }}"/>',
                                          verbose_name='object name')
        objcount_s = tables.TemplateColumn('<input type ="text" value="{{ record.objcount_s }}"/>',
                                           verbose_name='count')
        objfcpverbatim_s = tables.TemplateColumn('<input type ="text" value="{{ record.objfcpverbatim_s }}"/>',
                                                 verbose_name='field collection place')
        objassoccult_ss = tables.TemplateColumn('<input type ="text" value="{% record.objassoccult_ss %}"/>',
                                                verbose_name='culture')

    table = NameTable(data)

    context['reviewitems'] = table
    context['numberofitems'] = len(data)

    # set next workflow state
    context['action'] = context['applayout']['review']['parameter']

    if 'items' in context: del context['items']

    return context


def doUpdate(context, request):
    data = doQuery('query', 'objmusno_s objname_s id'.split(' '))

    class NameTable(tables.Table):
        objmusno_s = tables.Column(verbose_name='museum number')
        id = tables.Column(verbose_name='csid')
        updated = tables.Column(verbose_name='status')

    table = NameTable(data)

    context['enumerateditems'] = table
    context['numberofitems'] = len(data)

    # set next workflow state
    context['action'] = context['applayout']['update']['parameter']

    return context


def doSave(context, request):
    context['checkitems'] = getFields(request, context)
    context['enumerate'] = 'update'

    if 'items' in context: del context['items']

    # set next workflow state
    context['action'] = context['applayout']['save']['parameter']

    return context


def doMovecheck(context, request):
    context['checkitems'] = getFields(context, request)
    context['action'] = 'move'

    # set next workflow state
    context['action'] = context['applayout']['movecheck']['parameter']

    if 'items' in context: del context['items']

    return context

def xxx(request,context,config):
    hierarchies = getHierarchies()
    context['hierarchies'] = hierarchies
    if "hierarchy" in request.GET:
        hierarchy = request.GET["hierarchy"]
        context['selected_hierarchy'] = hierarchy
        config_file_name = 'HierarchyViewer'
        res = dbconnector.gethierarchy(hierarchy, config)
        hostname = config.get('connect', 'hostname')
        institution = config.get('info', 'institution')
        port = config.get('link', 'port')
        protocol = config.get('link', 'protocol')
        link = protocol + '://' + hostname + port + '/collectionspace/ui/' + institution
        if hierarchy == 'taxonomy':
            link += '/html/taxon.html?csid=%s'
        elif hierarchy == 'places':
            link += '/html/place.html?csid=%s'
        else:
            link += '/html/concept.html?csid=%s&vocab=' + hierarchy
        for row in res:
            pretty_name = row[0].replace('"', "'")
            if len(pretty_name) > 0 and pretty_name[0] == '@':
                pretty_name = '<' + pretty_name[1:] + '> '
            pretty_name = pretty_name + '", url: "' + link % (row[2])
        data = re.sub(r'\n { label: "(.*?)"},', r'''\n { label: "no parent >> \1"},''', res)
        context['data'] = data
        return context
