Input:LinearReglength(25),fastlength(12),slowlength(26),MACDlength(9),roclength(2),
N1(2.5),N2(2.5),N3(70),LN1(1.5),LN2(2),atrlength(10);

vars:minpoint(0),midline(0),upperband1(0),lowerband1(0),upperband2(0),lowerband2(0),ATR(0),mvalue(0),rvalue(0),blongstoped(false),
bshortstoped(false),rocvalue(0),var1(false),var0(0),var2(0),var3(0),ma5(0),var4(false),var5(false),
HiAfterEntry(0), LoAfterEntry(0), Stopline(0),ma20(0),flagb(0),flags(0);

if currentbar>=1 then
begin
{entry signal} 
ATR=AvgTrueRange(atrlength);
minpoint=MinMove*PriceScale;
midline=LinearRegValue( C,LinearReglength, 0 );
upperband1=midline+LN1*ATR;
lowerband1=midline-LN1*ATR;
upperband2=midline+LN2*ATR; 
lowerband2=midline-LN2*ATR;
var2 = MACD( Close, fastlength, slowlength ) ; 
var3 = XAverage( var2, MACDLength ) ;
mvalue = var2 - var3 ; 
rvalue=Average(RSI(c,14),5); 
ma5=Average(c,5);
ma20=XAverage(c,20);

condition1=c crosses over (upperband1) and c-o>=20*minpoint;
condition2=close crosses over (upperband2) and c-o>=20*minpoint;
condition3=c crosses under (lowerband1) and o-c>=20*minpoint; 
condition4=close crosses under (lowerband2) and o-c>=20*minpoint; 

if marketposition<>1 and condition2 and ma5>=Average(c,10)  then
begin
buy("buy1") 1 share next bar at Open;
flagb=1;
end; 

if marketposition<>1  and mvalue>0  and condition1 then 
begin  
buy("buy2") 1 share next bar at Open;
flagb=2;
end; 


if marketposition<>-1 and condition4 and ma5<=Average(c,10) then
begin
sellshort("sellshort1") 1 share next bar at Open;
flags=1;
end;  


if marketposition<>-1 and  mvalue<0 and condition3  then
begin
sellshort("sellshort2") 1 share next bar at Open;
flags=2;
end; 

{exit signal}
rocvalue=RateOfChange(Average(C,5) ,roclength);
value1=Divergence(C,rvalue,2,18,1);
value2=Divergence(C,rvalue,2,18,-1);

if marketposition=1 and rocvalue<=-1  and c<ma5 then 
begin
sell("sell1") 1 share next bar at market;
flagb=0;
end;

if marketposition=-1 and rocvalue>=1  and c>ma5 then 
begin
buytocover("BT1") 1 share next bar at market;
flags=0; 
end;

  
if marketposition=1 and C<ma20 and ma20<ma20[3] then 
begin
sell("sell2") 1 share next bar at market; 
flagb=0;
end;
   
if marketposition=-1 and C>ma20 and ma20>ma20[3] then 
begin
buytocover("BT2") 1 share next bar at market;
flags=0;
end;

if marketposition=1 and rvalue>=70 and value1=1 and c<=Average(c,5) then 
begin
sell("sell3") 1 share next bar at market;
flagb=0;    
end; 

if marketposition=-1 and rvalue<=30 and value2=1 and c>=Average(c,5) then 
begin
buytocover("BT3") 1 share next bar at market;
flags=0;
end;

{again entry}
value10=barssinceentry(1); 
If (MarketPosition=0 and  marketposition(1)=1 and  c>=highd(value10) and RateOfChange(c,2)>0  
and  value10<=10)then 
  begin
    buy("buy3") 1 share next bar at o;
    flagb=3;      
  end;
  
  If (MarketPosition=0 and marketposition(1)=-1 and  c<=lowd(value10) and RateOfChange(c,2)<0 and  
  value10<=10)then
  begin 
 sellshort("sellshort3") 1 share next bar at o; 
 flags=3; 
end;
   
 {stoploss}   
 setstoploss(1500);
  If (barssinceentry = 0) then
    HiAfterEntry = High; 
  If (BarsSinceEntry >= 1) then
    HiAfterEntry = Maxlist(HiAfterEntry,High); 
  If (BarsSinceEntry = 0) then 
    LoAfterEntry = Low; 
  If (BarsSinceEntry >= 1) then
    LoAfterEntry = minlist(LoAfterEntry,Low); 
 
  if (BarssinceEntry > 0 and MarketPosition = 1 and 
  (HiAfterEntry>=entryprice*1.02 and HiAfterEntry<entryprice*1.1)) then 
  begin
   setstopcontract;
   setpercenttrailing(entryprice*0.02*bigpointvalue,70);
    StopLine = HiAfterEntry-N1*ATR;
    If c<= StopLine then 
    begin
      Sell("stopb1")  1 share this bar at c;
        flagb=0; 
   end;
   end;
   
  if (BarssinceEntry > 0 and MarketPosition = 1 and HiAfterEntry>=entryprice*1.1) then 
  begin
  setstopcontract;
   setpercenttrailing(entryprice*0.1*bigpointvalue,50);
    StopLine = HiAfterEntry-N2*ATR;
    If c<= StopLine then 
    begin
      Sell("stopb3") 1 share this bar at c;
      flagb=0;  
   end;
   end;
   
     if (BarssinceEntry > 0 and MarketPosition = 1 and HiAfterEntry<entryprice*1.02) then 
  begin
    StopLine = entryprice-N3*minpoint;
    If c crosses under StopLine then 
    begin
      Sell("stopb2") 1 share this bar at c;
      flagb=0; 
   end;
   end;
   
   If (BarsSinceEntry > 0 and MarketPosition = -1 and 
   LoAfterEntry>=entryprice*0.9 and LoAfterEntry<entryprice*0.98) then  
  begin
    setstopcontract;
   setpercenttrailing(entryprice*0.02*bigpointvalue,70);
    StopLine = LoAfterEntry+N1*ATR;
    If c>= StopLine then begin 
      BuyToCover("stops1") 1 share this bar at c;
      flags=0; 
      end;
      end;
      
   If (BarsSinceEntry > 0 and MarketPosition = -1 and LoAfterEntry<=entryprice*0.9) then  
  begin
  setstopcontract;
   setpercenttrailing(entryprice*0.1*bigpointvalue,50);
    StopLine = LoAfterEntry+N2*ATR; 
    If c>= StopLine then begin 
      BuyToCover("stops3") 1 share this bar at c;
      flags=0; 
      end;
      End;
      
         
   If (BarsSinceEntry > 0 and MarketPosition = -1 and LoAfterEntry>=entryprice*0.98) then  
  begin
    StopLine = entryprice+N3*minpoint;
    If c crosses over StopLine then begin 
      BuyToCover("stops2") 1 share this bar at c;
      flags=0; 
      end;
      End;
      end;

