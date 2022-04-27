#!/usr/bin/python
# WoBe.py
#     Class definition for Work Bench output parsing


import sys
import re

if (len(sys.argv) < 4):
	print """
-------------------------------------------------------------
script to analyse ouptputfile from WB


Arg1: output from gwb (txtfile)


Arg2: file with  defined redox reactions

	e.g

	tag	denom	nom	order	group
	1H2(aq)+0.5O2(aq)->H2O	H2(aq):1,O2(aq):0.5	H2O:1	2	1
	1H2S(aq)+2O2(aq)->1HSO4-+1H+	H2S(aq):1,O2(aq):2	HSO4-:1,H+:1	1 1

	order => analyse reactions in this order
	group => indicating what reactions should be grouped together when calculating total dG
	
	
Arg3: output from R file with dG info from selected redox reactions
Updates conc and activites after reactions in same order

Arg4: oxygen correction factor (optional 0-1)

Arg5: sulfur correction factor (optional 0-1)

NOTE1:
correction for wrong O2 correction in gws script:
self.concentrations['O2(aq)']*=0.79


NOTE2:
Use of arg4 and arg5
arg4 is only in use when arg5 is unset or set to 1. Oxygen correction factor is then used to recalculate new oxygen 
concentrations with the formula factor*old_o2_concentration.
arg4 is handy for looking at the effect of different conc of O2 in the seawater.

if arg5 is set (eg 0.9), new HS- and H2S are calculated (new_conc=factor*old_conc). Oxygen is corrected accordingly and 
the corresponding oxygen correction factor is calculated. This is useful when looking at the effect of spontaneous reactions 
between HS-/H2S and oxygen.

oxygen and sulfur correction factors are printed for each gwb step.

NOTE3:
make sure that stepinfo.UpdateConcAct() is commented when doing abundance modelling. Uncomment when eg linking HS-/H2S oxidation.

-----------------------------------------------------------
"""
	sys.exit()

## arguments
gwb_out=sys.argv[1]
redox_file=sys.argv[2]
r_output=sys.argv[3]

#default
E_MODELLING=True
A_MODELLING=False
PRINT_CHEMISTRY=False

startstep = 0
stopstep = 100
if "-E" in sys.argv:
	E_MODELLING=True
	A_MODELLING=False
	PRINT_CHEMISTRY=False
elif "-A" in sys.argv:
	A_MODELLING=True
	E_MODELLING=False
	PRINT_CHEMISTRY=False
if "-C" in sys.argv:
	A_MODELLING=False
	E_MODELLING=False
	PRINT_CHEMISTRY=True
if "-start" in sys.argv:
	pos=sys.argv.index("-start")+1
	startstep = int(sys.argv[pos])
if "-stop" in sys.argv:
	pos=sys.argv.index("-stop")+1
	stopstep = int(sys.argv[pos])

# oxygen correction factor: eg 0.9 (new O2 consentration is 0.9*original)
try:
	oxygen_correction=float(sys.argv[4])
except:
	oxygen_correction=float(1.0)

# sulfur correction factor -  eg 0.9 (new HS- and H2S consentrations are 0.9*original) - 
# NOTE: this will influence/override oxygen correction set in argv4 
# (O2 consumed will be 2* the amount of HS-/H2S consumed)
try:
	sulfur_correction=float(sys.argv[5])
except:
	sulfur_correction=float(1.0)

#reactions={}

