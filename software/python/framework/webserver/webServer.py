import os
import sys
import  subprocess

class webServer ():
  
   serverPath = "framework/webserver/"   

   def startup (self):
      if not os.path.isdir(self.serverPath+"temp/") or not os.path.exists(self.serverPath+"temp/"):
         os.mkdir( self.serverPath+"temp/", 0777 )
      subprocess.call(["lighttpd", "-f", "./{0}lighttpd_pi.conf".format(self.serverPath)])
      #subprocess.call(["pwd"])
   
   def kill(self):
      file = open('framework/webserver/temp/lighttpd.pid', 'r') 
      subprocess.call(["kill", file.read()[:-1]])
      pass
