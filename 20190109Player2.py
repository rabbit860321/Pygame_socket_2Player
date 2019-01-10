import pygame,sys,socket,random,time,math,datetime
import connection
from tkinter import *
from tkinter import ttk
from pygame.locals import *

MY_SERVER_HOST = '192.168.0.3'
MY_SERVER_PORT = 8888
OTHER_HOST = '192.168.0.2'
OTHER_PORT = 9999

FPS = 60

class Option:          #選單
    
    hovered = False
    
    def __init__(self, text, pos):
        self.text = text
        self.pos = pos
        self.set_rect()
        self.draw()
            
    def draw(self):
        self.set_rend()
        screen.blit(self.rend, self.rect)
        
    def set_rend(self):
        self.rend = menu_font.render(self.text, True, self.get_color())
        
    def get_color(self):
        if self.hovered:
            return (255, 255, 255)
        else:
            return (100, 100, 100)
        
    def set_rect(self):
        self.set_rend()
        self.rect = self.rend.get_rect()
        self.rect.topleft = self.pos

class Player():
    def __init__(self, pos, count,name):
        self.img = pygame.surface.Surface((50, 50))
        self.rect = self.img.get_rect(center = pos)
        self.count = count                         #點擊次數
        self.name = name

    def click(self, dir):
        if dir == 'count':
            self.count += 1
            
    def draw(self):
        screen.blit(self.img, self.rect)
            
    def make_data_package(self):
        count = str(self.count).rjust(4, '0')
        name = str(self.name)
        return count + name


class Player_1(Player):
    def __init__(self, pos=(960, 360)):
        super().__init__(pos,0,'')
        self.img.fill((255,0,0))
        text = menu_font.render(str(self.count),True,(255,255,255))
        screen.blit(text,self.rect)

class Player_2(Player):
    def __init__(self, pos=(320, 360)):
        super().__init__(pos,0,'')
        self.img.fill((0,0,255))
        text = menu_font.render(str(self.count),True,(255,255,255))
        screen.blit(text,self.rect)

def ip_value(ip):
    """ ip_value returns ip-string as integer """
    return int(''.join([x.rjust(3, '0') for x in ip.split('.')]))


def define_players():
    if ip_value(MY_SERVER_HOST) > ip_value(OTHER_HOST):
        me = Player_1()
        enemy = Player_2()
    else:
        me = Player_2()
        enemy = Player_1()
    return me, enemy     
          

def data_transfer():
    me_data = me.make_data_package()
    connection.send(me_data, OTHER_HOST, OTHER_PORT) # the send code

    enemy_data = server.receive() # the receive code
    
    enemy.count = int(enemy_data[:4])
    enemy.name = enemy_data[4:]


def update_screen():
    screen.fill((255,255,255))
    enemy.draw()
    me.draw()
    
    pygame.time.wait(50)


pygame.init()
pygame.mixer.quit() 

screen = pygame.display.set_mode((1280, 720))  #畫面大小
menu_font = pygame.font.Font('msjh.ttc', 40)   #字體

Game_title = menu_font.render('手 速 遊 戲',True,(255,255,255))
options = [Option("開始", (600, 200)), Option("排行榜", (580, 250)),Option("離開", (600, 300))]

win_text = menu_font.render('WIN!',True,(0,0,0))

me, enemy = define_players()
server = connection.Server(MY_SERVER_HOST, MY_SERVER_PORT)

Playing = False
Movie_stop = False
GAME_OVER = False

clock = pygame.time.Clock()

movie = pygame.movie.Movie('second.mpg')
movie_screen = pygame.Surface(movie.get_size()).convert()
movie.set_display(movie_screen)

timer = [0.0]
dt = 1.0

cost_second = [0.0]

while GAME_OVER == False:
    clock.tick(FPS)
    
    for event in pygame.event.get():    
        if event.type == pygame.QUIT:   #按下X
            pygame.quit()
            sys.exit()
            
    screen.fill((0, 0, 0))           #黑背景

    screen.blit(Game_title,(545,100))

    for option in options:                
        if option.rect.collidepoint(pygame.mouse.get_pos()):  #滑鼠移到字體變色
            option.hovered = True
        else:
            option.hovered = False
        option.draw()           #貼上選項


    if event.type == pygame.MOUSEBUTTONDOWN:         #選項滑鼠點擊
        if options[0].rect.collidepoint(pygame.mouse.get_pos()):  #按下開始

            root=Tk()              #GUI
            root.title("名字")
            root.geometry("320x240")
            label=Label(root, text="請輸入名字:")
            entry=Entry(root)

            def get_name():
                me.name = entry.get()
                root.destroy()
            
            label.pack()
            entry.pack()
            button=Button(root, text="OK", command=get_name).pack()
            
            root.mainloop()
            
            Playing = True
            
        if options[2].rect.collidepoint(pygame.mouse.get_pos()):  #按下離開
            pygame.quit()
            sys.exit()
    


    if Playing == True:
        
        data_transfer()
        update_screen()
        
        pygame.draw.rect(screen,(0,0,0),(640,0,5,450),0)       #中間線

        me_name = menu_font.render(str(me.name),True,(0,0,0))        #自己和對方的的名字
        enemy_name = menu_font.render(str(enemy.name),True,(0,0,0))

        me_count = menu_font.render(str(me.count),True,(255,255,255))      #自己和對方的點擊次數
        enemy_count = menu_font.render(str(enemy.count),True,(255,255,255))
        
        screen.blit(me_count,me.rect)
        screen.blit(enemy_count,enemy.rect)
        
        screen.blit(me_name,(me.rect.x,me.rect.y - 50))
        screen.blit(enemy_name,(enemy.rect.x,enemy.rect.y - 50))

        movie.play()
        screen.blit(movie_screen,(428,180))


        if not(movie.get_busy()):  #影片撥放完
            Movie_stop = True
        
        if Movie_stop == True:
            
            if me.count < 99 and enemy.count < 99:     
                timer[0] += dt     #計時
            elif me.count == 99 or enemy.count == 99:     #自己或對方達到99 停止計時
 
                if me.count == 99:                       #自己先達到99
                    screen.blit(win_text,(me.rect.x,me.rect.y-100))
                    
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            
                            pygame.quit()
                            sys.exit()
                    
                elif enemy.count == 99:                 #對方先達到99
                    screen.blit(win_text,(enemy.rect.x,enemy.rect.y-100))

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            
                            pygame.quit()
                            sys.exit()
                    
                    
            
            time_string = str(datetime.timedelta(seconds=int(timer[0])))   
            time_blit = menu_font.render(time_string,True,(0,0,0))
            time_blit_size = time_blit.get_size()
            screen.blit(time_blit,(575,500))                         #貼上時間
            
            pygame.draw.rect(screen,(255,255,255),(428,180,426,240),0) #影片撥放完畢蓋掉
            pygame.draw.rect(screen,(0,0,0),(640,0,5,450),0)
            
            
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONDOWN:                #點到自己的方塊
                    x,y = pygame.mouse.get_pos()
                    if(x > me.rect.x and x < me.rect.x + 50 and y > me.rect.y and y < me.rect.y + 50 and me.count < 99 and enemy.count != 99):  #count上限99
                        me.click('count')
                    
                if event.type == pygame.QUIT:   #按下X
                    pygame.quit()
                    sys.exit()
           
                    
    pygame.display.flip()
            


    
