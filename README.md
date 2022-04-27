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

### AnalyseWoBeOutput options
LATER

### Shellscript
The  WoBe_pipline_2.sh is a wrapper script for running throgh AnalyseWoBeOutput.py multiple times to get the complete output for energy landscapes and community structure.

# Making a standard Gibbs energy database
In order to calculate energies, we need the Gibbs energy of ractions, $\Delta G_(r)$ :
<br/>

```math
$\Delta G_(r) = \Delta G^(0) + RTlnQ$
```

<img src="https://render.githubusercontent.com/render/math?math=\Delta G_(r) = \Delta G^(0) + RTlnQ">

<br/>

The Q term can be calculated from the activies in the GWB output. In order to obtain $\Delta G^(0)$ values relevant for a certain pressure and temperature range, run the script *get_dG_redox.R* [requires the 'CHNOSZ' package], e.g.:

```sh
Rscript get_dG_redox.R
```

For available options, run

```sh
Rscript get_dG_redox.R -h
```

 