class WoBe:
	def __init__(self,filename):
		self.filename=filename
		self.step=int(0)
		self.redoxreactions={}
		self.totalSteps=int(0)
		self.temp=0
		self.mass=0
		self.redoxCouple={}
		self.nr_electrons=int(0)
		self.concentrations={}
		self.logactivities={'H2O':0,'Fe(OH)3':0}
		self.available={}
		self.limiting=[]
		self.actcoeff={}
		self.conc_threshold = 1e-15
		self.CONC_HEADER_PRINTED=False
	
	
	def setStep(self, stepnr):
		self.step = stepnr
	def	getStep(self):
		return self.step
	def getMass(self):
		return self.mass
	def getTemp(self):
		return self.temp
	def getTotalSteps(self):
		return self.totalSteps
	def getRedoxCouple(self):
		return self.redoxCouple
	def getConcentrations(self):
		return self.concentrations
	
	def getdG_mole(self,dg,tag,redox_dict, test_step):
		step=self.step
		output={}
		temp=float(self.temp)
		temp=int(round(temp))+int(273)     # change from degC to K
		temp=str(temp)
		#print "TEMP ", temp
		#couple=self.redoxCouple
		#reactions=self.redoxreactions
		#nr_electrons=self.nr_electrons
		conc=self.concentrations
		limiting=self.limiting
		available=self.available
		#print "LIMITING", "AVAILABLE", limiting, available
		logact=self.logactivities
		#test_step=-1                      # set to -1 when test should not be run, otherwise eg 50
		#print "dg  ", dg
		dg_zero=float(dg[tag][temp])
		if int(step) == int(test_step):
			print "dG_zero", tag, "  ", dg_zero
		#print "DG_ZERO ", dg_zero
		
		denom = redox_dict[tag]['denom'].keys() # 
		nom = redox_dict[tag]['nom'].keys()
		
		#print "DENOM", denom
		
		log_a_denom=float(0)
		log_a_nom=float(0)
		
		
		
		####### HERE IS A BUG: MUST MULTIPLY WITH STOECK!!!!!! FIXED!!
		for element in denom:
			log_a=logact[element]
			if int(step) == int(test_step):
				print "DENOM: tag element loga ", tag, "   ", element, "  ", log_a 
			log_a_denom=float(log_a_denom)+(float(log_a)*float(redox_dict[tag]['denom'][element]))
		for element in nom:
			log_a=logact[element]
			if int(step) == int(test_step):
				print "NOM: element loga ", tag, "   ", element, "  ", log_a
			log_a_nom=log_a_nom+(float(log_a)*float(redox_dict[tag]['nom'][element]))
		
		log_q=log_a_nom-log_a_denom
		if int(step) == int(test_step):
			print "LOGQ, LOGA_nom LOGA_denom ", log_q, "  ", log_a_nom, "   ", log_a_denom
		output['logQ']=log_q
		#print "LOG Q  ", log_q
		
		RTlogQ = float(8.31*int(temp)*2.3*log_q)
		
		dG_mole = dg_zero+RTlogQ
		
		#print "dG ", dG_mole
		
		output['dG_mole']=dG_mole
		
		
		#print "Couple ", couple
		limiting_list = limiting.keys()
		sp=limiting_list[0]
		#print "Limiting ", limiting_list
		moles=(1/float(limiting[sp]))*available[sp]
		#print " Moles  ", moles
		#moles=limiting[0]
		#moles=moles.split(':')
		#moles=(1/limiting[limiting.keys()[0]])*available[limiting.keys()[0]]
		#moles = (1/float(moles[1]))*available[moles[0]]
		
		dG_kgMix = dG_mole*moles
		#print "dG_kgMix ", dG_kgMix
		output['dG_kgMix']=dG_kgMix
		
		mass=self.mass
		dG_kgFluid = dG_kgMix*mass
		#print "dG_kgFluid ", dG_kgFluid
		output['dG_kgFluid']=dG_kgFluid
		
		if int(step)==int(test_step):
			print "RTlogQ ", RTlogQ
			print "log_q ", log_q
			print "dG_mole ", dG_mole 
			print "dG_kgMix ", dG_kgMix 
			print "temp ", temp
			#print "dG_kgFluid, moles, mass, sp, limiting[sp], available[sp]", dG_mole, "  ", dG_kgMix, " ", dG_kgFluid, " ", moles, " ", mass, " ", sp, "  ", limiting[sp], " ", available[sp]
		
		return (output)
		
	def getInfo(self,oxygen_correction,sulfur_correction):
		
		#init
		x=''
		#redox=[]
		seen_redoxreactions={}
		read_conc=0
		read_logact=0
		
		filename=self.filename
		file=open(filename,'r')
		read=0
		#print read
		for line in file:
			#line=line.strip("\n")
			if line in ['\n','\r\n']:
				read_conc=0
				continue
			if 'Step #' in line:
				line = line.split()
				step_nr = int(line[2])
				if step_nr == self.step:
					read=1
					continue
				else:
					read=0
			if read==1:
				if '---------' in line:
					continue
				if 'e- ' in line:					
					continue
				if 'Temperature =' in line:
					line = line.split()
					temp = line[2]
					self.temp=temp
					#print "temp ",temp, "read ", read
					continue
				if "Activity of water" in line:
					line = line.split()
					self.concentrations['H2O']=float(line[-1])
					continue
				if 'Solution mass' in line:
					line = line.split()
					self.mass = float(line[-2])
					#print "mass ", self.mass, "read ",read
				if 'Aqueous species' in line:
					read_conc=1
					continue
				if 'only species' in line: ## careful: what happens when output is set to full...
					read_conc=0
				if 'Mineral saturation states' in line:
					read_conc=0
				if 'pH =' in line and 'log fO2' in line:
					line=line.split('pH =')
					line=line[1].split('log fO2')
					self.pH=float(line[0])
				if 'log fug.' in line:
					read_conc=1
					continue
				
				if read_conc==1:
					line=line.rstrip()
					line=line.split()
					#print "LINE: ", line
					self.concentrations[line[0]]=float(line[1])		# eg {'H2(g)': 0.1597, 'O2(g)': 0.2698, 'KCl(aq)': 2.891e-06,...}
					self.logactivities[line[0]]=float(line[-1])		# NB!! for gases this will be log fugacities eg {'H2(g)': -0.797, 'O2(g)': -0.569, 'KCl(aq)': -5.539,...}
					self.actcoeff[line[0]]=float(line[-2])			# NB!! for gases this will by fugacities, not actcoefficients, SO: do NOT use gases in reactants!!!
					continue
		# oxygen correction (correcting for wrong O2 correction in gws script)
		self.concentrations['O2(aq)']*=0.79
		
		# SO4-- correction (sum up SO4)
		self.concentrations['SO4--']+=self.concentrations['HSO4-']
		self.concentrations['SO4--']+=self.concentrations['KSO4-']
		self.concentrations['SO4--']+=self.concentrations['KHSO4(aq)']
		self.concentrations['SO4--']+=self.concentrations['CaSO4(aq)']
		if 'MgSO4(aq)' in self.concentrations:
			self.concentrations['SO4--']+=self.concentrations['MgSO4(aq)'] # only run for chemistry on ChimneySven data
		
		# NO3- correction (sum up NO3)
		self.concentrations['NO3-']+=self.concentrations['HNO3(aq)']
		
		# NH4+ correction (sum up NH4+)
		self.concentrations['NH4+']+=self.concentrations['NH3(aq)']
		
		# Sum up CO2?
		
		# user defined oxygen correction
		if (sulfur_correction==1):
			oldox=self.concentrations['O2(aq)']
			self.concentrations['O2(aq)']*=oxygen_correction		
		
		# user defined sulfide correction
		if (sulfur_correction < 1):
			oldox=self.concentrations['O2(aq)']
			#print "OLDOX", oldox
			self.concentrations['O2(aq)']-=2*self.concentrations['HS-']*(1-sulfur_correction) # 2 O2 consumed per HS-
			self.concentrations['HS-']*=sulfur_correction
			self.concentrations['O2(aq)']-=2*self.concentrations['H2S(aq)']*(1-sulfur_correction) # 2 O2 consumed per H2S
			self.concentrations['H2S(aq)']*=sulfur_correction
			#print "NEWOX", self.concentrations['O2(aq)']
			
		# make sure O2 is positive
		if (self.concentrations['O2(aq)'] < 0.00000000000000000000000001):
			self.concentrations['O2(aq)']= 0.00000000000000000000000001
		oxygen_correction=self.concentrations['O2(aq)']/oldox
		#print "FINALOX", self.concentrations['O2(aq)']
		return(oxygen_correction,sulfur_correction)
			
	def setLimiting(self,dict):
		#limiting=raw_input('species+stoech of limiting species (eg H2S(aq):1, O2(aq):2)')
		#limiting= 'O2(aq):0.5,H2(aq):1'
		#limiting=sp.strip()
		#limiting=sp_stoek_string.split(',')
		self.limiting = dict
		return(dict)

	def Available(self):
		limiting=self.limiting
		available={}
		concentrations=self.concentrations
		#print concentrations
		
		for element in limiting:
			#element=element.split(':')
			#element=element[0]
			available[element] = 10000.1
		
		for element in limiting:
			#element=element.split(':')
			#print "ELEMENT ", element
			species=element
			if species == 'H+':			# avoid that H+ is limiting
				continue
			factor=float(limiting[element])
			#print "FACTOR", factor
			#print "CONC ", concentrations
			total_conc=concentrations[species]
			#print "TOT CONC", total_conc
			current_min=available[species]
			#print "CURRENT_MIN", current_min
			#print "totalConc_Curent_min", total_conc, current_min
			if total_conc < current_min:
				available={}
				limiting_sp=species
				for item in limiting:
					#item=item.split(':')
					#print "ITEM ", item
					fac=float(limiting[item])
					tot=(fac/factor)*total_conc
					available[item]=tot
					#print "LOCAL AV ", available
		self.available=available
		#print "AVAILABLE ", available
		return(available,limiting_sp)
		
	def ModifyConsAndAct(self):
		# fraction of HS- and H2S to remove
		f=0.5
		
		self.concentrations		
		self.logactivities
		
		# get how much this is in molar (assuming molar==activity)
		rem=self.concentrations['HS-']*.5
		
		# remove this from both HS- and O2
		self.concentrations['HS-']-=rem
		self.concentrations['O2(aq)']-=rem
		
		# update logactivites
		l=-0.30103 # log(.5) = -.30103
		self.logactivities['HS-']+=l
		self.logactivities['O2(aq)']+=l
		
		# do the same thing as above for H2S
		rem=self.concentrations['H2S(aq)']*.5
		self.concentrations['H2S(aq)']-=rem
		self.concentrations['O2(aq)']-=rem
		self.logactivities['H2S(aq)']+=l
		self.logactivities['O2(aq)']+=l
		
		
		# make sure O2(aq) is positive
		if (self.concentrations['O2(aq)'] < .00000000000000000001):
			self.concentrations['O2(aq)'] = .00000000000000000001
		if (self.logactivities['O2(aq)'] < -20):
			self.logactivities['O2(aq)'] = -20
		
		return(self.logactivities)
	
	def print_chemistry(self):
		
		# chemicals to be printed
		chemical_list = ["H2S(aq)", "HS-", "Methane(aq)", "Fe++","H2(aq)", "NO3-", "O2(aq)", "NH4+", "SO4--", "MgSO4(aq)", "CaSO4(aq)", "KSO4-", "HCO3-", "MgHCO3+", "NaHCO3(aq)", "CO2(aq)"]
		
		# print header first time called
		if (not self.CONC_HEADER_PRINTED):
			h="CONSENTRATIONS\tstep\ttemp\tpH"
			for c in chemical_list:
				h+="\t"+c
			print h
			self.CONC_HEADER_PRINTED=True
		
		# print out info
		step=str(self.step)
		temp = str(self.temp)
		pH = str(self.pH)
		out="CONSENTRATIONS\t"+step+"\t"+temp+"\t"+pH
		for c in chemical_list:
			if c in self.concentrations:
				conc = str(self.concentrations[c])
			else:
				conc=str(0)
			out+="\t"+conc
		print (out)
		

		
	
	def SpAbSim(self,dGdict,fullreport):
	
		# Assume start absolute abundance=0. Then run through list of reactions only letting
		# a small number of e- react (eg nanomole). Keep track of amount of substrate beeing used. Stop reaction 
		# if one substrate <= 0. Continue loop until all reactions stops. For each step add abundances
		# assuming that abundance == added dG. Compare absolute abundances and calculate relative abundance (0-1) for each group.
		# A functional group may use several redoxreactions (eg H2S+O2, HS- + O2, HS- + NO3-, H2S + NO3-). In this case
		# only one of these reactions is allowed in each iteration. 
		
		# fullreport: 0 if no printing within this def, 1 to print full report
		
		#### Initialize
		# ab: abundance calculated from individual reactions
		# gr: abundance calculated from groups of reactions
		ab={}
		ab['1H2(aq)+0.5O2(aq)->H2O']=float(0)
		ab['1Methane(aq)+2O2(aq)->CO2(aq)+2H2O']=float(0)
		ab['1H2S(aq)+2O2(aq)->1HSO4-+1H+']=float(0)
		ab['1HS-+2O2(aq)->1HSO4-']=float(0)
		ab['10HS-+8H2O+16NO3-->10HSO4-+8N2(g)+16OH-']=float(0)
		ab['10H2S(aq)+16NO3-->10HSO4-+2H2O+8N2(g)+6OH-']=float(0)
		ab['CH4(aq)+SO42-+2H+->CO2(aq)+H2S(aq)+2H2O']=float(0)
		ab['10CH4(aq)+16NO3-->10CO2(aq)+8N2(g)+12H20+16OH-']=float(0)
		ab['4H2(aq)+CO2(aq)->CH4(aq)+2H2O']=float(0)
		ab['4H2(aq)+HCO3-+H+->CH4(aq)+3H2O']=float(0)
		ab['4H2(aq)+1SO42-+2H+->H2S(aq)+4H2O']=float(0)
		ab['NH4++2O2(aq)->NO3-+H2O+2H+']=float(0)
		ab['4Fe2++O2(aq)+10H2O->4Fe(OH)3+8H+']=float(0)
		ab['5H2(aq)+2NO3-+2H+->N2(g)+6H2O']=float(0)
		gr={}
		gr['sulfox']=float(0)
		gr['methox']=float(0)
		gr['anme']=float(0)
		gr['amo']=float(0)
		gr['srb']=float(0)
		gr['methanogens']=float(0)
		gr['feo']=float(0)
		
		# define redox reactions to consider
		reactionA = 0 # 1H2(aq)+0.5O2(aq)->H2O #### note this reaction is under SOB (rC), set to 0 because I dont wont to analyze it separately, kept code in case I change my mind
		reactionB = 1 # 1Methane(aq)+2O2(aq)->CO2(aq)+2H2O
		reactionC = 1 # 1H2S(aq)+2O2(aq)->1HSO4-+1H+### 1HS-+2O2(aq)->1HSO4-###1H2(aq)+0.5O2(aq)->H2O###10HS-+8H2O+16NO3-->10HSO4-+8N2(g)+16OH-###10H2S(aq)+16NO3-->10HSO4-+2H2O+8N2(g)+6OH-
		reactionD = 1 # 10CH4(aq)+16NO3-->10CO2(aq)+8N2(g)+12H20+16OH-###CH4(aq)+SO42-+2H+->CO2(aq)+H2S(aq)+2H2O
		reactionE = 1 # 4H2(aq)+CO2(aq)->CH4(aq)+2H2O ### 4H2(aq)+HCO3-+H+->CH4(aq)+3H2O
		reactionF = 1 # 4H2(aq)+1SO42-+2H+->H2S(aq)+4H2O
		reactionG = 1 # NH4++2O2(aq)->NO3-+H2O+2H+
		reactionH = 1 # 4Fe2++O2(aq)+10H2O->4Fe(OH)3+8H+
		
		# indicator of linked reactions where only one reactions is allowed for each iteration.
		indicatorSulfurox=0
		indicatorANME=0
		indicatorMet=0
		
		# get startconc of relevant sp.
		conc={}
		conc['O2']=self.concentrations['O2(aq)']
		conc['CH4']=self.concentrations['Methane(aq)']
		conc['H2']=self.concentrations['H2(aq)']
		conc['H2S']=self.concentrations['H2S(aq)']
		conc['NO3-']=self.concentrations['NO3-']
		conc['HS-']=self.concentrations['HS-']
		conc['SO4--']=self.concentrations['SO4--']
		conc['CO2']=self.concentrations['CO2(aq)']
		conc['HCO3-']=self.concentrations['HCO3-']
		conc['NH4+']=self.concentrations['NH4+']
		conc['Fe++']=self.concentrations['Fe++']
		
		# tag for printing
		tag='ABMODEL '
		
		# set startcon to zero if below threshold
		for e in conc:
			if conc[e] < self.conc_threshold:
				conc[e]=0
				
		# add absolute abundance iteratively to specified reactions	
		indicator = 1
		consume=0.00000001	# moles of electrons allowed to be transferred for each reaction at each step
		num=1
		c=1
		while (indicator > 0):
			indicator=0
			c+=1
			indicatorSulfurox=0
			indicatorANME=0
			if c>num:
				num=num+100
				if(fullreport==1):
					print tag,c
					print tag,"H2 ",conc['H2']
					print tag,"O2 ",conc['O2']
					print tag,"CH4 ",conc['CH4']
					print tag,"H2S ", conc['H2S']
					print tag,"HS- ", conc['HS-']
					print tag,"NO3- ", conc['NO3-']
					print tag,"SO4--", conc['SO4--']
			if (reactionA == 1):
				if (conc['H2'] > 0 and conc['O2'] > 0):
					#print "HEEEEERE"
					electrons=2
					ab['1H2(aq)+0.5O2(aq)->H2O'] += dGdict['1H2(aq)+0.5O2(aq)->H2O']*consume/electrons
					conc['O2'] -= consume*.5/electrons
					conc['H2'] -= consume/electrons
					indicator=1
			if (reactionB == 1):
				if (conc['CH4'] > 0 and conc['O2'] > 0):
					#print "HEEEEERE 2"
					electrons=8
					ab['1Methane(aq)+2O2(aq)->CO2(aq)+2H2O'] += dGdict['1Methane(aq)+2O2(aq)->CO2(aq)+2H2O']*consume/electrons
					gr['methox']+= dGdict['1Methane(aq)+2O2(aq)->CO2(aq)+2H2O']*consume/electrons
					conc['O2'] -= consume*.5/electrons
					conc['CH4'] -= consume/electrons
					indicator=1
			if (reactionC == 1):
				if (indicatorSulfurox == 0):
					if (conc['H2'] > 0 and conc['O2'] > 0):
						#print "HEEEEERE"
						electrons=2
						ab['1H2(aq)+0.5O2(aq)->H2O'] += dGdict['1H2(aq)+0.5O2(aq)->H2O']*consume/electrons
						gr['sulfox']+=dGdict['1H2(aq)+0.5O2(aq)->H2O']*consume/electrons
						conc['O2'] -= consume*.5/electrons
						conc['H2'] -= consume/electrons
						indicator=1				
						indicatorSulfurox=1
				if (indicatorSulfurox==0):
					if (conc['H2S'] > 0 and conc['O2'] > 0):
						#print "HEEEEERE 2"
						electrons=8
						ab['1H2S(aq)+2O2(aq)->1HSO4-+1H+'] += dGdict['1H2S(aq)+2O2(aq)->1HSO4-+1H+']*consume/electrons
						gr['sulfox']+= dGdict['1H2S(aq)+2O2(aq)->1HSO4-+1H+']*consume/electrons
						conc['O2'] -= consume*2/electrons
						conc['H2S'] -= consume/electrons
						indicator=1
						indicatorSulfurox=1
				if (indicatorSulfurox == 0):
					if (conc['H2'] > 0 and conc['NO3-'] > 0):
						electrons=10
						ab['5H2(aq)+2NO3-+2H+->N2(g)+6H2O'] +=dGdict['5H2(aq)+2NO3-+2H+->N2(g)+6H2O']*consume/electrons
						gr['sulfox']+=dGdict['5H2(aq)+2NO3-+2H+->N2(g)+6H2O']*consume/electrons
						conc['NO3-'] -= consume*2/electrons
						conc['H2'] -= consume*5/electrons
						indicator=1
						indicatorSulfurox=1
				if (indicatorSulfurox==0):
					if (conc['HS-'] > 0 and conc['O2']>0):
						electrons=8
						ab['1HS-+2O2(aq)->1HSO4-']+=dGdict['1HS-+2O2(aq)->1HSO4-']*consume/electrons
						gr['sulfox']+=dGdict['1HS-+2O2(aq)->1HSO4-']*consume/electrons
						conc['HS-'] -= consume*1/electrons
						conc['O2'] -= consume*2/electrons
						indicator=1
						indicatorSulfurox=1
				if (indicatorSulfurox == 0):
					if (conc['HS-'] > 0 and conc['NO3-'] > 0):
						electrons=80
						ab['10HS-+8H2O+16NO3-->10HSO4-+8N2(g)+16OH-'] += dGdict['10HS-+8H2O+16NO3-->10HSO4-+8N2(g)+16OH-']*consume/electrons
						gr['sulfox']+= dGdict['10HS-+8H2O+16NO3-->10HSO4-+8N2(g)+16OH-']*consume/electrons
						conc['NO3-'] -= consume*16/electrons
						conc['HS-'] -= consume*10/electrons
						indicator=1
						indicatorSulfurox=1
				if (indicatorSulfurox==0):
					if (conc['H2S'] > 0 and conc['NO3-']>0):
						electrons=80
						ab['10H2S(aq)+16NO3-->10HSO4-+2H2O+8N2(g)+6OH-']+=dGdict['10H2S(aq)+16NO3-->10HSO4-+2H2O+8N2(g)+6OH-']*consume/electrons
						gr['sulfox']+=dGdict['10H2S(aq)+16NO3-->10HSO4-+2H2O+8N2(g)+6OH-']*consume/electrons
						conc['H2S'] -= consume*10/electrons
						conc['NO3-'] -= consume*16/electrons
						indicator=1
						indicatorSulfurox=1		
			if (reactionD == 1):
				#if (conc['CH4'] > 0 and conc['NO3-'] > 0):
					#print "HEEEEERE 2"
					#electrons=80
					#ab['10CH4(aq)+16NO3-->10CO2(aq)+8N2(g)+12H20+16OH-'] += dGdict['10CH4(aq)+16NO3-->10CO2(aq)+8N2(g)+12H20+16OH-']*consume/electrons
					#gr['anme']+= dGdict['10CH4(aq)+16NO3-->10CO2(aq)+8N2(g)+12H20+16OH-']*consume/electrons
					#conc['CH4'] -= consume*10/electrons
					#conc['NO3-'] -= consume*16/electrons
					#indicator=1
					#indicatorANME=1
				if (indicatorANME==0):
					if (conc['CH4'] > 0 and conc['SO4--']>0):
						electrons=8
						ab['CH4(aq)+SO42-+2H+->CO2(aq)+H2S(aq)+2H2O']+=dGdict['CH4(aq)+SO42-+2H+->CO2(aq)+H2S(aq)+2H2O']*consume/electrons
						gr['anme']+=dGdict['CH4(aq)+SO42-+2H+->CO2(aq)+H2S(aq)+2H2O']*consume/electrons
						conc['CH4'] -= consume*1/electrons
						conc['SO4--'] -= consume*1/electrons
						indicator=1
						indicatorANME=1
			if (reactionE == 1):
				if (conc['H2'] > 0 and conc['CO2'] > 0):
					electrons=8
					ab['4H2(aq)+CO2(aq)->CH4(aq)+2H2O']+=dGdict['4H2(aq)+CO2(aq)->CH4(aq)+2H2O']*consume/electrons
					gr['methanogens']+=dGdict['4H2(aq)+CO2(aq)->CH4(aq)+2H2O']*consume/electrons
					conc['H2'] -= consume*4/electrons
					conc['CO2'] -= consume*1/electrons
					indicator=1
					indicatorMet=1
				elif (conc['H2'] > 0 and conc['HCO3-'] > 0):
					electrons=8
					ab['4H2(aq)+HCO3-+H+->CH4(aq)+3H2O']+=dGdict['4H2(aq)+HCO3-+H+->CH4(aq)+3H2O']*consume/electrons
					gr['methanogens']+=dGdict['4H2(aq)+HCO3-+H+->CH4(aq)+3H2O']*consume/electrons
					conc['H2'] -= consume*4/electrons
					conc['HCO3-'] -= consume*1/electrons
					indicator=1
					indicatorMet=1
			if (reactionF == 1):
				if (conc['H2'] > 0 and conc['SO4--'] > 0):
					electrons=8
					ab['4H2(aq)+1SO42-+2H+->H2S(aq)+4H2O']+=dGdict['4H2(aq)+1SO42-+2H+->H2S(aq)+4H2O']*consume/electrons
					gr['srb']+=dGdict['4H2(aq)+1SO42-+2H+->H2S(aq)+4H2O']*consume/electrons
					conc['H2'] -= consume*4/electrons
					conc['SO4--'] -= consume*1/electrons
					indicator=1
					indicatorMet=1		
			if (reactionG == 1):
				if (conc['NH4+'] > 0 and conc['O2'] > 0):
					electrons=8
					ab['NH4++2O2(aq)->NO3-+H2O+2H+']+=dGdict['NH4++2O2(aq)->NO3-+H2O+2H+']*consume/electrons
					gr['amo']+=dGdict['NH4++2O2(aq)->NO3-+H2O+2H+']*consume/electrons
					conc['NH4+'] -= consume*1/electrons
					conc['O2'] -= consume*2/electrons
					indicator=1
					indicatorMet=1
			if (reactionH == 1):
				if (conc['Fe++'] > 0 and conc['O2'] > 0):
					electrons=8
					ab['4Fe2++O2(aq)+10H2O->4Fe(OH)3+8H+']+=dGdict['4Fe2++O2(aq)+10H2O->4Fe(OH)3+8H+']*consume/electrons
					gr['feo']+=dGdict['4Fe2++O2(aq)+10H2O->4Fe(OH)3+8H+']*consume/electrons
					conc['Fe++'] -= consume*4/electrons
					conc['O2'] -= consume*1/electrons
					indicator=1
					indicatorMet=1
		### calculate relative abundances
	
		# get sum
		s=0
		for i in ab:
			s+=ab[i]
			#print "DETAIL_\t",i, "\t", ab[i] 
		#print "Conc O2: ", conc['O2']
		# get rel abundance
		relab_ab={}
		for i in ab:
			relab_ab[i]=ab[i]/s
	
		relab_gr={}
		for i in gr:
			relab_gr[i]=gr[i]/s
		
		return(relab_ab, relab_gr)
		
	def UpdateConcAct(self):
		import math
		#conc=self.concentrations
		#available=self.available
		#logacts=self.logactivities
		#coef=self.actcoeff
		#print "\nACT BEFORE LOOP:\n", self.logactivities,"\n"
		for item in self.available:
			self.concentrations[item] -= self.available[item] ## this should be ok since the mass is the same: x1 mmol/mass1 - x2 mmol/mass1 = x3 mmol/mass1	
			act=self.actcoeff[item]*self.concentrations[item]
			if act > 0:
				lact=math.log10(act)
				self.logactivities[item]=lact
			else:
				self.logactivities[item]=0
		#print "\nACT AFTER LOOP:\n", self.logactivities,"\n"	
		#self.logactivities=logacts
		#self.concentrations=conc
		
