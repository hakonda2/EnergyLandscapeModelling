#!/bin/bash

##### AnalyseWoBeOutput
## output from gwb needs to be in long format (see gwb) and be named "Reaction_output_<num>x.txt" where <num> is a number indicating V in gwb.
## Runas eg: 


function usage
{
echo
echo "Parse GWB output using AnalyseBoBeOut.py"
echo
echo "USAGE: WoBe_pipeline.txt <params>"
echo
echo "-h  --help" 
echo "    show this help text and quit"
echo
echo "-r  --redoxfile" 
echo "     redoxfile (default Redox.txt)"
echo
echo "-d  --dgfile" 
echo "      dgfile (default dG.txt)"
echo
echo
echo "-o  --outdir"
echo "      output directory (default: out)"
echo
echo
}

### debug
#redox_file="Redox.txt"
#dg_file="dG.txt"
#outdir="Test"
# in order to prepare files use eg.
#for i in {2,20,50,100,400,800,1600,5000,20000,100000}; do ln -s ../React_output_Bruse_sep16_${i}x_DBtcv8r6_fixpH.txt TEST/React_Output_${i}x.txt;done

### default
redox_file="Redox.txt"
dg_file="dG.txt"
outdir="out"
REMOVE=false
start_step=0
stop_step=100

while [ "$1" != "" ]; do
    case $1 in
         -ss | --start_step )    shift
                              start_step=$1
                                ;;
          -st | --start_step )    shift
                              stop_step=$1
                                ;;
        -r | --redoxfile )    shift
                              redox_file=$1
                                ;;
        -d | --dgfile )        shift
			        dg_file=$1
                                ;;
        -o | --outdir)        shift
				outdir=$1
				;;
        -h | --help )           usage
                                echo "exiting..2"
                                exit
                                ;;
        -t | --only-total )     echo "t"    
                                REMOVE=true
                                exit
                                ;;
        * )                     usage
                                echo "exitcode 4"
                                exit 1
    esac
    shift
done


##### make start_step2
start_step2=$((stop_step - 5))

echo $start_step
echo $start_step2
echo $stop_step


###### making outdir
if [ -d "$outdir" ]; then
echo "directory $outdir exists, exiting"
exit
fi
mkdir $outdir
cd $outdir




###################### ENERGY MODELLING ###########
######### CH4 + NO3- not included

### without sulfur correction
	for i in {2,20,50,100,400}; do AnalyseWoBeOutput_v17.py ../React_output_${i}x.txt ../$redox_file ../$dg_file 1 1 -E -start $start_step -stop $stop_step  > Out_${i}x_E_s1.txt; done

	for i in {800,1600,5000,20000,100000}; do AnalyseWoBeOutput_v17.py ../React_output_${i}x.txt ../$redox_file ../$dg_file 1 1 -E -start $start_step2 -stop $stop_step  > Out_${i}x_E_s1.txt; done
	
	cat Out_*x_E_s1.txt > Total_Energy_E_s1.txt

### with sulfur correction
	for i in {2,20,50,100,400}; do AnalyseWoBeOutput_v17.py ../React_output_${i}x.txt ../$redox_file ../$dg_file 1 0.9 -E -start $start_step -stop $stop_step  > Out_${i}x_E_s09.txt; done

	for i in {800,1600,5000,20000,100000}; do AnalyseWoBeOutput_v17.py ../React_output_${i}x.txt ../$redox_file ../$dg_file 1 0.9 -E -start $start_step2 -stop $stop_step  > Out_${i}x_E_s09.txt; done

	cat Out_*x_E_s09.txt | grep -v ABMODEL > Total_Energy_E_s09.txt




###### AUNDANCE MODELLING ###########

##### CH4 + NO3- not included

### without sulfur correction
	for i in {2,20,50,100,400}; do AnalyseWoBeOutput_v17.py ../React_output_${i}x.txt ../$redox_file ../$dg_file 1 1 -A -start $start_step -stop $stop_step  > Out_${i}x_A_s1.txt; done

	for i in {800,1600,5000,20000,100000}; do AnalyseWoBeOutput_v17.py ../React_output_${i}x.txt ../$redox_file ../$dg_file 1 1 -A -start $start_step2 -stop $stop_step  > Out_${i}x_A_s1.txt; done

	cat Out_*x_A_s1.txt | grep ABMODEL > Total_Abundance_A_s1.txt

### with sulfur correction
	for i in {2,20,50,100,400}; do AnalyseWoBeOutput_v17.py ../React_output_${i}x.txt ../$redox_file ../$dg_file 1 0.9 -A -start $start_step -stop $stop_step  > Out_${i}x_A_s09.txt; done

	for i in {800,1600,5000,20000,100000}; do AnalyseWoBeOutput_v17.py ../React_output_${i}x.txt ../$redox_file ../$dg_file 1 0.9 -A -start $start_step2 -stop $stop_step  > Out_${i}x_A_s09.txt; done

	cat Out_*x_A_s09.txt | grep ABMODEL > Total_Abundance_A_s09.txt


######### CHEMISTRY ####################
##### CH4 + NO3- not included

### without sulfur correction
	for i in {2,20,50,100,400}; do AnalyseWoBeOutput_v18.py ../React_output_${i}x.txt ../Redox.txt ../dG.txt 1 1 -C -start $start_step -stop $stop_step > Out_${i}x_C_s1.txt; done

	for i in {800,1600,5000,20000,100000}; do AnalyseWoBeOutput_v18.py ../React_output_${i}x.txt ../Redox.txt ../dG.txt 1 1 -C -start $start_step -stop $stop_step > Out_${i}x_C_s1.txt; done

	cat Out_*x_C_s1.txt | grep -v step > temp.txt
	cat Out_*x_C_s1.txt | grep step | head -1 > Total_Chemistry_C_s1.txt
	cat temp.txt >> Total_Chemistry_C_s1.txt
	rm temp.txt

## change directory back again
cd ..

