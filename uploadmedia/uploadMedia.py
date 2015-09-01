import csv
import sys
import codecs
import time

from cswaExtras import postxml, relationsPayload, getConfig, getCSID


def mediaPayload(mh, institution):
    payload = """<?xml version="1.0" encoding="UTF-8"?>
<document name="media">
<ns2:media_common xmlns:ns2="http://collectionspace.org/services/media" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<blobCsid>%s</blobCsid>
<rightsHolder>%s</rightsHolder>
<creator>%s</creator>
<title>%s</title>
<description>%s</description>
<languageList>
<language>urn:cspace:INSTITUTION.cspace.berkeley.edu:vocabularies:name(languages):item:name(eng)'English'</language>
</languageList>
<identificationNumber>%s</identificationNumber>
<typeList>
<type>%s</type>
</typeList>
<source>%s</source>
<copyrightStatement>%s</copyrightStatement>
</ns2:media_common>
<ns2:media_INSTITUTION xmlns:ns2="http://collectionspace.org/services/media/local/INSTITUTION" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
<approvedForWeb>%s</approvedForWeb>
<primaryDisplay>false</primaryDisplay>
IMAGENUMBERELEMENT
</ns2:media_INSTITUTION>
</document>
"""
    if institution == 'bampfa':
        payload = payload.replace('IMAGENUMBERELEMENT', '<imageNumber>%s</imageNumber>' % mh['imageNumber'])
    else:
        payload = payload.replace('IMAGENUMBERELEMENT', '')
    payload = payload.replace('INSTITUTION', institution)
    payload = payload % (
        mh['blobCsid'], mh['rightsHolderRefname'], mh['creator'], mh['name'], mh['contributor'], mh['objectNumber'],
        mh['imageType'], mh['source'], mh['copyrightStatement'], mh['approvedforweb'])
    # print payload
    return payload


def uploadmedia(mediaElements, config):
    try:
        realm = config.get('connect', 'realm')
        hostname = config.get('connect', 'hostname')
        username = config.get('connect', 'username')
        password = config.get('connect', 'password')
        institution = config.get('info', 'institution')
        alwayscreatemedia = config.get('info', 'alwayscreatemedia')
        alwayscreatemedia = True if alwayscreatemedia.lower() == 'true' else False
    except:
        print "could not get at least one of realm, hostname, username, password or institution from config file."
        # print "can't continue, exiting..."
        raise

    # for ucjeps
    if mediaElements['handling'] == 'slide':
        for extra in 'imagetype copyright source'.split(' '):
            try:
                mediaElements[extra] = config.get('info', extra)
            except:
                mediaElements[extra] = ''

    objectCSID = getCSID('objectnumber', mediaElements['objectnumber'], config)
    if objectCSID == [] or objectCSID is None:
        print "could not get (i.e. find) objectnumber's csid: %s." % mediaElements['objectnumber']
        mediaElements['objectCSID'] = ''
        # raise Exception("<span style='color:red'>Object Number not found: %s!</span>" % mediaElements['objectnumber'])
        # raise
    else:
        objectCSID = objectCSID[0]
        mediaElements['objectCSID'] = objectCSID

    if alwayscreatemedia or objectCSID is not None:

        updateItems = {'objectStatus': 'found',
                       'subjectCsid': '',
                       'objectCsid': mediaElements['objectCSID'],
                       'objectNumber': mediaElements['objectnumber'],
                       'imageNumber': mediaElements['imagenumber'],
                       'blobCsid': mediaElements['blobCSID'],
                       'name': mediaElements['name'],
                       'rightsHolderRefname': mediaElements['rightsholder'],
                       'contributor': mediaElements['contributor'],
                       'creator': mediaElements['creator'],
                       'mediaDate': mediaElements['mediaDate'],
                       'imageType': mediaElements['imagetype'],
                       'copyrightStatement': mediaElements['copyrightstatement'],
                       'source': mediaElements['source'],
        }

        uri = 'media'

        messages = []
        messages.append("posting to media REST API...")
        # print updateItems
        payload = mediaPayload(updateItems, institution)
        messages.append(payload)
        (url, data, mediaCSID, elapsedtime) = postxml('POST', uri, realm, hostname, username, password, payload)
        # elapsedtimetotal += elapsedtime
        messages.append('got mediacsid %s elapsedtime %s ' % (mediaCSID, elapsedtime))
        mediaElements['mediaCSID'] = mediaCSID
        messages.append("media REST API post succeeded...")

        # for PAHMA, each uploaded image becomes the primary
        if institution == 'pahma':
            primary_payload = """<?xml version="1.0" encoding="utf-8" standalone="yes"?>
            <ns2:invocationContext xmlns:ns2="http://collectionspace.org/services/common/invocable"
            <mode>single</mode>
            <docType>""" + mediaCSID + """</docType>
            <singleCSID></singleCSID>
            </ns2:invocationContext>
            """
            postxml('POST', 'batch/57c6de27-4f1e-48d3-a661', realm, hostname, username, password, primary_payload)
        else:
            pass

    # what about mediaElements['handling']?
    if objectCSID is not None:
        # now relate media record to collection object

        uri = 'relations'

        messages.append("posting media2obj to relations REST API...")

        updateItems['objectCsid'] = objectCSID
        updateItems['subjectCsid'] = mediaCSID
        # "urn:cspace:institution.cspace.berkeley.edu:media:id(%s)" % mediaCSID

        updateItems['objectDocumentType'] = 'CollectionObject'
        updateItems['subjectDocumentType'] = 'Media'

        payload = relationsPayload(updateItems)
        (url, data, csid, elapsedtime) = postxml('POST', uri, realm, hostname, username, password, payload)
        #elapsedtimetotal += elapsedtime
        messages.append('got relation csid %s elapsedtime %s ' % (csid, elapsedtime))
        mediaElements['media2objCSID'] = csid
        messages.append("relations REST API post succeeded...")

        # reverse the roles
        messages.append("posting obj2media to relations REST API...")
        temp = updateItems['objectCsid']
        updateItems['objectCsid'] = updateItems['subjectCsid']
        updateItems['subjectCsid'] = temp
        updateItems['objectDocumentType'] = 'Media'
        updateItems['subjectDocumentType'] = 'CollectionObject'
        payload = relationsPayload(updateItems)
        (url, data, csid, elapsedtime) = postxml('POST', uri, realm, hostname, username, password, payload)
        #elapsedtimetotal += elapsedtime
        messages.append('got relation csid %s elapsedtime %s ' % (csid, elapsedtime))
        mediaElements['obj2mediaCSID'] = csid
        messages.append("relations REST API post succeeded...")

    return mediaElements


