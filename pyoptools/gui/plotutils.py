#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from numpy import array, pi,sqrt, degrees
import Image as PIL
from StringIO import StringIO
from IPython.core.display import Image
from pylab import plot, axis

from OpenGL.GL import *
from OpenGL.GLU import *

from OpenGL import arrays
try:
	from OpenGL.platform import (CurrentContextIsValid, OSMesaCreateContext,
    OSMesaMakeCurrent, OSMesaDestroyContext)

except:
	print "need OSMesa installed, and the following environment variable"
	print "export PYOPENGL_PLATFORM=osmesa"

from pyoptools.raytrace.system import System
from pyoptools.raytrace.component import Component
from pyoptools.raytrace.surface import Surface
from pyoptools.misc.pmisc import wavelength2RGB,cross
	
##Nota toca exportar la veriable de ambiente 
## export PYOPENGL_PLATFORM=osmesa

def implot(buf):
    h, w, c = buf.shape
    image = PIL.fromstring( "RGBA", (w, h), buf )
    image = image.transpose( PIL.FLIP_TOP_BOTTOM)
    temppng=StringIO()
    image.save(temppng, "JPEG" )
    data=temppng.getvalue()
    temppng.close()
        #~ print 'Saved image to %s'% (os.path.abspath( filename))
        #~ return image
    return Image(data,embed=True,format=u"jpeg")

def draw_sys(os):
    if os != None:
        for i in os.prop_ray:
            draw_ray(i)
        #Draw Components
        for comp in os.complist:
            C,P,D=comp
            draw_comp(C,P,D)
                  
def draw_comp(C,P,D):
    
    #C,P,D = comp
    #glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glTranslatef(P[0],P[1],P[2])
    glRotatef(180*D[2]/pi,0.0,0.0,1.0)
    glRotatef(180*D[1]/pi,0.0,1.0,0.0)
    glRotatef(180*D[0]/pi,1.0,0.0,0.0)
    
    if isinstance(C, Component):
        for surf in C.surflist:
            S, P, D=surf
            draw_surf(S, P, D)
    elif isinstance(C, System):
        for comp in C.complist:
            C,P,D=comp
            draw_comp(C,P,D)
    glPopMatrix()
 
def draw_surf(surf, P, D):
    if isinstance(surf, Surface):
        #points, polylist =surf.shape.polylist(surf.topo)
        points, polylist =surf.polylist()
        glPushMatrix()
        glTranslatef(P[0],P[1],P[2])    
        glRotatef(180*D[2]/pi,0.0,0.0,1.0)
        glRotatef(180*D[1]/pi,0.0,1.0,0.0)
        glRotatef(180*D[0]/pi,1.0,0.0,0.0)
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [1.,1.,0,0.7])
        #glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [1.,1.,0.,1.])
        #glMaterialfv(GL_BACK, GL_AMBIENT_AND_DIFFUSE, [1.,0.,0.,1.])
        for p in polylist:
            if len(p)==3:
                p0=points[p[0]]
                p1=points[p[1]]
                p2=points[p[2]]
                v0=array(p1)-array(p0)
                v1=array(p2)-array(p0)
                v3=cross(v0,v1)
                v3=v3/sqrt(v3[0]**2+v3[1]**2+v3[2]**2)
                #if v3[2]<0: print "**"
                glBegin(GL_TRIANGLES) #Drawing Using Triangles
                #glColor4f(1,0,0, 1.)
                glNormal3f(v3[0],v3[1],v3[2])
                glVertex3f( p0[0], p0[1], p0[2])
                #glNormal3f(v3[0],v3[1],v3[2])
                glVertex3f( p1[0], p1[1], p1[2])
                #glNormal3f(v3[0],v3[1],v3[2])
                glVertex3f( p2[0], p2[1], p2[2])
                glEnd()                
            elif len(p)==4:
                p0=points[p[0]]
                p1=points[p[1]]
                p2=points[p[2]]
                p3=points[p[3]]
                v0=array(p1)-array(p0)
                v1=array(p2)-array(p0)
                v3=cross(v0,v1)
                v3=v3/sqrt(v3[0]**2+v3[1]**2+v3[2]**2)
                #print p0,p1,p2,p3
                
                glBegin(GL_QUADS)           # Start Drawing The Cube
                #glColor4f(1,0,0, 1.)
                glNormal3f(v3[0],v3[1],v3[2])
                glVertex3f( p0[0], p0[1], p0[2])
                #glNormal3f(v3[0],v3[1],v3[2])
                glVertex3f( p1[0], p1[1], p1[2])
                #glNormal3f(v3[0],v3[1],v3[2])
                glVertex3f( p2[0], p2[1], p2[2])
                #glNormal3f(v3[0],v3[1],v3[2])
                glVertex3f( p3[0], p3[1], p3[2])
                glEnd()                
        glPopMatrix()
 
