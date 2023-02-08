# VRX619-Pipeline

This pipeline executes a sequence oj jobs from monday to thursday at 19h: 
* Skip check: change the value of skipPipeline = true if you want want to skip the sequence, remember to put it back to "false" when you want to resume the periodic builds.
* Git update: this job takes a parameter "branch", the default value is "master".
* Build.
* Fw Download.
* Nightly test.
* Copy test results to alab.
If one of the stages fail, the pipeline will stop and not execute the rest.
