use strict;

my %count ;
my $delim = "\t";

open MEDIA,$ARGV[0] || die "couldn't open media file $ARGV[0]";
my %media ;
while (<MEDIA>) {
  $count{'media'}++;
  chomp;
  my ($objectcsid, $blobcsid) = split /$delim/;
  #print "$blobcsid $objectcsid\n";
  $media{$objectcsid} .= $blobcsid . ',';
}

open METADATA,$ARGV[1] || die "couldn't open metadata file $ARGV[1]";
while (<METADATA>) {
  $count{'metadata'}++;
  chomp;
  my ($objectcsid, @rest) = split /$delim/;
  # insert list of blobs as final column
  my $mediablobs = $media{$objectcsid};
  if ($mediablobs) {
    $count{'matched'}++;
  }
  else {
    $count{'unmatched'}++;
  }
  $mediablobs =~ s/,$//; # get rid of trailing comma
  print $_ . $delim . $mediablobs . "\n";
}

foreach my $s (sort keys %count) {
 warn $s . ": " . $count{$s} . "\n";
}
