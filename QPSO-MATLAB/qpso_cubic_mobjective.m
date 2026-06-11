clear
clc
popsize=100;
MAXITER=100;
dimension=6;
%irange_l=15;
%irange_r=30;
%xmax=200;
w2=1;
w1=0.5;
sum1=0;
sum2=0;
mean=0;
totaltime=0;
runno=2;
data1=zeros(runno,MAXITER);
data2=zeros(dimension,runno);
global data edata w B B0 B00 Pd
data=[0.0010 0.0920 14.50 -136.00 50 200
0.0004 0.0250 22.00 -3.50 20 80
0.0006 0.0750 23.00 -81.00 15 50
0.0002 0.1000 13.50	-14.50 10 50
0.0013 0.1200 11.50	-9.75 10 50
0.0004 0.0840 12.50	75.60 12 40
];
edata=[0.0015 0.0920 14.0 -16.0
0.0014 0.0250 12.5 -93.5
0.0016 0.0550 13.5 -85.0
0.0012 0.0100 13.5 -24.5
0.0023 0.0400 21.0 -59.0
0.0014 0.0800 22.0 -70.0
];
B=1e-4*[0 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 0
];%B=0.01*[0.06760 0.00953 -0.00507;0.00953 0.05210 0.00910;-0.00507 0.00901 0.02940];
B0=0.0*[0 0 0 0 0 0];
B00=000*.040357;
w=0.5;
Pd=150;
Pd=Pd+B00;
l=data(:,5)';
u=data(:,6)';
lu=[l' u'];
lu= lu';
range = lu(2,:) - lu(1,:);
for run=1:runno
    mean=0;
T=cputime;
%x=(data(:,6) - data(:,5))*rand(popsize,dimension,1) + data(:,5)';
%for dimension=1
%x=(200 - 50)*rand(popsize,dimension,1) + 50;
%for dimension=2
%x=(80 - 20)*rand(popsize,dimension,1) + 20;
%end
%for dimension=3
%x=(50 - 15)*rand(popsize,dimension,1) + 15;
%end
%for dimension=4
%x=(50 - 10)*rand(popsize,dimension,1) + 10;
%end
%for dimension=5
%x=(50 - 10)*rand(popsize,dimension,1) + 10;
%end
%for dimension=6
%x=(40- 12)*rand(popsize,dimension,1) + 12;
%end
x=rand(popsize,dimension,1) ;
%end
for k = 1:dimension
  x(:,k) = x(:,k)*range(k)+lu(1,k);
end
pbest=x;
gbest=zeros(1,dimension);
for i=1:popsize
    f_x(i)=f6_cubic_ELD_mobjective(x(i,:));
    f_pbest(i)=f_x(i);
end
    g=min(find(f_pbest==min(f_pbest(1:popsize))));%g=find(f_pbest==min(f_pbest(1:popsize)));
    gbest=pbest(g,:);
    f_gbest=f_pbest(g);
MINIUM=f_pbest(g);
for t=1:MAXITER
  disp('Minimum=');
    disp(MINIUM);
    disp('Iteration=');
       disp(t);
    
       beta=(w2-w1)*(MAXITER-t)/MAXITER+w1;
    mbest=sum(pbest)/popsize;
       
 for i=1:popsize  
     for j=1:6
data2(j,run)=gbest(j);%(i,:);
     end;
     %n=size(nest,1);
     %beta=3/2;
%sigma=(gamma(1+beta)*sin(pi*beta/2)/(gamma((1+beta)/2)*beta*2^((beta-1)/2)))^(1/beta);
%for j=1:n,
    %s=nest(j,:);
    %u=randn(size(s))*sigma;
    %=randn(size(s));
    %step=u./abs(v).^(1/beta);
        fi=rand(1,dimension);
        p=fi.*pbest(i,:)+(1-fi).*gbest;
        u=rand(1,dimension);
        b=beta*abs(mbest-x(i,:));
        v=-log(u);
        %y=p+((-1).^ceil(w1+u)).*b.*v;%
        y=p+((-1).^ceil(w1+rand(1,dimension))).*b.*v;
        x(i,:)=y;
        %x(i,:)=sign(y).*min(abs(y),xmax); 
          
        for j=1:1;
            if x(i,j)<50;
                x(i,j)=50;
            end;
            if x(i,j)>200.00;
                x(i,j)=200.00;
            end;
             %x(i,j)=round(x(i,j));
         end;
         for j=2:2;
             if x(i,j)<20;
                x(i,j)=20;
            end;
            if x(i,j)>80.00;
                x(i,j)=80.00;
            end;
            %x(i,j)=round(x(i,j));
         end;
         for j=3:3;
             if x(i,j)<15;
                x(i,j)=15;
            end;
            if x(i,j)>50.00;
                x(i,j)=50.00;
            end;
            %x(i,j)=round(x(i,j));
         end;
         for j=4:5;
             if x(i,j)<10;
                x(i,j)=10;
            end;
            if x(i,j)>50.00;
                x(i,j)=50.00;
            end;
            %x(i,j)=round(x(i,j));
         end;
         for j=6:6;
            if x(i,j)<12;
                x(i,j)=12;
            end;
            if x(i,j)>40;
                x(i,j)=40;
            end;
            %x(i,j)=round(x(i,j));
         end
         
            f_x(i)=f6_cubic_ELD_mobjective(x(i,:));
            if f_x(i)<f_pbest(i)
                pbest(i,:)=x(i,:);
                f_pbest(i)=f_x(i);
            end
            if f_pbest(i)<f_gbest
                gbest=pbest(i,:);
                f_gbest=f_pbest(i);
            end            
            MINIUM=f_gbest;                    
 end
 disp('Power Output=');
 disp(gbest);
    
    data1(run,t)=MINIUM;
    if MINIUM<2500
        mean=mean+1;
    end
  end
sum1=sum1+mean;  
sum2=sum2+MINIUM;
 %MINIUM
time=cputime-T;
totaltime=totaltime+time;

end
av1=sum1/runno;  
av2=sum2/runno;  
totaltime/runno;
disp('Minimum=');
    disp(MINIUM);
dec=var(data1);  
St_dev=sqrt(dec);    
gbestmin=min(data2,[],2)
Fmin=min(data1)
St_dev
%f_gbest
totaltime
        
 