#!/usr/bin/python

import sys
import re

if (len(sys.argv) < 2):
	print """
script to get dominating sp from gwb output


Arg1: gwb output


"""
	sys.exit()

## arguments
gwb_file=sys.argv[1]


def get_sp(filename):
	type="type"
	dict={}
	dict["aqsp"]={}
	dict["redox"]={}
	dict["gas"]={}
	
	p=0
	file = open(filename, "rt")
	for line in file:
		if "only" in line:
			continue
		if "Step" in line:
			p=0
			continue
		if "Aqueous species" in line:
			type="aqsp"
			p=1
			continue
		if "Gases" in line:
			type="gas"
			p=1
			continue
		if "--------" in line:
			continue
		if "Original basis" in line:
			p=0
		if "Elemental" in line:
			p=0
		if "Reactants" in line:
			p=0
		if "Mineral saturation" in line:
			p=0
		if "In fluid" in line:
			p=0
		if "redox" in line:
			p=0
			#type="redox"
			continue
			
		if (p==1):
			line=line.split()
			if (len(line)>0):
				dict[type][line[0]]=type
	return(dict)

def print_dict(dict):
	for element in dict:
		internal_dict=dict[element]
		for el in internal_dict:
			print el,"\t",element


sp_dict=get_sp(gwb_file)
print_dict(sp_dict)