def draw_ray(ray):
    P1=ray.pos
    w=ray.wavelength
    rc,gc,bc=wavelength2RGB(w)
    if len(ray.childs)>0:
        P2=ray.childs[0].pos
    else:
        P2=P1+10.*ray.dir

    if ray.intensity!=0:
        glMaterialfv(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE, [rc,gc,bc,1.])
        glBegin(GL_LINES)
        glColor4f(rc,gc,bc, 1.)
        glVertex3f( P1[0], P1[1], P1[2])
        glVertex3f( P2[0], P2[1], P2[2])
        glEnd()
    for i in ray.childs:
        draw_ray(i)

def plot3D(os, center=(0,0,0),size=(400,400),rot=[(0,0,0)],scale=1.):
    """
    Generate a 3D picture of the optical system under study
    
    Parameters:
    ===========
    
    os     Optical system, component or surface to be drawn
    center Tuple (x,y,z) with the coordinates of the center of the drawing
    size   Tuple (width, height) of the requested image
    rot    list of (rx,ry,rz) tuples containing a series of rotation angles
    scale  scale fot the image
    
    The rotations are applied first rx, then ry and then rz
    """
    
    left=-size[0]/2
    right=size[0]/2
    top=size[1]/2
    bottom=-size[1]/2
    
    #left=center[0]-size[0]/2
    #right=center[0]+size[0]/2
    #top=center[1]+size[1]/2
    #bottom=center[1]-size[1]/2
    
    ctx = OSMesaCreateContext(GL_RGBA, None)
    
    width,height=int(size[0]*scale),int(size[1]*scale)
    
    buf = arrays.GLubyteArray.zeros((height, width, 4))
    p = arrays.ArrayDatatype.dataPointer(buf)
    assert(OSMesaMakeCurrent(ctx, p, GL_UNSIGNED_BYTE, width, height))

    assert(CurrentContextIsValid())

    light_ambient = [.5, 0.5, 0.5, 1.0]
    light_diffuse = [1.0, 1.0, 1.0, 1.0]
    light_specular = [1.0, 1.0, 1.0, 1.0]
    light_position = [0.0, 1.0, -1.0, 1.]

    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)

    glShadeModel(GL_SMOOTH) #No parece estar funcionando
    
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
  
    #
    
    glEnable(GL_DEPTH_TEST)
    
    glEnable (GL_BLEND); glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    #gluPerspective(30., width/height, 0.1, 10000.)
    glOrtho(left,right,top,bottom, -1000.0, 10000.0)
    #glOrtho(-100, 100, -100, 100, 0, 100)
    #gluLookAt(cam_pos[0], cam_pos[1], cam_pos[2],
    #      lookat[0], lookat[1], lookat[2],
    #      up[0], up[1],up[2])
    

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    
    # Las rotaciones se aplican en orden inverso. No se por que, pero 
    # esta funcionando
    for rx,ry,rz in rot[::-1]:
        glRotatef(degrees(rz),0,0,1)
        glRotatef(degrees(ry),0,1,0)    
        glRotatef(degrees(rx),1,0,0)
        

    glTranslatef(-center[0],-center[1],-center[2])

    glLightfv(GL_LIGHT0, GL_POSITION, light_position)

    
    if isinstance(os, System):
        draw_sys(os)
    elif isinstance(os,Component):
        draw_comp(os,(0,0,0),(0,0,0))
    elif isinstance(os,Surface):
        draw_surf(os,(0,0,0),(0,0,0))

    glFinish()   
    
    return implot(buf)
    


def spot_diagram(s):
    """Plot the spot diagram for the given surface, or element
    """
    hl=s.hit_list
    X=[]
    Y=[]
    COL=[]
    if len(hl) >0:
        for i in hl:
            p=i[0]
            # Hitlist[1] points to the incident ray
            col=wavelength2RGB(i[1].wavelength)
            X.append(p[0])
            Y.append(p[1])
            COL.append(col)
    max=array(X+Y).max
    min=array(X+Y).min
    plot(X,Y,"o",)
    axis("equal")

def spot_diagram_c(s):
    """Plot the spot diagram for the given surface, or element
    """
    hl=s.hit_list
    X=[]
    Y=[]
    COL=[]
    if len(hl) >0:
        for i in hl:
            p=i[0]
            # Hitlist[1] points to the incident ray
            col=wavelength2RGB(i[1].wavelength)
            plot(p[0],p[1],"o",color=col)
            #X.append(p[0])
            #Y.append(p[1])
            #COL.append(col)
    #max=array(X+Y).max
    #min=array(X+Y).min
    axis("equal")
