SELECT 
h2.name id,
mc.blobcsid as blob_ss,
cc.objectnumber,
h1.name mediacsid,
mc.description,
b.name,
mc.creator creatorRefname,
mc.creator creator,
mc.copyrightstatement,
mc.identificationnumber,
mc.rightsholder rightsholderRefname,
mc.rightsholder rightsholder,
mc.contributor

FROM media_common mc

JOIN misc ON (mc.id = misc.id AND misc.lifecyclestate <> 'deleted')
LEFT OUTER JOIN hierarchy h1 ON (h1.id = mc.id)
INNER JOIN relations_common r on (h1.name = r.objectcsid)
LEFT OUTER JOIN hierarchy h2 on (r.subjectcsid = h2.name)
LEFT OUTER JOIN collectionobjects_common cc on (h2.id = cc.id)

JOIN hierarchy h3 ON (mc.blobcsid = h3.name)
LEFT OUTER JOIN blobs_common b on (h3.id = b.id);
