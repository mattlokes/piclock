include <pins.scad>

// Generate a Flaired Hole Cutout
module flaired_hole(lDia=6,lSpacing=30,lSpaceOff=2,thickness=20, offset=14)
{
  cylinder(r1=(lDia/2), r2=(lDia/2), h=thickness, $fn=100);
  translate([0,0,offset])
  cylinder(r1=(lDia/2), r2=((lSpacing/2)-lSpaceOff), h=(thickness-offset), $fn=100);
}

//Generate a 4x4 grid of Flaired Holes
module gen_flaired_grid()
{
  holeDepth=14;
  ledSpace =30;
  for ( j = [0:3])
  {
    for ( i = [0:3])
    {
      translate([(i*ledSpace),((-1*j)*ledSpace),0])
      flaired_hole(offset=holeDepth, lSpaceOff=2.5 ,lDia=7.5, thickness=25);
    }
  }
}

//Generate Basic Structure with PCB are removed
module gen_basic_struct()
{
  translate([0,-120,25])
  rotate([180,0,0])
  difference()
  {
    //bulk material
    translate([0,-120,0])
    cube([120,120,24.9]);

    // PCB Slot
    translate([(30/2)-4.5-1,((-100)-(30/2)+4.5)-1,-0.1])
    cube([102,102,14.2]);

    translate([15,-15,0.05])
    gen_flaired_grid();

  }
}

// Generate hollows for solder of pins
module solder_cutouts()
{
  //vertical main slot
  translate([(30/2)+12.5,-60-15,(25-14)-3])
  cube([7.5,30,4]);
  
  //vertical driver slot
  translate([15+30+30+30-7,-15-30+7.5-60,(25-14)-3])
  //translate([15+30+30+30-7,7.5,(25-14)-3])
  cube([5,15,4]);

  //horizontal slot1
  translate([15+30+7.5,-15-2.5,(25-14)-3])
  cube([15,5,4]);
  
  //horizontal slot2
  translate([15+30+7.5,-15-2.5-30-30-30,(25-14)-3])
  cube([15,5,4]);
}

//flip connector hole
module flipped_hole()
{
  rotate([180,0,0])
  translate([0,0,-10.2])
  pinhole();
}

//Generate Grid module connector holes
module connectors_cutouts()
{
 translate([-0.1,-12,25-4])
 cube([12.1,12.1,4.1]);
 translate([6,-6,(25-10)-4])
 flipped_hole();

 translate([120-12,-12,25-4])
 cube([12.1,12.1,4.1]);
 translate([120-6,-6,(25-10)-4])
 flipped_hole();

 translate([-0.1,-120.1,25-4])
 cube([12.1,12.1,4.1]);
 translate([6,-120+6,(25-10)-4])
 flipped_hole();

 translate([120-12,-120.1,25-4])
 cube([12.1,12.1,4.1]);
 translate([120-6,-120+6,(25-10)-4])
 flipped_hole();
}

//Generate Cable cutouts from bulk
module cable_cutouts()
{
  translate([-6-60+5,-20,25-5])
  cube([12,40,6]);

  translate([-6+60-5,-20,25-5])
  cube([12,40,6]);

  translate([-15,-6-60+5,25-5])
  cube([30,12,6]);

  translate([-15,-6+60-5,25-5])
  cube([30,12,6]); 
}

//Generate grid module one of 16 modules
module grid_module()
{
//color([0,0,0])
  difference()
  {
    translate([-60,60,0])
    difference()
    {
      gen_basic_struct();
      solder_cutouts();
      connectors_cutouts();
    }
    cable_cutouts();
  }
}

//Generate grid module connector 4 pins
module grid_connector4()
{
translate([-12,-12,0])
cube([24,24,4]);

translate([6,6,0])
pintack(br=4,bh=4);
translate([6,-6,0])
pintack(br=4,bh=4);
translate([-6,6,0])
pintack(br=4,bh=4);
translate([-6,-6,0])
pintack(br=4,bh=4);
}

//Generate grid module connector 4 pins
module grid_connector4_edge()
{
  difference()
  {
    union()
    {
    translate([-12,-12,0])
    cube([24,24,4]);
    translate([-12,-12,4])
    cube([24,12,4.4]);

    translate([6,-6,4.4])
    pintack(br=4,bh=4);
    translate([-6,-6,4.4])
    pintack(br=4,bh=4);
    }

    translate([6,6,-0.5])
    //pintack(br=4,bh=4);
    cylinder(r1=5,r2=1.5,h=5,$fn=100);
    translate([-6,6,-0.5])
    cylinder(r1=5,r2=1.5,h=5,$fn=100);
    //pintack(br=4,bh=4);
  }
}

//Generate grid module connector 2 pins
module grid_connector2()
{
translate([-12,-6,0])
cube([24,12,4]);

translate([-6,0,0])
pintack(br=4,bh=4);
translate([6,0,0])
pintack(br=4,bh=4);
}

//Generate Visulisation of all 16 Grid pieces
module full_grid_viz()
{
  translate([120,-120,0])
  for ( j = [0:3])
    {
      for ( i = [0:3])
      {
        translate([(-1*i)*120,j*120,0])
        grid_module();
      }
    }
}

//grid_connector4();  //x9
grid_connector4_edge();  //x12
//grid_module();      //x16
//cable_cutouts();
//translate([60,-60,0])
//full_grid_viz();


