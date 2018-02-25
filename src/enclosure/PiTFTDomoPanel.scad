/*******************************************************************************
* ENCLOSURE FOR RASPBERRY PI + PITFT + PIR SENSOR
* ------------------------------------------------------------------------------
* Copyright Damien Braillard, Switzerland
* ------------------------------------------------------------------------------
* Bill of materials:
*   - 4 M3 with 5mm long thread screws to hold the screen
*   - 2 M2 with 5mm long thread screws to hold the PIR
*   - 4 M4 with conic head to tighten he back part with the front part
*******************************************************************************/

// =============================================================================
// Defines all the measurements
// =============================================================================
tft_width           = 59;   // Width of the TFT display area
tft_height          = 45;   // Height of the TFT display area
tft_thick           =  4.5; // Thickness of the TFT display module (without board)
tft_pcb_thick       =  1;   // Thickness of the TFT PCB
tft_margin_left     = 11;   // Left distance from RPi board edge to TFT display area edge
tft_margin_right    = 15;   // Right distance from RPi board edge to TFT display area edge
tft_margin_top      =  9;   // Top distance from RPi board edge to TFT display area edge
tft_margin_bottom   =  3;   // Bottom distance from RPi board edge to TFT display area edge
tft_screw_diam      =  3;   // Diameter of the TFT attachement screw thread
tft_screw_height    =  5;   // Length of the TFT attachement screw thread
tft_hole_offsets    = [     // Offsets [X,Y] of holes in TFT board relative to top-left corner
                       [3.5, 3.5],
                       [81.5, 3.5],
                       [3.5, 52.5],
                       [81.5, 52.5]
                     ];

pi_width            = 85;   // Width of the RPi board
pi_height           = 56;   // Height of the RPi board
pi_thick            = 19;   // Thickness of the PI + TFT board (without the display)

pir_lens_diam       = 23;   // Diameter of the PIR lens
pir_lens_thick      =  3.5; // Thickness of the PIR lens base
pir_pcb_thick       =  1.5; // Thickness of the PIR board
pir_screw_height    =  5;   // Length of the PIR attachement screws thread
pir_screw_diam      =  2;   // Diameter of the PIR attachement screws thread
pir_hole_offsets    = [     // Offsets(X,Y) of PIR holes relative to PIR center (space between holes = 29mm)
                        -14.5,
                        14.5
                      ];
pir_height          = 24;   // Height of the PIR module
pir_width           = 33;   // Width of the PIR module
pir_spacing         =  5;   // Distance between the PIR and the PI board

screw_thread_diam   =  4;   // Diameter of the body screw threads
screw_head_diam     =  7;   // Diameter of the body screw head
screw_head_thick    =  2.5; // Thickness of the body screw head
screw_pillar_side   = 12;   // Side of the square pillars that hold the bolts.

cable_diam          =  4;   // Diameter of the USB cable

body_top_margin     =  2;   // Clearance on top of the last component
body_bottom_margin  = 20;   // Clearance before the firtst compnent can be found
body_back_margin    = 5;    // Clearance at the back of the PI board
body_angle          = 60;   // Inclinaison angle of the body in degrees

back_walls          =  3;   // Thickness of the back plate + stand walls
front_walls         =  2;   // Thickness of the front panel walls 
body_in_width       = tft_width + (2 * 30);        // 28mm + margin each side of the TFT
body_in_height      = pi_height + pir_height + body_bottom_margin + body_top_margin;
body_in_thick       = pi_thick + tft_thick + body_back_margin;

echo("Body In Width =",body_in_width);
echo("Body In Height =",body_in_height);
echo("Body In Thick =",body_in_thick);

$fn=100;

// Calculated values
_pi_top          = body_in_height - body_top_margin;
_pi_left         = ((body_in_width - tft_width) / 2) - tft_margin_right; // Correct because screen flipped down
_tft_top         = body_in_height - body_top_margin - tft_margin_top;
_tft_left        = (body_in_width - tft_width)/2;
_pir_center_top  = body_in_height - body_top_margin - pi_height - pir_spacing - pir_height / 2;
_pir_center_left = body_in_width / 2;

// Utiliy modules
module rounded_cube(size, r=5) {

  linear_extrude(height=size[2])
  hull() {
    translate([r, r])
      circle(r=r);
    translate([size[0]-r, r])
      circle(r=r);
    translate([r, size[1]-r])
      circle(r=r);
    translate([size[0]-r, size[1]-r])
      circle(r=r);    
  }
  
}

// Renders the front part
module front_part() {

