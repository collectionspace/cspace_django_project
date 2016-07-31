#!/usr/bin/env /usr/bin/python
# -*- coding: UTF-8 -*-

import csv, sys, time, os, datetime

reload(sys)
sys.setdefaultencoding('utf-8')


def getActivities(form):
    selected = form.get('activity')

    activities = [('acquisitions', 'acquisitions'),
                  ('citations', 'citations'),
                  ('claims', 'claims'),
                  ('collection objects', 'collectionobjects'),
                  ('concept authorities', 'conceptauthorities'),
                  ('concepts', 'concepts'),
                  ('condition hecks', 'conditionchecks'),
                  ('contacts', 'contacts'),
                  ('dimensions', 'dimensions'),
                  ('exhibitions', 'exhibitions'),
                  ('groups', 'groups'),
                  ('imports', 'imports'),
                  ('intakes', 'intakes'),
                  ('loansin', 'loansin'),
                  ('loansout', 'loansout'),
                  ('location authorities', 'locationauthorities'),
                  ('locations', 'locations'),
                  ('media', 'media'),
                  ('movements', 'movements'),
                  ('notes', 'notes'),
                  ('objectexit', 'objectexit'),
                  ('organizations', 'organizations'),
                  ('org authorities', 'orgauthorities'),
                  ('person authorities', 'personauthorities'),
                  ('persons', 'persons'),
                  ('place authorities', 'placeauthorities'),
                  ('places', 'places'),
                  ('public items', 'publicitems'),
                  ('relations', 'relations'),
                  ('reports', 'reports'),
                  ('taxon', 'taxon'),
                  ('taxonomy authority', 'taxonomyauthority'),
                  ('valuation controls', 'valuationcontrols'),
                  ('vocabularies', 'vocabularies'),
                  ('vocabulary items', 'vocabularyitems'),
                  ('work authorities', 'workauthorities'),
                  ('works', 'works')
                  ]

    return activities, selected


def getPeriods(form):
    selected = form.get('period')

    period = [('daily', 'day'),
              ('weekly', 'week'),
              ('monthly', 'month'),
              ('yearly', 'year')
              ]

    return period, selected


def tricoderUsers():
    # *** Ape prohibited list code to get table ***
    return {
        'A1732177': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7827)'Michael T. Black'",
         'A1676856': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(8700)'Raksmey Mam'",
         'A0951620': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7475)'Leslie Freund'",
         'A1811681': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7652)'Natasha Johnson'",
         'A2346921': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(9090)'Corri MacEwen'",
         'A2055958': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(8683)'Alicja Egbert'",
         'A2507976': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(8731)'Tya Ates'",
         'A2247942': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(9185)'Alex Levin'",
         'A2346563': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(9034)'Martina Smith'",
         'A1728294': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7420)'Jane L. Williams'",
         'A1881977': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(8724)'Allison Lewis'",
         'A2472847': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(RowanGard1342219780674)'Rowan Gard'",
         'A1687900': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7500)'Elizabeth Minor'",
         'A2472958': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(AlexanderJackson1345659630608)'Alexander Jackson'",
         'A2503701': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(GavinLee1349386412719)'Gavin Lee'",
         'A2504029': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(RonMartin1349386396342)'Ron Martin' ",
         'A1148429': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(8020)'Paolo Pellegatti'",
         'A0904690': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7267)'Victoria Bradshaw'",
         'A2525169': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(GrainneHebeler1354748670308)'Grainne Hebeler'",         '20271721': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(KatieFleming1353023599564)'KatieFleming'",
         'A2266779': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(KatieFleming1353023599564)'KatieFleming'",
         'A2204739': "urn:cspace:pahﬁma.cspace.berkeley.edu:personauthorities:name(person):item:name(PaigeWalker1351201763000)'PaigeWalker'",
         'A0701434': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7248)'Madeleine W. Fang'",
         'A2532024': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(LindaWaterfield1358535276741)'LindaWaterfield'",
         'A2581770': "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(JonOligmueller1372192617217)'JonOligmueller'"}


