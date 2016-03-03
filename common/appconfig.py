# set global variables

import csv
import solr
from os import path, popen
from copy import deepcopy

from cspace_django_site import settings
from common import cspace  # we use the config file reading function
from json import loads

def get_special(label,labels, row):
    # handle some special cases
    value = row[labels['Role']]
    if label in value:
        parsed_valued = value.replace('%s=' % label,'')
        try:
            values = loads(parsed_valued)
            row[labels['Role']] = [label, values]
        except:
            print 'could not parse JSON for %s: %s' % (value,parsed_valued)


def getParms(parmFile, prmz):
    try:
        f = open(parmFile, 'rb')
        csvfile = csv.reader(f, delimiter="\t")
    except IOError:
        raise
        message = 'Expected to be able to read %s, but it was not found or unreadable' % parmFile
        return message, -1
    except:
        raise

    try:
        rows = []
        for row, values in enumerate(csvfile):
            rows.append(values)

        f.close()

        return parseRows(rows, prmz)

    except IOError:
        message = 'Could not read (or maybe parse) rows from %s' % parmFile
        return message, -1
    except:
        raise


def parseRows(rows, prmz):
    prmz.PARMS = {}
    prmz.HEADER = {}
    labels = {}
    prmz.FIELDS = {}
    prmz.DEFAULTSORTKEY = 'None'

    prmz.SEARCHCOLUMNS = 0
    prmz.SEARCHROWS = 0
    prmz.CSRECORDTYPE = 'cataloging' # default

    functions = 'Search,Facet,bMapper,listDisplay,fullDisplay,gridDisplay,mapDisplay,inCSV'.split(',')
    for function in functions:
        prmz.FIELDS[function] = []

    fieldkeys = 'label fieldtype suggestions solrfield name X order searchtarget'.split(' ')

    for rowid, row in enumerate(rows):
        rowtype = row[0]

        if rowtype == 'header':
            for i, r in enumerate(row):
                prmz.HEADER[i] = r
                labels[r] = i

        elif rowtype == 'server':
            prmz.SOLRSERVER = row[1]

        elif rowtype == 'csrecordtype':
            prmz.CSRECORDTYPE = row[1]

        elif rowtype == 'core':
            prmz.SOLRCORE = row[1]

        elif rowtype == 'title':
            prmz.TITLE = row[1]

        elif rowtype == 'field':

            # nb: this function may modify the value of the 2nd parameter!
            get_special('colors', labels, row)
            get_special('radio', labels, row)

            needed = [row[labels[i]] for i in 'Label Role Suggestions SolrField Name Search SearchTarget'.split(' ')]
            if row[labels['Suggestions']] != '':
                # suggestname = '%s.%s' % (row[labels['Suggestions']], row[labels['Name']])
                suggestname = row[labels['Name']]
            else:
                suggestname = row[labels['Name']]
            needed[4] = suggestname
            prmz.PARMS[suggestname] = needed
            needed.append(rowid)
            if 'sortkey' in row[labels['Role']]:
                prmz.DEFAULTSORTKEY = row[labels['SolrField']]

            for function in functions:
                if len(row) > labels[function] and row[labels[function]] != '':
                    fieldhash = {}
                    for n, v in enumerate(needed):
                        if n == 5 and function == 'Search':  # 5th item in needed is search field x,y coord for layout
                            if v == '':
                                continue
                            searchlayout = (v + ',1').split(',')
                            fieldhash['column'] = int('0' + searchlayout[1])
                            fieldhash['row'] = int('0' + searchlayout[0])
                            prmz.SEARCHCOLUMNS = max(prmz.SEARCHCOLUMNS, int('0' + searchlayout[1]))
                            prmz.SEARCHROWS = max(prmz.SEARCHROWS, int('0' + searchlayout[0]))
                        else:
                            fieldhash[fieldkeys[n]] = v
                    fieldhash['style'] = ''  # temporary hack!
                    fieldhash['type'] = 'text'  # temporary hack!
                    prmz.FIELDS[function].append(fieldhash)

    if prmz.SEARCHROWS == 0: prmz.SEARCHROWS = 1
    if prmz.SEARCHCOLUMNS == 0: prmz.SEARCHCOLUMNS = 1

    return prmz


def loadConfiguration(configFileName):
    config = cspace.getConfig(path.join(settings.BASE_PARENT_DIR, 'config'), configFileName)

