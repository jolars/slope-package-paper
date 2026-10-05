use Cwd qw(abs_path);

# Use the bundled Elsevier CAS files when compiling the manuscript.
my $cas_dir = abs_path('els-cas-templates');
$ENV{'TEXINPUTS'} = "$cas_dir//:" . ($ENV{'TEXINPUTS'} // '');
$ENV{'BSTINPUTS'} = "$cas_dir:" . ($ENV{'BSTINPUTS'} // '');