def getHandlers(form):
    selected = form.get('handlerRefName')
    institution = form.get('institution')

    if institution == 'bampfa':
        handlerlist = [
            ('Kelly Bennett', 'KB'),
            ('Gary Bogus', 'GB'),
            ('Lisa Calden', 'LC'),
            ('Stephanie Cannizzo', 'SC'),
            ('Genevieve Cottraux', 'GC'),
            ('Laura Hansen', 'LH'),
            ('Michael Meyers', 'MM'),
            ('Scott Orloff', 'SO'),
            ('Pamela Pack', 'PP'),
            ('Julia White', 'JW'),
        ]
    else:

        handlerlist = [
            ("Victoria Bradshaw", "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7267)'Victoria Bradshaw'"),
            ("Zachary Brown", "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(ZacharyBrown1389986714647)'Zachary Brown'"),
            ("Alicja Egbert", "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(8683)'Alicja Egbert'"),
            ("Madeleine Fang", "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7248)'Madeleine W. Fang'"),
            ("Leslie Freund", "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7475)'Leslie Freund'"),
            ("Natasha Johnson", "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7652)'Natasha Johnson'"),
            ("Brenna Jordan", "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(BrennaJordan1383946978257)'Brenna Jordan'"),
            ("Corri MacEwen", "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(9090)'Corri MacEwen'"),
            ("Karyn Moore", "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(KarynMoore1399567930777)'Karyn Moore'"),
            ("Jon Oligmueller", "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(JonOligmueller1372192617217)'Jon Oligmueller'"),
            ("Martina Smith", "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(9034)'Martina Smith'"),
            ("Linda Waterfield", "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(LindaWaterfield1358535276741)'Linda Waterfield'"),
            ("Jane Williams", "urn:cspace:pahma.cspace.berkeley.edu:personauthorities:name(person):item:name(7420)'Jane L. Williams'")
        ]

    return handlerlist, selected


def getReasons(form):
    selected = form.get('reason')
    institution = form.get('institution')

    if institution == 'bampfa':
        reasons = [
            ("urn:cspace:bampfa.cspace.berkeley.edu:vocabularies:name(movereason):item:name(2015Inventory1422385313472)'2015 Inventory'", "2015 Inventory"),
            ("urn:cspace:bampfa.cspace.berkeley.edu:vocabularies:name(movereason):item:name(2015MoveStaging1423179160443)'2015 Move Staging'", "2015 Move Staging"),
            ("urn:cspace:bampfa.cspace.berkeley.edu:vocabularies:name(movereason):item:name(2015Packing1422385332220)'2015 Packing'", "2015 Packing"),
            ("urn:cspace:bampfa.cspace.berkeley.edu:vocabularies:name(movereason):item:name(movereason001)'Conservation'", "Conservation"),
            ("urn:cspace:bampfa.cspace.berkeley.edu:vocabularies:name(movereason):item:name(DataCleanUp1416598052252)'Data Clean Up'", "Data Clean Up"),
            ("urn:cspace:bampfa.cspace.berkeley.edu:vocabularies:name(movereason):item:name(movereason002)'Exhibition'", "Exhibition"),
            ("urn:cspace:bampfa.cspace.berkeley.edu:vocabularies:name(movereason):item:name(movereason003)'Inventory'", "Inventory"),
            ("urn:cspace:bampfa.cspace.berkeley.edu:vocabularies:name(movereason):item:name(movereason004)'Loan'", "Loan"),
            ("urn:cspace:bampfa.cspace.berkeley.edu:vocabularies:name(movereason):item:name(movereason005)'New Storage Location'", "New Storage Location"),
            ("urn:cspace:bampfa.cspace.berkeley.edu:vocabularies:name(movereason):item:name(movereason006)'Photography'", "Photography"),
            ("urn:cspace:bampfa.cspace.berkeley.edu:vocabularies:name(movereason):item:name(movereason007)'Research'", "Research"),
        ]
    else:
        # these are for PAHMA
        reasons = [
            ("None", "(none selected)"),
            ("(not entered)", "(not entered)"),
            ("Inventory", "Inventory"),
            ("GeneralCollManagement", "General Collections Management"),
            ("Research", "Research"),
            ("NAGPRA", "NAGPRA"),
            ("pershelflabel", "per shelf label"),
            ("NewHomeLocation", "New Home Location"),
            ("Loan", "Loan"),
            ("Exhibit", "Exhibit"),
            ("ClassUse", "Class Use"),
            ("PhotoRequest", "Photo Request"),
            ("Tour", "Tour"),
            ("Conservation", "Conservation"),
            ("CulturalHeritage", "cultural heritage"),
            ("", "----------------------------"),
            ("2012 HGB surge pre-move inventory", "2012 HGB surge pre-move inventory"),
            ("2014 Marchant inventory and move", "2014 Marchant inventory and move"),
            ("AsianTextileGrant", "Asian Textile Grant"),
            ("BasketryRehousingProj", "Basketry Rehousing Proj"),
            ("BORProj", "BOR Proj"),
            ("BuildingMaintenance", "Building Maintenance: Seismic"),
            ("CaliforniaArchaeologyProj", "California Archaeology Proj"),
            ("CatNumIssueInvestigation", "Cat. No. Issue Investigation"),
            ("DuctCleaningProj", "Duct Cleaning Proj"),
            ("FederalCurationAct", "Federal Curation Act"),
            ("FireAlarmProj", "Fire Alarm Proj"),
            ("FirstTimeStorage", "First Time Storage"),
            ("FoundinColl", "Found in Collections"),
            ("HearstGymBasementMoveKroeber20", "Hearst Gym Basement move to Kroeber 20A"),
            ("HGB Surge", "HGB Surge"),
            ("Kro20MezzLWeaponProj2011", "Kro20Mezz LWeapon Proj 2011"),
            ("Kroeber20AMoveRegatta", "Kroeber 20A move to Regatta"),
            ("MarchantFlood2007", "Marchant Flood 12/2007"),
            ("NAAGVisit", "Native Am Adv Grp Visit"),
            ("NEHEgyptianCollectionGrant", "NEH Egyptian Collection Grant"),
            ("Regattamovein", "Regatta move-in"),
            ("Regattapremoveinventory", "Regatta pre-move inventory"),
            ("Regattapremoveobjectprep", "Regatta pre-move object prep."),
            ("Regattapremovestaging", "Regatta pre-move staging"),
            ("SATgrant", "SAT grant"),
            ("TemporaryStorage", "Temporary Storage"),
            ("TextileRehousingProj", "Textile Rehousing Proj"),
            ("YorubaMLNGrant", "Yoruba MLN Grant")
        ]

    reasons = [(r[1], r[0]) for r in reasons]
    return reasons, selected


