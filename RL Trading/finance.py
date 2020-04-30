import os
import pandas as pd
import numpy as np
 
# portfolio class definition
class portfolio: 
    def __init__(self, capital, max_alloc):
        self.capital = capital # total initial capital
        self.max_alloc = max_alloc # max invested in a single security
        self.qty = dict()
        self.book_value = dict()
        self.realized_return = dict()
    
    '''get the quantity of a given security'''
    def get_qty(self, stock_symbol):
        if stock_symbol in self.qty:
            return self.qty[stock_symbol]
        else:
            return 0
    
    '''get the book value of a given security'''
    def get_book_value(self, stock_symbol):
        if stock_symbol in self.book_value:
            return self.book_value[stock_symbol]
        else:
            return 0
        
    '''get the realized return of a given security'''
    def get_realized_return(self, stock_symbol):
        if stock_symbol in self.realized_return:
            return self.realized_return[stock_symbol]
        else:
            return 0
        
    '''buy a security in the portfolio given a qty and buying price'''
    def buy(self, stock_symbol, qty, price):
        if (qty <= 0 or price <= 0):
            return        
        if stock_symbol in self.qty:
            self.qty[stock_symbol] += qty
        else:
            self.qty[stock_symbol] = qty

        if stock_symbol in self.book_value:
            self.book_value[stock_symbol] += qty * price
        else:
            self.book_value[stock_symbol] = qty * price
        
        if stock_symbol not in self.realized_return:
            self.realized_return[stock_symbol] = 0
            
    '''sell a security in the portfolio given a qty and selling price'''
    def sell(self, stock_symbol, qty, price):
        if (qty <= 0 or price <= 0):
            return   
        if stock_symbol in self.qty and stock_symbol in self.book_value:
            if self.qty[stock_symbol] == 0:
                return
            avg_book_price = self.book_value[stock_symbol]/self.qty[stock_symbol]
            if self.qty[stock_symbol] > qty:
                self.qty[stock_symbol] -= qty                   
                self.book_value[stock_symbol] = self.qty[stock_symbol] * avg_book_price
                if stock_symbol in self.realized_return:
                    self.realized_return[stock_symbol] += (price - avg_book_price) * qty                    
            else:
                self.realized_return[stock_symbol] += (price - avg_book_price) * self.qty[stock_symbol] 
                self.qty[stock_symbol] = 0
                if stock_symbol in self.book_value:
                    self.book_value[stock_symbol] = 0
                    
    '''return the total (unrealized) return (value) of a security in portfolio given a market price'''
    def total_return(self, stock_symbol, price):
        if stock_symbol in self.qty and stock_symbol in self.book_value:
            if self.qty[stock_symbol] == 0 or self.book_value[stock_symbol] == 0:
                return 0
            market_value = price * self.qty[stock_symbol]
            return (market_value - self.book_value[stock_symbol])
        else:
            return 0
        
    '''discretized total return that returns a value in [0-9] range'''
    def discrete_return(self, stock_symbol, price):
        
        return_ratio = self.total_return(stock_symbol, price)/self.max_alloc
        
        if (return_ratio < -0.30): 
            return 0
        elif (return_ratio < -0.15):
            return 1
        elif (return_ratio < -0.05):
            return 2
        elif (return_ratio < 0):
            return 3
        elif (return_ratio == 0):
            return 4
        elif (return_ratio < 0.05):
            return 5
        elif (return_ratio < 0.15):
            return 6
        elif (return_ratio < 0.3):
            return 7
        elif (return_ratio < 0.6):
            return 8
        else:
            return 9
    
    '''returns a list of possible actions for a given security'''
    def get_allowed_actions(self, stock_symbol, price):
        # initialize set of actions with 0 (hold action)
        actions = list()
        actions.append(0)
        
        # get current book value of security in our portfolio
        book_value = self.get_book_value(stock_symbol)
       
        # we can buy more if book_value[stock] < max_alloc
        if (book_value+price <= self.max_alloc):
            actions.append(0.5)
            if (book_value+price <= self.max_alloc/2):
                actions.append(1)
        
        # we can sell if book_value[stock] > 0           
        if (book_value > 0):
            actions.append(-0.5)
            if (book_value > self.max_alloc/2):
                actions.append(-1)
        
        actions.sort()
        return actions
        
    '''
    execute an action in portfolio, and return the difference in realized returns
    before and after the action as the reward.
    actions have number values with the following meanings:
    -1.0: sell 100% of holdings of a given security
    -0.5: sell 50% of holdings of a given security
    0: do nothing (hold)
    0.5: buy 50% of a default total amount of a given security
    1.0: buy 100% of a default total amount of a given security
    ''' 
    def execute_action(self, a, stock_symbol, price):
        
        return_before = self.total_return(stock_symbol, price)
        
        # qty to be calculated by the action and allowed investment limit 
        qty = 0
        
        # validate price
        if (price <= 0):
            return 0
        # if action is hold, do nothing, return
        if (a==0):
            return 0
        # buy the security if possible 
        elif (a > 0):
            # get current book value of security in our portfolio
            book_value = self.get_book_value(stock_symbol)
            # buy if we haven't reached our max allocation (investment) limit
            if (book_value < self.max_alloc):
                allowed_qty = int((self.max_alloc - book_value)/price)
                half_qty = int((self.max_alloc/2)/price)
                if (a == 0.5):
                    qty = min(half_qty, allowed_qty)
                elif (a == 1):
                    qty = allowed_qty
                    
                # execute buy order
                self.buy(stock_symbol, qty, price)
                
        # sell the security if possible
        else:           
            # get current qty of shares of security in our portfolio
            allowed_qty = self.get_qty(stock_symbol)
            
            # sell part or all of the security if holding
            if (allowed_qty > 0):
                # get current book value of security in our portfolio
                if (a == -0.5):
                    qty = int((allowed_qty/2))
                elif (a == -1):
                    qty = allowed_qty
                    
                # execute sell order
                self.sell(stock_symbol, qty, price)
                
        return_after = self.total_return(stock_symbol, price)
        return (return_after - return_before)
        
