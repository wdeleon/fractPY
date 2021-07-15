To run this project in Windows, perform these steps in the following order:

1. Install Python 3 for Windows:
   Download the 64 bit version of the Python installer from the Python website at https://www.python.org/downloads/windows/
   Run the installer. Check the Add Python to PATH option, and select Install Now.
   In the post-install screen, select the option to disable the path length limit.

2. Install Visual Studio:
   Download the Visual Studio 2019 Community Edition installer from: https://visualstudio.microsoft.com/
   Install the "Desktop development with C++" workload.
   This is required because in Windows the Nvidia Cuda Compiler (nvcc) only supports Microsoft Visual C++ as its host compiler.
   No other workloads or components are required.

4. Add to the Windows PATH environment variable: "C:\Program Files (x86)\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.25.28610\bin\Hostx64\x64"
   This ensures that nvcc will be able to find the necessary host compiler it depends on.

3. Install the Nvidia CUDA Toolkit:
   Download the installer from the Nvidia website at: https://developer.nvidia.com/cuda-toolkit

4. Install the most recent Nvidia video card drivers:
   Download the installer from the Nvidia website at: https://www.nvidia.com/Download/index.aspx

5. Open a command prompt window (this can be done by pressing Windows Key + R and entering "cmd")
   Ensure pip is fully upgraded by running: "python -m pip install --upgrade pip"
   
   Several additional packages for Python are required:
   
   Install pytools by running: "pip install pytools"
   
   Install numpy by running: "pip install numpy"
   
   Install numba by running: "pip install numba"
   
   Install pycuda by running: "pip install pycuda"
   
   Install pypng by running: "pip install pypng"

6. In the command window, use "cd" (change directory) to change to the directory containing the project files.
   Run the project by invoking fract.py in the Python interpreter and providing suitable options, for example:

   python fract.py test.csv -g -m

   If fract.py is invoked without any options provided, it will provide a help screen documenting the
   available options.