# holder for global variables and other parameters
    class prmz:
        pass

    try:
        prmz.DERIVATIVEGRID = config.get('search', 'DERIVATIVEGRID')
        prmz.DERIVATIVECOMPACT = config.get('search', 'DERIVATIVECOMPACT')
        prmz.SIZEGRID = config.get('search', 'SIZEGRID')
        prmz.SIZECOMPACT = config.get('search', 'SIZECOMPACT')
    except:
        print 'could not get image layout (size and derviative to use) from config file, using defaults'
        prmz.DERIVATIVEGRID     = "Thumbnail"
        prmz.DERIVATIVECOMPACT  = "Thumbnail"
        prmz.SIZEGRID           = "100px"
        prmz.SIZECOMPACT        = "100px"

    try:
        prmz.MAXMARKERS = int(config.get('search', 'MAXMARKERS'))
        prmz.MAXRESULTS = int(config.get('search', 'MAXRESULTS'))
        prmz.MAXLONGRESULTS = int(config.get('search', 'MAXLONGRESULTS'))
        prmz.MAXFACETS = int(config.get('search', 'MAXFACETS'))
        prmz.EMAILABLEURL = config.get('search', 'EMAILABLEURL')
        prmz.IMAGESERVER = config.get('search', 'IMAGESERVER')
        prmz.CSPACESERVER = config.get('search', 'CSPACESERVER')
        prmz.INSTITUTION = config.get('search', 'INSTITUTION')
        prmz.BMAPPERSERVER = config.get('search', 'BMAPPERSERVER')
        prmz.BMAPPERDIR = config.get('search', 'BMAPPERDIR')
        prmz.BMAPPERCONFIGFILE = config.get('search', 'BMAPPERCONFIGFILE')
        prmz.BMAPPERURL = config.get('search', 'BMAPPERURL')
        # SOLRSERVER = config.get('search', 'SOLRSERVER')
        # SOLRCORE = config.get('search', 'SOLRCORE')
        prmz.LOCALDIR = config.get('search', 'LOCALDIR')
        prmz.SEARCH_QUALIFIERS = config.get('search', 'SEARCH_QUALIFIERS').split(',')
        prmz.SEARCH_QUALIFIERS = [unicode(x) for x in prmz.SEARCH_QUALIFIERS]
        #prmz.FIELDDEFINITIONS = config.get('search', 'FIELDDEFINITIONS')
        prmz.CSVPREFIX = config.get('search', 'CSVPREFIX')
        prmz.CSVEXTENSION = config.get('search', 'CSVEXTENSION')
        # prmz.TITLE = config.get('search', 'TITLE')
        prmz.SUGGESTIONS = config.get('search', 'SUGGESTIONS')
        #LAYOUT = config.get('search', 'LAYOUT')

        try:
            prmz.VERSION = popen("cd " + settings.BASE_PARENT_DIR + " ; /usr/bin/git describe --always").read().strip()
            if prmz.VERSION == '':  # try alternate location for git (this is the usual Mac location)
                prmz.VERSION = popen("/usr/local/bin/git describe --always").read().strip()
        except:
            prmz.VERSION = 'Unknown'

    except:
        print 'error in configuration file %s' % path.join(settings.BASE_PARENT_DIR, 'config/' + configFileName)
        print 'this webapp will probably not work.'

    return prmz

def loadFields(fieldFile, prmz):
    # get "frontend" configuration from the ... frontend configuration file
    print 'Reading field definitions from %s' % path.join(settings.BASE_PARENT_DIR, 'config/' + fieldFile)

    prmz.LOCATION = ''
    prmz.DROPDOWNS = []
    prmz.FACETS = {}

    prmz = getParms(path.join(settings.BASE_PARENT_DIR, 'config/' + fieldFile), prmz)

    for p in prmz.PARMS:
        if 'dropdown' in prmz.PARMS[p][1]:
            prmz.DROPDOWNS.append(prmz.PARMS[p][4])
        if 'location' in prmz.PARMS[p][1]:
            prmz.LOCATION = prmz.PARMS[p][3]

    if prmz.LOCATION == '':
        print "LOCATION not set, please specify a variable as 'location'"

    facetfields = [f['solrfield'] for f in prmz.FIELDS['Search'] if f['fieldtype'] == 'dropdown']

    # facetNames = [f['name'] for f in FIELDS['Facet']]
    #facetfields = []

    #for f in FIELDS['Search']:
    #    if 'dropdown' in f['fieldtype'] and not f['name'] in facetNames:
    #        facetfields.append(f['solrfield'])

    # create a connection to a solr server

    print 'Starting facet search at %s/%s' % (prmz.SOLRSERVER, prmz.SOLRCORE)
    s = solr.SolrConnection(url='%s/%s' % (prmz.SOLRSERVER, prmz.SOLRCORE))

    try:
        response = s.query('*:*', facet='true', facet_field=facetfields, fq={},
                           rows=0, facet_limit=1000, facet_mincount=1, start=0)

        print 'Solr search succeeded, %s results' % (response.numFound)

        # facets = getfacets(response)

        facets = response.facet_counts
        facets = facets['facet_fields']
        _facets = {}
        for key, values in facets.items():
            _v = []
            for k, v in values.items():
                _v.append((k, v))
            _facets[key] = sorted(_v, key=lambda (a, b): b, reverse=True)
        facets = _facets

        for facet, values in facets.items():
            print 'facet', facet, len(values)
            prmz.FACETS[facet] = sorted(values, key=lambda tup: tup[0])
            # build dropdowns for searching
            for f in prmz.FIELDS['Search']:
                #if f['solrfield'] == facet and 'dropdown' in f['fieldtype']:
                if 'dropdown' in f['fieldtype'] and f['solrfield'] == facet:
                    # tricky: note we are in fact inserting the list of dropdown
                    # values into the existing global variable FIELDS
                    f['dropdowns'] = sorted(values, key=lambda tup: tup[0])

    #except:
    except Exception as inst:
        #raise
        errormsg = 'Solr query for facets failed: %s' % str(inst)
        solrIsUp = False
        print 'Solr facet search failed. Concluding that Solr is down or unreachable... Will not be trying again! Please fix and restart!'

    # figure out which solr fields are the required ones...
    prmz.REQUIRED = []
    requiredfields = 'csid mainentry location accession objectno sortkey blob card primaryimage'.split(' ')
    for p in prmz.PARMS:
        for r in requiredfields:
            if r in prmz.PARMS[p][1]:
                if prmz.PARMS[p][3] not in prmz.REQUIRED:
                    prmz.REQUIRED.append(prmz.PARMS[p][3])

    return prmz

