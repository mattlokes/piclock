#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
#	
#                      Name:   ClockAppConsts
#                    Author:   Matt
#
#               Description:   Clock Application Constants 
#
#=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

PRE_TIME =[
      [{'x':1,'y':0,'len':3},{'x':7,'y':0,'len':4},{'x':13,'y':0,'len':2}], #The Time Is
      [{'x':6,'y':0,'len':2},{'x':13,'y':0,'len':2}],  #It is
      [{'x':9,'y':4,'len':1},{'x':9,'y':5,'len':1},{'x':9,'y':6,'len':1},{'x':9,'y':7,'len':1}]
      #Matt
         ]

MIN_NUM =[
         [{'x':0,'y':0,'len':0}], #0
         [{'x':7,'y':3,'len':3}], #1
         [{'x':12,'y':2,'len':3}], #2
         [{'x':1,'y':3,'len':5}], #3
         [{'x':6,'y':2,'len':4}], #4
         [{'x':11,'y':1,'len':4}], #5
         [{'x':0,'y':5,'len':3}], #6
         [{'x':11,'y':3,'len':5}], #7
         [{'x':0,'y':2,'len':5}], #8
         [{'x':10,'y':4,'len':4}], #9
         [{'x':7,'y':1,'len':3}], #10
         [{'x':10,'y':5,'len':6}], #11
         [{'x':3,'y':5,'len':6}], #12
         [{'x':1,'y':6,'len':4},{'x':5,'y':6,'len':4}], #13
         [{'x':6,'y':2,'len':4},{'x':5,'y':6,'len':4}], #14
         [{'x':1,'y':4,'len':7}], #QUARTER
         [{'x':0,'y':5,'len':3},{'x':5,'y':6,'len':4}], #16
         [{'x':11,'y':3,'len':5},{'x':5,'y':6,'len':4}], #17
         [{'x':0,'y':2,'len':4},{'x':5,'y':6,'len':4}], #18
         [{'x':10,'y':4,'len':4},{'x':5,'y':6,'len':4}], #19
         [{'x':0,'y':1,'len':6}], #20
         [{'x':7,'y':3,'len':3},{'x':0,'y':1,'len':6}], #21
         [{'x':12,'y':2,'len':3},{'x':0,'y':1,'len':6}], #22
         [{'x':1,'y':3,'len':5},{'x':0,'y':1,'len':6}], #23
         [{'x':6,'y':2,'len':4},{'x':0,'y':1,'len':6}], #24
         [{'x':11,'y':1,'len':4},{'x':0,'y':1,'len':6}], #25
         [{'x':0,'y':5,'len':3},{'x':0,'y':1,'len':6}], #26
         [{'x':11,'y':3,'len':5},{'x':0,'y':1,'len':6}], #27
         [{'x':0,'y':2,'len':5},{'x':0,'y':1,'len':6}], #28
         [{'x':10,'y':4,'len':4},{'x':0,'y':1,'len':6}], #29
         [{'x':10,'y':6,'len':4}] #HALF
         ]

MIN_WORDS =[
           [{'x':2,'y':7,'len':7},{'x':11,'y':7,'len':4}], #MINUTES PAST
           [{'x':2,'y':7,'len':7},{'x':1,'y':8,'len':2}],  #MINUTES TO
           [{'x':11,'y':7,'len':4}],                       #PAST
           [{'x':1,'y':8,'len':2}],                        #TO
           [{'x':2,'y':7,'len':6},{'x':11,'y':7,'len':4}], #MINUTE PAST
           [{'x':2,'y':7,'len':6},{'x':1,'y':8,'len':2}]   #MINUTE TO
           ]

HOUR_NUM =[
           [{'x':9,'y':8,'len':6}],   #0
           [{'x':4,'y':8,'len':3}],   #1
           [{'x':6,'y':10,'len':3}],  #2
           [{'x':0,'y':9,'len':5}],   #3
           [{'x':11,'y':10,'len':4}], #4
           [{'x':2,'y':12,'len':4}],  #5
           [{'x':2,'y':10,'len':3}],  #6
           [{'x':7,'y':9,'len':5}],   #7
           [{'x':1,'y':11,'len':5}],  #8
           [{'x':11,'y':9,'len':4}],  #9
           [{'x':9,'y':12,'len':3}],  #10
           [{'x':8,'y':11,'len':6}],  #11
           [{'x':9,'y':8,'len':6}]    #12
          ]

