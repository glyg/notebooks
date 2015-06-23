
module attachment_sites(Mk, r, d)
{
union()
	{for(i=[0:Mk]) 
		{
		translate([r, 0, i*d - Mk*d/2])
		sphere(r, $fn=30);
		}
	}
}

module kinetochore(Mk, r, d)
{
difference()
	{
	cylinder((Mk+1)*d, r, r, center=true, $fn=100);
	cylinder((Mk+1)*d*1.1, r*0.8, r*0.8, center=true, $fn=100);
	translate([-r/1.9, 0, 0])
		{
		cube([r, r*2.1, (Mk+1)*d*1.1], center=true);
		}
	%attachment_sites(Mk, r, d);	
	}
}

translate([5, 1, 2])
{
	rotate([5, 0, 0])
	{
	kinetochore(4, 0.5, 1.5);
	}
}

translate([2, 1, 2])
{
	rotate([10, 0, 180])
	{
	kinetochore(4, 0.5, 1.5);
	}
}