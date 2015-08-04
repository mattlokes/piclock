import os
import sys
import  subprocess

class webServer ():
  
   serverPath = "framework/webserver/"
   platform = ""     
 
   def __init__(self, **kwargs):
      if "platform" in kwargs.keys():
            self.platform = kwargs['platform']

   def startup (self):
      if not os.path.isdir(self.serverPath+"temp/") or not os.path.exists(self.serverPath+"temp/"):
         os.mkdir( self.serverPath+"temp/", 0777 )
      if self.platform == "PI":
        subprocess.call(["lighttpd", "-f", "./{0}lighttpd_pi.conf".format(self.serverPath)])
      elif self.platform == "PC":
        subprocess.call(["lighttpd", "-f", "./{0}lighttpd_pc.conf".format(self.serverPath)])
      else:
         print "INVALID PLATFORM"
      #subprocess.call(["pwd"])
   
   def kill(self):
      file = open('framework/webserver/temp/lighttpd.pid', 'r') 
      subprocess.call(["kill", file.read()[:-1]])
      pass
