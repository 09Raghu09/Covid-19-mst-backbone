This repository provides the data and scripts associated with the ncov
to execute the whole workflow one may to install nexttrain with dependencies (see nextstrain.yml) in conda environment
install auspice : npm install --global auspice
activate conda environment
remove old input: rm -rf output/ auspice/
execute then: snakemake
to visualize the output: auspice view --datasetDir auspice
