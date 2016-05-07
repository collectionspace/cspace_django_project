
-- data extract to provision data-driven elements of the the BAMPFA public website
-- based on view piction.bampfa_metadata_v and the Solr4 metadata.sql queries

SELECT
   -- the first field must be the unique id field and it must be called "id"
   h1.name id,
   co.objectnumber idNumber_s,
   cb.sortableEffectiveObjectNumber sortObjectNumber_s,
   case when (cb.artistdisplayoverride is null or cb.artistdisplayoverride='') then utils.concat_artists(h1.name)
     else cb.artistdisplayoverride end as artistCalc_s,
   case when (pc.birthplace is null or pc.birthplace='') then pcn.item 
     else pcn.item||', born '||pc.birthplace end as artistorigin_s,
   concat_ws('-', sdgpb.datedisplaydate, case when sdgpd.datedisplaydate='' then NULL else sdgpd.datedisplaydate end) artistdates_s,
   sdgpb.datedisplaydate as startdate_s,
   sdgpd.datedisplaydate as enddate_s,
   pc.birthplace as birthplace_s,
   pcn.item as nationality_s,
   bt.bampfatitle title_s,
   sdg.datedisplaydate dateMade_s,
   case when (pp.objectproductionplace is not null and pp.objectproductionplace<>'') then pp.objectproductionplace
      else null
   end as site_s,
   utils.getdispl(cb.itemclass) itemclass_s,
   co.physicaldescription materials_s,
   replace(mp.dimensionsummary, '-', ' ') measurement_s,
   case when (cb.creditline='' or cb.creditline is null)  then
     'University of California, Berkeley Art Museum and Pacific Film Archive'
     else 'University of California, Berkeley Art Museum and Pacific Film Archive; '||cb.creditline
   end as fullBAMPFAcreditline_s,
   case when (cb.copyrightCredit is null or cb.copyrightCredit='') then pb.copyrightCredit
      else cb.copyrightCredit end as copyrightCredit_s,
   -- cb.photoCredit_s,
   concat_ws('|', utils.getdispl(st1.item), utils.getdispl(st2.item), utils.getdispl(st3.item), utils.getdispl(st4.item), utils.getdispl(st5.item)) subjects_s,
   concat_ws('|', utils.getdispl(col1.item), utils.getdispl(col2.item), utils.getdispl(col3.item)) collections_s,
   concat_ws('|', utils.getdispl(ps1.item), utils.getdispl(ps2.item), utils.getdispl(ps3.item), utils.getdispl(ps4.item), utils.getdispl(ps5.item)) periodstyles_s,
   '' caption_s,
   '' tags_s,
   case when (cb.permissiontoreproduce is null or cb.permissiontoreproduce='') then 'Unknown'
      else cb.permissiontoreproduce 
   end as permissiontoreproduce_s,
   utils.getdispl(cb.legalstatus) legalstatus_s,
   utils.getdispl(co.computedcurrentlocation) currentlocation_s,
   utils.getdispl(cb.computedcrate) currentcrate_s,
   utils.get_first_blobcsid(h1.name) image1blobcsid_s,
   core.updatedat as updatedat_s
