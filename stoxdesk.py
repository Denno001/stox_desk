import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu
import plotly.graph_objs as go
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
from newsapi import NewsApiClient
from datetime import datetime
import mplfinance as mpf
import matplotlib.pyplot as plt

#..page set up
st.set_page_config(page_title='Stox Desk',layout='wide')

#removing white space on top
st.markdown("""
        <style>
               .block-container {
                    padding-top: 1.5rem;
                    padding-bottom: 0rem;
                    padding-left: 1rem;
                    padding-right: 1rem;
                }
        </style>
        """, unsafe_allow_html=True)

#..API keys...




#..uploading logo pic....
uploaded_image = (r"stox_logo2.png")
image = Image.open(uploaded_image)
#st.image(image, use_column_width=None)
#..squeezing/insering logo image using columns
col1, col2, col3,col4 = st.columns([1,1.5,2,7])
with col1:
    st.image(image,use_column_width=None)
with col2:
    st.write('### Stocks Desk')
with col3:
    st.write('')
with col4:
    st.write('')

#..squeezing ticker search input using columns
buff, col, buff2 = st.columns([1,3,1])

#..ticker symbol input
ticker_symbol = buff.text_input('Search ticker:')

#..calculating % change...
#Dow Jones, S&P 500, NASDAQ, and NYSE Composite tickers
tickers = ["^DJI", "^GSPC", "^IXIC", "^NYA"]


# Download historical data for the tickers
data = yf.download(tickers, period="ytd", interval="1d")

# loop to calculate YTD percentage change for each ticker
ytd_percentage_change = {}
for ticker in tickers:
    ytd_returns = (data['Adj Close'][ticker] / data['Adj Close'][ticker].iloc[0] - 1) * 100
    ytd_returns = round(ytd_returns,2)
    ytd_percentage_change[ticker] = ytd_returns
    
# Create a DataFrame to display the results
ytd_df = pd.DataFrame(ytd_percentage_change)
ytd_df.columns = ["Dow Jones", "S&P 500", "NASDAQ", "NYSE Composite"]
ytd_df.index.name = "Date"
latest_value = ytd_df.tail(1)
#latest_value

#..calculating period/value change for each index....
data = yf.download(tickers,period='ytd',interval='1d')

#.loop for each ticker value change..
ytd_value_change = {}
for ticker in tickers:
    ytd_change = data['Adj Close'] - data['Adj Close'].iloc[0]
    ytd_change = round(ytd_change,2)
    ytd_value_change[ticker] = ytd_change
    
ytd_diff = pd.DataFrame(ytd_change)
ytd_diff.columns = ["Dow Jones", "S&P 500", "NASDAQ", "NYSE Composite"]
ytd_diff.index.name = "Date"
latest_diff = ytd_diff.tail(1)
#latest_diff

#..getting scanner data top gainers vs top losers
url = 'https://thestockmarketwatch.com/markets/topstocks'

response = requests.get(url) #.send request to url
soup = BeautifulSoup(response.content, 'html.parser') #.parse content

table1 = soup.find('table') #.find 1st table

top_gainers = pd.read_html(str(table1))[0] #.insert table in pd dataframe

table2 = soup.find_all('table')[1]  # finding 2nd table
top_losers = pd.read_html(str(table2))[0]
#top_losers
#top_gainers

# formatting and modifying data in tables
#.removing k from Volume column and dividing by 1000
top_gainers['Volume'] = pd.to_numeric(top_gainers['Volume'].str.replace('k', '')) / 1000
#.introducing m(million) and k(thousand)
top_gainers['Volume'] = top_gainers['Volume'].apply(lambda x: f'{x:.2f}M' if x>=1 else f'{x*1000:.0f}K')  #..the :.2f is f' for rounding
top_gainers = top_gainers[['Symb','Last','%Chg','Volume']]    #..filtering columns to show
top_gainers.rename(columns={'Symb':'Ticker', '%Chg': 'Change'},inplace=True) #..renaming some
top_gainers.set_index('Ticker',inplace=True)      #..index column
def apply_green(val):    #..func to change color
    color = 'green' if '%' in val else 'black'
    return 'color: {}'.format(color)
top_gainers = top_gainers.style.applymap(apply_green,subset=pd.IndexSlice[:,['Change']])
top_gainers.format({'Last': '{:.2f}'})
#top_gainers

#.removing k from Volume column and dividing by 1000
top_losers['Volume'] = pd.to_numeric(top_losers['Volume'].str.replace('k', '')) / 1000
#.introducing m(million) and k(thousand)
top_losers['Volume'] = top_losers['Volume'].apply(lambda x: f'{x:.2f}M' if x>=1 else f'{x*1000:.0f}K')  #..the :.2f is f' for rounding
top_losers = top_losers[['Symb','Last','%Chg','Volume']]    #..filtering columns to show
top_losers.rename(columns={'Symb':'Ticker', '%Chg': 'Change'},inplace=True) #..renaming some
top_losers.set_index('Ticker',inplace=True)      #..index column
def apply_red(val):    #..func to change color
    color = 'red' if '%' in val else 'black'
    return 'color: {}'.format(color)