def getPrinters(form):
    selected = form.get('printer')

    printerlist = [
        ("Hearst Gym Basement", "cluster1"),
        ("Marchant", "cluster2")
    ]

    # printerlist = [ (r[1], r[0]) for r in printerlist]
    return printerlist, selected


def getFieldset(form):
    selected = form.get('fieldset')

    fieldsets = [
        ("Key Info", "keyinfo"),
        ("Name & Desc.", "namedesc"),
        ("Registration", "registration"),
        ("HSR Info", "hsrinfo"),
        ("Object Type/CM", "objtypecm"),
    ]

    return fieldsets, selected


def getHierarchies(form):
    selected = form.get('authority')

    authorities = [
        ("Ethnographic Culture", "concept"),
        ("Places", "places"),
        ("Archaeological Culture", "archculture"),
        ("Ethnographic File Codes", "ethusecode"),
        ("Materials", "material_ca"),
        ("Taxonomy", "taxonomy")
    ]

    return authorities, selected


def getAltNumTypes(form):
    selected = form.get('altnumtype')

    altnumtypes = [
        ("(none selected)", "(none selected)"),
        ("additional number", "additional number"),
        ("attributed pahma number", "attributed PAHMA number"),
        ("burial number", "burial number"),
        ("moac subobjid", "moac subobjid"),
        ("museum number (recataloged to)", "museum number (recataloged to)"),
        ("previous number", "previous number"),
        (u"previous number (albert bender’s number)", "prev. number (Bender)"),
        (u"previous number (bascom’s number)", "prev. number (Bascom)"),
        (u"previous number (collector's original number)", "prev. number (collector)"),
        ("previous number (design dept.)", "prev. number (Design)"),
        ("previous number (mvc number, mossman-vitale collection)", "prev. number (MVC)"),
        ("previous number (ucas: university of california archaeological survey)", "prev. number (UCAS)"),
        ("song number", "song number"),
        ("tag", "tag"),
        ("temporary number", "temporary number"),
        ("associated catalog number", "associated catalog number"),
        ("field number", "field number"),
        ("original number", "original number"),
        ("previous museum number (recataloged from)", "prev. number (recataloged from)"),
        (u"previous number (anson blake’s number)", "prev. number (Blake)"),
        (u"previous number (donor's original number)", "prev. number (donor)"),
        ("previous number (uc paleontology department)", "prev. number (Paleontology)"),
        ("tb (temporary basket) number", "tb (temporary basket) number")

    ]

    # altnumtypes = [ (r[1], r[0]) for r in altnumtypes]
    return altnumtypes, selected


def getObjType(form):
    selected = form.get('objectType')

    objtypes = [
        ("Archaeology", "archaeology"),
        ("Ethnography", "ethnography"),
        ("(not specified)", "(not specified)"),
        ("Documentation", "documentation"),
        ("None (Registration)", "none (Registration)"),
        ("None", "None"),
        ("Sample", "sample"),
        ("Indeterminate", "indeterminate"),
        ("Unknown", "unknown")
    ]

    return objtypes, selected


