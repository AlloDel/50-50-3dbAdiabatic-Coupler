from phidl import quickplot as qp, geometry as pg
from phidl import Device, Layer, CrossSection, Path
from phidl.geometry import Port
import phidl.path as pp, phidl.routing as pr
import numpy as np
from lyipc.client import kqp

D = Device('adiabatic_coupler')
WG1 = Device()
WG2 = Device()

w1 = 0.4
w2 = 0.6
w3 = 0.5
Lin = 15
Lbend = 30
Lcoupling = 100
g = 0.2
S = 2.5

def generate_arc(radius, width, angle, layer):
    dev = pg.arc(radius = radius, width = width, theta = angle, layer = layer,)
    return dev

def generate_rec(length, width, layer):
    dev = pg.rectangle(size = (length, width), layer = layer,)
    dev.add_port(Port(name=1, midpoint=[dev.xmin, dev.ysize/2], width=dev.ysize, orientation=180))
    dev.add_port(Port(name=2, midpoint=[dev.xmax, dev.ysize/2], width=dev.ysize, orientation=0))
    return dev

def generate_taper(length, width1, width2, layer): 
    dev = pg.taper(length = length, width1 = width1, width2 = width2, layer = layer)
    return dev

# # WG1 = rec > taper > rec > taper > arc == wg11 > wg12 > wg13 > wg14 > wg15 
# Add the components to WG1
wg11ref = WG1 << generate_rec(width=w3, length=5, layer=1,)
wg12ref = WG1 << generate_taper(length=Lin, width1=w3, width2=w1, layer = 1)
wg13ref = WG1 << generate_rec(width=w1, length=Lbend, layer=1)
wg14ref = WG1 << generate_taper(length=Lcoupling, width1=w1, width2=w3, layer = 1)
wg15ref = WG1 << generate_arc(radius=5, angle=45,width=w3, layer =1).rotate(270)

# # WG2 = rec > taper > rec > arc > rec > arc > taper > arc 
# Add the components to WG1
wg21ref = WG2 << generate_rec(width=w3, length=5, layer = 1) 
wg22ref = WG2 << generate_taper(length=Lin, width1=w3, width2=w2, layer = 1) 
wg23ref = WG2 << generate_arc(radius=3, angle=3,width=w2, layer = 1).rotate(270) 
wg24ref = WG2 << generate_rec(width=w2, length=Lbend, layer=1,) 
wg25ref = WG2 << generate_arc(radius=3, angle=-3,width=w2, layer = 1).rotate(90) 
wg26ref = WG2 << generate_taper(length=Lcoupling, width1=w2, width2=w3, layer = 1) 
wg27ref = WG2 << generate_arc(radius=5, angle=-45,width=w3, layer = 1).rotate(90) 


def conn_wg1():
    # Connect all the components for WG1
    wg14ref.connect(port = 2, destination = wg15ref.ports[1])
    wg13ref.connect(port = 2, destination = wg14ref.ports[1])
    wg13ref.connect(port = 1, destination = wg12ref.ports[2])
    wg12ref.connect(port = 2, destination = wg13ref.ports[1])
    wg11ref.connect(port = 2, destination = wg12ref.ports[1])
    wg14ref.connect(port = 1, destination = wg13ref.ports[2])
    wg15ref.connect(port = 1, destination = wg14ref.ports[2])
    return

def conn_wg2():
    # # Connect all the components for WG2
    wg26ref.connect(port = 2, destination = wg27ref.ports[1])
    wg25ref.connect(port = 2, destination = wg26ref.ports[1])
    wg24ref.connect(port = 2, destination = wg25ref.ports[1])
    wg23ref.connect(port = 2, destination = wg24ref.ports[1])
    wg22ref.connect(port = 2, destination = wg23ref.ports[1])
    wg21ref.connect(port = 2, destination = wg22ref.ports[1])
    wg21ref.connect(port = 2, destination = wg22ref.ports[1])
    # wg27ref.connect(port = 1, destination = wg26ref.ports[2])
    return

conn_wg1()
conn_wg2()

# WG2_flatt = WG2.flatten() 
# WG1_flatt = WG1.flatten() 
WG1.move(origin = WG1.bbox[0], destination = (0, 0))
WG2.move(origin = WG2.bbox[0], destination = (0, 0))

D << WG2 
D << WG1 

D.distribute(direction = 'y', spacing = g)


# Adding optical ports
WG1.add_port(name="opt_in_1", port=wg11ref.ports[1])
WG2.add_port(name="opt_in_2", port=wg21ref.ports[1])
WG1.add_port(name="opt_out_1", port=wg15ref.ports[2])
WG2.add_port(name="opt_out_2", port=wg27ref.ports[2])
# # Function to add a marker at a port location
# def add_marker(device, port, size=1):
#     marker = pg.rectangle(size=(size, size), layer=2)  # Create a small square as a marker
#     device.add_ref(marker).center = port.midpoint  # Position the marker at the port location
# # Add markers to all the ports
# for port_name, port in WG1.ports.items():
#     add_marker(WG1, port)
# for port_name, port in WG2.ports.items():
#     add_marker(WG2, port)

D.flatten()
# kqp(D) #use for viewing in klayout- start server by cmd/ctrl + I
D.write_gds(filename="Allo_Prosper_ADC.gds")