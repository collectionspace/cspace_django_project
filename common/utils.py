# -*- coding: UTF-8 -*-
import re
import time, datetime
import csv
import solr
import cgi

from os import path
from copy import deepcopy

from django.http import HttpResponse, HttpResponseRedirect
# from cspace_django_site.main import cspace_django_site



SolrIsUp = True  # an initial guess! this is verified below...


def loginfo(logger, infotype, context, request):
    logdata = ''
    # user = getattr(request, 'user', None)
    if request.user and not request.user.is_anonymous():
        username = request.user.username
    else:
        username = '-'
    if 'count' in context:
        count = context['count']
    else:
        count = '-'
    if 'querystring' in context:
        logdata = context['querystring']
    if 'url' in context:
        logdata += ' :: %s' % context['url']
    logger.info('%s :: %s :: %s :: %s' % (infotype, count, username, logdata))


def getfromXML(element, xpath):
    result = element.find(xpath)
    if result is None: return ''
    result = '' if result.text is None else result.text
    result = re.sub(r"^.*\)'(.*)'$", "\\1", result)
    return result


def deURN(urn):
    # find identifier in URN
    m = re.search("\'(.*)\'$", urn)
    if m is not None:
        # strip out single quotes
        return m.group(0)[1:len(m.group(0)) - 1]


def getfields(fieldset, pickField, prmz):
    result = []
    pickField = pickField.split(',')
    for pick in pickField:
        if not pick in 'name solrfield label'.split(' '):
            pick = 'solrfield'
        result.append([f[pick] for f in prmz.FIELDS[fieldset] if f['fieldtype'] != 'constant'])
    if len(pickField) > 1:
        # is this right??
        return zip(result[0], result[1])
    else:
        return result[0]


def getfacets(response):
    # facets = response.get('facet_counts').get('facet_fields')
    facets = response.facet_counts
    facets = facets['facet_fields']
    _facets = {}
    for key, values in facets.items():
        _v = []
        for k, v in values.items():
            _v.append((k, v))
        _facets[key] = sorted(_v, key=lambda (a, b): b, reverse=True)
    return _facets


def parseTerm(queryterm):
    queryterm = queryterm.strip(' ')
    terms = queryterm.split(' ')
    terms = ['"' + t + '"' for t in terms]
    result = ' AND '.join(terms)
    if 'AND' in result: result = '(' + result + ')'  # we only need to wrap the query if it has multiple terms
    return result


def makeMarker(location):
    if location:
        location = location.replace(' ', '')
        latitude, longitude = location.split(',')
        latitude = float(latitude)
        longitude = float(longitude)
        return "%0.2f,%0.2f" % (latitude, longitude)
    else:
        return None


def checkValue(cell):
    # the following few lines are a hack to handle non-unicode data which appears to be present in the solr datasource
    if isinstance(cell, unicode):
        try:
            cell = cell.translate({0xd7: u"x"})
            cell = cell.decode('utf-8', 'ignore').encode('utf-8')
        except:
            print 'unicode problem', cell.encode('utf-8', 'ignore')
            cell = cell.encode('utf-8', 'ignore')
    return cell


def writeCsv(filehandle, fieldset, items, writeheader=False, csvFormat='csv'):
    # print "Fieldset: %s" % fieldset
    writer = csv.writer(filehandle, delimiter='\t')
    # write the header
    if writeheader:
        writer.writerow(fieldset) 
    for item in items:
        # get the cells from the item dict in the order specified; make empty cells if key is not found.
        row = []
        if csvFormat == 'bmapper':
            r = []
            for x in item['otherfields']:
                if x['name'] not in fieldset:
                    continue
                if type(x['value']) == type([]):
                    x['value'] = '|'.join(x['value'])
                    pass
                r.append(checkValue(x['value']))
            location = item['location']
            l = location.split(',')
            r.append(l[0])
            r.append(l[1])
            for cell in r:
                row.append(cell)
        elif csvFormat == 'statistics':
            row.append(checkValue(item[0]))  # summarizeon
            row.append(checkValue(item[1]))  # count
            for x in item[2]:
                if type(x) == type([]):
                    x = '|'.join(x)
                    pass
                cell = checkValue(x)
                row.append(cell)
        else:
            for x in item['otherfields']:
                if x['name'] not in fieldset:
                    continue
                if type(x['value']) == type([]):
                    x['value'] = '|'.join(x['value'])
                    pass
                cell = checkValue(x['value'])
                row.append(cell)
        writer.writerow(row)
    return filehandle


