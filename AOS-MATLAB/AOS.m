%% Atomic Orbital Search (AOS) Algorithm source code - version 1.0 
%% Programmer and Author: Mahdi Azizi 
%% E-mail: mehdi.azizi875@gmail.com

%% Clear Workspace & Command Window
clc; clear all;

%% Problem Information
CostFunction = @(x) Sphere(x);          % @ Cost Function
VarNumber = 10;                         % Number of variables;
VarMin = -10 *ones(1,VarNumber);        % Lower bound of variable;
VarMax = 10 *ones(1,VarNumber);         % Upper bound of variable;

%% General Parameters of the Algorithm
MaxFes = 150000 ;     % Maximum number of generations
nPop = 25 ;           % Maximum number of initial candidates
LayerNumber = 5 ;     % Maximum number of Layers around nucleus
FotonRate = 0.1 ;     % Foton Rate for position determination of electrons

%% Counters
Iter=0;
FEs=0;

%% Initialization
Pop=[]; Cost=[];
for i=1:nPop
    % Initialize Positions
    Pop(i,:)=unifrnd(VarMin,VarMax,[1 VarNumber]);
    % Cost Function Evaluations
    Cost(i,1)=CostFunction(Pop(i,:));
    FEs=FEs+1;
end

% Sort Population
[Cost, SortOrder]=sort(Cost);
Pop=Pop(SortOrder,:);
BestPop=Pop(1,:);
MeanPop=mean(Pop);

%% Main Loop
while FEs<MaxFes           
    Iter=Iter+1;    
    PopC=[];  
    CostC=[];
    NorDispCal=[];
    % Creat Quantum Layers
    MaxLay = randi(LayerNumber);
    NorDispInptut = 1:1:MaxLay;
    mu = 0;
    sigma = MaxLay/6;
    pd = makedist('Normal','mu',mu,'sigma',sigma);
    NorDisp = pdf(pd,NorDispInptut);
    NorDispCal(1,:)=NorDisp;
    NorDispCal(2,:)=NorDispCal(1,:)./sum(NorDispCal(1,:));
    NorDispCal(3,:)=nPop*NorDispCal(2,:);
    NorDispCal(4,:)=round(NorDispCal(3,:));
    NorDispCal(5,:)=cumsum(NorDispCal(4,:));   
    LayCol=[0 NorDispCal(5,:)];
    LayCol(LayCol>nPop)=nPop;   
    % Search Loop   
    for i=1:MaxLay        
        PopA=Pop(LayCol(i)+1:LayCol(i+1) , :);
        CostA=Cost(LayCol(i)+1:LayCol(i+1) , 1);
        Energy=mean(CostA);
        Orbit=i;      
        for j=1:size(PopA,1)                                              
            if rand>FotonRate                
                if CostA(j,1)>Energy                    
                    Ir=unifrnd(0,1,1,2);
                    Jr=unifrnd(0,1,1,VarNumber);                   
                    Xold=PopA(j,:);
                    Xbest=BestPop;
                    Xmean=MeanPop;                   
                    PopB(j,:)=Xold+(Jr.*(Ir(1)*Xbest-Ir(2)*Xmean)/Orbit);                                         
                    PopB(j,:) = max(PopB(j,:),VarMin);
                    PopB(j,:) = min(PopB(j,:),VarMax);                    
                    CostB(j,1)=CostFunction(PopB(j,:));                    
                    FEs=FEs+1;                   
                else                    
                    Ir=unifrnd(0,1,1,2);
                    Jr=unifrnd(0,1,1,VarNumber);                    
                    Xold=PopA(j,:);
                    Xbest=PopA(1,:);
                    if size(PopA,1)==1
                        Xmean=PopA; 
                    else
                        Xmean=mean(PopA);
                    end
                    PopB(j,:)=Xold+(Jr.*(Ir(1)*Xbest-Ir(2)*Xmean));
                    PopB(j,:) = max(PopB(j,:),VarMin);
                    PopB(j,:) = min(PopB(j,:),VarMax);                    
                    CostB(j,1)=CostFunction(PopB(j,:));                    
                    FEs=FEs+1;                    
                end                
            else                                                
                PopB(j,:)=unifrnd(VarMin,VarMax,[1 VarNumber]);                                    
                CostB(j,1)=CostFunction(PopB(j,:));     
                FEs=FEs+1;              
            end            
        end    
        PopC=[PopC ; PopB];
        CostC=[CostC ; CostB];        
    end
    
    % Merge Candidates
    Pop=[Pop ; PopC];
    Cost=[Cost ; CostC];   

    % Sort Population
    [Cost, SortOrder]=sort(Cost);
    Pop=Pop(SortOrder,:);
    BestPop=Pop(1,:);
    BestCost=Cost(1,1);
    MeanPop=mean(Pop);    
    Pop=Pop(1:nPop,:);
    Cost=Cost(1:nPop,:);
    
    % Store Best Cost Ever Found
    BestCosts(Iter,1)=BestCost;

    % Show Iteration Information
    disp(['Iteration ' num2str(Iter) ': Best Cost = ' num2str(BestCosts(Iter))]);

    
end

Eval_Number=FEs;
Conv_History=BestCosts;
Best_Pos=BestPop;

%% Objective Function
function z=Sphere(x)
    z=sum(x.^2);
end
