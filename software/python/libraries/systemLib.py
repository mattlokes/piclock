class sysPrint( object ):
   ID=""
   debugEnable=False
  
   def __init__(self, ID, debugEnable):
      self.maxIDStr = 12
      self.ID = ID
      self.debugEnable = debugEnable
   
   def debug (self, string ):
      if self.debugEnable:
         print "{0} :: DEBUG :: {1}".format(self.ID.ljust(self.maxIDStr) , string)
   
   def rxDebug (self, rx ):
      if self.debugEnable:
         print "{0} :: DEBUG :: RX -- SRC: {1} -- TYPE: {2}".format(self.ID.ljust(self.maxIDStr) , rx['src'], rx['typ'])
   
   def info (self, string ):
      print "{0} :: INFO  :: {1}".format(self.ID.ljust(self.maxIDStr) , string)
   
   def error (self, string ):
      print "{0} :: ERROR :: {1}".format(self.ID.ljust(self.maxIDStr) , string)
