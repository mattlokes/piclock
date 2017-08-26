import os
import subprocess

class ledDisplay ():
  
   def __init__( self ):
      pass 

   def startup ( self ):
      pythonPath = os.environ['PYTHONPATH']
      subprocess.call(["{0}/displays/ledDisplay".format(pythonPath)])
   
   def kill( self ):
      pass

if __name__ == "__main__":
    ledDisplay = ledDisplay()
    ledDisplay.startup()