top_losers = top_losers.style.applymap(apply_red,subset=pd.IndexSlice[:,['Change']])
top_losers.format({'Last': '{:.2f}'})
#top_losers

# market news

def market_news():
    newsapi = NewsApiClient(api_key=news_api_key)
    news_articles = newsapi.get_top_headlines(category='business', language='en', country='us') #.fetch general stock news.
    result = ""
    
    for i, article in enumerate(news_articles['articles'][:15], 1): #.display 1st 15 articles
        result += f"Title: {article['title']}\n"
        result += f"URL: {article['url']}\n\n" #.the n/n is for line spacing
        if i == 15:
            break   #..end loop after first 15
    return result

#..function for horizontal menu bar & ticker search..
def stox_menu():
    options = ['Home','Markets', 'News', 'Earnings', 'Forex', 'Crypto', 'Commodities', 'Subscribe']
    icons = ['cast','graph-up-arrow', 'menu-up', 'piggy-bank', 'currency-exchange', 'currency-bitcoin', 'coin',
             'envelope-at-fill']
    
    if ticker_symbol:     #..checks if ticker is entered
        types = ['candle','line','ohlc']
        #type = st.selectbox('',types)
        periods = ['ytd','6mo','1y','2y','5y','10y','max']
        #period = st.selectbox('',periods)

        

        url = f'https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker_symbol}&apikey={av_api_key}'
        r = requests.get(url)
        overview_data = r.json()
        #st.write(data)

        col1, col2,col3,col4,col5,col6 = st.columns([1,0.5,1,2,0.5,0.5],gap='small')
        col1.write(overview_data['Name'])
        col2.write(overview_data['Symbol'])
        col3.write(overview_data['Sector'])
        col4.write(overview_data['Industry'])
        col5.write(overview_data['Exchange'])
        col6.write(overview_data['Country'])

        # row for type, period and metric
        col7, col8, col9, col10 = st.columns([0.5,1,1,1.5],gap='small')
        type = col9.selectbox('',types)
        period = col8.selectbox('',periods)

        data = yf.download(ticker_symbol, period=period)
        daily_change = data['Adj Close'].pct_change() * 100  #..daily % change
        last_change = daily_change[-1]
        #f'{last_change:.2f}%'     #..rounding off
        last_price = data['Adj Close'][-1]
        #f'{last_price:.2f}'

        dat = f"{data.index[-1]}"
        dat = datetime.strptime(dat, '%Y-%m-%d %H:%M:%S') # parsing string to datetime
        dat = dat.strftime('%b-%d')   #.droping year, time and changing month to string
        #dat

        with col7:
            st.metric(label=f'{dat} (04:00PM ET)',value=f'{last_price:.2f}',delta=f'{last_change:.2f}%')
        col10 = st.write('')

        # Plot the chart
        fig, axes = mpf.plot(data, type=type, style='yahoo', title='', ylabel='', volume=True, ylabel_lower='M', returnfig=True)
        fig.set_size_inches(6, 3)  # resize width and height separately

        for ax in axes:          #.background color inside chart
            ax.patch.set_facecolor('skyblue')
            ax.tick_params(axis='x', labelsize=4.5)  #size x and y labels size
            ax.tick_params(axis='y', labelsize=5)
        st.write(fig)

        #...making huge figures easily readable...
        variables = {'Market Cap': int(overview_data['MarketCapitalization']), 'EBITDA': int(overview_data['EBITDA']), 
                     'Revenue': int(overview_data['RevenueTTM']), 'Gross Profit': int(overview_data['GrossProfitTTM']),
                       'Shares Outstanding': int(overview_data['SharesOutstanding'])}
        new_values = {}

        for key, value in variables.items():
            if value >= 1000000000000:
                new_values[key] = f'{value / 1000000000000:.2f}T'
            elif value >= 1000000000:
                new_values[key] = f'{value / 1000000000:.2f}B'
            elif value >= 1000000:
                new_values[key] = f'{value / 1000000:.2f}M'
            elif value >= 1000:
                new_values[key] = f'{value / 1000:.2f}K'
            else:
                new_values[key] = value
        
        #..2nd dict to parse remaining values...
        other_variables = {'Book Value': overview_data['BookValue'], 'Dividend Per Share': overview_data['DividendPerShare'], 
                   'Dividend Yield': overview_data['DividendYield'], 'EPS': overview_data['EPS'], 'Profit Margin': overview_data['ProfitMargin'],
                  'Operating Margin': overview_data['OperatingMarginTTM'], 'Return On Assets': overview_data['ReturnOnAssetsTTM'],
                  'Return on Equity': overview_data['ReturnOnEquityTTM'], '52 Week High': overview_data['52WeekHigh'], 
                   '52 Week Low': overview_data['52WeekLow'], 'Beta': overview_data['Beta'], 'Forward PE': overview_data['ForwardPE'],
                  'P/S': overview_data['PriceToSalesRatioTTM'],'P/B': overview_data['PriceToBookRatio'],
                  'Target Price': overview_data['AnalystTargetPrice']}
        
        final_variables = {**new_values, **other_variables}     #.merging dicts
        
        #.. slicing first 10 rows in dict
        def top_dict(d):
            sliced_dict = {}
            count = 0
            for key, value in d.items():
                if count < 10:
                    sliced_dict[key] = value
                    count += 1
                else:
                    break
            return sliced_dict
        first_dict = top_dict(final_variables)

        #..slicing last 10 rows in dict
        def bottom_dict(d):
            sliced_dict = {}
            count = 0
            for key in reversed(list(d.keys())):        #.iterate reversed dict
                if count < 10:
                    sliced_dict[key] = d[key]
                    count += 1
                else:
                    break
            return sliced_dict
        bot_dict = bottom_dict(final_variables)

        col1, col2 = st.columns(2)
        with col1:
            st.table(first_dict)
        with col2:
            st.table(bot_dict)
        
        def ticker_news():
            newsapi = NewsApiClient(api_key=news_api_key)
            query = ticker_symbol
            news_articles = newsapi.get_everything(q=query, language='en', sort_by='publishedAt', page_size=10)
            result = ''
            for i, article in enumerate(news_articles['articles'][:10], 1):
                result += f"Title: {article['title']}\n"
                result += f"URL: {article['url']}\n\n"
                if i == 10:
                    break
            return result
        col3, col4 = st.columns([2,1],gap='small')
        col3.subheader('Company News')
        with col3:
            with st.container(border=True,height=500):
                st.write(ticker_news())
        col4.subheader('Profile')
        with col4:
            with st.container(border=True):
                st.write(overview_data['Description'])     
    else:
        selected = option_menu(
            menu_title='',
            options=options,
            icons=icons,
            default_index=0, orientation='horizontal'
        )
        if selected == 'Markets':
            st.write(latest_value)
            st.write(latest_diff)
        elif selected == 'News':
            st.write('News Today')
        elif selected == 'Earnings':
            st.write('Earnings Calendar')
        elif selected == 'Forex':
            st.write('Forex Markets')
        elif selected == 'Crypto':
            st.write('Crypto Markets')
        elif selected == 'Commodities':
            st.write('Various Commodities')
        elif selected == 'Subscribe':
            st.write('Enter Email')
        elif selected == 'Home':
              #..func for plotting and printing indicies charts
            def index_charts(index_name, index_symbol):
                data = yf.download(index_symbol, period='ytd', interval='1d')
                fig = go.Figure(data=[go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name="Candlesticks",)])
                
                fig.update_layout(
                    title=f"{index_name}",
                    xaxis_title='',
                    yaxis_title='Price',
                    xaxis_rangeslider_visible=False,
                    plot_bgcolor='lightgray',
                    width=300,
                    height=300)
                
                return fig
            
              #..dict to parse index_symbols
            index_symbols = {'Dow Jones': '^DJI', 'S&P 500': '^GSPC',
                  'NASDAQ': '^IXIC', 'NYSE Composite': '^NYA'}
            
            dow = index_charts('Dow Jones', index_symbols['Dow Jones'])
            nasdaq = index_charts('NASDAQ', index_symbols['NASDAQ'])
            sp = index_charts('S&P 500', index_symbols['S&P 500'])
            nyse = index_charts('NYSE Composite', index_symbols['NYSE Composite'])

            col1, col2, col3,col4 = st.columns(4,gap='small') #.inserting 4 charts columns

            subcol1, subcol2 = col1.columns([1,2],gap='small')
            subcol2.metric(label="", value= f'{latest_value.iloc[0,0]}%', delta= latest_diff.iloc[0,0])
            subcol1.write(dow)

            subcol3, subcol4 = col2.columns([1,2],gap='small')
            subcol3.write(nasdaq)
            subcol4.metric(label='', value = f'{latest_value.iloc[0,2]}%', delta= latest_diff.iloc[0,2])

            subcol5, subcol6 = col3.columns([1,2],gap='small')
            subcol5.write(sp)
            subcol6.metric(label="", value = f'{latest_value.iloc[0,1]}%', delta = latest_diff.iloc[0,1])

            subcol7, subcol8 = col4.columns([1,2],gap='small')
            subcol7.write(nyse)
            subcol8.metric(label="", value = f'{latest_value.iloc[0,3]}%', delta = latest_diff.iloc[0,3])
             
            #.top gainers and top losers tables... 
            col5, col6, col7,col8 = st.columns([0.7,0.7,1.5,0.2],gap='small')
            col5.subheader('Top Gainers')
            col6.subheader('Top Losers')
            col7.subheader('Markets Headlines')
            col5.write(top_gainers)
            col6.write(top_losers)
            with col7:
                with st.container(height=400):
                    st.write(market_news())
            col8.write('')

    
    return ''


#m1, m2 = st.columns([1,0.17])
#with m1:
#    st.write(stox_menu())
st.write(stox_menu())
