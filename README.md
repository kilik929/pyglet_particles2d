pyglet_particles2d
==================

2D Particles Demo with pyglet (1.2alpha1) and Python 2.7/3.3

Features  
	* Works with python 2.7 and 3.3  
	* Create Particles with an initial speed and direction, gravity, and/or zigzag movement pattern 
    * Small memory footprint, instead of creating an object for each particle, only the creation time and number of particle is stored  	
	* different emitter classes, to emit from a point, line or rectangluar region.
	* Have the emitter follow a predefined path with an optional smoothing parameter
	* and other emitter types...
		
Other:  
    * Slowest part, as always, is drawing the particles.  
		FastEmitter uses OpenGl for a rough 10x speed up over direct blit.  
		Limiting frame rate (even if only for the emitter) will  
		save execution time.  
		
Roadmap:  
	* particles that change shape over time. Implemented for particles that use blit directly, not for the OpenGl case.  
	* particles that change color over time. Alpha and or color, could be done by dynamically creating new images based off of a reference image.  
	* For the direct blit method, it chokes at roughly 150 particles.  For the OpenGl approach, FastEmitter, it chokes in the 1500 particles range. 
		In one test using 1K particles; turning blit off runs at the same rate as the openGl FastEmitter. This seems to indicate that at that point the bottleneck is no longer in drawing the image.
	   
	   
	