def redoxinfo(filename):
	dict={}
	file = open(filename,'rt')
	for line in file:
			if "denom" in line:
				continue
			if line is "\n":
				continue
			if "#" in line:
				continue
			line=line.strip("\n")
			line=line.split("\t")
			tag=line[0]
			dict[tag]={}
			
			dict[tag]['denom']={}
			dict[tag]['nom']={}
			denom=line[1]
			nom=line[2]
			denom=denom.split(",")
			nom=nom.split(",")
			#print "NOM, DENOM", nom, "  ", denom
			for element in denom:
				element=element.split(":")
				#print "ELEMENT ", element
				dict[tag]['denom'][element[0]]=element[1]
			#print "DICT ",dict
			for element in nom:
				element=element.split(":")
				#print "EL ",element
				dict[tag]['nom'][element[0]]=element[1]
			
			
			
			#dict[line[0]]['denom']=line[1]
			#dict[line[0]]['nom']=line[2]
	return(dict) 
				

def dg_redox(filename):
	dict={}
	file=open(filename,'rt')
	for line in file:
		if "info" in line:
			continue
		if line is "\n":
			continue
		line=line.strip("\n")
		line=line.split()
		tag=line[9]
		tag=tag.replace('"','')
		if tag not in dict:
			dict[tag]={}
		temp=line[0]				# here T is in K, but in self.temp T is in degC, this is corrected for in getdG_mole
		dG=line[4]
		dict[tag][temp]=dG
	return(dict)

