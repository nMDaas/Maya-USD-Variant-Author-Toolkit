# Maya tool which allows users to easily and quickly place objects in/around another object 
# with a set radius and many other customizable parameters.

# Instructions: Make any changes to the path desired and run this file.

import sys

if 'src' in sys.modules:
    del sys.modules['src']
if 'src.errorDialogWrapper' in sys.modules:
    del sys.modules['src.errorDialogWrapper']
import src.errorDialogWrapper

def errorDialog_exec_tool(errorTitle, errorMessage):
 window = src.errorDialogWrapper.createErrorDialogWindow(errorTitle, errorMessage)