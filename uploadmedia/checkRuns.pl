##!/usr/bin/perl -w

use strict;

sub checkJobs {
  my %jobs = %{shift()} ;
  my %joberrors = %{shift()} ;
  my %totals;

  print "number of jobs found: ";
  print scalar keys %jobs;
  print "\n";

  my @columnheaders = split(' ','step1 original step2 step3 processed inprogress discrepancy logerrors');
  print "job................\t";
  print join "\t",@columnheaders;
  print "\n";

  foreach my $job (reverse sort keys %jobs) {
    print $job."\t";
    my %steps = %{$jobs{$job}};

    $steps{'discrepancy'} = $steps{'original'} - $steps{'processed'};
    delete $steps{'discrepancy'} if $steps{'discrepancy'} == 0;
    $steps{'logerrors'} = $joberrors{$job};

    foreach my $step (@columnheaders) {
      #print $step."\t";
      print $steps{$step} . "\t";
      $totals{$step} += $steps{$step};
    }
    print "\n";
  } 
  print "totals.............\t";
  foreach my $step (@columnheaders) {
    print $totals{$step} . "\t";
  }
  print "\n";
}

sub checkMissing {
  my %images = %{shift()};
  my %missing = %{shift()};

  foreach my $name (sort keys %images) {
    my $isMissing = 1;
    my %runs = %{$images{$name}};
    foreach my $run (sort keys %runs) { 
      #print $run."\t";
      my %steps = %{$runs{$run}};
      foreach my $step (sort keys %steps) { 
	#print $step."\t";
	$isMissing = 0 if $step =~ /(processed|step1|inprogress)/;
      }
    }
  print "$name ::: \t$missing{$name}\n" if $isMissing;
  }
}


sub checkDuplicates {
  my %images = %{shift()};
  my %duplicates = %{shift()};
  my %missing = %{shift()};

  foreach my $name (sort keys %duplicates) {
  print "$missing{$name}\n" if $duplicates{$name} > 1;
  }
}


sub checkCsids {
  my %csids = %{shift()};
  foreach my $name (sort keys %csids) {
    print $name . "\t";
    my %csidlist = %{$csids{$name}};
    foreach my $type (split(' ','objectnumber blob media object')) {	
      $csidlist{$type} =~ s/,$//;	      
      print "$csidlist{$type}\t";
    }
    print "\n";
  }
}

sub checkSteps {
  my %images = %{shift()};

  foreach my $name (sort keys %images) {
    print $name."\t";
    my %runs = %{$images{$name}};
    foreach my $run (sort keys %runs) { 
      print $run."\t";
      my %steps = %{$runs{$run}};
      foreach my $step (sort keys %steps) { 
	print $step."\t";
      }
    }
  print "\n";
  }
}

########## Main ##############
my $DIR = $ARGV[1];
my %images;
my %jobs;
my %missing;
my %duplicates;
my %joberrors;
my %errors;
my %csids;
my $JOB;

if ($ARGV[1] =~ /^[\d\-]+$/) { #if we have a single job, just do stats for it..
  $JOB = $ARGV[1];
}


foreach my $filename ( <$DIR/$JOB*.csv>) { # nb: no slash between dir and file...
   open FH,"<$filename";
   $filename =~ s/$DIR\///;
   $filename =~ s/.csv$//;
   my ($run,$step) = $filename =~ /^(.*?)\.(.*?)$/;
   my $i = 0;
   while (<FH>) {
     next if /^name/; # skip header rows
     $i++;
     chomp;
     s/\r//g;
     my ($name,$size,$objectnumber,$blobcsid,$date,$creator,$contributor,$rightsholder,$fullpath,$mediacsid,$objectcsid);
     if ($step =~ /(step1|original)/) {
       ($name,$size,$objectnumber,$date,$creator,$contributor,$rightsholder) = split /[\t\|]/;
     }
     else {
       ($name,$size,$objectnumber,$blobcsid,$date,$creator,$contributor,$rightsholder,$fullpath,$mediacsid,$objectcsid) = split /[\t\|]/;
     }
     #next if $objectcsid =~ /NoObjectFound/;
     #next if $step =~ /step1/;
     #print "  $run\t$step\t$i\t$name\n";
     $jobs{$run}{$step}++;
     $images{$name}{$run}{$step}++;
     $duplicates{$name}++ if $step eq 'processed';
     $missing{$name} = $_ if $step =~ /(original|step1)/;
     $csids{$name}{'objectnumber'} = $objectnumber if $objectnumber;
     $csids{$name}{'media'} .= $mediacsid . ',' if ($mediacsid && !($csids{$name}{'media'} =~ /$mediacsid/));
     $csids{$name}{'object'} .= $objectcsid . ',' if ($objectcsid && !($csids{$name}{'object'} =~ /$objectcsid/));
     $csids{$name}{'blob'} .= $blobcsid . ',' if ($blobcsid && !($csids{$name}{'blob'} =~ /$blobcsid/));
   }
}

foreach my $filename ( <$DIR/$JOB*.trace.log>) { # nb: no slash between dir and file...
   open FH,"<$filename";
   $filename =~ s/$DIR\///;
   $filename =~ s/.trace.log$//;
   my ($run,$step) = $filename =~ /^(.*?)\.(.*?)$/;
   my $i = 0;
   while (<FH>) {
     #print;
     chomp;
     my $error;
     next if /\/tmp\/upload_cache\/name/; # special case
     /(Missing file|Post did not return a 201 status code|No output file\, something failed)/ && ($error = $1);
     if ($error) {
       #print $_."\n";
       my ($name) = / $DIR.(.+?\.jpe?g)$/i;
       $joberrors{$filename}++;
       #print "error $filename :: $name :: $error\n";
       $errors{$name}+=$error;
     }
   }
}


if ($ARGV[0] eq 'jobs') {
  print "Directory: $DIR\n\n";
  checkJobs(\%jobs,\%joberrors);
}

elsif  ($ARGV[0] eq 'missing') { 
  checkMissing(\%images,\%missing);
}

elsif  ($ARGV[0] eq 'duplicates') { 
  checkDuplicates(\%images,\%duplicates,\%missing);
}

elsif  ($ARGV[0] eq 'images') { 
  checkSteps(\%images);
}

elsif  ($ARGV[0] eq 'csids') { 
  checkCsids(\%csids);
}

else {
  print "usage: perl checkRuns.pl <jobs missing duplicates images csids> [yyyy-mm-dd-hh-mm-ss]\n";
}
  