TOD_WORDS =[
       [{'x':13,'y':12,'len':2}],                                               #AM
       [{'x':0,'y':14,'len':2}],                                                #PM
       [{'x':1,'y':13,'len':2},{'x':5,'y':13,'len':3},{'x':0,'y':15,'len':7}],  #IN THE MORNING
       [{'x':1,'y':13,'len':2},{'x':5,'y':13,'len':3},{'x':3,'y':14,'len':9}],  #IN THE AFTERNOON
       [{'x':1,'y':13,'len':2},{'x':5,'y':13,'len':3},{'x':9,'y':13,'len':7}],  #IN THE EVENING
       [{'x':4,'y':13,'len':2},{'x':11,'y':15,'len':5}],                        #AT NIGHT
       [{'x':8,'y':14,'len':4}],                                                #NOON
       [{'x':8,'y':15,'len':8}]                                                 #MIDNIGHT
           ]

DIGNUM_5_3 = [
               [ 1,1,1,   #0
                 1,0,1,
                 1,0,1,
                 1,0,1,
                 1,1,1],
               [ 0,1,0,   #1
                 1,1,0,
                 0,1,0,
                 0,1,0,
                 1,1,1],
               [ 1,1,1,   #2
                 0,0,1,
                 1,1,1,
                 1,0,0,
                 1,1,1],
               [ 1,1,1,   #3
                 0,0,1,
                 1,1,1,
                 0,0,1,
                 1,1,1],
               [ 1,0,1,   #4
                 1,0,1,
                 1,1,1,
                 0,0,1,
                 0,0,1],
               [ 1,1,1,   #5
                 1,0,0,
                 1,1,1,
                 0,0,1,
                 1,1,1],
               [ 1,1,1,   #6
                 1,0,0,
                 1,1,1,
                 1,0,1,
                 1,1,1],
               [ 1,1,1,   #7
                 0,0,1,
                 0,0,1,
                 0,0,1,
                 0,0,1],
               [ 1,1,1,   #8
                 1,0,1,
                 1,1,1,
                 1,0,1,
                 1,1,1],
               [ 1,1,1,   #9
                 1,0,1,
                 1,1,1,
                 0,0,1,
                 0,0,1]
               ]

DIGNUM_8_5 = [
               [ 1,1,1,1,1,   #0
                 1,1,1,1,1,
                 1,1,0,1,1,
                 1,1,0,1,1,
                 1,1,0,1,1,
                 1,1,0,1,1,
                 1,1,1,1,1,
                 1,1,1,1,1],
               [ 0,0,1,1,0,   #1
                 1,1,1,1,0,
                 1,1,1,1,0,
                 0,0,1,1,0,
                 0,0,1,1,0,
                 0,0,1,1,0,
                 1,1,1,1,1,
                 1,1,1,1,1],
               [ 1,1,1,1,1,   #2
                 1,1,1,1,1,
                 0,0,0,1,1,
                 1,1,1,1,1,
                 1,1,1,1,1,
                 1,1,0,0,0,
                 1,1,1,1,1,
                 1,1,1,1,1],
               [ 1,1,1,1,1,   #3
                 1,1,1,1,1,
                 0,0,0,1,1,
                 1,1,1,1,1,
                 1,1,1,1,1,
                 0,0,0,1,1,
                 1,1,1,1,1,
                 1,1,1,1,1],
               [ 1,1,0,1,1,   #4
                 1,1,0,1,1,
                 1,1,0,1,1,
                 1,1,1,1,1,
                 1,1,1,1,1,
                 0,0,0,1,1,
                 0,0,0,1,1,
                 0,0,0,1,1],
               [ 1,1,1,1,1,   #5
                 1,1,1,1,1,
                 1,1,0,0,0,
                 1,1,1,1,1,
                 1,1,1,1,1,
                 0,0,0,1,1,
                 1,1,1,1,1,
                 1,1,1,1,1],
               [ 1,1,1,1,1,   #6
                 1,1,1,1,1,
                 1,1,0,0,0,
                 1,1,1,1,1,
                 1,1,1,1,1,
                 1,1,0,1,1,
                 1,1,1,1,1,
                 1,1,1,1,1],
               [ 1,1,1,1,1,   #7
                 1,1,1,1,1,
                 0,0,0,1,1,
                 0,0,0,1,1,
                 0,0,0,1,1,
                 0,0,0,1,1,
                 0,0,0,1,1,
                 0,0,0,1,1],
               [ 1,1,1,1,1,   #8
                 1,1,1,1,1,
                 1,1,0,1,1,
                 1,1,1,1,1,
                 1,1,1,1,1,
                 1,1,0,1,1,
                 1,1,1,1,1,
                 1,1,1,1,1],
               [ 1,1,1,1,1,   #9
                 1,1,1,1,1,
                 1,1,0,1,1,
                 1,1,1,1,1,
                 1,1,1,1,1,
                 0,0,0,1,1,
                 0,0,0,1,1,
                 0,0,0,1,1],
               [ 0,0,0,0,0,   #:
                 0,1,1,0,0,
                 0,1,1,0,0,
                 0,0,0,0,0,
                 0,0,0,0,0,
                 0,1,1,0,0,
                 0,1,1,0,0,
                 0,0,0,0,0]
               ]