def getMapPoints(context, requestObject):
    mappableitems = []
    if 'select-item' in requestObject:
        mapitems = context['items']
        numSelected = len(mapitems)
    else:
        selected = []
        for p in requestObject:
            if 'item-' in p:
                selected.append(requestObject[p])
        numSelected = len(selected)
        mapitems = []
        for item in context['items']:
            if item['csid'] in selected:
                mapitems.append(item)
    for item in mapitems:
        try:
            m = makeMarker(item['location'])
            if m is not None:
                mappableitems.append(item)
        except KeyError:
            pass
    return mappableitems, numSelected


def setupGoogleMap(requestObject, context, prmz):
    context = doSearch(context, prmz)
    selected = []
    for p in requestObject:
        if 'item-' in p:
            selected.append(requestObject[p])
    mappableitems = []
    markerlist = []
    markerlength = 200
    for item in context['items']:
        if item['csid'] in selected:
            # if True:
            try:
                m = makeMarker(item['location'])
                if markerlength > 2048: break
                if m is not None:
                    markerlist.append(m)
                    mappableitems.append(item)
                    markerlength += len(m) + 8  # 8 is the length of '&markers='
            except KeyError:
                pass
    context['mapmsg'] = []
    if len(context['items']) < context['count']:
        context['mapmsg'].append('%s points plotted. %s selected objects examined (of %s in result set).' % (
            len(markerlist), len(selected), context['count']))
    else:
        context['mapmsg'].append(
            '%s points plotted. all %s selected objects in result set examined.' % (len(markerlist), len(selected)))
    context['items'] = mappableitems
    context['markerlist'] = '&markers='.join(markerlist)
    # context['markerlist'] = '&markers='.join(markerlist[:MAXMARKERS])

    # if len(markerlist) >= MAXMARKERS:
    #    context['mapmsg'].append(
    #        '%s points is the limit. Only first %s accessions (with latlongs) plotted!' % (MAXMARKERS, len(markerlist)))

    return context


def setupBMapper(requestObject, context, prmz):
    context['berkeleymapper'] = 'set'
    context = doSearch(context, prmz)
    mappableitems, numSelected = getMapPoints(context, requestObject)
    context['mapmsg'] = []
    filename = 'bmapper%s.csv' % datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filehandle = open(path.join(prmz.LOCALDIR, filename), 'wb')
    writeCsv(filehandle, getfields('bMapper', 'name', prmz), mappableitems, writeheader=False, csvFormat='bmapper')
    filehandle.close()
    context['mapmsg'].append('%s points of the %s selected objects examined had latlongs (%s in result set).' % (
        len(mappableitems), numSelected, context['count']))
    # context['mapmsg'].append('if our connection to berkeley mapper were working, you be able see them plotted there.')
    context['items'] = mappableitems
    bmapperconfigfile = '%s/%s/%s' % (prmz.BMAPPERSERVER, prmz.BMAPPERDIR, prmz.BMAPPERCONFIGFILE)
    tabfile = '%s/%s/%s' % (prmz.BMAPPERSERVER, prmz.BMAPPERDIR, filename)
    context['bmapperurl'] = prmz.BMAPPERURL % (tabfile, bmapperconfigfile)
    return context
    # return HttpResponseRedirect(context['bmapperurl'])


def computeStats(requestObject, context, prmz):
    context['summarizeonlabel'] = prmz.PARMS[requestObject['summarizeon']][0]
    context['summarizeon'] = requestObject['summarizeon']
    context['summaryrows'] = [requestObject[z] for z in requestObject if 'include-' in z]
    context['summarylabels'] = [prmz.PARMS[var][0] for var in context['summaryrows']]
    context = doSearch(context, prmz)
    return context


def setupCSV(requestObject, context, prmz):
    if 'downloadstats' in requestObject:
        context = computeStats(requestObject, context, prmz)
        csvitems = context['summaryrows']
        format = 'statistics'
    else:
        format = 'csv'
        context = doSearch(context, prmz)
        selected = []
        # check to see if 'select all' is clicked...if so, skip checking individual items
        if 'select-item' in requestObject:
            csvitems = context['items']
        else:
            for p in requestObject:
                if 'item-' in p:
                    selected.append(requestObject[p])
            csvitems = []
            for item in context['items']:
                if item['csid'] in selected:
                    csvitems.append(item)

    if 'downloadstats' in requestObject:
        fieldset = [context['summarizeonlabel'], 'N'] + context['summarylabels']
    else:
        fieldset = getfields('inCSV', 'name', prmz)

    return format, fieldset, csvitems


