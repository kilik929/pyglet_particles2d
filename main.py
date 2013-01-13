#! python3 -OO $this
import pyglet
from pyglet.gl import *
import particles2D as P2D
from pyglet.window import key
from math import cos,sin,pi
import sys

class MainWindow(pyglet.window.Window):
    
    def __init__(self):
        #960x540?
        super(MainWindow,self).__init__(800,512,
            caption="Particles",
            visible=False,
            vsync=False)
            
        #self.hkey = pyglet.window.key.KeyStateHandler()
        #self.push_handlers(self.hkey)
        
        self.Fs = 60.0;
        self.Ts = 1/self.Fs;
        
        pyglet.clock.schedule_interval(self.update, self.Ts)
        
        x = self.width//2
        y = self.height//2
        self.texture = demotexture()
        self.texture.anchor_x = self.texture.width//2
        self.texture.anchor_y = self.texture.height//2
        self.emitter = P2D.PointEmitter(self.texture,x,y);
        self.emitter.set_fps(self.Fs)
        self.emitter.set_rate(100,1)
        self.emitter.set_direction(0,0);
        self.emitter.set_gravity(270,.5);
        self.emitter.set_speed(4,-2);
        self.emitter.set_scale([1,1.5]);
        self.emitter.set_lifetime(10000);
        self.emitter.allowReverseDirection(False);
        
        
        self.fpsdisp = pyglet.clock.ClockDisplay();
        self.fpsdisp.label = pyglet.font.Text(self.fpsdisp.label.font, '', color=(.5, .5, .5, .5), x=10, y=30)

        self.set_visible()
        
        self.label = pyglet.text.Label('Hello, world', 
                          font_name='Times New Roman', 
                          font_size=20,color=(0,0,0,255),
                          x=0, y=0)
        self.label2 = pyglet.text.Label('1-9: Change Demo', 
                          font_name='Times New Roman', 
                          font_size=20,color=(0,0,0,255),
                          x=0, y=self.height-20)
    def update(self,dt):
        self.emitter.update(dt);
        time = self.emitter.time
        count= sum( idx.N for _,idx in self.emitter.emit_idx )
        typ = self.emitter.__class__.__name__
        self.label.text = "TIME={0} TYPE={2} COUNT={1:4d} ".format(time,count,typ);
    def on_draw(self):
        self.clear();
        
        
        #self.texture.blit(self.emitter.x,self.emitter.y)
        self.label.draw()
        self.label2.draw()
        self.emitter.draw()
        self.fpsdisp.draw();
        
    def on_key_press(self,symbol, modifiers):
        x = self.width//2
        y = self.height//2
        w = self.width
        h = self.height
        if symbol == key.W:
            self.emitter.set_gravity(90,self.emitter.acceleration*self.emitter.fps);
        elif symbol == key.A:
            self.emitter.set_gravity(180,self.emitter.acceleration*self.emitter.fps);
        elif symbol == key.S:
            self.emitter.set_gravity(270,self.emitter.acceleration*self.emitter.fps);
        elif symbol == key.D:
            self.emitter.set_gravity(0,self.emitter.acceleration*self.emitter.fps);
        elif symbol == key.SPACE:
            self.emitter.emit(20)  
        elif symbol == key._1:
            # 3d fountain effect
            self.emitter = P2D.PointEmitter(self.texture,x,y);
            self.emitter.set_fps(self.Fs)
            self.emitter.set_rate(100,(5,10))
            self.emitter.set_direction(90,45);
            self.emitter.set_gravity(270,3);
            self.emitter.set_speed(2,.5);
            self.emitter.set_scale([1,1.5]);
        elif symbol == key._2:
            # warp speed / star field
            self.emitter = P2D.LineEmitter(self.texture,w,0,w,h);
            self.emitter.set_fps(self.Fs)
            self.emitter.set_rate(250,10);    
            #self.emitter.set_rate(100,5);    
            self.emitter.set_variable_speed(3,7);
            self.emitter.set_direction(180);
            self.emitter.set_lifetime(4000);
        elif symbol == key._3:
            # Sow, emit particles randomly of a rectangular region
            self.emitter = P2D.RectEmitter(self.texture,0,100,w,h+100);
            self.emitter.set_fps(self.Fs)
            self.emitter.set_rate(500,10);
            self.emitter.set_direction(270,0);
            self.emitter.set_speed(2,0);
            self.emitter.set_gravity(0,0);
            self.emitter.set_xzigzag(30,30,3);
            self.emitter.set_scale([2,.5])
            
            self.emitter.life=1000;
        elif symbol == key._4:   
            # emit particles randomly from a point x,y given by some function
            self.emitter = P2D.FuncEmitter(self.texture,x,y,demofunc,-200,200);
            self.emitter.set_fps(self.Fs)
            self.emitter.set_rate(500,20);
            self.emitter.set_speed(0,0);
            self.emitter.set_gravity(270,1);
            self.emitter.set_lifetime(23000);
        elif symbol == key._5:
            # emit particles on a non-smooth path
            path = [(x,y+100),(x+100,y),(x,y-100),(x-100,y),(x,y+100)]
            self.emitter = P2D.PathEmitter(self.texture,path,resolution=300,smooth=False);
            self.emitter.set_fps(self.Fs)
            self.emitter.set_rate(33,1);
            self.emitter.set_direction(0,360);
            self.emitter.set_speed(5,0);
        elif symbol == key._6:
            # particles that are emitted from a point on a smooth path
            #path = [(x,y+100),(x+100,y),(x,y-100),(x-100,y),(x,y+100)]
            path = [ (x,y), (x+300,y+200), (x-300,y+200), (x,y), (x+300,y-200), (x-300,y-200), (x,y)]
            self.emitter = P2D.PathEmitter(self.texture,path,resolution=200,smooth=True);
            self.emitter.set_rate(66,1);
            self.emitter.set_fps(self.Fs)
            self.emitter.set_gravity(270,.3);   
        elif symbol == key._7:
            # particles that converge to a point
            self.emitter = P2D.Absorber(self.texture,x,y);
            self.emitter.set_rate(250,2);
            self.emitter.set_fps(self.Fs)
            self.emitter.set_direction(90,45);
            self.emitter.set_gravity(270,3);
            self.emitter.set_speed(2,.5);
            self.emitter.set_scale([1,2]);
            self.emitter.set_rate(500,2);
        elif symbol == key._8:
            # openGl emitter, instead of using blit to draw each particle
            self.emitter = P2D.FastEmitter(self.texture,x,y);
            self.emitter.set_fps(self.Fs)
            self.emitter.set_rate(50,20) # 50, 30 is the first time i see significant frame rate drop. (~1500 particles)
            self.emitter.set_direction(90,45);
            self.emitter.set_gravity(270,3);
            self.emitter.set_speed(2,.5);
            self.emitter.set_scale([1,1.5]);   
        elif symbol == key._9:
            # zig zag particles in direction other than 0,90,180 or 270
            #self.emitter = P2D.LineEmitter(self.texture,.75*w,0,w,.25*h);
            self.emitter = P2D.PointEmitter(self.texture,w,h);
            self.emitter.set_fps(self.Fs)
            self.emitter.set_rate(250,1);    
            #self.emitter.set_rate(100,5);    
            zz = 25;
            direction = 135;
            xzz = zz*cos(direction*pi/180.0)
            yzz = zz*sin(direction*pi/180.0)
            self.emitter.set_speed(5);
            self.emitter.set_direction(direction);
            self.emitter.set_xzigzag(xzz,xzz);
            self.emitter.set_yzigzag(yzz,yzz);
            self.emitter.set_lifetime(2000);   
            
def demofunc(r):
    return (2*r, (100*sin(((r)/100.0)*pi)));
    
def demotexture():
    """
        return an ImageData object to use as a particle texture.
    """
    fmt = "BGRA";
    lfmt=4;
    w=h=9;
    data = [0,0,0,0]*(w*h);
    pitch = w*lfmt;
    for i in range(w):
        # draws a star, or an 'x' superimposed on an '+'
        data[i*pitch + i*lfmt + 3] = 255 # /
        data[i*pitch + (w-i-1)*lfmt + 3] = 255 # \
        data[(h//2)*pitch + i*lfmt + 3] = 255 # --
        data[i*pitch + (w//2)*lfmt + 3] = 255 # |
    if sys.version_info<(3,):    
        data = bytes(bytearray(data)) #2.7 is crazy
    else:
        data = bytes(data)
    imgdata = pyglet.image.ImageData(w,h,fmt,data,pitch)
    return  imgdata

if __name__ == "__main__":
    window = MainWindow();
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) 
    pyglet.gl.glClearColor(1, 1, 1, 1)
    pyglet.app.run()
    