from
   hierarchy h1
   INNER JOIN collectionobjects_common co
      ON (h1.id = co.id AND h1.primarytype = 'CollectionObjectTenant55')
   INNER JOIN misc m
      ON (co.id = m.id AND m.lifecyclestate <> 'deleted')
   INNER JOIN collectionobjects_bampfa cb
      ON (co.id = cb.id)
   INNER JOIN collectionspace_core core on co.id=core.id
   LEFT OUTER JOIN hierarchy h2
      ON (h2.parentid = co.id AND h2.name='collectionobjects_common:objectProductionDateGroupList' and h2.pos=0)
   LEFT OUTER JOIN structuredDateGroup sdg ON (h2.id = sdg.id)
   LEFT OUTER JOIN hierarchy h4
      ON (h4.parentid = co.id AND h4.name = 'collectionobjects_bampfa:bampfaTitleGroupList' and h4.pos=0)
   LEFT OUTER JOIN bampfatitlegroup bt
      ON (h4.id = bt.id)
   LEFT OUTER JOIN hierarchy h7
      ON (h7.parentid = co.id AND h7.name = 'collectionobjects_common:measuredPartGroupList' and h7.pos=0)
   LEFT OUTER JOIN measuredpartgroup mp
      ON (h7.id = mp.id)
   LEFT OUTER JOIN collectionobjects_bampfa_acquisitionsources cas on (co.id=cas.id and cas.pos=0)
   LEFT OUTER JOIN hierarchy h11
      ON (h11.parentid = co.id AND h11.name = 'collectionobjects_bampfa:bampfaObjectProductionPersonGroupList' and h11.pos=0)
   LEFT OUTER JOIN bampfaobjectproductionpersongroup ba
      ON (h11.id = ba.id)  
   LEFT OUTER JOIN persons_common pc on (ba.bampfaobjectproductionperson=pc.refname)
   LEFT OUTER JOIN persons_common_nationalities pcn on (pc.id=pcn.id and pcn.pos=0)
   LEFT OUTER JOIN hierarchy h12
      ON (h12.parentid = pc.id AND h12.name='persons_common:birthDateGroup')
   LEFT OUTER JOIN structuredDateGroup sdgpb ON (h12.id = sdgpb.id)
   LEFT OUTER JOIN hierarchy h13
      ON (h13.parentid = pc.id AND h13.name='persons_common:deathDateGroup')
   LEFT OUTER JOIN structuredDateGroup sdgpd ON (h13.id = sdgpd.id)
   LEFT OUTER JOIN persons_bampfa pb on (pc.id=pb.id)
   LEFT OUTER JOIN hierarchy h14
      ON (h14.parentid = co.id AND h14.name = 'collectionobjects_common:objectProductionPlaceGroupList' and h14.pos=0)
   LEFT OUTER JOIN objectproductionplacegroup pp
      ON (h14.id = pp.id)
   LEFT OUTER JOIN collectionobjects_bampfa_subjectthemes st1 ON (st1.id=co.id and st1.pos=0)
   LEFT OUTER JOIN collectionobjects_bampfa_subjectthemes st2 ON (st2.id=co.id and st2.pos=1)
   LEFT OUTER JOIN collectionobjects_bampfa_subjectthemes st3 ON (st3.id=co.id and st3.pos=2)
   LEFT OUTER JOIN collectionobjects_bampfa_subjectthemes st4 ON (st4.id=co.id and st4.pos=3)
   LEFT OUTER JOIN collectionobjects_bampfa_subjectthemes st5 ON (st5.id=co.id and st5.pos=4)
   LEFT OUTER JOIN collectionobjects_bampfa_bampfacollectionlist col1 ON (col1.id=co.id and col1.pos=0)
   LEFT OUTER JOIN collectionobjects_bampfa_bampfacollectionlist col2 ON (col2.id=co.id and col2.pos=1)
   LEFT OUTER JOIN collectionobjects_bampfa_bampfacollectionlist col3 ON (col3.id=co.id and col2.pos=2)
   LEFT OUTER JOIN collectionobjects_common_styles ps1 ON (ps1.id=co.id and ps1.pos=0)
   LEFT OUTER JOIN collectionobjects_common_styles ps2 ON (ps2.id=co.id and ps2.pos=1)
   LEFT OUTER JOIN collectionobjects_common_styles ps3 ON (ps3.id=co.id and ps3.pos=2)
   LEFT OUTER JOIN collectionobjects_common_styles ps4 ON (ps4.id=co.id and ps4.pos=3)
   LEFT OUTER JOIN collectionobjects_common_styles ps5 ON (ps5.id=co.id and ps5.pos=4)
where utils.getdispl(cb.legalstatus) in ('permanent collection', 'extended loan')
order by cb.sortableEffectiveObjectNumber
;
