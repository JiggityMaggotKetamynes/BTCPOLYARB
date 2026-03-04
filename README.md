Polymarket event: Bitcoin Up or Down - 1 hour @ 0700 - 0800 UTC everyday. 0700 = t.
up or down from BTC/USDT 1 hour candle that begins on the time and date specified in the title
which comes from Binance (almost positive it's the 1 hour *open*, not lesser time increments) 

call spread: 
*open*
sell
buy 
                   
put spread:
buy 
sell
*open*

On derebit, the strike prices between options contracts are separated by 500 dollars 
|strike 1 - strike 2| == 500 dollar increments, which represent a variable cost when buying and selling( a net cost) less than or equal to 500, that pays strictly 500
normalizing polymarket requires us to buy 500 x (cost from (0,1), which tells us the cost to acquire the payout for payout strictly 500

in the last 30 days, the absolute difference of the price at p @ 0800- p @ 0700 closes in ~ on 200, that means that there is a good shot that if our 
strategy is more profitable at the prices closer to the strikes than there our plenty of days due to high nominal value of change that it would run into a favorable 
condition

examples:

1 - call spread
-- 
price at 65030 = c 

sell 65000
buy 64500
check that payout exceeds polymarket +2% (slippage, fees) (down arrow)
but no on polymarket ( up arrow)
we want the call to come up on a low price, and polymarket to come down on c
arb condition fulfilled if price finishes above 65000, or below 65030

65029 pays from PM

2 - put spread 
-- 
price at 65495

put spread ( sell above threshold which pays strictly 1 below) // I believe the sell is the reference point for anything below
buy at 67000
sell at 66500 ( anything below 66 pays strictly 1) 

buy yes on PM such that everything above 65495 pays strictly 1

example 65497 pays from PM, 



Christoper's Additions:

- If the trading fees can be accessed by the api then they should be set programaticly, if not then you should be able to take in trading fees either through CSV or CLI interface.

fees are completely negligible with minimum order size and assuming our deviation still exists when order book depth is within ~5% of the average which will offer us in the decimal points of slippage + 0.1% fee on everything on polymarket.... derebit/binance fees amount: 0.03% of notional value for options orders.

- Time slipage needs to be backtest to make sure that the arbitrage opetunity doesn't slip away between the time that the script sees the opertunity and the execution of the order on both markets. There are two approches that we can take to this end:

my solution:

what is the smallest, most obvious way to detect a positive arbitrage opporuntity 
-- 
options contract (sold-bought) --> cost variable, 1/ cost variable --> payout per optiosn chain 
1) call spread payout, our options yes, yes_call
2) put spread payout, our options no, no_call

polymarket payouts, 1/y, 1/n 

backtest, or creation of loop that will check, must confirm, by how much, and whether these opporutunities exist in our time slot

when

yes_call >  yes_PM && (1 - yes_call) < no_PM

how much more does it pay (( this metric will be easy to infer arb edge from) )) 

no_call > no_Pm && (1 - no_call) < yes_pm

having this collection per day, would actually us to see, even based on one day, whether payouts increase closer or farther away from our relatively clumsy bounds from the options strikes

- we do back testing to figure out how long they last. If you have optunities that persit for several hours or days the is likly not a real issue but if the oppertunites last for several seconds then this become a major statical issue.
    
- Since the script is running on a loop that repeats every so often eg 30 sec, on min, 5min etc then we can do back testing to figure out what is the optimum time interval to detect these arb opps. Obviously we will only know the min amount of time after we write the script but since we are using python and have stacking tolarences between differnt apis as well as python's slower speed especily if we are doing non trival math assume that the min time for each loop would be abt a 60secs.

If this is too slow and we are missing good arb opps then we can proably get down to something like a 10 sec loop if we try to rerite the script in something like Go, but if we are talking about 5min or so oppertunitys then the actual time problem becomes trival.

- Oppertunity cost back tests: once we have the script running the we come to the best type of problem to have how much do we put in. We are WELL withing the short term cap gains window so we can basicly buy the arb and then sell it as soon as it closes. We have two opertunity costs to account for frequency and duration.

- Duration: if the arb opp is a dimond shape (i guess it would techincly rhombus) then it would be worth backtesting to figure out if we should strike once and try to get as close to the wide point as possible or if we take a statistical approch and try to spread our trades out through out the dimond either equaltly or accoriding to a distribution. Of note is this is again dependent on the duration of the arb opps. If they only last for like 200% of the time it takes the program to loop then this becomes a moot point.

- Frequency: ideally the arb opps would all be sequenctial where if you have $100,000 then you just dump all the cash into the first trade and make $1,000 and sell when it closes and then repeat for the next one and make $2,200 so on but the problem is if they are nested (see figure 1) in this case it might be worth selling and buying the dip (assuming the spike isn't below slipage). Though this for whatever reason Im having a heard to intuiting if this is the correct stratigy. 








