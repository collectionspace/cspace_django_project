-- data extract to provision data-driven elements of the the core public website

SELECT
  -- the first field must be the unique id field and it must be called "id"
  h1.name                                                             AS id,
  h1.name                                                             AS csid_s,
  regexp_replace(ong.objectname, '^.*\)''(.*)''$', '\1')              AS objectname_s,
  coc.objectnumber                                                    AS objectnumber_s,
  coc.numberofobjects                                                 AS numberofobjects_s,
  coc.computedcurrentlocation                                         AS computedcurrentlocationrefname_s,
  regexp_replace(coc.computedcurrentlocation, '^.*\)''(.*)''$', '\1') AS currentlocation_s,
  regexp_replace(coc.recordstatus, '^.*\)''(.*)''$', '\1')            AS recordstatus_s,
  regexp_replace(coc.physicaldescription, E'[\\t\\n\\r]+', ' ', 'g')  AS physicaldescription_s,
  regexp_replace(coc.contentdescription, E'[\\t\\n\\r]+', ' ', 'g')   AS contentdescription_s,
  regexp_replace(coc.contentnote, E'[\\t\\n\\r]+', ' ', 'g')          AS contentnote_s,
  regexp_replace(coc.fieldcollectionplace, '^.*\)''(.*)''$', '\1')    AS fieldcollectionplace_s,
  regexp_replace(coc.collection, '^.*\)''(.*)''$', '\1')              AS collection_s,
  sdg.datedisplaydate                                                 AS datemade_s,
  coc.physicaldescription                                             AS materials_s,
  replace(mp.dimensionsummary, '-', ' ')                              AS measurement_s,
  core.updatedat                                                      AS updatedat_s

FROM collectionobjects_common coc
  JOIN hierarchy h1 ON (h1.id = coc.id)
  JOIN misc ON (coc.id = misc.id AND misc.lifecyclestate <> 'deleted')

  LEFT OUTER JOIN hierarchy h2
    ON (coc.id = h2.parentid AND h2.name = 'collectionobjects_common:objectNameList' AND h2.pos = 0)
  LEFT OUTER JOIN objectnamegroup ong ON (ong.id = h2.id)

  INNER JOIN collectionspace_core core ON coc.id = core.id
  LEFT OUTER JOIN hierarchy h3
    ON (h3.parentid = coc.id AND h3.name = 'collectionobjects_common:objectProductionDateGroupList' AND h3.pos = 0)
  LEFT OUTER JOIN structuredDateGroup sdg ON (h3.id = sdg.id)
  LEFT OUTER JOIN hierarchy h7
    ON (h7.parentid = coc.id AND h7.name = 'collectionobjects_common:measuredPartGroupList' AND h7.pos = 0)
  LEFT OUTER JOIN measuredpartgroup mp
    ON (h7.id = mp.id)
  LEFT OUTER JOIN hierarchy h14
    ON (h14.parentid = coc.id AND h14.name = 'collectionobjects_common:objectProductionPlaceGroupList' AND h14.pos = 0)
;
