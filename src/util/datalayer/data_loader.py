
import requests
import uqer
from uqer import DataAPI
from src.util.exception import RequestError, InputParameterError
import pandas as pd, json
from src.util.config import TOKEN, INDEX_NAME_MAPPING, DATAYES_FACTOR_ORDER

class DataAPILoader:
    def __init__(self, inner_api=True):
        self.inner_api = inner_api
        self.session = requests.session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=100, pool_maxsize=100)
        if not inner_api:
            self.session.mount('https://api.wmcloud.com:443', adapter)
            self.token = TOKEN
        else:
            self.session.mount('http://vip.newapi.wmcloud.com/', adapter)
        self.client = uqer.Client(token=TOKEN)

    def get_request_result(self, url):
        if not self.inner_api:
            data = self.session.get(
                "https://%s:%d/data/v1%s" % ('api.wmcloud.com', 443, url),
                headers={
                    "Authorization": "Bearer " + self.token,
                    'Connection': 'keep-alive'
                })
        else:
            data = self.session.get(
                "http://%s/%s" % ('vip.newapi.wmcloud.com', url))
        data = json.loads(data.content)
        if data[u'retCode'] == 1:
            return pd.DataFrame.from_dict(data['data'])
        else:
            msg = 'load data fail, reason %s' % data['retMsg']
            raise RequestError(message=msg)

    def get_benchmark_weight(self, trading_day_list, ticker_name):
        ticker = INDEX_NAME_MAPPING[ticker_name]
        benchmark_weight_dict = {}
        for date in trading_day_list:
            df = self.get_request_result(
                '/api/idx/getIdxWeight.json?field=&ticker=%s&secID=&callback=&beginDate=%s&endDate=%s&dataType='
                % (ticker, date, date))
            res = df[['consID', 'weight']].set_index('consID')['weight']
            res /= 100.
            wegight_sum = res.sum()
            # res = res.divide(wegight_sum)
            benchmark_weight_dict[date] = res
        return benchmark_weight_dict

    def get_idx_universe(self, trading_day_list, benchmark):
        ticker = INDEX_NAME_MAPPING.get(benchmark)
        universe_list_dict = {}
        for date in trading_day_list:
            df = self.get_request_result(
                '/api/idx/getIdxWeight.json?field=&ticker=%s&secID=&callback=&beginDate=%s&endDate=%s&dataType='
                % (ticker, date, date))
            universe_list_dict[date] = list(df['consID'])
        return universe_list_dict

    def get_trading_day_list(self, start, end, frequency, exchange_cd='XSHG'):
        """
		输入起始日期和频率，即可获得日期列表（daily包括起始日，其余的都是位于起始日中间的）
		输入：
		start，开始日期，'YYYYMMDD'形式
		end，截止日期，'YYYYMMDD'形式
		frequency，频率，day为所有交易日，week为每周最后一个交易日，month为每月最后一个交易日，quarter为每季最后一个交易日
		返回：
		获得list型日期列表，以'YYYYMMDD'形式存储
		"""
        df = DataAPI.TradeCalGet(
            exchangeCD=exchange_cd,
            beginDate=start,
            endDate=end,
            field=u"",
            pandas="1")
        df['calendarDate'] = df['calendarDate'].apply(
            lambda x: x.replace('-', ''))
        if frequency == 'quarter':
            res = df.query('isQuarterEnd==1')
        elif frequency == 'semi':
            res = df.query('isQuarterEnd==1')
            res = res.reset_index()
            res = res.loc[res['calendarDate'].apply(
                lambda x: (x[4:6] == '06' or x[4:6] == '12'))]
        elif frequency == 'month':
            res = df.query('isMonthEnd==1')
        elif frequency == 'week':
            res = df.query('isWeekEnd==1')
        elif frequency == 'day':
            res = df.query('isOpen==1')
        else:
            raise ValueError('调仓频率必须为day/week/month/quarter/semi！！！')
        return list(res['calendarDate'])

    def get_latest_trading_day_map(self):
        df = DataAPI.TradeCalGet(exchangeCD=u"XSHG", field=u"", pandas="1")
        df['calendarDate'] = df['calendarDate'].apply(
            lambda x: x.replace('-', ''))
        trading_day_series = df[df['isOpen'] == 1]['calendarDate']
        trading_day_series.index = trading_day_series.values
        df.set_index('calendarDate', inplace=True)
        df['tradeDate'] = trading_day_series
        df['tradeDate'].fillna(method='ffill', inplace=True)
        return df['tradeDate']

    def get_sw_industry_classification(self, trading_day_list, universe):
        industry_classification = {}
        for date in trading_day_list:
            df = DataAPI.EquIndustryGet(
                secID=universe,
                industryVersionCD=u"010303",
                industry=u"",
                intoDate=date,
                field=u"secID,industryName1",
                pandas="1")
            df.set_index('secID', inplace=True)
            df.rename(columns={'industryName1': 'ind'}, inplace=True)
            industry_classification[date] = df['ind']
        return industry_classification

    def get_float_mkt_cap(self, trading_day_list, sec_ids):
        float_mkt_cap_dict = {}
        for date in trading_day_list:
            df = DataAPI.MktEqudGet(
                secID=sec_ids,
                tradeDate=date,
                field=u"secID,negMarketValue",
                pandas="1")
            df.set_index('secID', inplace=True)
            float_mkt_cap_dict[date] = df['negMarketValue']
        return float_mkt_cap_dict

    def get_equity_overnight_return(self, trading_day_list, sec_ids):
        equity_overnight_return_dict = {}
        for date in trading_day_list:
            df = DataAPI.MktEqudGet(
                secID=sec_ids,
                tradeDate=date,
                field=u"secID,openPrice,preClosePrice",
                pandas="1")
            df['overnight_return'] = df['openPrice'] / df['preClosePrice'] - 1
            df.set_index('secID', inplace=True)
            equity_overnight_return_dict[date] = df['overnight_return']
        return equity_overnight_return_dict

    def get_open_price(self, trading_day_list, sec_ids):
        open_price_dict = {}
        for date in trading_day_list:
            df = DataAPI.MktEqudGet(
                secID=sec_ids,
                tradeDate=date,
                field=u"secID,openPrice",
                pandas="1")
            df.set_index('secID', inplace=True)
            open_price_dict[date] = df['openPrice']
        return open_price_dict

    def get_equity_reinvest_return(self, trading_day_list, sec_ids,
                                   freq='day'):
        equity_reinvest_return_dict = {}
        trading_day_list.sort()
        for i, date in enumerate(trading_day_list):
            if freq == 'day':
                df = DataAPI.EquRetudGet(
                    secID=sec_ids,
                    beginDate=date,
                    endDate=date,
                    field=u"secID,dailyReturnReinv",
                    pandas="1")
                equity_reinvest_return_dict[date] = df.fillna(0).set_index(
                    'secID')['dailyReturnReinv']

            else:
                if i > 0:
                    last_period_end = trading_day_list[i - 1]
                    df = DataAPI.EquRetudGet(
                        secID=sec_ids,
                        beginDate=last_period_end,
                        endDate=date,
                        field=u"secID,dailyReturnReinv,tradeDate",
                        pandas="1")
                    df['tradeDate'] = df['tradeDate'].apply(
                        lambda x: x.replace('-', ''))
                    df = df[df['tradeDate'] > last_period_end]
                    df.drop('tradeDate', axis=1, inplace=True)
                    df['dailyReturnReinv'] = df['dailyReturnReinv'] + 1
                    return_reinv = df.groupby('secID').prod(skipna=True) - 1
                    equity_reinvest_return_dict[date] = return_reinv[
                        'dailyReturnReinv']
        return equity_reinvest_return_dict

    def get_specific_risk(self, trading_day_list, sec_ids):
        specific_risk_dict = {}
        for date in trading_day_list:
            specific_risk = {}
            res = \
             DataAPI.RMSriskShortGet(tradeDate=date, secID=sec_ids, field=u"secID,SRISK", pandas="1").set_index(
              'secID')[
              'SRISK'] / 100.
            specific_risk['specific_risk'] = res
            specific_risk_dict[date] = specific_risk
        return specific_risk_dict

    def get_risk_model(self, trading_day_list, universe):
        result = {}
        specific_return = {}
        for date in trading_day_list:
            result[date] = {}
            result[date]['exposure'] = DataAPI.RMExposureDayGet(
                secID=universe,
                tradeDate=date).set_index('secID').iloc[:, 4:-1]
            result[date]['factor_covariance'] = DataAPI.RMCovarianceShortGet(
                tradeDate=date).set_index('Factor').iloc[:, 2:-1] / 10000.
            result[date]['specific_risk'] = \
             DataAPI.RMSriskShortGet(secID=universe, tradeDate=date).set_index('secID')['SRISK'] / 100.
            specific_return[date] = \
             DataAPI.RMSpecificRetDayGet(secID=universe, tradeDate=date).set_index('secID')['spret']

        return result, specific_return

    def get_specific_return(self, trading_day_list, universe):
        specific_return = {}
        for date in trading_day_list:
            specific_return[date] = \
                DataAPI.RMSpecificRetDayGet(secID=universe, tradeDate=date).set_index('secID')['spret']
        return specific_return

    def get_factor_return(self, trading_day_list, freq='day'):
        factor_return_dict = {}

        trading_day_list.sort()
        for i, date in enumerate(trading_day_list):
            if freq == 'day':
                factor_return_dict[date] = DataAPI.RMFactorRetDayGet(tradeDate=date,field=u"",pandas="1")[DATAYES_FACTOR_ORDER].T[0]

            else:
                if i > 0:
                    last_period_end = trading_day_list[i - 1]
                    df = DataAPI.RMFactorRetDayGet(beginDate=last_period_end, endDate=date,field=u"",pandas="1")
                    df['tradeDate'] = df['tradeDate'].apply(lambda x: x.replace('-', ''))
                    df = df[df['tradeDate'] > last_period_end]
                    df.drop(['tradeDate', 'updateTime'], axis=1, inplace=True)
                    df += 1
                    factor_return_dict[date] = df.prod() - 1

        return factor_return_dict

    def get_stock_return(self, begin_date, end_date, freq='month'):
        if freq == 'week':
            stock_return = DataAPI.MktEquwGet(
                beginDate=begin_date,
                endDate=end_date,
                field=['secID', 'endDate', 'chgPct'])
            stock_return = stock_return.pivot(
                index='endDate', columns='secID', values='chgPct')
            stock_return.index = stock_return.index.str.replace('-', '')
        elif freq == 'month':
            stock_return = DataAPI.MktEqumGet(
                beginDate=begin_date,
                endDate=end_date,
                field=['secID', 'endDate', 'chgPct'])
            stock_return = stock_return.pivot(
                index='endDate', columns='secID', values='chgPct')
            stock_return.index = stock_return.index.str.replace('-', '')
        elif freq == 'day':
            stock_return = DataAPI.MktEqudGet(
                beginDate=begin_date,
                endDate=end_date,
                field=['secID', 'tradeDate', 'chgPct'])
            stock_return = stock_return.pivot(
                index='tradeDate', columns='secID', values='chgPct')
            stock_return.index = stock_return.index.str.replace('-', '')
        else:
            raise InputParameterError('不支持的频率格式')

        return stock_return

    def get_factor_signal(self, trading_day_list, universe, factor_name):
        factor_signal = {}
        for date in trading_day_list:
            factor = DataAPI.MktStockFactorsOneDayGet(
                tradeDate=date,
                secID=universe,
                field="secID,%s" % factor_name,
                pandas="1").set_index('secID')
            factor_signal[date] = factor[factor_name]
        return factor_signal

    def get_bond_valuation(self, trading_day_list, universe):
        bond_valuation_df_dict = {}
        for trading_day in trading_day_list:
            bond_valuation_df = DataAPI.BondValuationShClearingGet(
                secID=universe, beginDate=trading_day, endDate=trading_day)
            bond_valuation_df_dict[trading_day] = bond_valuation_df[[
                'grossPx', 'AI', 'netPx', 'YTM', 'modifiedDuration',
                'convexity'
            ]]
        return bond_valuation_df_dict

    def get_bond_info(self, universe_list):
        df = DataAPI.BondGet(secID=universe_list)
        idx = df['actMaturityDate'].isnull()
        df['actMaturityDate'][idx] = df['maturityDate'][idx]
        df['actMaturityDate'] = df['actMaturityDate'].apply(
            lambda x: str(x).replace('-', ''))
        df['maturityDate'] = df['maturityDate'].apply(
            lambda x: str(x).replace('-', ''))

        idx = df['listDate'].isnull()
        df['listDate'][idx] = df['publishDate'][idx]
        df['listDate'] = df['listDate'].apply(
            lambda x: str(x).replace('-', ''))
        df['publishDate'] = df['publishDate'].apply(
            lambda x: str(x).replace('-', ''))
        return df

    def get_bond_cf(self, universe_list):
        df = DataAPI.BondCfGet(secID=universe_list)
        df['paymentDate'] = df['paymentDate'].apply(
            lambda x: str(x).replace('-', ''))
        return df[['paymentDate', 'secID', 'payment', 'interest']]

    def get_fund_holdings(self, ticker, begin_date='', end_date=''):
        df = DataAPI.FundHoldingsGet(
            ticker=ticker, beginDate=begin_date, endDate=end_date)
        df['reportDate'] = df['reportDate'].apply(
            lambda x: str(x).replace('-', ''))
        return df[[
            'reportDate', 'holdingsecType', 'holdingSecID', 'holdVolume',
            'marketValue', 'ratioInNa'
        ]]

    def get_market_index_daily(self, index_ticker, begin_date, end_date):
        df = DataAPI.MktIdxdGet(ticker=index_ticker, beginDate=begin_date, endDate=end_date)
        df['tradeDate'] = df['tradeDate'].apply(lambda x: str(x).replace('-', ''))
        return df.set_index('tradeDate')['closeIndex']

    def get_equity_close_price_daily(self, universe_list, begin_date, end_date):
        df = DataAPI.MktEqudGet(secID=universe_list, beginDate=begin_date, endDate=end_date)
        df['tradeDate'] = df['tradeDate'].apply(lambda x: str(x).replace('-', ''))
        trading_day_list = sorted(df['tradeDate'].unique())
        close_price_series_dict = {}
        for trading_day in trading_day_list:
            close_price_series_dict[trading_day] = df[df['tradeDate'] == trading_day].set_index('secID')['closePrice']
        return close_price_series_dict

    def get_fund_nav(self, ticker, begin_date='', end_date=''):
        df = DataAPI.FundNavGet(ticker=ticker,beginDate=begin_date,endDate=end_date,pandas="1")
        df['endDate'] = df['endDate'].apply(lambda x: x.replace('-', ''))
        return df.set_index('endDate')['ADJUST_NAV']