"""returns the csv path given the symbol"""
def symbol_to_path(symbol, base_dir="data"):
    return os.path.join(base_dir, "{}.csv" .format(str(symbol)))

"""return stock data (adjusted close) for given symbols from CSV files."""
def get_data(symbols, dates):
    df = pd.DataFrame(index=dates)
    if 'GSPC' not in symbols:
        symbols.insert(0, 'GSPC')
       
    for symbol in symbols:
        df_temp = pd.read_csv(symbol_to_path(symbol), index_col='Date',
                              parse_dates=True, usecols=['Date', 'Adj Close'], 
                              na_values=['nan'])
        df_temp = df_temp.rename(columns = {'Adj Close':symbol})
        df = df.join(df_temp)
        if symbol == 'GSPC':
            df = df.dropna(subset=['GSPC'])
        
    return df

"""returns the price momentum 
given price as 1-dim series, start index and n_days time frame"""
def momentum(price, start, n_days):
    if (start-n_days) < 0:
        return 0
    else:
        return price[start] / price[start-n_days] - 1

"""returns a pandas series containing the price momentums
given price as 1-dim series and n_days time frame"""
def momentum_series(price, n_days):
    return price.pct_change(n_days)[n_days:]

"""applies a series of functions to the price data series
and returns the normalized, discretized momentum"""
def get_discrete_momentum_series(price, n_days):
    
    # calculate the momentum and store in data series
    momentum_ds = momentum_series(price, n_days)
    
    # normalize the momentum values between 0 and 1
    norm_mom_ds = min_max_normalize(momentum_ds)
    
    # get the thresholds used for discretizing the normalized momentum values
    thresholds = discrete_thresholds(norm_mom_ds, 10)
    
    # get the discretized momentum values in a data series
    disc_norm_mom_ds = discretize_series(norm_mom_ds, thresholds)
    return disc_norm_mom_ds
    
"""returns the price[t] to n_days simple moving average ratio 
given the price as 1-dim series, start index and n_days time frame"""
def price_sma(price, n_days, start=None):
    if start is None:
        start = n_days
        
    if (start-n_days) < 0:
        return 0
    else:
        return price[start] / price[start-n_days:start].mean() - 1

