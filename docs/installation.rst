Installation
======================

Installation will vary depending on whether you are using Anaconda or a regular installation of Python. Here are my recommendations...

(Windows) For Anaconda Users
****************************
1. Download the wheel file (.whl) from the latest release on github (https://github.com/jwarndt/kbdi-ffdi/releases)  

2. Start anaconda and activate the Python virtual environment that you would like to install kbdi-ffdi into
::

	C:/Users/Jacob> activate py36
	(py36) C:/Users/Jacob>


3. Navigate to the location of the wheel file that you donwloaded  
::

	(py36) C:/Users/Jacob> cd Downloads

4. pip install the wheel file
::

	(py36) C:/Users/Jacob/Downloads> pip install kbdi_ffdi-0.1.0-py3-none-any.whl


5. Test to see that the package was installed correctly by activating python, and then importing kbdiffdi
::

	(py36) C:/Users/Jacob/Downloads> python

.. code-block:: python

	>>> from kbdiffdi import *
	>>> 

If the package was installed correctly, you shouldn't see any errors.

(Windows) For those that do not have Anaconda Installed
*******************************************************
1. Download the latest version of Anaconda for Windows from: https://www.anaconda.com/download/
Be sure to choose the Python 3.7 version  


2. Download the wheel file from the latest release of kbdi-ffdi on github (https://github.com/jwarndt/kbdi-ffdi/releases)  


3. After Anaconda is installed, open the Anaconda Prompt.  

4. Navigate to the location of the wheel file that you donwloaded  
::

	(C:/Users/Jacob>) cd Downloads

5. pip install the wheel file
::

	(C:/Users/Jacob/Downloads>) pip install kbdi_ffdi-0.1.0-py3-none-any.whl


6. Test to see that the package was installed correctly by activating python, and then importing kbdiffdi
::

	(C:/Users/Jacob/Downloads>) python

.. code-block:: python

	>>> from kbdiffdi import *
	>>> 

If the package was installed correctly, you shouldn't see any errors.

(Windows) For Regular Python installation Users
***********************************************