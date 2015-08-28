use strict;

my %count ;

open MEDIA,'media.csv';
my %media ;
while (<MEDIA>) {
  $count{'media'}++;
  chomp;
  my ($objectcsid, $objectnumber, $mediacsid, $description, $filename, $creatorrefname, $creator, $blobcsid, 
      $copyrightstatement, $identificationnumber, $rightsholderrefname, $rightsholder, 
      $contributor, $approvedforweb) = split '\|';
  #print "$blobcsid $objectcsid\n";
  $media{$blobcsid} = "$objectcsid|$objectnumber|$mediacsid";

}

open IMAGESLOADED,'csids.csv';
while (<IMAGESLOADED>) {
  $count{'imagesloaded'}++;
  chomp;
  my ($imagefile,$objectnumber,$blobcsid,$mediacsid,$objectcsid) = split "\t";
  # insert list of blobs as final column
  my $mediablob;
  foreach my $blob (split ',',$blobcsid) {
    $count{'blobs'}++;
    $mediablob = $media{$blob};
    #print "mediablob: $mediablob :: blobcsid $blobcsid\n";
    last if $mediablob;
  }
  $mediablob = 'None' unless $mediablob;
  #my $match = $mediablobs=~ /$mediacsid/ ? 'OK' : 'NoMatch';
  my $match = $mediacsid =~ /$mediablob/ ? 'OK' : 'NoMatch';
  print $_ . '|' . $match . '|' . $mediablob . "\n";
}

foreach my $s (sort keys %count) {
 warn $s . ": " . $count{$s} . "\n";
}