def setDisplayType(requestObject):
    if 'displayType' in requestObject:
        displayType = requestObject['displayType']
    elif 'search-list' in requestObject:
        displayType = 'list'
    elif 'search-full' in requestObject:
        displayType = 'full'
    elif 'search-grid' in requestObject:
        displayType = 'grid'
    else:
        displayType = 'list'

    return displayType


def extractValue(listItem, key):
    # make all arrays into strings for display
    if key in listItem:
        if type(listItem[key]) == type([]):
            temp = ', '.join(listItem[key])
        else:
            temp = listItem[key]
    else:
        temp = ''

    # handle dates (convert them to collatable strings)
    if isinstance(temp, datetime.date):
        try:
            # item[p] = item[p].toordinal()
            temp = temp.isoformat().replace('T00:00:00+00:00', '')
        except:
            print 'date problem: ', temp

    return temp


def setConstants(context, prmz):
    if not SolrIsUp: context['errormsg'] = 'Solr is down!'
    context['suggestsource'] = prmz.SUGGESTIONS
    context['title'] = prmz.TITLE
    context['apptitle'] = prmz.TITLE
    context['imageserver'] = prmz.IMAGESERVER
    context['cspaceserver'] = prmz.CSPACESERVER
    context['institution'] = prmz.INSTITUTION
    context['emailableurl'] = prmz.EMAILABLEURL
    context['version'] = prmz.VERSION
    #context['layout'] = prmz.LAYOUT
    context['dropdowns'] = prmz.FACETS
    context['derivativecompact'] = prmz.DERIVATIVECOMPACT
    context['derivativegrid'] = prmz.DERIVATIVEGRID
    context['sizecompact'] = prmz.SIZECOMPACT
    context['sizegrid'] = prmz.SIZEGRID
    context['timestamp'] = time.strftime("%b %d %Y %H:%M:%S", time.localtime())
    context['qualifiers'] = [{'val': s, 'dis': s} for s in prmz.SEARCH_QUALIFIERS]
    context['resultoptions'] = [100, 500, 1000, 2000, 10000]

    context['searchrows'] = range(prmz.SEARCHROWS + 1)[1:]
    context['searchcolumns'] = range(prmz.SEARCHCOLUMNS + 1)[1:]

    emptyCells = {}
    for row in context['searchrows']:
        for col in context['searchcolumns']:
            empty = True
            for field in prmz.FIELDS['Search']:
                if field['row'] == row and field['column'] == col:
                    empty = False
            if empty:
                if not row in emptyCells:
                    emptyCells[row] = {}
                emptyCells[row][col] = 'X'
    context['emptycells'] = emptyCells

    context['displayTypes'] = (
        ('list', 'List'),
        ('full', 'Full'),
        ('grid', 'Grid'),
    )

    # copy over form values to context if they exist
    try:
        requestObject = context['searchValues']

        # build a list of the search term qualifiers used in this query (for templating...)
        qualfiersInUse = []
        for formkey, formvalue in requestObject.items():
            if '_qualifier' in formkey:
                qualfiersInUse.append(formkey + ':' + formvalue)

        context['qualfiersInUse'] = qualfiersInUse

        context['displayType'] = setDisplayType(requestObject)
        if 'url' in requestObject: context['url'] = requestObject['url']
        if 'querystring' in requestObject: context['querystring'] = requestObject['querystring']
        if 'core' in requestObject: context['core'] = requestObject['core']
        if 'pixonly' in requestObject: context['pixonly'] = requestObject['pixonly']
        if 'maxresults' in requestObject: context['maxresults'] = int(requestObject['maxresults'])
        context['start'] = int(requestObject['start']) if 'start' in requestObject else 1
        context['maxfacets'] = int(requestObject['maxfacets']) if 'maxfacets' in requestObject else prmz.MAXFACETS
        context['sortkey'] = requestObject['sortkey'] if 'sortkey' in requestObject else prmz.DEFAULTSORTKEY
    except:
        print "no searchValues set"
        context['displayType'] = setDisplayType({})
        context['url'] = ''
        context['querystring'] = ''
        context['core'] = prmz.SOLRCORE
        context['maxresults'] = 0
        context['start'] = 1
        context['sortkey'] = prmz.DEFAULTSORTKEY

    if context['start'] < 1: context['start'] = 1

    context['PARMS'] = prmz.PARMS
    if not 'FIELDS' in context:
        context['FIELDS'] = prmz.FIELDS

    return context


