#!/usr/bin/env python

# ROOT
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from ROOT import gROOT
gROOT.SetBatch(True)

# HistFitter core
from configManager import configMgr
from configWriter import fitConfig, Measurement, Channel, Sample
from systematic import Systematic

from math import sqrt

#
perform_simfit = True

configMgr.ignoreSystematics = False
configMgr.prun = False

configMgr.analysisName = "ThesisTest"

configMgr.blindSR = False
configMgr.blindCR = False
configMgr.blindVR = False

configMgr.inputLumi = 139 # fb-1
configMgr.outputLumi = 139 # fb-1
configMgr.setLumiUnits("fb-1")

configMgr.weights = ["1"]

configMgr.calculatorType = 2 # calculator type: 0= Frequentist, 1=Hybrid, 2=Aymptotic
configMgr.testStatType = 3 # # test stat type: 0=LEP, 1=Tevatron, 2=Profile Likelihood, 3=One-sided PLL
configMgr.nPoints = 20
configMgr.writeXML = True

configMgr.histCacheFile = "data/" + configMgr.analysisName + ".root"
configMgr.outputFileName = "results/" + configMgr.analysisName + "_Output.root"


print "is discovery ? %s" % (myFitType == FitType.Discovery)

sample_bkg0 = Sample("bkg0", ROOT.kBlue)
sample_bkg0.setStatConfig(True)

sample_bkg1 = Sample("bkg1", ROOT.kGreen)
sample_bkg1.setStatConfig(True)

sample_bkg2 = Sample("bkg2", ROOT.kMagenta)
sample_bkg2.setStatConfig(True)

sample_data = Sample("data", ROOT.kBlack)
sample_data.setData()

sample_sig = Sample("sig", ROOT.kRed)
sample_sig.setStatConfig(True)

all_samples = [sample_bkg0, sample_bkg1, sample_bkg2, sample_data]

# systematics
norm_syst_bkg1 = Systematic("Norm_Bkg1_0", configMgr.weights, 1.0 + 0.1, 1.0 - 0.1, "user", "userHistoSys")
norm_syst2_bkg1 = Systematic("Norm_Bkg1_1", configMgr.weights, 1.0 + 0.1, 1.0 - 0.1, "user", "userHistoSys")
norm_syst_bkg2 = Systematic("Norm_Bkg2", configMgr.weights, 1.0 + 0.10, 1.0 - 0.10, "user", "userHistoSys")
sample_bkg1.addSystematic(norm_syst_bkg1)
sample_bkg1.addSystematic(norm_syst2_bkg1)
sample_bkg2.addSystematic(norm_syst_bkg2)
#sample_bkg0.addSystematic(norm_syst_bkg0)

#cb1a = Systematic("Norm_Bkg1_A", configMgr.weights, 1.0 + 0.80, 1.0 - 0.80, "user", "userHistoSys")
#cb1b = Systematic("Norm_Bkg1_B", configMgr.weights, 1.0 + 0.1, 1.0 - 0.1, "user", "userHistoSys")
#cb1c = Systematic("Norm_Bkg1_C", configMgr.weights, 1.0 + 0.1, 1.0 - 0.1, "user", "userHistoSys")
#cb1d = Systematic("Norm_Bkg1_D", configMgr.weights, 1.0 + 0.1, 1.0 - 0.1, "user", "userHistoSys")
#sample_bkg1.addSystematic(cb1a)
#sample_bkg1.addSystematic(cb1b)
#sample_bkg1.addSystematic(cb1c)
#sample_bkg1.addSystematic(cb1d)

def sample_by_name(name) :
    global all_samples
    for s in all_samples :
        if s.name.lower() == name.lower() :
            return s
    print "sample_by_name  failed"
    return None

# setup the yields
yields_dict = {
    "CR_BKG0" : {
        "bkg0" : 20.
        ,"bkg1" : 80.
        #,"bkg2" : 80.
        ,"data" : 100.
        ,"sig" : 0.
    }
    ,
    "CR_BKG1" : {
        "bkg0" : 0.
        ,"bkg1" : 100. 
        #,"bkg2" : 0.
        ,"data" : 100.
        ,"sig" : 0.
    }
}

stat_err_dict = {
    "CR_BKG0" : {
    }
    ,
    "CR_BKG1" : {
    }
}

fit_samples = []
for s in all_samples :
    fit_samples.append(s)
fit_samples.append(sample_sig)
for s in fit_samples :
#    if "data" not in s.name.lower() : continue
    for region_name in yields_dict :
        s.buildHisto([ yields_dict[region_name][s.name] ], region_name, "cuts", 0.5)
        if "bkg0" in s.name.lower() : continue
        if s.name in stat_err_dict[region_name] :
            s.buildStatErrors( [stat_err_dict[region_name][s.name]], region_name, "cuts" )
        else :
            print "Setting stat errors for %s in region %s --> %.5f" % (s.name, region_name, float(sqrt( yields_dict[region_name][s.name] )))
            s.buildStatErrors( [sqrt( yields_dict[region_name][s.name] )], region_name, "cuts")

# measuremnt
tlx = configMgr.addFitConfig("BkgOnly")
meas = tlx.addMeasurement(name = "NormalMeasurement", lumi = 1., lumiErr = 0.01)
meas.addPOI("mu_SIG")
tlx.statErrThreshold = 0.001

# setup the channels
all_channels = []
cr_channels = []
vr_channels = []

for region_name in yields_dict :
    c = tlx.addChannel("cuts",[region_name], 1.0, 0.5, 1.5)
    if "CR" in region_name : #and "BKG" in region_name :
        cr_channels.append(c)
    all_channels.append(c)

if cr_channels : #and perform_simfit :
    tlx.addBkgConstrainChannels(cr_channels)
if vr_channels :
    tlx.addValidationChannels(vr_list)

for isample, sample in enumerate(all_samples) :
    if "data" in sample.name.lower() : continue

    sample.setStatConfig(False)

    set_norm_by_theory = True
    for region in yields_dict :
        configMgr.cutsDict[region] = "1."
        if "CR" in region and "BKG0" in region and perform_simfit :
            sample_for_cr = region.split("_")[1].lower()
            if sample.name.lower() == sample_for_cr :
                set_norm_by_theory = False
                sample.setNormFactor("mu_%s" % sample.name.lower(), 1.0, 0.0, 10.0)
                sample.setNormRegions([ (region, "cuts") ])
    if set_norm_by_theory :
        sample.setNormByTheory()

# add the samples
tlx.addSamples(all_samples)

## signal
#if myFitType == FitType.Exclusion :
#
#    sample_sig.setStatConfig(True)
#
#    sample_sig.setNormFactor("mu_Test", 1.0, 0.0, 10.0)
#    sample_sig.setNormRegions( [ ("CR_BKG0", "cuts") ] )#, ("CR_BKG1", "cuts") ] )
#    sample_sig.setNormByTheory()
#    tlx.addSamples(sample_sig)
##    tlx.setSignalSample(sample_sig)
#
##    tlx.addSignalChannels(sr_channels)

#if myFitType == FitType.Background :
#    tlx.addSignalChannels(cr_channels)
#    #tlx.addSignalChannels(sr_channels)
#    #tlx.addValidationChannels(sr_channels)
