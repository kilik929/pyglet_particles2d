pyglet_particles2d
==================

2D Particles Demo with pyglet and Python 2/3

Features
	Works with python 2.7 and 3.3
	Create Particles with an initial speed and direction, gravity, 
		and/or zigzag movement pattern
	Small memory footprint, instead of creating an object for each particle,
		only the creation time and number of particle is stored
		
Other:
    Slowest part, as always, is drawing the particles.
		FastEmitter uses OpenGl for a rouch 10x speed up over direct blit.
		Limiting frame rate (even if only for the emitter) will
		save execution time.
		
Roadmap:
	particles that change shape over time.
		Implemented for particles that use blit directly, not for the OpenGl 
		case.
	particles that change color over time.
		Alpha and or color, could be done by dynamically creating new images 
		based off of a reference image.
	For the direct blit method, it chokes at roughly 150 particles,
		For the OpenGl approach, FastEmitter, it chokes in the 1500 paticles 
		range.
	
	
	