def get_Tagorder(filename):
	dict={}
	file=open(filename,'rt')
	for line in file:
		if "denom" in line:
			continue
		if line is "\n":
			continue
		if line[0] is "#":
			continue
		line=line.strip("\n")
		line=line.split()
		tag=line[0]
		order=int(line[3])
		dict[order]=tag
	return(dict)

def get_Groupinfo(filename):
	dict={}
	file=open(filename,'rt')
	for line in file:
		if "denom" in line:
			continue
		if line is "\n":
			continue
		if line[0] is "#":
			continue
		line=line.strip("\n")
		line=line.split()
		order=int(line[3])
		group=int(line[4])
		dict[order]=group
	return(dict)	


def	main():
	
	#initialize
	dG_result={}
	
	selected_redox_dict=redoxinfo(redox_file) # {'1H2+0.5O2->H2O': {'denom': 'H2(aq):1,O2(aq):0.5', 'nom': 'H2O'}, etc
	#print "REDOXDICT", selected_redox_dict
	dg=dg_redox(r_output) # {'1H2(aq)+O.5O2(aq)->H2O': {'344': '-261220.2064' etc   T in degC
	#print "DG ",dg['1Methane(aq)+2O2(aq)->CO2(aq)+2H2O']['276']
	#step=80
	stepinfo=WoBe(gwb_out)
	#print "STEPINFO", stepinfo
	order_tag=get_Tagorder(redox_file)		# {1: tag1  ..}
	#print "ORDERTAG", order_tag
	orderlist=order_tag.keys() 
	orderlist.sort()						# [1,2,3..]
	order_group=get_Groupinfo(redox_file)	# {1:1,2:1,3:2 ..}, used to connect reactions to get max energy for taxonomic group
	#stepinfo.getInfo()
	step=startstep									# step in gwb_output		
	#
	#print "TAG LIMITING ",tag,"  ",limiting
	#stepinfo=WoBe(gwb_out)
	#stepinfo.setStep(step)
	#stepinfo.getInfo()
	#step=16
	#print "L1",stepinfo.limiting
	while step <= stopstep:

		#print "HERE"
		group=-11111111							# initialize with non-existing group nr. 
		stepinfo.setStep(step)
		for element in orderlist:
			tag=order_tag[element]
			if order_group[element]!=group:
				group=order_group[element]
				(oxcor,sulfcor)=stepinfo.getInfo(oxygen_correction,sulfur_correction)	#reset	and return current oxygen and sulfur corrections		
			limiting=stepinfo.setLimiting(selected_redox_dict[tag]['denom'])  # limiting eg {'O2(aq)': '0.5', 'H2(aq)': '1'}
			#print "TAG", "LIMITING", tag, limiting
			available,limiting_sp = stepinfo.Available()   # available: {'O2(aq)': 7.6920000000000002e-06, 'H2(aq)': 1.5384e-05}
			#print "CONS ", stepinfo.concentrations
			#print "LOGA ", stepinfo.logactivities
			#print "LOG Before ", stepinfo.logactivities['HS-'], stepinfo.logactivities['H2S(aq)'], stepinfo.logactivities['O2(aq)'] 
			#print "CONS Befor", stepinfo.concentrations['HS-'], stepinfo.concentrations['H2S(aq)'], stepinfo.concentrations['O2(aq)']
			##### modify available (allow defined spontaneous reactions) REMEMBER TO COMMENT when not in use!!
			#####stepinfo.ModifyConsAndAct()
			#print "LOG After ", stepinfo.logactivities['HS-'], stepinfo.logactivities['H2S(aq)'], stepinfo.logactivities['O2(aq)']
			#print "CONS After", stepinfo.concentrations['HS-'], stepinfo.concentrations['H2S(aq)'], stepinfo.concentrations['O2(aq)']
			#print "TAG AVAILABLE ",tag, "  ", available
			dG=stepinfo.getdG_mole(dg,tag,selected_redox_dict,-1) # last parameter indicates step for full print report (useful for debugging), set to -1 for no "test"
			#test.defineRedoxCouple()
			dgmole=dG['dG_mole']
			dgmix=dG['dG_kgMix']
			dgfluid=dG['dG_kgFluid']
			temp = stepinfo.getTemp()
			mass = stepinfo.getMass()
			num_digits=1
			if (E_MODELLING):
				print tag,"\t",step,"\t", temp,"\t",round(dgmole,num_digits),"\t",round(dgmix,num_digits),"\t",round(dgfluid,num_digits),"\t",group,"\t",limiting_sp,"\t",mass
			## put result into dict for use in abundance modeling
			if (A_MODELLING):
				dG_result[tag]=dgmole
			
			if (E_MODELLING):
				stepinfo.UpdateConcAct() # DO NOT DELETE, ?Used to avoid eg that same O2 is used by both HS- and H2S. stepinfo.getInfo
				# above and below, will reset when starting reaction belonging to different group or when starting abundance
				# modelling? But what about dG_result? What could happen is that you get a far too low dG for the reaction that comes first
				# of f.ex H2S and HS-. To be sure: run this when the purpose is energy modelling, but not abundance modelling 
		
		if (PRINT_CHEMISTRY):
			(oxcor,sulfcor)=stepinfo.getInfo(oxygen_correction,sulfur_correction) # make sure to reset
			stepinfo.print_chemistry()
		
		#### Do abundance simulation
		# make sure data are reloded (removes unwanted effect of UpdateConcAct)
		if (A_MODELLING):
			(oxcor,sulfcor)=stepinfo.getInfo(oxygen_correction,sulfur_correction)
		
			# do simulation
			num_digits=6
			sys.stderr.write("\n"+"ABUNDANCE MODELLING"+"\n")
			(RelAbundance_reaction, RelAbundance_group)=stepinfo.SpAbSim(dG_result,0) # set last argument to 0 or 1 (print iterations or only abundances)
			for i in RelAbundance_reaction:
				print 'ABMODEL_REACTION',"\t",i,"\t",step,"\t",temp,"\t",round(RelAbundance_reaction[i],num_digits)
			for i in RelAbundance_group:
				print 'ABMODEL_GROUP',"\t",i,"\t",step,"\t",temp,"\t",round(RelAbundance_group[i],num_digits)

		
		# print info to stderr
		sys.stderr.write("\n"+"STEPNR. "+str(step)+"\n")
		sys.stderr.write("File: "+str(gwb_out)+"\n")
		sys.stderr.write("OxygenCorrection: "+str(oxcor)+"\n")
		sys.stderr.write("SulfurCorrection: "+str(sulfcor)+"\n")
		sys.stderr.write("conc below " + str(stepinfo.conc_threshold) + " set to zero in abundance modelling\n")
		sys.stderr.write("E_MODELLING / A_MODELLING: "+str(E_MODELLING)+","+str(A_MODELLING)+"\n")
		sys.stderr.write("---------------"+"\n")		
		
		step=step+1


if	__name__ == '__main__':
	main()


################################## Some thermodynamic data
###### Fe(OH)3+3H+->3H2O+Fe3+
# OH- dG0f: -37.595 kcal/mole = -157.2 kJ/mole (r6 db)
# Fe(OH)3 dG0f: -696.5 kJ/mole (r6 db)
# H+	dG0f: 0
# H2O	dG0f: -56.688 kcal/mole = -237.2 kJ/mole (r6 db)
# Fe+++ dG0f: -4.12 kcal/mole = 
# Fe(OH)3 + 3H+ -> 3H2O + Fe3+ dG0f: -3*237.2 - 4.12 + 696.5 = -19.22 kj/mole
# when calculating dG in script, assume reaction where Fe(OH)3 is in solid state (activity=1)