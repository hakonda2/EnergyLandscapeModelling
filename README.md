# Running the model script in GWB
1. Load database (File > open > Thermo Data)
2. Set print option to long (Config > Print options > Aqueous sp. > long
3. Paste in the script and run it
4. Save the ouput

Repeat the above step with different values for *reactant times*, e.g. 
2,20,50,100,400,800,1600,5000,20000,100000


# Parsing the output
The output from the GWB modelling can be parsed with the AnalyseWoBeOutput_v17.py script, which produces energy densities and a microbial community composition (functional level) at different temperatures. The input for the script is <br/>
A GWB output file (e.g. ReactOutput_400x.txt) <br/>
A database of standard Gibbs Energies (dG.txt) <br/>
A file indicating what redoxreactions to analyse and what functional group each reaction belongs to (e.g. Redox.txt) <br/>
<br/>
In order to run it on a single output from GWB, one could run
```sh
AnalyseWoBeOutput_v17.py React_output_400x.txt Redox.txt dG.txt > Output.txt
```

# Make plots
Prepare a *Chemistry* file, an *Energy* file, and an *Abundance* file. Run R scripts to produce graphs, e.g.:

```sh

Rscript plot_chemistry_r_2.txt -i Total_Chemistry_C_s1.txt -o Total_Chemistry_C_s1_nov16_mt120.pdf -mt 120 -bruse_2014

Rscript plot_energy_r_3.txt -ltt 2.5 -htt 121 -mt 120 -i Total_Energy_E_s1.txt -o Total_Energy_E_s1_mt120_htt121_ltt2c5.pdf -bruse_2014

Rscript plot_abundance_r_3.txt -i Total_Abundance_A_s1.txt -htt 121 -ltt 2.5 -mt 120 -o Total_Abundance_A_s1_mt120_htt121_ltt2c5.pdf

```

### AnalyseWoBeOutput options
LATER

### Shellscript
The  WoBe_pipline_2.sh is a wrapper script for running throgh AnalyseWoBeOutput.py multiple times to get the complete output for energy landscapes and community structure.

# Making a standard Gibbs energy database
In order to calculate energies, we need the Gibbs energy of ractions:
<br/>


<img src="https://render.githubusercontent.com/render/math?math=\Delta G_r = \Delta G^0"> +
<img src="https://render.githubusercontent.com/render/math?math=RTlnQ"> 

<br/>

The Q term can be calculated from the activies in the GWB output. In order to obtain standard Gibbs energy values relevant for a certain pressure and temperature range, run the script *get_dG_redox.R* [requires the 'CHNOSZ' package], e.g.:

```sh
Rscript get_dG_redox.R
```

For available options, run

```sh
Rscript get_dG_redox.R -h
```

# Modifying a database
For various reasons, it is not so easy to fully automate the process of modifying a GWB database and some manual work might be necessary. However, most modifications may be completed using the following approach indicated below. The idea is that you first run an inital mixing (e.g. at moderate temperature and pressure (using a standard database), then identify the species involved, then modify the database for the entires of those species, then rerun the mixing and repeat until no new species occur. 

### Get the relevant species
In order to see what species that are in the output and what category they belong to (e.g. gases, aqous species...), run the *Getsp.py* script:

```sh
Getsp.py <Output_from_GWB> > getsp_out.txt
```

### Check 
The *subcrt_commands_database.txt* file is a database of species found in *dat files and a corresponding subcrt command for recalculation of logK values based in given Temp and Pres values.

Check what entries that is relevant for a given gwb database, e.g.


```sh
CheckType.py subcrt_commands_database.txt thermo.com.v8.r6+.dat r6
```

### Make list

Guided by the above step, make a list of species you want to change, e.g. *SpToFix_thermo_r6_FILE_A.txt*


### Make an R script to run CHNOSZ

*MakeRscript_v3.py* is a python script that makes an R script:

```sh
MakeRscript_v3.py  SpToFix_thermo_r6_FILE_A.txt subcrt_commands_database.txt r6 > r_script.txt
```

### Run the R script

It will produce a *logK_out.txt* file with new logK values.

### Change the database

Run *ChangeDb_v3.py* to change the database

```sh
ChangeDb_v3.py logK_out.txt thermo.com.v8.r6+.dat > new_db.dat
```

In the new database it should now be indicated what changes that have been made, who made them, and when.




