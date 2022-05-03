#!/usr/bin/python

import sys
import re

if (len(sys.argv) < 4):
	print """
script to check reaction types in R command database


Arg1: R command database OR species list

Arg2: gwb database (e.g. thermo.dat)

Arg3: tag indicating database (e.g. thermo)

"""
	sys.exit()

## arguments
r_db=sys.argv[1]
gwb_file=sys.argv[2]
tag=sys.argv[3]

def get_sp(filename):
	type="type"
	dict={}
	file = open(filename, "rt")
	for line in file:
		line=line.strip("\n")
		if "basis species" in line:
			type="basis"
			continue
		if "aqueous species" in line:
			type="aqsp"
			continue
		if "gases" in line:
			type="gas"
			continue
		if "redox" in line:
			type="redox"
			continue
		if "oxides" in line:
			type="oxide"
			continue
		line=line.split()
		if (len(line)==1):
			if line[0] not in dict:
				dict[line[0]]={}
			dict[line[0]][type]=1
	return(dict)
			

def print_out(dict,filename, tag):
	file=open(filename,"rt")
	for line in file:
		line=line.strip("\n")
		if "Pressure=" in line:
			continue
		if "Temperature=" in line:
			continue
		if "Eh" in line:
			continue
		m="MISMATCH"
		line.strip("\n")
		if tag in line:
			if '#' is line[0]:
				continue
			if 'Eh' in line:
				continue
		
			line_copy=line
			line_copy=line_copy.split()
			sp=line_copy[0]
			type_rdb=line_copy[1]
			if sp in dict:
				if type_rdb in dict[sp]:
					m="OK"
				if (len(dict[sp].keys()) > 1):
					m="CAREFUL"
				type=dict[sp]
			else:
				type="NoType"
			print line,"\t",type,"\t", m


dict_gwb=get_sp(gwb_file)



print_out(dict_gwb, r_db, tag)



