# BTCPOLYARB


pulls option spread from Derebit
pulls up or down from: 
the Binance 1 minute candle for BTC/USDT (day before, '26) 12:00 in the ET timezone (noon)  == threshold 
on the following day at the same 12:00 ET candle.

looks at Polymarket yes/no.

pull yes == y, no == x
payouts 1/y, 1/x 

checks options @ threshold
see if calls spread, sell at k + delta == threshodl, buy at k, where delta is the smallest internal in strikes 
pays more than polymarket yes. 

if 
checks arb, does strat 
buys no PM and call spread in porportion 

else checks if
put spread pays more than 1/n, 
buys spread and yes in porportion

3 am options expiry, poylmarket 12 pm expiry
9 hours 

if have 
