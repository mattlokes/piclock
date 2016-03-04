import os
import subprocess

class ledDisplayStart ():
  
   def __init__( self ):
      pass 

   def startup ( self ):
      pythonPath = os.environ['PYTHONPATH']
      subprocess.call(["{0}/displays/ledDisplay".format(pythonPath)])
   
   def kill( self ):
      pass

if __name__ == "__main__":
    ledDisplay = ledDisplayStart()
    ledDisplay.startup()
