#! python3 -OO main.py
import random
import math
import sys
from collections import deque,namedtuple
from pyglet.gl import *
idxbase = namedtuple('idxbase',['N',])
idxpoint = namedtuple('idxpoint',['N','x','y'])


def factorial(n):
    r = 1
    for i in range(1, n+1):
        r *= i
    return r

def binomial(n, k):
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    return factorial(n) // (factorial(k) * factorial(n-k))

def linerp(bins,resolution):
    """
        return a new array of length 'rsolution'
        where each new bin value is linearly interpolated between bins
        in the origina; 'bins' list
    """
    lp = len(bins)-1
    d,m = divmod(resolution,lp)
    #---------------------------
    k = [d,]*lp # number of steps from one point to the next
    for i in range(m):
        k[i] += 1 # add up any rollover
    #---------------------------
    newbins = [];
    # note the enumerate intentionally drops the last bin in bins
    for i,(n,s1) in enumerate(zip(k,bins)):
        s2 = bins[i+1]
        for j in range(n):
            _s = s1 + (float(j)/n)*(s2-s1)
            newbins.append( _s )
    newbins.append(bins[-1])
    return newbins
    
class Emitter(object):
    """
        Base class for a Particle Emitter.
        
    """
    def __init__(self,texture):
        self.random = random.Random();
        self.texture = texture 
        self.seed = 0
        self.fps  = 60.0; # number of frames in a second
                          # this is separate from game logic so that execution rate can be easily modified.
        self.life = 2500 # float, number of millisecond that a particle should live
                         # it will live for life*fps/1000 frames.
                         
        self.lifetime = int(self.fps*self.life/1000.0);
        self.time = 0;  # ==int(delta*fps)
        self.delta = 0; # keeps track of floating point time in seconds elapsed
        self.gravity_direction = 270.0; # down!
        self.gaccely = 0; # down!
        self.gaccelx = 0; # down!
        self.acceleration = 0 # zero for no gravity_direction
        self.direction = 0; # in degrees
        self.spread    = 0; # in degrees
        self.impulse  = 0;  # initial speed of the particle 
                            # i would like to make this either of type
                            # int,float, or tuple, of (a,b)
                            # where impulse is a random number in the range a<=impulse<=b
        self.friction = 0; # how much the particle slows down at each step
        self.pstep = 15; # every 'pstep' call emit. seconds = pstep/fps
        self.pemit = 1;  # emit this number of particles per step
        # i need a boolean that prevents inverting speed i.e.
        #   if (speed - friction*age < 0) then 
        #   or : max_age = speed/friction # 
        #       after this value use max_age instead of age
        #       in speed calculations.
        #   so if it comes to a stop, it stops.
        self.allowInverseSpeed=False;
        
        self.emit_idx = deque(); # deques 'decks' pop faster
        self.xzig=0;
        self.xzag=0;
        self.xzzrate=1;
        self.yzig=0;
        self.yzag=0;
        self.yzzrate=1;
        self.oscale = 1; # memory for what the value was set as by the user
        self.scale = 1;  # scale to draw the particle at.
        
    def set_seed(self,seed):
        random.seed(seed);
        
    def rand(self): 
        return random.random();
        
    def get_xy(self):
        """return a new x,y pair to use as the initial position
           it is safe to use random here
        """
        pass
        
    def update(self,dt):
        # i don't currently expect integer any of the usual problems to occur
        # for continally incrementing numbers in python, like you would see in some typed language
        # there may be a 2.x error where int!=long.
        self.delta += dt
        self.time = int(self.delta*self.fps)
        # emit new particles ifpstep is non-zero, and  some amount of time has passed. 
        if self.pstep > 0 and self.time%self.pstep==0:
            if not isinstance(self.pemit,int):
                self.emit( self.pemit[0] + int(random.random()*self.pemit[1]) )
            else:
                self.emit( self.pemit )
        # remove any particles thats are too old    
        if self.emit_idx and self.emit_idx[0][0] < self.time - self.lifetime:
            self.emit_idx.popleft();

    def draw(self):
        #TODO somewhere i need to handle multiple idx values with the same time stamp
        # while not strictly required, if N is the same, all of the particles from both
        # sets will draw in the same locations.
        for ctime,idx in self.emit_idx:
            self.set_seed(self.seed+ctime)
            age = self.time - ctime
            if age >= 0: # if age is negative it has not been 'born' yet
                self._create_particles(age,idx)
    
    def emit(self,N,delay=0):
        """
            register a batch of N particles to be emitted at some time 
            N : number of particles to emit
            delay : (in milliseconds) how long to wait until
                    these particles should be emitted
            Thsi can be called asynchronously, or is called automatically whenever self.pstep is non zero        
                    
        """
        time = self.time + 1 + int(self.fps*(delay/1000.0));
        idx = idxbase(N)
        self.emit_idx.append((time,idx));
     
    def _create_particles(self,age,idx):
        """
            create all of the particles for a given idx
            if you have a custom idx format, this should be reimplemented.
        """
        for i in range(idx.N):
            x,y = self.get_xy();
            self._emit_one(x,y,age);
    
    def _emit_one(self,x,y,age=0):
        """
            age as an integer, indicating how long ago this
                particle was originally created, in frames ( age/fps ) = seconds
            draws a single particle with initial position (x,y)
        """
        if self.spread > 0:
            direction = self.direction + self.spread*self.rand() - self.spread/2.0
        else:
            direction = self.direction;
            
        direction = direction*math.pi/180.0 # convert to radians, i should do this ahead of time

        # note: for positive values 'n':    
        # (n)(n-1)//2 == sum(range(n))
        # (n)(n+1)//2 == sum(range(n+1))
        #-----------------------------------
        # position is : speed + (speed + friction) + (speed + 2*friction) + ... (speed + (age-1)*friction)
        #               (speed + 0*friction) + (speed + 1*friction) + (speed + 2*friction) + ... (speed + (age-1)*friction)
        #                speed*age + friction*(0+1+2..+(age-1))
        #                speed*age + friction*((age)*(age-1)//2 )
        if isinstance(self.impulse,tuple):
            # somewhat of a dirty hack to allow variable speed
            speed = self.impulse[0] + self.impulse[1]*self.rand()
        else:
            speed = self.impulse;
            
        tage = age;
        if not self.allowInverseSpeed and self.friction != 0:
            # prevent the particle from reverseing direction
            tmaxage = int(abs(speed/self.friction))
            tage = min(tmaxage,age)
        posvec = speed*tage + self.friction*((tage)*(tage-1)//2 )
        #-----------------------------------
        # calculate x/y zig zag values
        xzz=0;
        yzz=0;
        if self.xzig+self.xzag:
            n = int(age/self.xzzrate + (self.xzig+self.xzag)*self.rand() )
            t = n%(self.xzig+self.xzag)
            # if the zig and the zag are not the same, it will not end where it started
            xerr = n//(self.xzig+self.xzag)
            xzz = (-t if t<=self.xzig else -self.xzig+t-self.xzig) + xerr*(self.xzag-self.xzig);
        if self.yzig+self.yzag:
            n = int(age/self.yzzrate + (self.yzig+self.yzag)*self.rand() )
            t = n%(self.yzig+self.yzag)
            yerr = n//(self.yzig+self.yzag)
            yzz = (-t if t<=self.yzig else -self.yzig+t-self.yzig) + yerr*(self.yzag-self.yzig);
        #-----------------------------------
        # x86 has FSINCOS? also sin(x)^2 + cos(x)^2==1,
        # i wonder if there is any way to speed up these calls
        # there is some argument for sqrt + sign reoconstructing being slightly faster,
        # i do not think sin/cos is a bottleneck here.
        c = ( age*(age-1)//2 ) # accel constant for gravity_direction
        _y = posvec*math.sin(direction) + self.gaccely*c + yzz
        _x = posvec*math.cos(direction) + self.gaccelx*c + xzz
        #-----------------------------------
        if isinstance(self.scale,(int,float)):
            scale = self.scale;
        else:
            scale = self.scale[age]
        # by commenting out this line i can prove that
        # this is the framerate bottleneck
        # i don't see framerate drop until about 1500 articles, 
        self.texture.blit(int(x+_x),int(y+_y),width=self.texture.width*scale,height=self.texture.height*scale);
    
    def set_speed(self,speed,friction_per_second=0):
        self.impulse = speed
        self.friction = friction_per_second/self.fps
        
    def set_variable_speed(self,minspd,maxspd,friction_per_second=0):
        mn = min(minspd,maxspd); # one of you will screw this up, i know it
        mx = max(minspd,maxspd);
        self.impulse = (mn,mx-mn)
        self.friction = friction_per_second/self.fps
        
    def allowReverseDirection(self,b):
        """
            When true, if friction is negative, then the particle
            will not reverse direction, but come to a complete stop.
            
            TODO: naming on this is inconsistent, but i don't know which is better.
        """
        self.allowInverseSpeed = b;
    
    def set_gravity(self,direction,acceleration_per_second=0):
        """
            set the gravity_direction direction and accleration
        """
        self.gravity_direction = direction
        self.acceleration = acceleration_per_second/self.fps
        gdirection = self.gravity_direction*math.pi/180.0
        # i can avoid a sin/cos call at every step by precomputing the x/y magnitudes
        self.gaccelx = self.acceleration*math.cos(gdirection)
        self.gaccely = self.acceleration*math.sin(gdirection)
         
    def set_direction(self,direction,spread=0):
        """
            in degrees
            spread controls a random variable such that direction equals:
                direction = direction + (spread*random)-spread/2
            a spread of 0 means every particle will go the same direction    
        """
        self.direction = direction; # in degrees
        self.spread    = spread; # in degrees
    
    def set_xzigzag(self,zig,zag=None,rate=1):
        """
            causes the particle to zigzag on the x-axis
            zig one direction and zag back the other
            if zig!=zag, them some error will accumulate over time
            causeing the particle to slowly drift that direction
            TODO, rounded corners? what about arbitrary directions,
                such that it is not limited to one axis or the other?
                I bet, i can do some fancy math like in gravity_direction
                to produce the arbitrary direction zig zag
                where 
                    xzig=xzag=some_value*cos(direction)
                    yzig=yzag=some_value*sin(direction)
                See demo #9 in main.py    
        """
        self.xzig = abs(zig)
        self.xzag = abs(zag) if zag!=None else self.xzig
        self.xzzrate = rate;
    def set_yzigzag(self,zig,zag=None,rate=1):
        """
            causes the particle to zigzag on the y-axis
        """
        self.yzig = abs(zig)
        self.yzag = abs(zag) if zag!=None else self.yzig
        self.yzzrate = rate;
        
    def set_scale(self,scale):
        """
           scale can either be a float or a list/tuple of integers.
           if a list is given then the scale of the particle will
           be linearly interpolated across the life time of the particle
           e.g.
           self.setscale(2)
           self.set_scale([1,.5])
           self.set_scale([1,2,.5])
        """
        self.oscale=scale
        if isinstance(scale,(int,float)):
            self.scale = scale
            return;
            
        self.scale = linerp(scale,self.lifetime+1)

    def set_alpha(self,alpha):
        """
            todo, i would like to do something similar to what is done with scale
            ... doesnt look easy with pyglet.
            i might have to prerender all frames of the particle at varying alpha levels.
            if that is true, i would bother going to any deeper resolution than 16, or 32
            frames such that alpha = 255*(i/15) for i in range(16), as a memory vs accuracy tradeoff.
            i would probably have to open up the raw image data as BGRA, and manually set the alpha channel
            
            the last thing to consider:
                change this to set_color,
            and allow linear interpolation over R,G,B and A
            in some fancy user friendly way
        """
        pass
      
    def set_rate(self,rate_ms,count=1):
        """
            set how many particles to emit and how often
            if count is some kind of an indexable container, a random 
            number of particels will be emitted at every pstep, equal to
                count[0] + random()*count[1]
            TODO random step size
            of rate_ms is zero, pstep will be zero, causing no particles to be emited at a regular rate
        """
        self.pstep = 0 if rate_ms == 0 else max(1, int((rate_ms/1000.0)*self.fps) )
        self.pemit = count
     
    def set_fps(self,fps):
        # note that you will also need to reinterpolate scale and others
        self.fps = fps
        self.lifetime = int(self.fps*self.life/1000.0);
        self.set_scale(self.oscale)
        
    def set_lifetime(self,milliseconds):
        # note that you will also need to reinterpolate scale and others
        self.life = milliseconds
        self.lifetime = int(self.fps*self.life/1000.0);
        self.set_scale(self.oscale)
        
class PointEmitter(Emitter):
    def __init__(self,texture,x,y):
        super(PointEmitter,self).__init__(texture);
        self.x = x
        self.y = y
        
    def get_xy(self):
        return self.x,self.y;
            
class LineEmitter(Emitter):
    def __init__(self,texture,x1,y1,x2,y2):
        super(LineEmitter,self).__init__(texture); 
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2       
        self.m = 0 if (x2-x1)==0 else (y2-y1)/(x2-x1)
        self.b = y1-self.m*x1
        
    def get_xy(self):
        
        if (self.x2-self.x1)==0:
            yp =  self.y1 + (self.y2-self.y1)*self.rand()
            return self.x1,yp;
        xp =  self.x1 + (self.x2-self.x1)*self.rand()    
        return xp,self.m*xp + self.b;   
        
class RectEmitter(Emitter):
    def __init__(self,texture,x1,y1,x2,y2):
        super(RectEmitter,self).__init__(texture); 
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2       

    def get_xy(self):
        xp =  self.x1 + (self.x2-self.x1)*self.rand()
        yp =  self.y1 + (self.y2-self.y1)*self.rand()
        return xp,yp;    
        
class FuncEmitter(PointEmitter):
    def __init__(self,texture,x,y,func,start=0,end=100):
        """ randomly emit at position:
                x,y = func(r) for start <= r <= end;
        """
        super(FuncEmitter,self).__init__(texture,x,y);  
        self.func = func
        self.rs = min(start,end)
        self.re = max(start,end)
        
        
    def get_xy(self):
        rp =  self.rs + (self.re-self.rs)*self.rand()
        _x,_y = self.func(rp);      
        return  self.x+_x,self.y+_y;
        
class PathEmitter(Emitter):
    """
        This Emitter takes a path as a list-of-points as tuples of (x,y)
        The emitter will then follow this path and whenever emit is called
        that location is saved and particles will be emitted from that position.
    
        this actually isnt far removed from the FuncEmitter
        However, remembering the position of where particles
        were first emited allows for some cool things down the road,
        such as anchored emitters.
    """
    def __init__(self,texture,path,resolution=100,smooth=False):
        """
            path : as a list of points, [(x1,y1),(x2,y2),...]
            the points will be linearly interpolated between using
            resolution. Note that resolution also controls
            how long it takes to traverse the path, at resolution/fps seconds.
            
            if spline is true, a spline curve will be fit
            to the points in path. TODO, this would be fun
            but i don't know how yet.
            
            TODO: should i derive from point emitter, and allow relative paths?
        """
        super(PathEmitter,self).__init__(texture)#path[0][0],path[0][1]); 
        self.opath = path
        self.path = self.interp_path(path,resolution,smooth);
        self.resolution = resolution
            
    def _create_particles(self,age,idx):
        for i in range(idx.N):
            self._emit_one(idx.x,idx.y,age);   
            
    def emit(self,N,delay=0):
        
        time = self.time + 1 + int(self.fps*(delay/1000.0));
        x,y = self.path[self.time%self.resolution]
        idx = idxpoint(N,x,y)
        
        self.emit_idx.append((time,idx));
        
    def interp_path(self,path,resolution,smooth=False):
        if smooth:
            return self._smooth(path,resolution);
        return self._linerp(path,resolution)
        
    def _smooth(self,path,resolution):
        newpath = []
        N = len(path)-1
        # bezier curve, from wikipedia
        for i in range(resolution):
            t = i/float(resolution-1);
            x=y=0
            for j,p in enumerate(path):
                k=binomial(N,j)*float((1-t)**(N-j))*(t**j)
                x += k*(p[0])
                y += k*(p[1])
            newpath.append( (x,y) )
        return newpath          
        
    def _linerp(self,path,resolution):
        res = resolution - 1
        lp = len(path)-1
        d,m = res//lp,res%lp
        #---------------------------
        k = [d,]*lp # number of steps from one point to the next
        for i in range(m):
            k[i] += 1 # add up any rollover
        #---------------------------
        newpath = [];
        for i,(n,p1) in enumerate(zip(k,path)):
            p2 = path[i+1]
            for j in range(n):
                _x = p1[0] + (float(j)/n)*(p2[0]-p1[0]) # float needed for 2.x support
                _y = p1[1] + (float(j)/n)*(p2[1]-p1[1])
                newpath.append( (_x,_y) )
        newpath.append(path[-1])
        return newpath;
        
    def set_resolution(self,res):
        self.path = self.interp_path(self.opath,res);
        self.resolution = res;
  
class Absorber(PointEmitter):
    """
        inverts the age parameter so that it appears as though
        the particles are converging to a point instead of being emitted from that point.
    """
    def _create_particles(self,age,idx):
        for i in range(idx.N):
            x,y = self.get_xy();
            self._emit_one(x,y,self.lifetime-age);   
 
class FastEmitter( PointEmitter ):
    """
        OpenGl particle code ripped from the DeltaV game someone posted in the pyglet-users group
            I'm sure I could find the link again for proper credit if I searched...
    """
    def draw(self):
        # on my computer the FPS hovers around 80-200 (bounces around a lot)
        # when the number of particles reach 1500, it doesnt seem to go over 120ish
        # when the number of particles reach 2000 it doesnt seem to go over 60
        # using this method i see know way to do individual particle scaling, as with the (slower) direct blit method.
        # With both methods i see know way of doing alpha blending or color interpolation in real time for individual particles.
        tex = self.texture.get_texture();
        glDepthMask(False)

        glPushAttrib(GL_ENABLE_BIT | GL_CURRENT_BIT)
        glColor3f(1, 1, 1)
        glDisable(GL_LIGHTING)

        glEnable(GL_BLEND)
        glEnable(tex.target)
        pointsize=self.texture.width
        minsize=self.texture.width
        point_size = GLfloat()
        glGetFloatv(GL_POINT_SIZE_MAX_ARB, point_size)
        glBindTexture(tex.target, tex.id)
        glPointSize(pointsize) # what does this do?
        glPointParameterfvARB(GL_POINT_DISTANCE_ATTENUATION_ARB,
            (GLfloat * 3)(0, 0, .01))
        glPointParameterfARB(GL_POINT_SIZE_MIN_ARB, minsize) # this seems to be req'd
        glTexEnvf(GL_POINT_SPRITE_ARB, GL_COORD_REPLACE_ARB, GL_TRUE)
        glEnable(GL_POINT_SPRITE_ARB)

        self.varray = []
        for ctime,idx in self.emit_idx:
            self.set_seed(self.seed+ctime)
            age = self.time - ctime
            if age >= 0:
                self._create_particles(age,idx)# populate the varray
                
        nump = len(self.varray)//3;
        self.varray = (GLfloat * len(self.varray))(*self.varray)
        
        glPushClientAttrib(GL_CLIENT_VERTEX_ARRAY_BIT)
        glVertexPointer(3, GL_FLOAT, 0, self.varray)
        glEnableClientState(GL_VERTEX_ARRAY)
        glDrawArrays(GL_POINTS, 0, nump)
        glPopClientAttrib()
        
        glPopAttrib()

        glDepthMask(True)
        
    def _emit_one(self,x,y,age=0):
        """
            age as an integer, indicating how long ago this
                particle was originally created, in frames ( age/fps ) = seconds
            draws a single particle with initial position (x,y)
            position is a function of direction
        """
        if self.spread > 0:
            direction = self.direction + self.spread*self.rand() - self.spread/2.0
        else:
            direction = self.direction;
        direction = direction*math.pi/180.0
        #-----------------------------------
        if isinstance(self.impulse,tuple):
            speed = self.impulse[0] + self.impulse[1]*self.rand()
        else:
            speed = self.impulse;
        tage = age;
        if not self.allowInverseSpeed and self.friction != 0:
            tage = min(int(abs(speed/self.friction)),age)
        posvec = speed*tage + self.friction*((tage)*(tage-1)//2 )
        #-----------------------------------
        xzz=0;
        yzz=0;
        if self.xzig+self.xzag:
            n = int(age/self.xzzrate + (self.xzig+self.xzag)*self.rand() )
            t = n%(self.xzig+self.xzag)
            # if the zig and the zag are not the same, it will not end where it started
            xerr = n//(self.xzig+self.xzag)
            xzz = (-t if t<=self.xzig else -self.xzig+t-self.xzig) + xerr*(self.xzag-self.xzig);
        if self.yzig+self.yzag:
            n = int(age/self.yzzrate + (self.yzig+self.yzag)*self.rand() )
            t = n%(self.yzig+self.yzag)
            xerr = n//(self.yzig+self.yzag)
            xzz = (-t if t<=self.yzig else -self.yzig+t-self.yzig) + xerr*(self.yzag-self.yzig);
        #-----------------------------------
        c = ( age*(age-1)//2 ) # accel constant for gravity_direction
        _y = posvec*math.sin(direction) + self.gaccely*c + yzz
        _x = posvec*math.cos(direction) + self.gaccelx*c + xzz
        self.varray += [int(x+_x),int(y+_y),0];


if __name__ == "__main__":
    pass
    #s = 4
    #f = -.5
    #g=270
    #a=.1
    #for age in range(20):
    #    pos = s*age + f*fsum(age)
    #    gra = .1
    #    print pos
    #speed = base + 0*a + 1*a + 2a + 3a... 
    
    #em = PointEmitter(None,0,0);
    #for i in range(10):
    #    print em.rand();