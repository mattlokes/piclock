import os
import subprocess

class webServer ():
  
   def __init__( self ):
      pythonpath = os.environ['PYTHONPATH']
      self.serverPath = "{0}/framework/webserver".format(pythonpath)
      self.configPath = "{0}/lighttpd.conf".format(self.serverPath)
   

   def startup ( self ):
      if not os.path.isdir(self.serverPath+"temp/") or not os.path.exists(self.serverPath+"temp/"):
         os.mkdir( self.serverPath+"temp/", 0777 )
      subprocess.call(["lighttpd", "-D", "-f", self.configPath])
   
   def kill( self ):
      file = open(self.serverPath+'temp/lighttpd.pid', 'r') 
      subprocess.call(["kill", file.read()[:-1]])
      pass

if __name__ == "__main__":
    webServ = webServer()
    webServ.startup()
