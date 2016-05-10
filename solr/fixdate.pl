use strict;

while (<>) {
  chomp;
  my (@columns) = split '\|',$_,-1;
  #my ($Y,$M,$D) = split '-',$columns[7];
  @columns[7] .= "T00:00:00Z" if @columns[7];
  @columns[25] =~ s/ /T/;
  @columns[25] .= 'Z';
  #print scalar @columns, "\n";
  print join('|',@columns). "\n";
}

