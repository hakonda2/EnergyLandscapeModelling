#!/usr/bin/python

import sys
import re

if (len(sys.argv) < 3):
	print """
script to change logK values in thermo.dat


Arg1: txtfile specifiying logK values for selected reactions (from R_script)


Arg2: database (e.g. thermo.dat)



"""
	sys.exit()



## arguments
logK_file=sys.argv[1]
db_file=sys.argv[2]


## get user time date
import os
import pwd
user = pwd.getpwuid(os.getuid())[0]
import datetime
now = datetime.datetime.now()
date=now.strftime("%Y-%m-%d %H:%M")

def get_logK_info(filename):
	logK_info={}
	file = open(filename, "r")
	for line in file:
		#print line
		line = line.strip("\n")
		if "info" in line:
			continue
		line=line.split("\t")
		line[4]=int(line[4])
		line[3]=line[3].translate(None,'"')
		if (line[4] == 1):
			logK_info[line[3]]={}
		logK_info[line[3]][line[4]]=line[2]	
	file.close()
	return(logK_info)

def fixList(list):
	list=str(list)
	list=list.replace("[","")
	list=list.replace("]","")
	list=list.replace("'","")
	return(list)
	
def parse_db(logK_val,filename):
	temperature=logK_val['temperature'].values()
	pressure=logK_val['pressure'].values()
	
	line_type=['a','b']
	mod=0
	count=0
	nr_sp=100
	file = open(filename,'rt')
	for line in file:
		
		line=line.strip("\n")
		line=line.strip("\r")
		if '* debye huckel' in line:
			mod=0
			print line
			continue
		if '* temperatures' in line:
			reaction='temperature'
			print line
			mod=2
			continue
		if '* pressures' in line:
			reaction='pressure'
			print line
			mod=2
			continue
		if '* log k for eh reaction' in line:
			reaction='Eh_main'
			print line
			mod=2
			continue
		if '* log k for o2 gas solubility' in line:
			reaction='O2(g)_main'
			print line
			mod=2
			continue
		if '* log k for h2 gas solubility' in line:
			reaction='H2(g)_main'
			print line
			mod=2
			continue
		if '* log k for n2 gas solubility' in line:
			reaction='N2(g)_main'
			print line
			mod=2
			continue

		#print "TEST1", line
		if "oxides" in line:
			line_type[1]="oxides"
		if "minerals" in line:
			line_type[1]="mineral"
		if "basis" in line:
			line_type[1]="basis"
		if "redox" in line:
			line_type[1]="redox"
		if "aqueous species" in line:
			line_type[1]="aqsp"
		if "gases" in line:
			line_type[1]="gas"
		

		line_type[0]=line
		test="_".join(line_type)
		if test in logK_val:
			print line
			mod=1
			reaction=test
			continue
		if (mod==1):
			if "species in reaction" in line:
				nr_sp = line.split()
				nr_sp = int(nr_sp[0])
				count=0
				print line
				continue
			if "." in line:
				count = count + line.count('.')
			if (count == nr_sp):
				mod=2
				print line
		if (mod==2):
			print "       ",logK_val[reaction][1],"  ",logK_val[reaction][2],"   ",logK_val[reaction][3],"   ",logK_val[reaction][4]
			mod=3
			continue
		if (mod==3):
			print "       ",logK_val[reaction][5],"  ",logK_val[reaction][6],"   ",logK_val[reaction][7],"   ",logK_val[reaction][8]
			Tmod=fixList(temperature)
			Pmod=fixList(pressure)
			
			print "* Modified by ", user, " ", date, "T =",Tmod, "   P =", Pmod
			mod=4
			continue
		if (mod==4):
			mod=0
			count=0
			nr_sp=100
			continue
		print line

def get_temp_pres(filename):
	count=0
	temp_pres={}
	temp_pres['pressure']={}
	temp_pres['temperature']={}
	file = open(filename,'rt')
	for line in file:
		if 'logK' in line:
			continue
		if (count<8):
			count=count+1
			line=line.split()
			temp_pres['temperature'][count]=line[0]
			temp_pres['pressure'][count]=line[1]
	
	return(temp_pres)
	
#len(str(a).split('.')[0])

		
## get logK_val from redox, aquos and gas reactions
logK_val = get_logK_info(logK_file)
#print logK_val

## get temperatures and pressures
temp_pres = get_temp_pres(logK_file)
#print temp_pres

## concatenate dictionaries
total=dict(logK_val.items()+temp_pres.items())
#print total

## change db
parse_db(total,db_file)

