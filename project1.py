import sys
!{sys.executable} -m pip install -r requirements.txt

#load packages
import pandas as pd
import numpy as np
import helper
import project_helper
import project_tests


####  Market data
#     Load data
df = pd.read_csv('../../data/project_1/eod-quotemedia.csv', parse_dates=['date'], index_col=False)

close = df.reset_index().pivot(index='date', columns='ticker', values='adj_close')

print('Loaded Data')

#     view data
project_helper.print_dataframe(close)

#     stock example
apple_ticker = 'AAPL'
project_helper.plot_stock(close[apple_ticker], '{} Stock'.format(apple_ticker))

####  Resample Adjusted Prices
def resample_prices(close_prices, freq='M'):

    weekly=close_prices.resample(freq).last()
    return weekly

project_tests.test_resample_prices(resample_prices)

#     view data
monthly_close = resample_prices(close)
project_helper.plot_resampled_prices(
    monthly_close.loc[:, apple_ticker],
    close.loc[:, apple_ticker],
    '{} Stock - Close Vs Monthly Close'.format(apple_ticker))


####  Compute Log Returns
def compute_log_returns(prices):
    #straightforward
    return np.log(prices) - np.log(prices.shift(1))

project_tests.test_compute_log_returns(compute_log_returns)

#     view data 
monthly_close_returns = compute_log_returns(monthly_close)
project_helper.plot_returns(
    monthly_close_returns.loc[:, apple_ticker],
    'Log Returns of {} Stock (Monthly)'.format(apple_ticker))
    
    
####  Shift Returns
def shift_returns(returns, shift_n):
    #straightforward
    return returns.shift(shift_n)

project_tests.test_shift_returns(shift_returns)

#    view data
prev_returns = shift_returns(monthly_close_returns, 1)
lookahead_returns = shift_returns(monthly_close_returns, -1)

project_helper.plot_shifted_returns(
    prev_returns.loc[:, apple_ticker],
    monthly_close_returns.loc[:, apple_ticker],
    'Previous Returns of {} Stock'.format(apple_ticker))
project_helper.plot_shifted_returns(
    lookahead_returns.loc[:, apple_ticker],
    monthly_close_returns.loc[:, apple_ticker],
    'Lookahead Returns of {} Stock'.format(apple_ticker))

####  Generate Trading Signal
def get_top_n(prev_returns, top_n):
    # TODO: Implement Function
    #new df for storing the results
    copy_df=prev_returns.copy()
    #fill it with zeros
    copy_df[:]=0
    #use iterrows to iterare over rows of returns and dates
    for date, returns in prev_returns.iterrows():
    #choose the nlargest, per date, and mark them as 1
        copy_df.loc[date, returns.nlargest(top_n).index]=1
    #convert from float64 to int64
    return copy_df.astype(np.int64) 

project_tests.test_get_top_n(get_top_n)

#     view data
top_bottom_n = 50
df_long = get_top_n(prev_returns, top_bottom_n)
df_short = get_top_n(-1*prev_returns, top_bottom_n)
project_helper.print_top(df_long, 'Longed Stocks')
project_helper.print_top(df_short, 'Shorted Stocks')


####  Projected Returns
def portfolio_returns(df_long, df_short, lookahead_returns, n_stocks):
    # TODO: Implement Function
    
    return (df_long-df_short)*lookahead_returns/n_stocks

project_tests.test_portfolio_returns(portfolio_returns)

#     view data
expected_portfolio_returns = portfolio_returns(df_long, df_short, lookahead_returns, 2*top_bottom_n)
project_helper.plot_returns(expected_portfolio_returns.T.sum(), 'Portfolio Returns')

#### Statistical Tests
#    Annualized Rate of Return
expected_portfolio_returns_by_date = expected_portfolio_returns.T.sum().dropna()
portfolio_ret_mean = expected_portfolio_returns_by_date.mean()
portfolio_ret_ste = expected_portfolio_returns_by_date.sem()
portfolio_ret_annual_rate = (np.exp(portfolio_ret_mean * 12) - 1) * 100

print("""
Mean:                       {:.6f}
Standard Error:             {:.6f}
Annualized Rate of Return:  {:.2f}%
""".format(portfolio_ret_mean, portfolio_ret_ste, portfolio_ret_annual_rate))

#    T-Test
from scipy import stats

def analyze_alpha(expected_portfolio_returns_by_date):
    # TODO: Implement Function
    t_value, p_value = stats.ttest_1samp(expected_portfolio_returns_by_date,0)

    return t_value, p_value/2

project_tests.test_analyze_alpha(analyze_alpha)

# view data 
t_value, p_value = analyze_alpha(expected_portfolio_returns_by_date)
print("""
Alpha analysis:
 t-value:        {:.3f}
 p-value:        {:.6f}
""".format(t_value, p_value))






