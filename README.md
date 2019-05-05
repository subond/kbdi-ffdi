# kdbi-ffdi
kbdi-ffdi is a Python package for calculating the Keech-Byram Drought Index (KBDI) and McArthur’s Forest Fire Danger Index (FFDI) from daily surface-level meteorological data. KBDI and FFDI are commonly used metrics for assessing drought and fire danger in South Africa and Australia. With the kbdi-ffdi Python package, you can compute KBDI and FFDI from csv data or netCDF data and save the results.

### building
make sure to change the version number in the setup.py file
#### build source distribution
python setup.py sdist
#### build platform (Windows) wheel file distribution
python setup.py bdist_wheel