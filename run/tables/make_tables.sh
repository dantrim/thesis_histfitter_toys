#!/bin/bash

workspace="../results/ThesisTest/BkgOnly_combined_NormalMeasurement_model_afterFit.root"
backgrounds="bkg0,bkg1,bkg2,sig"
backgrounds="bkg0,bkg1" #,bkg1,bkg2,sig"
YieldsTable.py -b -c CR_BKG0,SR_BKG0 -s ${backgrounds} -w $workspace -o yields_ThesisTest.tex
#YieldsTable.py -b -c CR_BKG0,CR_BKG1 -s ${backgrounds} -w $workspace -o yields_ThesisTest.tex
#YieldsTable.py -b -c CR_BKG0,SR -s ${backgrounds} -w $workspace -o yields_ThesisTest.tex
rm *.pickle
