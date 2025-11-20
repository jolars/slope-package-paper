In addition, Journal of Statistical Software requires that the software usage is
illustrated on simple problems run step-by-step in the manuscript, showing
command lines and their results. This is currently done for the R package but we
would find beneficial to have a similar code for the other two packages.
Finally, based on the R example, we found some issues in the R package that also
need to be solved.  
We thus ask the authors to address all detailed comments and resubmit their work
as a new submission along with point-by-point answer to raised issues.  
Note: We did not try to test nix env.  
Detailed comments:

o The introduction must include a discussion on related software implementations
available in all languages (e.g., software implementations related to l1
penalized linear regression for instance, or even slope problem estimation),
highlighting the specific contribution of slope.

o None of the files  
libslope-6.1.1.tar.gz SLOPE-1.2.0.tar.gz SLOPE-jl-1.1.0.tar.gz sortedl1-1.7.0.tar.gz  
can be uncompressed (or used) using gunzip. For instance,  
tar zxvf SLOPE-1.2.0.tar.gz gzip: stdin: not in gzip format tar: Child returned
status 1 tar: Error is not recoverable: exiting now  
or  
R CMD INSTALL ~/Downloads/SLOPE-1.2.0.tar.gz Error in untar2(tarfile, files,
list, exdir, restore_times) : incomplete block on file

o The object 'fit' as obtained by 'example("SLOPE")' is of class
"MultinomialSLOPE" that inherits from "SLOPE". We found:  
methods(class = "SLOPE") \[1\] coef deviance plot predict print see '?methods'
for accessing help and source code \> methods(class = "MultinomialSLOPE") \[1\]
predict score see '?methods' for accessing help and source code  
It means that, at least a summary method is missing. Other methods might be
missing that would avoid exposing the internal structure of objects in the
replication material (as in pattern \<- fit_pat$patterns\[\[20\]\]).

o A summary methods is also missing for TrainedSLOPE:  
\> methods(class = "TrainedSLOPE") \[1\] plot print see '?methods' for accessing
help and source code  
o Using  
example("SLOPE") plot(fit)  
results in an empty plot. It is probably not expected: Can the authors look into
this?

o Replication material should be cleaned and simplified a bit, in particular to
remove hidden configuration files coming from github. Make sure to upload only
files required to reproduce results of the manuscript and to adapt README files
to avoid having to use the github repository in the instructions (you can of
course mention that these files are duplicated in a github repository but
explain how to run the replication code from the local directory).

o Following the instructions to run the benchmark given in the README file of
benchmark_slope (after activating a virtual environment for Python), we
obtained:  
benchopt install ./benchmark_slope Traceback (most recent call last): File
"myvenv/bin/benchopt", line 8, in
\<module\> sys.exit(benchopt()) ^^^^^^^^^^ File
"myvenv/lib/python3.12/site-packages/click/core.py", line 1485, in
\_\_call\_\_ return self.main(\*args,
\*\*kwargs) ^^^^^^^^^^^^^^^^^^^^^^^^^^ File
"myvenv/lib/python3.12/site-packages/click/core.py", line 1406, in main rv =
self.invoke(ctx) ^^^^^^^^^^^^^^^^ File
"myvenv/lib/python3.12/site-packages/click/core.py", line 1873, in invoke return
\_process_result(sub_ctx.command.invoke(sub_ctx)) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File
"myvenv/lib/python3.12/site-packages/click/core.py", line 1269, in invoke return
ctx.invoke(self.callback,
\*\*ctx.params) ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ File
"myvenv/lib/python3.12/site-packages/click/core.py", line 824, in invoke return
callback(\*args, \*\*kwargs) ^^^^^^^^^^^^^^^^^^^^^^^^^ File
"myvenv/lib/python3.12/site-packages/benchopt/cli/main.py", line 452, in
install raise RuntimeError( RuntimeError: No conda environment is activated. You
should be in a conda environment to use 'benchopt install'.  
If conda has to be used, this should be mentioned in the installation
instructions. The README file of the replication material indicates that this is
the case: please make the two files consistent or remove the README files of
subdirectories. Also provide a more detailed information about setting the conda
environment for user not familiar with it.  
o Running benchmop run in benchmark_slope results in errors due to missing
dependencies (skglm for instance). It would be preferable to provide a
requirements.txt file allowing users to install all required dependencies
without the need to search what they are.  
o Trying to run the same benchmark, we also had:  
Traceback (most recent call last): File
"replication-material/benchmark_slope/solvers/slope_path.py", line 5, in
\<module\> from modules import path_solver ImportError: cannot import name
'path_solver' from 'modules'
anaconda3/lib/python3.12/site-packages/modules.py) |--SlopePath: not
installed |--Newt-ALM\[inner_solver=standard\]: done Traceback (most recent call
last): File
"replication-material/benchmark_slope/solvers/pgd_safe_screening.py", line 6, in
\<module\> from slopescreening.solver.parameters import
SlopeParameters ModuleNotFoundError: No module named
'slopescreening' |--PGD_safe_screening: not installed  
Can you instruct how this should be solved?  
o Could you please also provide scripts with minimal command lines to run the
equivalent of example.R and/or real-data.R with Python and Julia?  
o help(package = "SLOPE") shows that not man page titles are not in title
styles.  
o In the R package, ?cvSLOPE contains:  
See Also:  
‘plot.TrainedSLOPE()’  
Other model-tuning: ‘plot.TrainedSLOPE()’, ‘trainSLOPE()’  
Probably, ‘plot.TrainedSLOPE()’ should be removed from "Other model-tuning".  
o It seems that the output of cvSLOPE only gives a way to obtain the optimal
hyperparameters. In R programming, it is standard to also return the best model
fit with these parameters (see e.g., ?e1071:tune). Can the authors think of an
handy way for the user to either obtain this trained model from cvSLOPE or use
the output of cvSLOPE in a method that would directly train the optimal model?
