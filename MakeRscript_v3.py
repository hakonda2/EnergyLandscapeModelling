#!/usr/bin/python

import sys
import re

if (len(sys.argv) < 2):
	print ""
	print "script to make R script for getting logK values"
	print ""
	print ""
	print "Arg1: txtfile specifiying temperatures and pressures (8 each)"
	print "and for what sp. logK should be calculated"
	print ""
	print "Arg2: genaral R commands for getting logK"
	print ""
	print "Arg3: choose database name (r6 or thermo)"
	print ""
	print ""
	print "example of input file (Arg1):"
	print "Pressure=rep(245,8)"
	print "Temperature=c(25,50,60,80,100,120,150,200)"
	print "HS-	redox	r6,thermo"
	print "CH4(aq)	redox	r6,thermo"
	print "CO2(aq)	aqsp	r6,thermo"
	print ""
	print "example of input file (Arg2):"
	print "CH4(aq)	redox	subcrt(c('CH4','water','H+', 'HCO3-','O2'), c(-1,1,1,1,-2), c('aq','','','','aq'), T=temp, P=pres)	thermo,r6"
	print "HS-	redox	subcrt(c('HS-','SO4-2','H+','O2'), c(-1,1,1,-2), c('','','','aq'), T=temp, P=pres)	thermo,r6"
	print "CO2(aq) aqsp	subcrt(c('CO2','water','H+', 'HCO3-'), c(-1,-1,1,1), c('aq','','',''), T=temp, P=pres)	thermo,r6"
	print ""
	print ""
	sys.exit()

## arguments
input_one=sys.argv[1]
input_two=sys.argv[2]
db=sys.argv[3]

def get_temp_pres(filename):
	pres_temp={}
	file = open(filename, "r")
	for line in file:
		#print line
		line = line.strip("\n")
		if "Pressure=" in line:
			line=line.split("=")
			pres_temp["Pressure"]=line[1]
		if "Temperature=" in line:
			line=line.split("=")
			pres_temp["Temperature"]=line[1]	
	file.close()
	return(pres_temp)

def get_sp_to_change(filename):
	file = open(filename, "r")
	dict={}
	for line in file:
		line=line.strip("\n")
		if "basis" in line:
			continue
		if "#" in line:
			continue
		if db in line:
			line=line.split()
			if (len(line) <= 1):
				continue
			#if db in line:
			#print line
			line="_".join(line[:2])
			dict[line]=1
	return(dict)

def build_command(filename,dict):
	command_string=""
	file = open(filename,"r")
	for line in file:
		if "#" in line:
			continue
		if "basis" in line:
			continue
		if db in line:
			line=line.strip("\n")
			line=line.split("\t")
			#print line
			r_command=line.pop()
			r_command=line.pop()
			#print line
			#print r_command
			line="_".join(line)
			if line in dict:
				command_string=command_string+',\n'+"\""+line+"\""+","+"\""+r_command+"\""
	command_string= command_string[2:]
	command_string="commands <- c("+command_string+")"
	return (command_string)

def print_script(commands,temp_pres_dict):
	pres=temp_pres_dict["Pressure"]
	temp=temp_pres_dict["Temperature"]
	print "library('CHNOSZ')"
	print "conv=0.239    # 1J = 0.239cal"
	print "mod.OBIGT('ferrihydrite', formula='Fe(OH)3', state='cr',G=-709500*conv, H=-828000*conv, S=127*conv, V=34.36, Cp=33.4,a=0, b=0, c=0, d=0, e=0, f=0, lambda=0) #thermo.com.r6, Majzlan 2003, Snow 2012"
	#print "mod.obigt('twolineferrihydrite', formula='FeOOH', state='cr',G=-709500*conv, H=-828000*conv, S=127*conv, V=34.36, Cp=33.4,a=0, b=0, c=0, d=0, e=0, f=0, lambda=0,force=T) #thermo.com.r6, Majzlan 2003, Snow 2012"
	print "temp <- "+temp
	print "pres <- "+pres 
	print ""
	print commands
	print """

i <- 0

while (i < length(commands)-1) {
	i <- i+1
	info <- commands[i]
	i<-i+1
	command<-commands[i] 
	command <- parse(text=command)
	output<-eval(command)
	output<-output$out
	output$logK <- round(output$logK,digits=4)
	output$info <- info
	output$count <- 1:length(output[,1])
	output <- output[,-c(3,5,6,7,8,9)]
	if (i==2){
		write.table(output, file="logK_out.txt", append=F, sep="\\t", row.names=F,col.names=T)
	} else {
		write.table(output, file="logK_out.txt", append=T, sep="\\t", row.names=F,col.names=F)
	}

}"""
	
	
		
## get temp and pressure (from input_one)
tp = get_temp_pres(input_one)
#print tp


## get dict of sp and type (from input_one)
given_sp = get_sp_to_change(input_one)
#print given_sp


## build commands definitions (from input_two)
command_string = build_command(input_two, given_sp)
#print command_string


## print script
print_script(command_string, tp)
