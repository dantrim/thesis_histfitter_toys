#!/bin/env python


from optparse import OptionParser
import os
import sys

import ROOT as r
r.PyConfig.IgnoreCommandLineOptions = True
r.gROOT.SetBatch(True)
r.gStyle.SetOptStat(False)

from array import array 

class Parameter :
    def __init__(self, name_="") :
        self.name = name_ 
        self.final_value = 0.0
        self.up_error = 0.0
        self.down_error = 0.0
        self.is_norm_factor = False

    def setNormFactor(self) :
        self.is_norm_factor = True

    def isNormFactor(self) :
        return self.is_norm_factor

    def Print(self) :
        print "XXX NP %s %f %f %f"%(self.name, self.final_value, self.up_error, self.down_error)


def get_final_value_lines(infile="") :

    np_lines = []

    final_value_line = -1
    lines = open(infile).readlines()
    for iline, line in enumerate(lines) :
        if not line : continue
        line = line.strip()
        if "Floating Parameter" in line and "InitialValue" in line and "FinalValue" in line :
            if iline > final_value_line :
                final_value_line = iline

    print final_value_line

    last_line_to_consider = -1
    for iline, line in enumerate(lines[final_value_line:]) :
        line = line.strip()
        #print line
        if not line : continue
        if '+/-' not in line and "------" not in line :
            last_line_to_consider = iline
            break

    last_line_to_consider = final_value_line + last_line_to_consider
    print last_line_to_consider

    for line in lines[final_value_line:last_line_to_consider] :
        line = line.strip()
        if not line : continue
        if "Floating" in line : continue
        if "-----" in line : continue
        np_lines.append(line)

    return np_lines

def get_final_values_from_lines(nplines) :
    if len(nplines) == 0 :
        print "get_final_values_from_lines    Input NP list is empty!"
        sys.exit()

    out_nps = []

    template = "Floating Parameter  InitialValue    FinalValue +/-  Error     GblCorr."
    for np in nplines :
        # skip stat uncertainty
        if "gamma_stat" in np : continue


        cols = np.split()
        #print cols
        parameter = Parameter(cols[0]) 
        parameter.final_value = float(cols[2])
        if "Lumi" in parameter.name :
            parameter.final_value = parameter.final_value - 1.0
        parameter.up_error = float(cols[4])
        parameter.down_error = float(cols[4])
        if "mu" in parameter.name and "test" not in parameter.name.lower() :
            parameter.setNormFactor()
            parameter.final_value = parameter.final_value - 1.0
        #if "mu" in parameter.name and "sig" in parameter.name.lower() : continue
        out_nps.append(parameter)

    return out_nps

def make_pull(final_nps) :

    nps = []
    norms = []
    mu_bin = -1
    for i, np in enumerate(final_nps) :
        if not np.isNormFactor() :
            nps.append(np)
        else :
            if mu_bin < 0 :
                mu_bin = i
            norms.append(np)
    nps += norms


    # canvas
    c = r.TCanvas("c_pulls","", 1200, 600)
    c.SetBottomMargin(0.38)
    #c.SetBottomMargin(0.42)
    c.SetTopMargin(1.5*0.03)
    c.SetRightMargin(0.02)
    c.SetLeftMargin(0.06)
    c.cd()

    r.gPad.SetTickx()
    r.gPad.SetTicky()

    # axes
    nbins = len(final_nps)
    frame = r.TH2F('frame_%s'%outfile, '', nbins, -0.5, nbins-0.5, 6, -2, 2)
    frame.SetYTitle("Post-fit Parameter Value") #Final NP Value")
    frame.SetXTitle("")
    frame.GetYaxis().SetTitleOffset(1.45*0.5)
    for ibin, np in enumerate(final_nps) :
        if np.isNormFactor() :
            frame.GetXaxis().SetBinLabel( ibin+1, "%s - 1"%str(np.name).replace("alpha_","").replace("AR_","") )
        elif "Lumi" in np.name :
            frame.GetXaxis().SetBinLabel( ibin+1, "Lumi - 1" )
        else :
            frame.GetXaxis().SetBinLabel( ibin+1, "%s"%str(np.name).replace("alpha_","").replace("AR_","") )
    frame.GetXaxis().LabelsOption("v")

    frame.Draw('axis')

    # graph for error points
    nom = []
    up = []
    down = []
    for np in nps :
        np.Print()
        nom.append(float(np.final_value))
        up.append(float(np.up_error))
        down.append(float(np.down_error))

    y = array('d', nom)
    y_up_error = array('d', up)
    y_down_error = array('d', down)
    x = array('d', [ i for i in xrange(len(final_nps))])
    x_error = array('d', [ 0 for i in xrange(len(final_nps))])

    g = r.TGraphAsymmErrors(len(final_nps), x, y, x_error, x_error, y_down_error, y_up_error)
    g.SetMarkerStyle(20)
    g.Draw("same p")

    # some reference lines
    line_plus1 = r.TLine(-0.5, 1, nbins-0.5, 1)
    line_plus1.SetLineStyle(2)
    line_plus1.SetLineWidth(1)
    line_plus1.SetLineColor(r.kRed)
    line_plus1.Draw('same')

    line_initial = r.TLine(-0.5, 0, nbins-0.5, 0)
    line_initial.SetLineColor(r.kBlue)
    line_initial.Draw('same')

    line_minus1 = r.TLine(-0.5, -1, nbins-0.5, -1)
    line_minus1.SetLineStyle(2)
    line_minus1.SetLineWidth(1)
    line_minus1.SetLineColor(r.kRed)
    line_minus1.Draw('same')

    mu_sep = r.TLine(mu_bin-0.5, -2, mu_bin-0.5, 2)
    mu_sep.SetLineStyle(4)
    mu_sep.SetLineWidth(2*mu_sep.GetLineWidth())
    mu_sep.Draw('same')


    c.SaveAs(outfile + ".eps")

if __name__ == "__main__" :

    global infile, outfile
    parser = OptionParser()
    parser.add_option("-i", "--input", help="HistFitter log", default="")
    parser.add_option("-o", "--output", help="Name of output file", default="")
    (options, args) = parser.parse_args()

    infile = options.input
    outfile = options.output

    if infile == "" or outfile == "" :
        print "You must provide an input and output file. You have:"
        print "    > input (-i/--input): %s"%infile
        print "    > output (-o/--output): %s"%outfile
        sys.exit()

    # should check that file exists but whatever

    # get the lines that contain the final values of the NPs
    raw_lines = get_final_value_lines(infile)

    # now get the final values
    final_values = get_final_values_from_lines(raw_lines)

    # now make that plot
    make_pull(final_values)
