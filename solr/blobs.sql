    SELECT cc.id, cc.updatedat, cc.updatedby, b.name, c.data AS md5
    FROM  blobs_common b
      INNER JOIN  picture p
         ON (b.repositoryid = p.id)
      INNER JOIN hierarchy h2
         ON (p.id = h2.parentid AND h2.primarytype = 'view')
      INNER JOIN view v
         ON (h2.id = v.id AND v.tag='original')
      INNER JOIN hierarchy h1
         ON (v.id = h1.parentid AND h1.primarytype = 'content')
      INNER JOIN content c
         ON (h1.id = c.id)
      INNER JOIN collectionspace_core cc
        ON (cc.id = b.id)
      ;