"""returns a pandas series contating price to simple moving average ratio 
given the price as 1-dim series, start index and n_days time frame"""
def price_sma_series(price, n_days, start=None):
    if start is None:
        start = n_days
        
    if (start-n_days) < 0:
        return pd.Series()
    else:
        return pd.Series(price[start:].values / price[start-n_days:start].mean() - 1)

"""applies a series of functions to the price data series
and returns the normalized, discretized price to sma ratio (psr)"""
def get_discrete_price_sma_series(price, n_days, start=None):
    if start is None:
        start = n_days
        
    # calculate the psr and store in data series
    psr_ds = price_sma_series(price, n_days, start)
    
    # normalize the psr values between 0 and 1
    norm_psr_ds = min_max_normalize(psr_ds)
    
    # get the thresholds used for discretizing the normalized psr values
    thresholds = discrete_thresholds(norm_psr_ds, 10)
    
    # get the discretized psr values in a data series
    disc_norm_psr_ds = discretize_series(norm_psr_ds, thresholds)
    return disc_norm_psr_ds

"""returns the ratio of price-sma and bollinger band (2 std)
given the price as 1-dim series, start index, and n_days time frame"""
def price_bb(price, n_days, start=None):
    if start is None:
        start = n_days
        
    if (start-n_days) < 0:
        return 0
    else:
        price_sma_delta = price[start] - price_sma(price, n_days, start)
        bollinger_band = 2*price[start-n_days:start].std()
        return price_sma_delta / bollinger_band

"""returns pandas series containing the ratio of price-sma and bollinger band (2 std)
given the price as 1-dim series, start index, and n_days time frame"""
def price_bb_series(price, n_days, start=None):
    if start is None:
        start = n_days
        
    if (start-n_days) < 0:
        return pd.Series()
    else:
        price_sma_delta = pd.Series(price[start:].values - price_sma_series(price, n_days, start))
        bollinger_band = 2*price[start-n_days:start].std()
        return price_sma_delta / bollinger_band
    
"""applies a series of functions to the price data series
and returns the normalized, discretized price to bollinger band ratio (pbr)"""
def get_discrete_price_bb_series(price, n_days, start=None):
    if start is None:
        start = n_days
        
    # calculate the pbr and store in data series
    pbr_ds = price_bb_series(price, n_days, start)
    
    # normalize the pbr values between 0 and 1
    norm_pbr_ds = min_max_normalize(pbr_ds)
    
    # get the thresholds used for discretizing the normalized pbr values
    thresholds = discrete_thresholds(norm_pbr_ds, 10)
    
    # get the discretized pbr values in a data series
    disc_norm_pbr_ds = discretize_series(norm_pbr_ds, thresholds)
    return disc_norm_pbr_ds

"""normalizes a dataframe using min and max and returns the result
result will be between 0 and 1"""
def min_max_normalize(data):
    minimum = data.min()
    maximum = data.max()
    data_range = maximum - minimum
    return ( data - minimum ) / data_range

"""normalizes a dataframe and returns the result
result will have mean=0 and std=1"""
def mean_std_normalize(data):
    mean = data.mean()
    std = data.std()
    return ( data - mean ) / std

"""given a data series and number of bins, 
returns a numpy array with thresholds that can be used to discretize the data"""
def discrete_thresholds(data, num_bins):
    if num_bins == 0:
        return
    step_size = len(data) / num_bins
    sorted_data_series = pd.Series(list(data.sort_values()))
    thresholds = np.empty([num_bins])
    for i in range(0, num_bins):
        thresholds[i] = sorted_data_series[int((i+1)*step_size)-1]
    return thresholds

"""given a float number and a set of threshold values
returns an integer"""
def discretize(num, thresholds):
    if len(thresholds) == 0:
        return 0
    num_bins = len(thresholds)
    i = num_bins-1
    while (i >= 0):
        if (num < thresholds[i]):
            i = i - 1
        else: 
            return i+1
        
    return 0

"""vectorized implementation of the discretize function applied to a series"""
def discretize_series(ds, thresholds):
    vect_disc_func = np.vectorize(discretize, excluded=['thresholds'])
    return pd.Series(vect_disc_func(ds, thresholds=thresholds))


    

        