my $tenant = @ARGV[0];
my $portal = @ARGV[1];
print  "#\tParameters for $tenant-$portal Solr core\n";
print "#\n";
print "date\t\t09/01/15\n";
print "revision\t\t0.1\n";
print "#\n";
print "title\tCollection Browser\n";
print "server\thttp://localhost:8983/solr\n";
print "core\t$tenant-$portal\n";
print "#\n";
print "#\n";
print "#\t\tFields\t\t\t\t\t\trow,column\n";
print "#\n";
print "header\t\tName\tLabel\tSolrField\tSearchTarget\tSuggestions\tRole\tSearch\tFacet\tbMapper\tfullDisplay\tlistDisplay\tgridDisplay\tmapDisplay\tinCSV\tplaceholder\n";
print "field\t1\tid\tID\tid\t\t\tid,csid\t\t\t\t\t\t\t\t1\tx\n";
print "field\t2\tkeyword\tKeyword\ttext\t\t\tkeyword\t1,1\t\t\t\t\t\t\t\tx\n";
print "field\t3\tidnumber\tID Number\tidnumber_s\t\tob\tobjectno,accession,sortkeystring\t2,1\t\t\t\t\t\t\t2\tx\n";
print "field\t4\tblobs\tblobs\tblob_ss\t\t\tblob\t\t\t\t\t\t\t\t\tx\n";
print "#\tfor now, we need a dummy location value in this file.\t\t\t\t\t\t\t\t\t\t\t\t\t\t\tx\n";
print "field\t5\tlatlong\tLatLong\tlatlong_p\t\t\tlocation\t\t\t\t\t\t\t\t\tx\n";
my $i = 2;
my $header = <STDIN>; # skip header
my $j = 1;
my $rows = 5;
while (<STDIN>) {
  chomp;
  next if /^(csid_s|id|blob_ss|idnumber_s)$/;
  $internalname = $_;
  $internalname =~ s/_(s|ss|dt|i)$//;
  $label = $internalname;
  $label =~ s/\b(\w)/\U$1/g;
  $i++;
  $rows++;
  if ($i == 11) { $i = 1 ; $j++ ; }
  print "field\t$rows\t$internalname\t$label\t$_\t\t\tkeyword\t$i,$j\t$i\t$i\t$i\t$i\t$i\t$i\t$i\tx\n";
}
