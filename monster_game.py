#!/usr/bin/env python3
import curses 
import time


# GLOBAL CONSTANTS
UP    = 0
DOWN  = 1
LEFT  = 2
RIGHT = 3

FACE_RIGHT = 0
FACE_LEFT = 1

MOUTH_X_OFFSET = 3
MOUTH_Y_OFFSET = 2

CHOMP_TIME = 85000
MISSILE_TIME = 30000
MISSILE_INCREMENT = 2


# MONSTER DRAWINGS
monster = [[  0, '|','(','0','(','0',')', 0],
           [  0,'/','v','v','v','v',  0,  0],
           ['/','l','^','^','^','^','\\','\\'],
           [  0,']','[',' ',' ',']','[',  0]]

monster_mouth = [[  0, '|','(','@','(','@',')', 0],
                 [  0,'/','v','v','v','v',  0,  0],
                 ['/','|','%',  0,  0,  0,  0,  0],
                 [  0,'l','^','^','^','^','}',  0],
                 [  0,']','[',' ',' ',']','[',  0]]


############################################################################
# FUNCTION: reverse_monster_chars
############################################################################
def reverse_monster_chars(char):

  output = char
  if output == '(':
    output = ')'
  elif output == ')':
    output = '('
  elif output == '/':
    output = '\\'
  elif output == '\\':
    output = '/'
  elif output == '[':
    output = ']'
  elif output == ']':
    output = '['

  return output


############################################################################
# CLASS: Monster
############################################################################
class Monster():


  def __init__(self,screen):
    self.screen = screen
    self.x = 0
    self.y = 0
    self.maxy, self.maxx = screen.getmaxyx()
    self.orientation = FACE_RIGHT
    self.shape = monster


  def __update_coord(self,direction):
    if direction == UP:
      self.y = (self.y - 1) % self.maxy
    elif direction == DOWN:
      self.y = (self.y + 1) % self.maxy
    elif direction == LEFT:
      self.x = (self.x - 1) % self.maxx
      if self.orientation == FACE_RIGHT:
        self.orientation = FACE_LEFT
    elif direction == RIGHT:
      self.x = (self.x + 1) % self.maxx
      if self.orientation == FACE_LEFT:
        self.orientation = FACE_RIGHT
      

  def move(self,direction):
    self.__overwrite_old()
    self.__update_coord(direction)
    self.draw()


  def draw(self):
    for y in range(len(self.shape)):
      for x in range(len(self.shape[y])):
        if self.orientation == FACE_LEFT:
          xind = len(self.shape[y]) - x - 1
        else:
          xind = x
        if self.shape[y][xind] != 0:
          xcoord = (self.x + x) % self.maxx
          ycoord = (self.y + y) % self.maxy
          output = self.shape[y][xind]
          if (self.orientation == FACE_LEFT):
            output = reverse_monster_chars(output)
          self.screen.addstr(ycoord,xcoord,output)
    self.screen.refresh()


  def __overwrite_old(self):
    for y in range(len(self.shape)):
      for x in range(len(self.shape[y])):
        xcoord = (self.x + x) % self.maxx
        ycoord = (self.y + y) % self.maxy
        self.screen.addstr(ycoord,xcoord,' ')
    self.screen.refresh()


  def fire_missile(self):
    return Missile(self.screen,self.x,self.y,self.orientation)


  def chomp(self):
    self.__overwrite_old()
    self.shape = monster_mouth
    self.draw()


  def unchomp(self):
    self.__overwrite_old()
    self.shape = monster
    self.draw()


############################################################################
# CLASS: Missile
############################################################################
class Missile():

  def __init__(self,screen,xcoord,ycoord,direction):
    self.screen = screen
    self.maxy, self.maxx = screen.getmaxyx()
    self.x = (xcoord + MOUTH_X_OFFSET) % self.maxx
    self.y = (ycoord + MOUTH_Y_OFFSET) % self.maxy
    self.direction = direction
    if direction == FACE_RIGHT:
      self.missile = '>'
    else:
      self.missile = '<'
    self.valid = True


  def draw(self):
    self.screen.addch(self.y,self.x,' ')
    self.__update()
    if not self.valid:
      return
    self.screen.addch(self.y,self.x,self.missile)
    self.screen.refresh()


  def __update(self):
    if self.direction == FACE_RIGHT:
      self.x += MISSILE_INCREMENT
    else:
      self.x -= MISSILE_INCREMENT
    if self.x < 0:
      self.valid = False
    if self.x >= self.maxx:
      self.valid = False


    
############################################################################
# MAIN:
############################################################################
def main(screen):

  # clear screen
  screen.clear()
  screen.nodelay(True)
  curses.curs_set(0)

  monster = Monster(screen) 
  monster.draw()

  chomp_count = 0
  missile_count = 0
  missiles = []

  while(True):

    try:
      char = screen.getch()
      # USE KEYPAD AND VIM BINDINGS 
      if (char == curses.KEY_LEFT) or (char == ord('h')):
          monster.move(LEFT)
      elif (char == curses.KEY_RIGHT) or (char == ord('l')):
          monster.move(RIGHT)
      elif (char == curses.KEY_DOWN) or (char == ord('j')): 
          monster.move(DOWN)
      elif (char == curses.KEY_UP) or (char == ord('k')): 
          monster.move(UP)
      elif (char == ord(' ')):
          monster.chomp()
          missiles.append(monster.fire_missile())
          chomp_count = 1
          missile_count = 1
      elif char == ord('q'): break

      if chomp_count == CHOMP_TIME:
        monster.unchomp()
        chomp_count = 0

      if chomp_count:
        chomp_count += 1
      if missile_count:
        missile_count += 1


      if missiles and (missile_count == MISSILE_TIME):
        for m in missiles:
          if not (m.valid):
            missiles.remove(m)
          else:
            m.draw()
        missile_count = 1


    except KeyboardInterrupt:
      break


if __name__ == "__main__":
  curses.wrapper(main)
