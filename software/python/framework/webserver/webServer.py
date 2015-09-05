import os
import sys
import subprocess

class webServer ():
  
   serverPath = "framework/webserver/"
   def __init__(self, customConfigPath):
      if customConfigPath != None:
         self.configPath = customConfigPath
      else:
         if os.environ['USER'] == "pi" or os.environ['USER'] == 'root':
            self.configPath = "./{0}lighttpd_pi.conf".format(self.serverPath)
         else:
            self.configPath = "./{0}lighttpd_pc.conf".format(self.serverPath)
   

   def startup (self):
      if not os.path.isdir(self.serverPath+"temp/") or not os.path.exists(self.serverPath+"temp/"):
         os.mkdir( self.serverPath+"temp/", 0777 )
      subprocess.call(["lighttpd", "-f", self.configPath])
      #subprocess.call(["pwd"])
   
   def kill(self):
      file = open(self.serverPath+'temp/lighttpd.pid', 'r') 
      subprocess.call(["kill", file.read()[:-1]])
      pass

if __name__ == "__main__":
    customConfigPath = None
    if len(sys.argv) > 1:
       customConfigPath = sys.argv[1]
    
    webServ = webServer(customConfigPath)
    webServ.startup()
