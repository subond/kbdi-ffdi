Installation
======================

Installation will vary depending on whether you are using Anaconda or a regular installation of Python. Here are my recommendations...

For Anaconda Users
*******************
1. Download wheel file from the latest release on github (https://github.com/jwarndt/kbdi-ffdi/releases)  

2. Start anaconda and activate the Python virtual environment that you would like to install kbdi-ffdi into
::

	C:/Users/Jacob> activate py36
	(py36) C:/Users/Jacob>


3. Navigate to the location of the wheel file that you donwloaded  
::

	(py36) C:/Users/Jacob> cd Downloads

4. pip install the wheel file
::

	(py36) C:/Users/Jacob/Downloads> python pip install kbdi_ffdi-0.1.0-py3-none-any.whl


5. Test to see that the package was installed correctly by activating python, and then importing kbdiffdi
::

	(py36) C:/Users/Jacob/Downloads> python

.. code-block:: python

	>>> from kbdiffdi import *
	>>> 

If the package was installed correctly, you shouldn't see any errors.

For Regular Python installation Users
**************************************