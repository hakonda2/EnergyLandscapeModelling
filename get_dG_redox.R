


## help
h <- "\nUse this script to get dG at different temperatures and a pressure\n\nArguments\n-tl  Lower temperature range (in K) [default: 274]\n-th  Higher temperature range (in K) [default: 374]\n-p  Pressure (in atm) [default: 10]\n-o  Name of outputfile [default: dG_out.txt]\n"
## arguments
args <- commandArgs(TRUE)


if ("-h" %in% args){
message(h)
quit()
}
#######

##### lib
library('CHNOSZ')
#####


##### args
if ("-tl" %in% args){
	p<-which(args=="-tl")
	temperature_low <- as.numeric(args[p+1])
} else {
temperature_low <- 274
}

if ("-th" %in% args){
	p<-which(args=="-th")
	temperature_high <- as.numeric(args[p+1])
} else {
temperature_high <- 374
}



if ("-p" %in% args){
	pos<-which(args=="-p")
	pressure <- as.numeric(args[pos+1])
} else {
pressure <- 10
}

if ("-o" %in% args){
	p<-which(args=="-o")
	out_file <- args[p+1]
} else {
out_file <- "dG_out.txt"
}
####


commands <- c("1H2(aq)+0.5O2(aq)->H2O", "subcrt(c('H2O','H2','O2'),c(1,-1,-0.5),c('liq','aq','aq'), T=temp, P=pres)",
"1H2S(aq)+2O2(aq)->1HSO4-+1H+", "subcrt(c('H2S','O2','HSO4-','H+'), c(-1,-2,1,1), c('aq','aq','aq','aq'), T=temp, P=pres)",
"1HS-+2O2(aq)->1HSO4-", "subcrt(c('HS-','O2','HSO4-'), c(-1,-2,1), c('aq','aq','aq'), T=temp, P=pres)",
"10H2S(aq)+16NO3-->1HSO4-+2H2O++8N2(g)+6OH-", "subcrt(c('H2S', 'NO3-', 'HSO4-','H2O','N2','OH-'), c(-10,-16,10,2,8,6),c('aq','aq','aq','liq','g','aq'), T=temp, P=pres)",
"1Methane(aq)+2O2(aq)->CO2(aq)+2H2O","subcrt(c('CH4','O2','CO2','H2O'), c(-1,-2,1,2), c('aq','aq','aq','liq'), T=temp,P=pres)",
"4H2(aq)+1SO42-+2H+->H2S(aq)+4H2O","subcrt(c('H2','SO4-2','H+','H2S','H2O'),c(-4,-1,-2,1,4),c('aq','aq','aq','aq','liq'),T=temp,P=pres)",
"4H2(aq)+CO2(aq)->CH4(aq)+2H2O","subcrt(c('H2','CO2','CH4','H2O'),c(-4,-1,1,2),c('aq','aq','aq','liq'),T=temp,P=pres)",
"CH4(aq)+SO42-+2H+->CO2(aq)+H2S(aq)+2H2O","subcrt(c('CH4','SO4-2','H+','CO2','H2S','H2O'),c(-1,-1,-2,1,1,2),c('aq','aq','aq','aq','aq','liq'),T=temp,P=pres)",
"10CH4(aq)+16NO3-->10CO2(aq)+8N2(g)+12H20+16OH-","subcrt(c('CH4','NO3-','CO2','N2','H2O','OH-'),c(-10,-16,10,8,12,16),c('aq','aq','aq','g','liq','aq'),T=temp,P=pres)",
"4Fe+2+O2+10H2O->4F(OH3)+8H+","subcrt(c('Fe+2','O2', 'H2O', 'Fe(OH)3','H+'), c(-4,-1,-10,4,8), c('aq','aq','liq','cr','aq'),T=temp,P=pres)",
"NH4++2O2(aq)->NO3-+H2O+2H+","subcrt(c('NH4+','O2','NO3-','H2O','H+'),c(-1,-2,1,1,2), c('aq','aq','aq','liq','aq'),T=temp,P=pres)")


# add fe info
conv=0.239    # 1J = 0.239cal
mod.OBIGT('ferrihydrite', formula='Fe(OH)3', state='cr',G=-709500*conv, H=-828000*conv, S=127*conv, V=34.36, Cp=33.4,a=0, b=0, c=0, d=0, e=0, f=0, lambda=0)

# change units
E.units("J")
T.units("K")
P.units("bar")


print(temperature_low)
print(temperature_high)
temp=temperature_low:temperature_high
pres=pressure

i <- 0

while (i < length(commands)-1) {
	i <- i+1
	info <- commands[i]
	i<-i+1
	command<-commands[i] 
	command <- parse(text=command)
	output<-eval(command)
	output<-output$out
	output <- round(output,digits=4)
	output$info <- info
	#output$count <- 1:length(output[,1])
	#output <- output[,-c(3,5,6,7,8,9)]
	if (i==2){
		write.table(output, file=out_file, append=F, sep="\t", row.names=F,col.names=T)
	} else {
		write.table(output, file=out_file, append=T, sep="\t", row.names=F,col.names=F)
	}

}
