# forestplot
Simple forest plots in python with matplotlib

![small_forest_plot](/figures/forest_plot_example.png)

forest_plot is a basic but reasonably flexible function that plots a horizontal scatter and makes use of ax.text() with clip_on set to False. Width of columns can be adjusted using the annot_* args. Plots are setup to generate figures systematic reviews; meta-analysis results were not tested but should work fine by sorting beforehand and passing a custom marker for the meta-analysis results

Horizontal bars should fit to figure width by taking the left and right-most annotation locations from the figure, but the right-hand-side may need adjusting - a tuple can be passed to hbar_lim in this case. If you're saving a figure for publication then the save_fig function can be used for tiffs with lzw compression if needed.

See the examples notebook for small variations. Plots were used to create the figures in the paper [Machine learning for genetic prediction of psychiatric disorders: a systematic review](https://doi.org/10.1038/s41380-020-0825-2) by Bracher-Smith et al.

**Required packages**
- matplotlib
- numpy
- pandas

**Basic use**
- git clone https://github.com/seafloor/forestplot.git
- follow code in /examples

**To download and install required packages (shouldn't be necessary as it's just standard scipy):**
This will also install jupyter notebooks for running examples
- git clone https://github.com/seafloor/forestplot.git
- cd forestplot
- conda env create -f environment.yml
