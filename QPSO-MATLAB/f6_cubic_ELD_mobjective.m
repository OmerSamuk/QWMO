function[F E P1 Pd]=f6_cubic_ELD_mobjective(in)
in=abs(in);
global data edata B B0 w Pd
a=data(:,1);
b=data(:,2);
c=data(:,3);
d=data(:,4);
e=edata(:,1);
f=edata(:,2);
g=edata(:,3);
h=edata(:,4);
y1=in.^3*diag(a)+in.^2*diag(b)+in*diag(c);%y1=P.^2*diag(a)+P*diag(b);
y2=in.^3*diag(e)+in.^2*diag(f)+in*diag(g);
P11=(in*B).*in+in*diag(B0);
P1=sum(P11')';
lam=abs(Pd-sum(in')+P1')';
%lam=abs(sum(in')-Pd-P1')';
F=sum(y1')+sum(d)+100*lam;
E=sum(y2')+sum(h);
%Ft=(sum(w*F'))+(sum(1-w)*E')+100*lam;
F;
E;




% function[F P1]=f6(in)
% in=abs(in);
% global data B B0 Pd 
% a=data(:,1);
% b=data(:,2);
% c=data(:,3);
% y1=in.*in*diag(a)+in*diag(b);
% P11=(in*B).*in+in*diag(B0);
% P1=sum(P11')';
% lam=abs(Pd-sum(in')+P1')';
% F=(sum(y1')+sum(c))'+100*lam;