def getCollMan(form):
    selected = form.get('collMan')

    collmans = [
        ("Natasha Johnson", "Natasha Johnson"),
        ("Leslie Freund", "Leslie Freund"),
        ("Alicja Egbert", "Alicja Egbert"),
        ("Victoria Bradshaw", "Victoria Bradshaw"),
        ("Uncertain", "uncertain"),
        ("None (Registration)", "No collection manager (Registration)")
    ]

    return collmans, selected


def getAgencies(form):
    selected = form.get('agency')

    agencies = [
        ("Bureau of Indian Affairs", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(8452)"),
        ("Bureau of Land Management", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(3784)"),
        ("Bureau of Reclamation", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(6392)"),
        ("California Department of Transportation", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(9068)"),
        ("California State Parks", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(8594)"),
        ("East Bay Municipal Utility District", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(EastBayMunicipalUtilityDistrict1370388801890)"),
        ("National Park Service", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(1533)"),
        ("United States Air Force", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(UnitedStatesAirForce1369177133041)"),
        ( "United States Army", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(3021)"),
        ("United States Coast Guard", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(UnitedStatesCoastGuard1342641628699)"),
        ("United States Fish and Wildlife Service", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(UnitedStatesFishandWildlifeService1342132748290)"),
        ("United States Forest Service", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(3120)"),
        ("United States Marine Corps", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(UnitedStatesMarineCorps1365524918536)"),
        ("United States Navy", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(9079)"),
        ("U.S. Army Corps of Engineers", "urn:cspace:pahma.cspace.berkeley.edu:orgauthorities:name(organization):item:name(9133)"),
    ]

    return agencies, selected


def getIntakeFields(fieldset):
    if fieldset == 'intake':

        return [
            ('TR', 20, 'tr', '31', 'fixed'),
            ('Number of Objects:', 5, 'numobjects', '1', 'text'),
            ('Source:', 40, 'pc.source', '', 'text'),
            ('Date in:', 30, 'datein', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), 'text'),
            ('Receipt?', 40, 'receipt', '', 'checkbox'),
            ('Location:', 40, 'lo.location', '', 'text'),
            ('Disposition:', 30, 'disposition', '', 'text'),
            ('Artist/Title/Medium', 10, 'atm', '', 'text'),
            ('Purpose:', 40, 'purpose', '', 'text')
        ]
    elif fieldset == 'objects':

        return [
            ('ID number', 30, 'id', '', 'text'),
            ('Title', 30, 'title', '', 'text'),
            ('Comments', 30, 'comments', '', 'text'),
            ('Artist', 30, 'pc.artist', '', 'text'),
            ('Creation date', 30, 'cd', '', 'text'),
            ('Creation technique', 30, 'ct', '', 'text'),
            ('Dimensions', 30, 'dim', '', 'text'),
            ('Responsible department', 30, 'rd', '', 'text'),
            ('Computed current location', 30, 'lo.loc', '', 'text')
        ]



if __name__ == '__main__':

    def handleResult(result, header):
        items, selected = result
        htmlobject = '\n<tr><td>%s<td>' % header

        htmlobject += '''<select class="cell" "><option value="None">Select an option</option>'''

        for options in items:
            htmlobject += """<option value="%s">%s</option>""" % (options[1], options[0])
        htmlobject += '\n      </select>'

        return htmlobject

    form = {}
    config = {}

    result = '<html>\n'

    # all the following return HTML)
    result += '<h2>Dropdowns</h2><table border="1">'
    # result += handleResult(getAppOptions('pahma'),'getAppOptions')
    result += handleResult(getAltNumTypes(form), 'getAltNumTypes')
    form = {'institution': 'bampfa'}
    result += handleResult(getHandlers(form), 'getHandlers: bampfa')
    form = {}
    result += handleResult(getHandlers(form), 'getHandlers')
    form = {'institution': 'bampfa'}
    result += handleResult(getReasons(form), 'getReasons:bampfa')
    form = {}
    result += handleResult(getReasons(form), 'getReasons')
    result += handleResult(getPrinters(form), 'getPrinters')
    result += handleResult(getFieldset(form), 'getFieldset')
    result += handleResult(getHierarchies(form), 'getHierarchies')
    result += handleResult(getAgencies(form), 'getAgencies')
    result += '</table>'

    # these two return python objects
    result += '<h2>Tricoder users</h2><table border="1">'
    t = tricoderUsers()
    for k in t.keys():
        result += '<tr><td>%s</td><td>%s</td></tr>' % (k, t[k])
    result += '</table>'

    print '''Content-Type: text/html; charset=utf-8

    '''
    print result

    result += '</html>\n'

