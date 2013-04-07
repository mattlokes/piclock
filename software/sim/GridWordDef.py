
class GridWordDef:
      #THE TIME IS     T     H     E     T     I     M    E       I      S
      the_time_is = [[1,0],[2,0],[3,0],[6,0],[7,0],[8,0],[9,0],[13,0],[14,0]]
      #----------------------------------------------------------
      #MIN (ONE)   O     N     E
      min_one = [[7,1],[8,1],[9,1]]
      #MIN (TWO)   T       W      O
      min_two = [[10,1],[11,1],[12,1]]
      #MIN (THREE)   T     H    R     E     E
      min_three = [[0,2],[1,2],[2,2],[3,2],[4,2]]
      #MIN (FOUR)   F     O     U     R
      min_four = [[6,2],[7,2],[8,2],[9,2]]
      #MIN (FIVE)   F       I     V       E
      min_five = [[11,2],[12,2],[13,2],[14,2]]
      #MIN (SIX)
      min_six = [[8,3],[9,3],[10,3]]
      #MIN (SEVEN)
      min_seven = [[11,3],[12,3],[13,3],[14,3],[15,3]]
      #MIN (EIGHT)
      min_eight = [[0,4],[1,4],[2,4],[3,4],[4,4]]
      #MIN (EIGH)
      min_eigh = [[0,4],[1,4],[2,4],[3,4]]
      #MIN (NINE)
      min_nine = [[7,4],[8,4],[9,4],[10,4]]
      #MIN (TEN)
      min_ten = [[12,4],[13,4],[14,4]]
      #MIN (ELEVEN)
      min_eleven = [[10,5],[11,5],[12,5],[13,5],[14,5],[15,5]]
      #MIN (TWELEVE)
      min_tweleve = [[0,6],[1,6],[2,6],[3,6],[4,6],[5,6]]
      #MIN (THIR)
      min_thir = [[1,5],[2,5],[3,5],[4,5]]
      #MIN (TEEN)
      min_teen = [[5,5],[6,5],[7,5],[8,5]]
      #QUARTER
      quarter = [[0,3],[1,3],[2,3],[3,3],[4,3],[5,3],[6,3]]
      #MIN (TWENTY)
      min_twenty = [[0,1],[1,1],[2,1],[3,1],[4,1],[5,1]]
      #HALF
      half = [[1,7],[2,7],[3,7],[4,7]]
      #MINUTES
      minutes = [[9,6],[10,6],[11,6],[12,6],[13,6],[14,6],[15,6]]
      #MINUTE
      minute = [[9,6],[10,6],[11,6],[12,6],[13,6],[14,6]]
      #PAST
      past = [[8,7],[9,7],[10,7],[11,7]]
      #TOO
      too = [[5,7],[6,7],[7,7]]
      #----------------------------------------------------------
      #HOUR (ONE)
      hour_one = [[13,7],[14,7],[15,7]]
      #HOUR (TWO)
      hour_two = [[0,8],[1,8],[2,8]]
      #HOUR (THREE)
      hour_three = [[0,11],[1,11],[2,11],[3,11],[4,11]]
      #HOUR (FOUR)
      hour_four = [[11,8],[12,8],[13,8],[14,8]]
      #HOUR (FIVE)
      hour_five = [[1,9],[2,9],[3,9],[4,9]]
      #HOUR (SIX)
      hour_six = [[6,9],[7,9],[8,9]]
      #HOUR (SEVEN)
      hour_seven = [[10,9],[11,9],[12,9],[13,9],[14,9]]
      #HOUR (EIGHT)
      hour_eight = [[0,10],[1,10],[2,10],[3,10],[4,10]]
      #HOUR (NINE)
      hour_nine = [[6,10],[7,10],[8,10],[9,10]]
      #HOUR (TEN)
      hour_ten = [[11,10],[12,10],[13,10]]
      #HOUR (ELEVEN)
      hour_eleven = [[4,8],[5,8],[6,8],[7,8],[8,8],[9,8]]
      #HOUR (TWELEVE)
      hour_tweleve = [[5,11],[6,11],[7,11],[8,11],[9,11],[10,11],[11,11]]
      #----------------------------------------------------------
      #IN THE
      in_the = [[12,11],[13,11],[0,12],[1,12],[2,12]]
      #AT
      at = [[14,11],[15,11]]
      #MORNING
      morning = [[9,12],[10,12],[11,12],[12,12],[13,12],[14,12],[15,12]]
      #AFTERNOON
      afternoon = [[0,13],[1,13],[2,13],[3,13],[4,13],[5,13],[6,13],[7,13],[8,13]]
      #EVENING
      evening = [[9,13],[10,13],[11,13],[12,13],[13,13],[14,13],[15,13]] 
      #NIGHT
      night = [[4,12],[5,12],[6,12],[7,12],[8,12]]
      ##############################################
      # Conversion Functions

      def time_conv(self,timestr):
        tmparr = []
        tmparr = tmparr + self.min_str_conv(timestr[2:4])
        if int(timestr[2:4]) > 30:
           if (int(timestr[0:2])+1) > 12:
               timestr = '01' + timestr[2:]
           elif (int(timestr[0:2])+1) < 10:
               timestr = '0' + str(int(timestr[0:2])+1) + timestr[2:]
           else:
               timestr = str(int(timestr[0:2])+1) + timestr[2:]
        print timestr
        tmparr = tmparr + self.hour_str_conv(timestr[0:2])
        return tmparr

      def min_str_conv(self,min_str):
          tmparr = []
          mins = int(min_str)
          if mins == 0:
              pass
          elif mins == 30:
             tmparr= tmparr + self.half + self.past
          elif mins > 30:
             mins = 60 - mins #MINS TOO
             ret = self._min_num_conv(mins)
             tmparr = tmparr + ret
             if mins == 15:
                 pass
             elif mins == 1:
                 tmparr = tmparr + self.minute
             else:
                 tmparr = tmparr + self.minutes
             tmparr = tmparr + self.too         
          else:
             ret = self._min_num_conv(mins)
             tmparr = tmparr + ret
             if mins == 1:
                 tmparr = tmparr + self.minute
             else:
                 tmparr = tmparr + self.minutes
             tmparr = tmparr + self.past        
          return tmparr

      def _min_num_conv(self,mins_int):
          minstr = str(mins_int)
          if minstr[0:1] == '0':
              return self.min_first_dec[mins_int]
          elif minstr[0:1] == '1':
              return self.min_sec_dec[mins_int-10]
          elif minstr[0:1] == '2':
              return self.min_third_dec[mins_int-20]
          else:
              print "PANIC PANIC PANIC PANIC PANIC!"

      def hour_str_conv(self,hour_str):
          hours = int(hour_str)
          return self.hour_arr[hours]

      min_first_dec = [0,min_one,min_two,min_three,min_four,min_five,min_six,\
                       min_seven,min_eight,min_nine]

      min_sec_dec   = [min_ten,min_eleven,min_tweleve,min_thir+min_teen,\
                       min_four+min_teen,quarter,min_six+min_teen,\
                       min_seven+min_teen,min_eigh+min_teen,min_nine+min_teen]

      min_third_dec = [min_twenty,min_twenty+min_one,min_twenty+min_two,\
                       min_twenty+min_three,min_twenty+min_four,\
                       min_twenty+min_five,min_twenty+min_six,\
                       min_twenty+min_seven,min_twenty+min_eight,\
                       min_twenty+min_nine]
      hour_arr = [0,hour_one,hour_two,hour_three,hour_four,hour_five,hour_six,\
                       hour_seven,hour_eight,hour_nine,hour_ten,hour_eleven,hour_tweleve]
      ###############################################
      # Test Iterator
      iterator = [the_time_is,min_one,min_two,min_three,min_four,min_five,\
                  min_six,min_seven,min_eight,min_nine,min_ten,min_eleven,\
                  min_tweleve,min_thir,min_teen,quarter,min_twenty,half,\
                  minutes,minute,past,too,hour_one,hour_two,hour_three,\
                  hour_four,hour_five,hour_six,hour_seven,hour_eight,\
                  hour_nine,hour_ten,hour_eleven,hour_tweleve,in_the,at,\
                  morning,afternoon,evening,night]

