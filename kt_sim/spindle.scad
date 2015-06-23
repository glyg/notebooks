Mk = 3;



module attachment_sites(r, d)
{
    union()
    {for(i=[0:Mk-1])
	{
	    translate([r, 0, (i-1)*d])
	    sphere(r, $fn=12);
	}
    }
}

module centromere(r=0.1, d=0.2)
{
    difference()
    {
	cylinder((Mk)*d, r, r, center=true, $fn=24);
	cylinder((Mk)*d*1.1, r*0.8, r*0.8, center=true, $fn=24);
	translate([-r/1.9, 0, 0])
	{
	    cube([r, r*2.1, (Mk)*d*1.1], center=true);
	}
	attachment_sites(r, d);
    }
}


module chromosome
(
    position=[0, 0, 0],
    stretch=0.3,
    theta=0,
    phi=0,
    r=0.1,
)
{
    translate(position)
    {
	rotate([0, 0, theta])
	rotate([0, phi, 0])
	{
	    rotate([0, 90, 0]) cylinder(stretch, r, r,
		center=true, $fn=24);
	    translate([stretch/2, 0, 0])
	    centromere();
	    translate([-stretch/2, 0, 0])
	    rotate([0, 0, 180])
	    centromere();
	}
    }
}

module spb(position, r=0.4)
{
    translate(position)
    sphere(r, $fn=24);
}

module spindle_midzone(length, r_mz=0.2)
{
    color([0.1, 0.1, 0.1, 0.4])
    {
	rotate([0, 90, 0])
	cylinder(length, r_mz, r_mz,
	    center=true, $fn=12);
	spb([-length/2, 0, 0]);
	spb([length/2, 0, 0]);
    }
}

spindle_midzone(4);
chromosome([0.4, 0.3, 1], 0.3, 30, 30);