class CleanlinesFile(file):
    def next(self):
        line = super(CleanlinesFile, self).next()
        return line.replace('\r', '').replace('\n', '') + '\n'


def getRecords(rawFile):
    # csvfile = csv.reader(codecs.open(rawFile,'rb','utf-8'),delimiter="\t")
    try:
        f = CleanlinesFile(rawFile, 'rb')
        csvfile = csv.reader(f, delimiter="|")
    except IOError:
        message = 'Expected to be able to read %s, but it was not found or unreadable' % rawFile
        return message, -1
    except:
        raise

    try:
        records = []
        for row, values in enumerate(csvfile):
            records.append(values)
        return records, len(values)
    except IOError:
        message = 'Could not read (or maybe parse) rows from %s' % rawFile
        return message, -1
    except:
        raise


if __name__ == "__main__":

    print "MEDIA: input  file (fully qualified path): %s" % sys.argv[1]
    print "MEDIA: config file (fully qualified path): %s" % sys.argv[2]

    try:
        form = {'webapp': sys.argv[2]}
        config = getConfig(form)
    except:
        print "MEDIA: could not get configuration"
        sys.exit()

    # print 'config',config
    records, columns = getRecords(sys.argv[1])
    if columns == -1:
        print 'MEDIA: Error! %s' % records
        sys.exit()

    print 'MEDIA: %s columns and %s lines found in file %s' % (columns, len(records), sys.argv[1])
    outputFile = sys.argv[1].replace('.step2.csv', '.step3.csv')
    outputfh = csv.writer(open(outputFile, 'wb'), delimiter="\t")

    for i, r in enumerate(records):

        elapsedtimetotal = time.time()
        mediaElements = {}
        for v1, v2 in enumerate(
                'name size objectnumber blobCSID date creator contributor rightsholder imagenumber handling approvedforweb filenamewithpath'.split(' ')):
            mediaElements[v2] = r[v1]
        mediaElements['approvedforweb'] == 'true' if mediaElements['approvedforweb'] == 'on' else 'false'
        # print mediaElements
        print 'objectnumber %s' % mediaElements['objectnumber']
        try:
            mediaElements = uploadmedia(mediaElements, config)
            print "MEDIA: objectnumber %s, objectcsid: %s, mediacsid: %s, %8.2f" % (
                mediaElements['objectnumber'], mediaElements['objectCSID'], mediaElements['mediaCSID'],
                (time.time() - elapsedtimetotal))
            r.append(mediaElements['mediaCSID'])
            r.append(mediaElements['objectCSID'])
            outputfh.writerow(r)
        except:
            print "MEDIA: create failed for objectnumber %s, %8.2f" % (
                mediaElements['objectnumber'], (time.time() - elapsedtimetotal))
            # raise