def doSearch(context, prmz):
    elapsedtime = time.time()
    solr_server = prmz.SOLRSERVER
    solr_core = prmz.SOLRCORE
    context = setConstants(context, prmz)
    requestObject = context['searchValues']

    formFields = deepcopy(prmz.FIELDS)
    for searchfield in formFields['Search']:
        if searchfield['name'] in requestObject.keys():
            searchfield['value'] = requestObject[searchfield['name']]
        else:
            searchfield['value'] = ''

    context['FIELDS'] = formFields

    # create a connection to a solr server
    s = solr.SolrConnection(url='%s/%s' % (solr_server, solr_core))
    queryterms = []
    urlterms = []

    if 'berkeleymapper' in context:
        displayFields = 'bMapper'
    elif 'csv' in requestObject:
        displayFields = 'inCSV'
    else:
        displayFields = context['displayType'] + 'Display'

    facetfields = getfields('Facet', 'solrfield', prmz)
    if 'summarize' in requestObject or 'downloadstats' in requestObject:
        solrfl = [prmz.PARMS[p][3] for p in context['summaryrows']]
        solrfl.append(prmz.PARMS[context['summarizeon']][3])
    else:
        solrfl = getfields(displayFields, 'solrfield', prmz)
    solrfl += prmz.REQUIRED  # always get these
    if 'map-google' in requestObject or 'csv' in requestObject or 'map-bmapper' in requestObject or 'summarize' in requestObject or 'downloadstats' in requestObject:
        querystring = requestObject['querystring']
        url = requestObject['url']
        # Did the user request the full set?
        if 'select-item' in requestObject:
            context['maxresults'] = min(requestObject['count'], prmz.MAXRESULTS)
            context['start'] = 1
    else:
        for p in requestObject:
            if p in ['csrfmiddlewaretoken', 'displayType', 'resultsOnly', 'maxresults', 'url', 'querystring', 'pane',
                     'pixonly', 'locsonly', 'acceptterms', 'submit', 'start', 'sortkey', 'count', 'summarizeon',
                     'summarize', 'summaryfields']: continue
            if '_qualifier' in p: continue
            if 'select-' in p: continue  # skip select control for map markers
            if 'include-' in p: continue  # skip form values used in statistics
            if 'item-' in p: continue
            if not requestObject[p]: continue  # uh...looks like we can have empty items...let's skip 'em
            searchTerm = requestObject[p]
            terms = searchTerm.split(' OR ')
            ORs = []
            querypattern = '%s:%s'  # default search expression pattern (dates are different)
            for t in terms:
                t = t.strip()
                if t == 'Null':
                    t = '[* TO *]'
                    index = '-' + prmz.PARMS[p][3]
                else:
                    if p in prmz.DROPDOWNS:
                        # if it's a value in a dropdown, it must always be an "exact search"
                        # only our own double quotes are unescaped
                        t = t.replace('"','\\"')
                        t = '"' + t + '"'
                        index = prmz.PARMS[p][3].replace('_txt', '_s')
                    elif p + '_qualifier' in requestObject:
                        # print 'qualifier:',requestObject[p+'_qualifier']
                        index = prmz.PARMS[p][3]
                        # if this is a "switcharoo field", use the specified shadow
                        if prmz.PARMS[p][6] != '':
                            index = prmz.PARMS[p][6]
                        qualifier = requestObject[p + '_qualifier']
                        if qualifier == 'exact':
                            # for exact searches, reset the index to the original in case the switcharoo changed it
                            index = prmz.PARMS[p][3]
                            index = index.replace('_txt', '_s')
                            # only our own double quotes are unescaped
                            t = t.replace('"','\\"')
                            t = '"' + t + '"'
                        elif qualifier == 'phrase':
                            index = index.replace('_ss', '_txt').replace('_s', '_txt')
                            # only our own double quotes are unescaped
                            t = t.replace('"', '\\"')
                            t = '"' + t + '"'
                        elif qualifier == 'keyword':
                            # eliminate some characters that might confuse solr's query parser
                            t = re.sub(r'[\[\]\:\(\)\" ]', ' ', t).strip()
                            # hyphen is allowed, but only as a negation operator
                            t = re.sub(r'([^ ])-', '\1 ', ' ' + t).strip()
                            # get rid of muliple spaces in a row
                            t = re.sub(r' +', ' ', t)
                            t = t.split(' ')
                            t = ' +'.join(t)
                            t = '(+' + t + ')'
                            t = t.replace('+-', '-')  # remove the plus if user entered a minus
                            index = index.replace('_ss', '_txt').replace('_s', '_txt')
                    elif '_dt' in prmz.PARMS[p][3]:
                        querypattern = '%s: "%sZ"'
                        index = prmz.PARMS[p][3]
                    else:
                        # if no search qualifier is specified use the 'phrase' approach, copied from above
                        # eliminate some characters that might confuse solr's query parser
                        index = prmz.PARMS[p][3]
                        #index = index.replace('_ss', '_txt').replace('_s', '_txt')
                        # escape funny characters
                        t = re.sub(r'([\[\]\:\(\)\")\-\. ])', r'\\\g<1>', t)
                        #t = '"' + t + '"'
                if t == 'OR': t = '"OR"'
                if t == 'AND': t = '"AND"'
                ORs.append(querypattern % (index, t))
            searchTerm = ' OR '.join(ORs)
            if ' ' in searchTerm and not '[* TO *]' in searchTerm: searchTerm = ' (' + searchTerm + ') '
            # print searchTerm
            queryterms.append(searchTerm)
            urlterms.append('%s=%s' % (p, cgi.escape(requestObject[p])))
            if p + '_qualifier' in requestObject:
                # print 'qualifier:',requestObject[p+'_qualifier']
                urlterms.append('%s=%s' % (p + '_qualifier', cgi.escape(requestObject[p + '_qualifier'])))
        querystring = ' AND '.join(queryterms)

        if urlterms != []:
            urlterms.append('displayType=%s' % context['displayType'])
            urlterms.append('maxresults=%s' % context['maxresults'])
            urlterms.append('start=%s' % context['start'])

            if 'summarize' in requestObject or 'downloadstats' in requestObject:
                urlterms.append('summarize=%s' % context['summarizeon'])
                urlterms.append('summaryfields=%s' % ','.join(context['summaryrows']))
        url = '&'.join(urlterms)

    if 'pixonly' in context:
        pixonly = context['pixonly']
        querystring += " AND %s:[* TO *]" % prmz.PARMS['blobs'][3]
        url += '&pixonly=True'
    else:
        pixonly = None

    if 'locsonly' in requestObject:
        locsonly = requestObject['locsonly']
        querystring += " AND %s:[-90,-180 TO 90,180]" % prmz.LOCATION
        url += '&locsonly=True'
    else:
        locsonly = None

    # print 'Solr query: %s' % querystring
    try:
        startpage = context['maxresults'] * (context['start'] - 1)
    except:
        startpage = 0
        context['start'] = 1
    try:
        solrtime = time.time()
        response = s.query(querystring, facet='true', facet_field=facetfields, fq={}, fields=solrfl,
                           rows=context['maxresults'], facet_limit=prmz.MAXFACETS, sort=context['sortkey'],
                           facet_mincount=1, start=startpage)
        print 'Solr search succeeded, %s results, %s rows requested starting at %s; %8.2f seconds.' % (
            response.numFound, context['maxresults'], startpage, time.time() - solrtime)
    # except:
    except Exception as inst:
        # raise
        print 'Solr search failed: %s' % str(inst)
        context['errormsg'] = 'Solr4 query failed'
        return context

    results = response.results

    context['items'] = []
    summaryrows = {}
    imageCount = 0
    for i, rowDict in enumerate(results):
        item = {}
        item['counter'] = i

        if 'summarize' in requestObject or 'downloadstats' in requestObject:
            summarizeon = extractValue(rowDict, prmz.PARMS[context['summarizeon']][3])
            summfields = [extractValue(rowDict, prmz.PARMS[p][3]) for p in context['summaryrows']]
            if not summarizeon in summaryrows:
                x = []
                for ii in range(len(context['summaryrows'])): x.append([])
                summaryrows[summarizeon] = [0, deepcopy(x)]
            for sumi, sumcol in enumerate(summfields):
                if not sumcol in summaryrows[summarizeon][1][sumi]:
                    summaryrows[summarizeon][1][sumi] += [sumcol, ]
                    # print summarizeon, sumi, sumcol, summaryrows[summarizeon][1][sumi]
            summaryrows[summarizeon][0] += 1

        # pull out the fields that have special functions in the UI
        for p in prmz.PARMS:
            if 'mainentry' in prmz.PARMS[p][1]:
                item['mainentry'] = extractValue(rowDict, prmz.PARMS[p][3])
            elif 'accession' in prmz.PARMS[p][1]:
                x = prmz.PARMS[p]
                item['accession'] = extractValue(rowDict, prmz.PARMS[p][3])
                item['accessionfield'] = prmz.PARMS[p][4]
            if 'sortkey' in prmz.PARMS[p][1]:
                item['sortkey'] = extractValue(rowDict, prmz.PARMS[p][3])


        otherfields = []
        for p in prmz.FIELDS[displayFields]:
            try:
                multi = len(rowDict[p['solrfield']]) if '_ss' in p['solrfield'] else 0
                value2use = rowDict[p['solrfield']]
                if type(p['fieldtype']) == type({}):
                    value2use = [p['fieldtype'][v] for v in value2use]
                    otherfields.append({'label': p['label'], 'name': p['name'], 'multi': multi, 'value': value2use, 'special': True})
                else:
                    otherfields.append({'label': p['label'], 'name': p['name'], 'multi': multi, 'value': value2use})
            except:
                #raise
                otherfields.append({'label': p['label'], 'name': p['name'], 'multi': 0, 'value': ''})
        item['otherfields'] = otherfields
        if 'csid_s' in rowDict.keys():
            item['csid'] = rowDict['csid_s']
        # the list of blob csids need to remain an array, so restore it from psql result
        if 'blob_ss' in rowDict.keys():
            item['blobs'] = rowDict['blob_ss']
            imageCount += len(item['blobs'])
        if prmz.LOCATION in rowDict.keys():
            item['marker'] = makeMarker(rowDict[prmz.LOCATION])
            item['location'] = rowDict[prmz.LOCATION]
        context['items'].append(item)

    # if context['displayType'] in ['full', 'grid'] and response._numFound > prmz.MAXRESULTS:
    # context['recordlimit'] = '(limited to %s for long display)' % prmz.MAXRESULTS
    #    context['items'] = context['items'][:prmz.MAXLONGRESULTS]
    if context['displayType'] in ['full', 'grid', 'list'] and response._numFound > context['maxresults']:
        context['recordlimit'] = '(display limited to %s)' % context['maxresults']

    # I think this hack works for most values... but really it should be done properly someday... ;-)
    numberOfPages = 1 + int(response._numFound / (context['maxresults'] + 0.001))
    context['lastpage'] = numberOfPages
    context['pagesummary'] = 'Page %s of %s [items %s to %s]. ' % (
        context['start'], numberOfPages, startpage + 1,
        min(context['start'] * context['maxresults'], response._numFound))

    context['count'] = response._numFound

    m = {}
    for p in prmz.PARMS:
        m[prmz.PARMS[p][3]] = prmz.PARMS[p][4]

    facets = getfacets(response)
    context['labels'] = [p['label'] for p in prmz.FIELDS[displayFields]]
    context['facets'] = [[m[f], facets[f]] for f in facetfields]
    context['fields'] = getfields('Facet', 'label', prmz)
    context['statsfields'] = getfields('inCSV', 'name,label,solrfield', prmz)
    context['summaryrows'] = [[r, summaryrows[r][0], summaryrows[r][1]] for r in sorted(summaryrows.keys())]
    context['itemlisted'] = len(context['summaryrows'])
    context['range'] = range(len(facetfields))
    context['pixonly'] = pixonly
    context['locsonly'] = locsonly
    try:
        context['pane'] = requestObject['pane']
    except:
        context['pane'] = '0'
    try:
        context['resultsOnly'] = requestObject['resultsOnly']
    except:
        pass

    context['imagecount'] = imageCount
    context['url'] = url
    context['querystring'] = querystring
    context['core'] = solr_core
    context['time'] = '%8.3f' % (time.time() - elapsedtime)
    return context