    difference() {
      translate([-front_walls, -front_walls, -front_walls])
        rounded_cube([body_in_width+front_walls*2, body_in_height+front_walls*2, body_in_thick+front_walls+back_walls]);
      
      // Main opening
      cube([body_in_width, body_in_height, body_in_thick+back_walls+1]);
      
      // Hole for PIR sensor
      translate([_pir_center_left, _pir_center_top, 0])
        sphere(d=pir_lens_diam*1.03);
      
      // Hole for screen
      translate([_tft_left, _tft_top-tft_height, -(front_walls*2-.005)])
        minkowski() {
          cube([tft_width, tft_height, front_walls]);
          cylinder(r1=front_walls, r2=0, h=front_walls);
        } 
    }

    // TFT fixation holes
    for(i = tft_hole_offsets) {
      translate([_pi_left + pi_width - i[0], _pi_top - i[1], 0]) {
        difference() {
          cylinder(d=tft_screw_diam+2.4, h=tft_thick-.4);
          translate([0, 0, tft_thick+tft_pcb_thick-tft_screw_height-.5])
            cylinder(d=tft_screw_diam-.5, h=tft_thick+1);
        }
      }
    }
    
    // PIR fixation holes
    for(i = pir_hole_offsets) {
      translate([_pir_center_left + i, _pir_center_top, 0])
        difference() {
          cylinder(d=pir_screw_diam+2.4, h=pir_lens_thick-.4);
          translate([0, 0, pir_lens_thick+pir_pcb_thick-pir_screw_height-.5])
            cylinder(d=pir_screw_diam-.25, h=pir_screw_height+1);
        }      
    }
    
    // Screw holders
    for(x = [0, body_in_width-screw_pillar_side], y = [0, body_in_height-screw_pillar_side]) {
      translate([x, y, 0])
      difference() {
        cube([screw_pillar_side, screw_pillar_side, body_in_thick]);
        translate([screw_pillar_side/2, screw_pillar_side/2, 0])
          cylinder(d=screw_thread_diam-.5, h=body_in_height+2);
      }
    }
  
}

// Renders the back part
module back_part() {
  base_depth = cos(body_angle)*body_in_height;
  difference() {
    union() {
      // Main plate
      rotate([body_angle, 0, 0]) { 
        cube([body_in_width, body_in_height, back_walls]);        
      }
      
      // Foot
      hull() {
        translate([body_in_width/2, base_depth-10, 0])
          cylinder(d=20, h=10);
        rotate([body_angle, 0, 0]) {
          cube([body_in_width, body_in_height/2, back_walls]);
        }
      }
    }
    
    // == SCREW HOLES == 
    rotate([body_angle, 0, 0]) { 
      for(x = [screw_pillar_side/2, body_in_width-screw_pillar_side/2],
          y = [screw_pillar_side/2, body_in_height-screw_pillar_side/2]) {
        translate([x, y, -.005]) {
          cylinder(d=screw_thread_diam, h=back_walls+.01);
          cylinder(d1=screw_head_diam+.5, d2=screw_thread_diam, h=screw_head_thick+.5);
          translate([0, 0, -30])
            cylinder(d=screw_head_diam+.5, h=30.001);
        }
      }    
    }

    // == CABLE OPENING ==
    channel_width = cable_diam*2;
    peg_center    = base_depth*3/4;
    peg_thick     = 2;
    peg_len       = 5;
    peg_spacing   = cable_diam;
    {
      // Plate Cable opening
      rotate([body_angle, 0, 0])
      translate([(body_in_width-channel_width)/2, -.1, -20])
        cube([channel_width, cable_diam*4+.1, back_walls+20.1]);
      // Foot channel
      translate([(body_in_width-channel_width)/2, 0, -.01]) {
        // Main channel
        translate([0, 0, peg_thick-.1])
          cube([channel_width, base_depth, cable_diam+2.1]);
        // Front main opening 
        cube([channel_width, peg_center-peg_len-peg_spacing/2, peg_thick]);
        // Front peg
        translate([0, peg_center-peg_len-peg_spacing/2-.1, -.1])
          cube([channel_width/2, peg_len+.2, peg_thick+.1]);
        // Space between pegs 
        translate([0, peg_center-peg_spacing/2, 0])
          cube([channel_width, peg_spacing, peg_thick]);
        // Back peg
        translate([channel_width/2, peg_center+peg_spacing/2-.1, -.1])
          cube([channel_width/2, peg_len+.2, peg_thick+.1]);
        // Back main opening
        translate([0, peg_center+peg_len+peg_spacing/2, 0])
          cube([channel_width, base_depth-peg_center-peg_len-peg_spacing/2, peg_thick]);
      }
    }
  }  
}

// =============================================================================
// Main rendering
// =============================================================================

// Uncomment to render the front part
front_part();
// Uncomment to render the back part
translate([body_in_width*1.5, 0, 0]) back_part();
