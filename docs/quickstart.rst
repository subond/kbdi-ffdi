Quickstart
================

Using the command line tools
****************************
The primary mechanism for using this application is the command line script named ``kbdi-ffdi-run``. To run the script, open the Anaconda command line prompt and type the script name followed by its parameters.   
  
The ``kbdi-ffdi-run`` script has an input parameter (the name of the input file that you will compute kbdi and ffdi from) and an output parameter (the name of the output file that data will be saved to). These parameters are specified by including the flags ``-i`` followed by the input filename and ``-o`` followed by the output filename.  
  

1. Open the Anaconda Prompt and activate the virtual environment where you installed kdbi-ffdi  


2. run the following command with the input filename you'd like to process and specify the output filename  

::

	C:\Users\Jacob> activate py36
	(py36) C:\Users\Jacob> kbdi-ffdi-run -i C:/Users/Jacob/my_weather_data.csv -o C:/Users/Jacob/my_output_data.csv


Jupyter Notebook Example
***********************
