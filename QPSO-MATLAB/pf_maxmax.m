%Penalty Factor of F-CO2 for Max/Max

P1=200;
P2=80;
P3=50;
P4=50;
P5=50;
P6=40;

%Emission of CO2

ac1=0.0015; bc1=0.0920; cc1=14.0; dc1=-16.0;
ac2=0.0014; bc2=0.0250; cc2=12.5; dc2=-93.5;
ac3=0.0016; bc3=0.0550; cc3=13.5; dc3=-85.0;
ac4=0.0012; bc4=0.0100; cc4=13.5; dc4=-24.5;
ac5=0.0023; bc5=0.0400; cc5=21.0; dc5=-59.0;
ac6=0.0014; bc6=0.0800; cc6=22.0; dc6=-70.0;

Ec1=P1^3*ac1+P1^2*bc1+P1*cc1+dc1;
Ec2=P2^3*ac2+P2^2*bc2+P2*cc2+dc2;
Ec3=P3^3*ac3+P3^2*bc3+P3*cc3+dc3;
Ec4=P4^3*ac4+P4^2*bc4+P4*cc4+dc4;
Ec5=P5^3*ac5+P5^2*bc5+P5*cc5+dc5;
Ec6=P6^3*ac6+P6^2*bc6+P6*cc6+dc6;
Ec=Ec1+Ec2+Ec3+Ec4+Ec5+Ec6;

Ec

%Fuel Cost

af1=0.0010;	bf1=0.0920;	cf1=14.50;	df1=-136.00;
af2=0.0004;	bf2=0.0250;	cf2=22.00;	df2=-3.50;
af3=0.0006;	bf3=0.0750;	cf3=23.00;	df3=-81.00;
af4=0.0002;	bf4=0.1000;	cf4=13.50;	df4=-14.50;
af5=0.0013;	bf5=0.1200;	cf5=11.50;	df5=-9.75;
af6=0.0004;	bf6=0.0840;	cf6=12.50;	df6=75.60;

F1=P1^3*af1+P1^2*bf1+P1*cf1+df1;
F2=P2^3*af2+P2^2*bf2+P2*cf2+df2;
F3=P3^3*af3+P3^2*bf3+P3*cf3+df3;
F4=P4^3*af4+P4^2*bf4+P4*cf4+df4;
F5=P5^3*af5+P5^2*bf5+P5*cf5+df5;
F6=P6^3*af6+P6^2*bf6+P6*cf6+df6;

F=F1+F2+F3+F4+F5+F6;

F

%Calculation of hco2
hc1=F1/Ec1;
hc2=F2/Ec2;
hc3=F3/Ec3;
hc4=F4/Ec4;
hc5=F5/Ec5;
hc6=F6/Ec6;
hco2=hc1+hc2+hc3+hc4+hc5+hc6;

hc1
hc2
hc3
hc4
hc5
hc6
hco2

