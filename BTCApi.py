import requests
import simplejson as json
import time, datetime
import hmac, hashlib
import sys

class BTCException(Exception):
	def __init__(self, value):
		self.value = value
		
	def __str__(self):
		return repr(self.value)

class BTCApi:
	HTTP_METHOD_GET = 'GET'
	HTTP_METHOD_POST = 'POST'
	HTTP_METHOD_DELETE = 'DELETE'
	
	# Request
	ERROR_CODE_MISSING_HEADER = 1
	ERROR_CODE_INACTIVE_API_KEY = 2
	ERROR_CODE_INVALID_API_KEY                   = 3
	ERROR_CODE_INVALID_NONCE                     = 4
	ERROR_CODE_INVALID_SIGNATURE                 = 5
	ERROR_CODE_INSUFFICIENT_CREDITS              = 6
	ERROR_CODE_INVALID_ROUTE                     = 7
	ERROR_CODE_UNKOWN_API_ACTION                 = 8
	ERROR_CODE_ADDITIONAL_AGREEMENT_NOT_ACCEPTED = 9
	ERROR_CODE_API_KEY_BANNED                    = 32
	ERROR_CODE_IP_BANNED                         = 33
	
	ERROR_CODE_NO_KYC_FULL                              = 44
	ERROR_CODE_NO_2_FACTOR_AUTHENTICATION               = 10
	ERROR_CODE_NO_BETA_GROUP_USER                       = 11
	ERROR_CODE_TECHNICAL_REASON                         = 12
	ERROR_CODE_TRADING_API_CURRENTLY_UNAVAILABLE        = 13
	ERROR_CODE_NO_ACTION_PERMISSION_FOR_API_KEY         = 14
	ERROR_CODE_MISSING_POST_PARAMETER                   = 15
	ERROR_CODE_MISSING_GET_PARAMETER                    = 16
	ERROR_CODE_INVALID_NUMBER                           = 17
	ERROR_CODE_NUMBER_TOO_LOW                           = 18
	ERROR_CODE_NUMBER_TOO_BIG                           = 19
	ERROR_CODE_TOO_MANY_DECIMAL_PLACES                  = 20
	ERROR_CODE_INVALID_BOOLEAN_VALUE                    = 21
	ERROR_CODE_FORBIDDEN_PARAMETER_VALUE                = 22
	ERROR_CODE_INVALID_MIN_AMOUNT                       = 23
	ERROR_CODE_INVALID_DATETIME_FORMAT                  = 24
	ERROR_CODE_DATE_LOWER_THAN_MIN_DATE                 = 25
	ERROR_CODE_INVALID_VALUE                            = 26
	ERROR_CODE_FORBIDDEN_VALUE_FOR_GET_PARAMETER        = 27
	ERROR_CODE_FORBIDDEN_VALUE_FOR_POST_PARAMETER       = 28
	ERROR_CODE_EXPRESS_TRADE_TEMPORARILY_NOT_AVAILABLE  = 29
	ERROR_CODE_END_DATETIME_YOUNGER_THAN_START_DATETIME = 30
	ERROR_CODE_PAGE_GREATER_THAN_LAST_PAGE              = 31
	ERROR_CODE_INVALID_TRADING_PAIR                     = 34
	
	# Order
	ERROR_CODE_ORDER_NOT_FOUND                         = 50
	ERROR_CODE_ORDER_NOT_POSSIBLE                      = 51
	ERROR_CODE_INVALID_ORDER_TYPE                      = 52
	ERROR_CODE_PAYMENT_OPTION_NOT_ALLOWED_FOR_TYPE_BUY = 53
	ERROR_CODE_CANCELLATION_NOT_ALLOWED                = 54
	ERROR_CODE_TRADING_SUSPENDED                       = 55
	ERROR_CODE_EXPRESS_TRADE_NOT_POSSIBLE              = 56
	ERROR_CODE_NO_BANK_ACCOUNT                         = 57
	
	# Trade
	ERROR_CODE_NO_ACTIVE_RESERVATION           = 70
	ERROR_CODE_EXPRESS_TRADE_NOT_ALLOWED       = 71
	ERROR_CODE_EXPRESS_TRADE_FAILURE_TEMPORARY = 72
	ERROR_CODE_EXPRESS_TRADE_FAILURE           = 73
	ERROR_CODE_INVALID_TRADE_STATE             = 74
	ERROR_CODE_TRADE_NOT_FOUND                 = 75
	ERROR_CODE_RESERVATION_AMOUNT_INSUFFICIENT = 76
	
	METHOD_SHOW_ORDERBOOK        = 'showOrderbook'
	METHOD_CREATE_ORDER          = 'createOrder'
	METHOD_DELETE_ORDER          = 'deleteOrder'
	METHOD_SHOW_MY_ORDERS        = 'showMyOrders'
	METHOD_SHOW_MY_ORDER_DETAILS = 'showMyOrderDetails'
	METHOD_EXECUTE_TRADE         = 'executeTrade'
	METHOD_SHOW_MY_TRADES        = 'showMyTrades'
	METHOD_SHOW_MY_TRADE_DETAILS = 'showMyTradeDetails'
	METHOD_SHOW_ACCOUNT_INFO     = 'showAccountInfo'
	METHOD_SHOW_ACCOUNT_LEDGER   = 'showAccountLedger'
	
	# LEGACY API-METHODS
	METHOD_SHOW_PUBLIC_TRADE_HISTORY = 'showPublicTradeHistory'
	METHOD_SHOW_ORDERBOOK_COMPACT    = 'showOrderbookCompact'
	METHOD_SHOW_RATES                = 'showRates'
	
	HEADER_X_NONCE         = 'X-API-NONCE'
	HEADER_X_API_KEY       = 'X-API-KEY'
	HEADER_X_API_SIGNATURE = 'X-API-SIGNATURE'
	
	ORDER_TYPE_BUY  = 'buy'
	ORDER_TYPE_SELL = 'sell'
	
	# Mandatory parameters for searching the orderbook
	SHOW_ORDERBOOK_PARAMETER_TYPE   = 'type' # string (buy|sell)
	SHOW_ORDERBOOK_PARAMETER_AMOUNT = 'amount' # float
	SHOW_ORDERBOOK_PARAMETER_PRICE  = 'price' # float
	
	# Optional parameters for searching the orderbook
	SHOW_ORDERBOOK_PARAMETER_ORDER_REQUIREMENTS_FULLFILLED = 'order_requirements_fullfilled' # boolean (default: false)
	SHOW_ORDERBOOK_PARAMETER_ONLY_KYC_FULL                 = 'only_kyc_full' # boolean (default: false)
	SHOW_ORDERBOOK_PARAMETER_ONLY_EXPRESS_ORDERS           = 'only_express_orders' # boolean (default: false)
	SHOW_ORDERBOOK_PARAMETER_ONLY_SAME_BANKGROUP           = 'only_same_bankgroup' # boolean (default: false)
	SHOW_ORDERBOOK_PARAMETER_ONLY_SAME_BIC                 = 'only_same_bic' # boolean (default: false)
	SHOW_ORDERBOOK_PARAMETER_SEAT_OF_BANK                  = 'seat_of_bank' # array (default: all possible countries)
	
	# Mandatory parameters for create new order
	CREATE_ORDER_PARAMETER_TYPE       = 'type' # string (buy|sell)
	CREATE_ORDER_PARAMETER_MAX_AMOUNT = 'max_amount' # float
	CREATE_ORDER_PARAMETER_PRICE      = 'price' # float
	
	# Optional parameters for create new order
	CREATE_ORDER_PARAMETER_MIN_AMOUNT                     = 'min_amount' # float (default: max_amount/2)
	CREATE_ORDER_PARAMETER_END_DATETIME                   = 'end_datetime' # string (format: RFC 3339, default: current date + 5 days)
	CREATE_ORDER_PARAMETER_NEW_ORDER_FOR_REMAINING_AMOUNT = 'new_order_for_remaining_amount' # boolean ( default: false)
	CREATE_ORDER_PARAMETER_MIN_TRUST_LEVEL                = 'min_trust_level' # string (bronze|silver|gold, default: default setting user account)
	CREATE_ORDER_PARAMETER_ONLY_KYC_FULL                  = 'only_kyc_full' # boolean (default: false)
	CREATE_ORDER_PARAMETER_PAYMENT_OPTION                 = 'payment_option' # integer (1|2|3)
	CREATE_ORDER_PARAMETER_SEAT_OF_BANK                   = 'seat_of_bank' # array (default: all possible countries)
	
	# Mandatory parameters for delete order
	DELETE_ORDER_PARAMETER_ORDER_ID = 'order_id' # string
	
    # Optional parameters for my orders list
	SHOW_MY_ORDERS_PARAMETER_TYPE           = 'type' # string (buy|sell)
	SHOW_MY_ORDERS_PARAMETER_TRADING_PAIR   = 'trading_pair' # string
	SHOW_MY_ORDERS_PARAMETER_STATE          = 'state' # integer (-2, -1, 0 | default: 0)
	SHOW_MY_ORDERS_PARAMETER_DATE_START     = 'date_start' # string
	SHOW_MY_ORDERS_PARAMETER_DATE_END       = 'date_end' # string
	SHOW_MY_ORDERS_PARAMETER_PAGE           = 'page' # string
	SHOW_MY_ORDERS_PARAMETER_SINCE_ORDER_ID = 'since_order_id' # string

	# Mandatory parameters for my order details
	SHOW_MY_ORDER_DETAILS_PARAMETER_ORDER_ID = 'order_id' # string

	# Mandatory parameters for execute trade
	EXECUTE_TRADE_PARAMETER_TYPE     = 'type' # string (buy|sell)
	EXECUTE_TRADE_PARAMETER_ORDER_ID = 'order_id' # string
	EXECUTE_TRADE_PARAMETER_AMOUNT   = 'amount' # string

	# Optional parameters for my trade list
	SHOW_MY_TRADES_PARAMETER_TYPE           = 'type' # string (buy|sell)
	SHOW_MY_TRADES_PARAMETER_TRADING_PAIR   = 'trading_pair' # string
	SHOW_MY_TRADES_PARAMETER_STATE          = 'state' # integer (-2, -1, 0 | default: 0)
	SHOW_MY_TRADES_PARAMETER_DATE_START     = 'date_start' # string
	SHOW_MY_TRADES_PARAMETER_DATE_END       = 'date_end' # string
	SHOW_MY_TRADES_PARAMETER_PAGE           = 'page' # string
	SHOW_MY_TRADES_PARAMETER_SINCE_TRADE_ID = 'since_trade_id' # string

	# Mandatory parameters for my trade details
	SHOW_MY_TRADE_DETAILS_PARAMETER_TRADE_ID = 'trade_id' # string

	# Optional parameters for public trade history
	SHOW_PUBLIC_TRADE_HISTORY_PARAMETER_SINCE_TID = 'since_tid' # integer

	# Optional parameters for show account statement
	SHOW_ACCOUNT_LEDGER_PARAMETER_TYPE           = 'type' # string
	SHOW_ACCOUNT_LEDGER_PARAMETER_DATETIME_START = 'datetime_start' # string
	SHOW_ACCOUNT_LEDGER_PARAMETER_DATETIME_END   = 'datetime_end' # string
	SHOW_ACCOUNT_LEDGER_PARAMETER_PAGE           = 'page' # string

	ORDER_STATE_EXPIRED   = -2
	ORDER_STATE_CANCELLED = -1
	ORDER_STATE_PENDING   = 0

	TRADE_STATE_CANCELLED  = -1
	TRADE_STATE_PENDING    = 0
	TRADE_STATE_SUCCESSFUL = 1

	TRADE_PAYMENT_METHOD_SEPA    = 1
	TRADE_PAYMENT_METHOD_EXPRESS = 2

	ORDER_PAYMENT_OPTION_ONLY_EXPRESS   = 1
	ORDER_PAYMENT_OPION_ONLY_SEPA       = 2
	ORDER_PAYMENT_OPION_EXPRESS_OR_SEPA = 3

	MIN_TRUST_LEVEL_BRONZE = 'bronze'
	MIN_TRUST_LEVEL_SILVER = 'silver'
	MIN_TRUST_LEVEL_GOLD   = 'gold'
	MIN_TRUST_LEVEL_PLATIN = 'platin'

	RATING_PENDING  = 'pending'
	RATING_NEGATIVE = 'negative'
	RATING_NEUTRAL  = 'neutral'
	RATING_POSITIVE = 'positive'

	ACCOUNT_LEDGER_TYPE_ALL             = 'all'
	ACCOUNT_LEDGER_TYPE_BUY             = 'buy'
	ACCOUNT_LEDGER_TYPE_SELL            = 'sell'
	ACCOUNT_LEDGER_TYPE_INPAYMENT       = 'inpayment'
	ACCOUNT_LEDGER_TYPE_PAYOUT          = 'payout'
	ACCOUNT_LEDGER_TYPE_AFFILIATE       = 'affiliate'
	ACCOUNT_LEDGER_TYPE_BUY_YUBIKEY     = 'buy_yubikey'
	ACCOUNT_LEDGER_TYPE_BUY_GOLDSHOP    = 'buy_goldshop'
	ACCOUNT_LEDGER_TYPE_BUY_DIAMONDSHOP = 'buy_diamondshop'
	ACCOUNT_LEDGER_TYPE_KICKBACK        = 'kickback'

	TRADING_PAIR_BTCEUR = 'btceur'
	TRADING_PAIR_BCHEUR = 'bcheur'

	api_key = ''
	secret = ''

	method_settings = {
		METHOD_SHOW_ORDERBOOK : {
			'http_method' : HTTP_METHOD_GET,
			'entity'      : 'orders',
			'parameters'  : [ SHOW_ORDERBOOK_PARAMETER_TYPE,]
		},
		METHOD_CREATE_ORDER : {
			'http_method' : HTTP_METHOD_POST,
			'entity'      : 'orders',
			'parameters'  : [
				CREATE_ORDER_PARAMETER_TYPE,
				CREATE_ORDER_PARAMETER_PRICE,
				CREATE_ORDER_PARAMETER_MAX_AMOUNT,
			],
		},
		METHOD_DELETE_ORDER : {
			'http_method' : HTTP_METHOD_DELETE,
			'entity'      : 'orders',
			'id'          : 'order_id',
		},
		METHOD_SHOW_MY_ORDERS : {
			'http_method' : HTTP_METHOD_GET,
			'entity'      : 'orders',
			'subentity'   : 'my_own',
		},
		METHOD_SHOW_MY_ORDER_DETAILS : {
			'http_method' : HTTP_METHOD_GET,
			'entity'      : 'orders',
			'id'          : 'order_id',
		},
		METHOD_EXECUTE_TRADE : {
			'http_method' : HTTP_METHOD_POST,
			'entity'      : 'trades',
			'parameters'  : [
				EXECUTE_TRADE_PARAMETER_TYPE,
				EXECUTE_TRADE_PARAMETER_AMOUNT,
			],
			'id'          : EXECUTE_TRADE_PARAMETER_ORDER_ID,
		},
		METHOD_SHOW_MY_TRADES : {
			'http_method' : HTTP_METHOD_GET,
			'entity'      : 'trades',
		},
		METHOD_SHOW_MY_TRADE_DETAILS : {
			'http_method' : HTTP_METHOD_GET,
			'entity'      : 'trades',
			'id'          : 'trade_id',
		},
		METHOD_SHOW_ACCOUNT_INFO : {
			'http_method' : HTTP_METHOD_GET,
			'entity'      : 'account',
		},

		# LEGACY API
		METHOD_SHOW_PUBLIC_TRADE_HISTORY : {
			'http_method' : HTTP_METHOD_GET,
			'entity'      : 'trades',
			'subentity'   : 'history',
		},
		METHOD_SHOW_ORDERBOOK_COMPACT : {
			'http_method' : HTTP_METHOD_GET,
			'entity'      : 'orders',
			'subentity'   : 'compact',
		},
		METHOD_SHOW_RATES : {
			'http_method' : HTTP_METHOD_GET,
			'entity'      : 'rates',
		},
		METHOD_SHOW_ACCOUNT_LEDGER : {
			'http_method' : HTTP_METHOD_GET,
			'entity'      : 'account',
			'subentity'   : 'ledger',
		},
	}

	options = {
		'uri' : 'https://api.bitcoin.de/',
		'verify_ssl_peer' : True,
		'api_version' : 1,
	}

	#Constructor
	def __init__(self, lapi_key, lsecret, loptions = {}):
		self.api_key = lapi_key
		self.secret  = lsecret
		if len(loptions) > 0:
			self.options     = loptions


	def doRequest(self, api_method, parameters = {}):
		# Check if the method exists
		if not api_method in self.method_settings:
			raise BTCException('API-Method >>' + api_method + '<< doesnt exists')

		# Are all mandatory parameters given?
		if 'parameters' in self.method_settings[api_method]:
			for mandatory_parameter in self.method_settings[api_method]['parameters']:
				if not mandatory_parameter in parameters:
					raise BTCException('Value for mandatory ' + self.method_settings[api_method]['http_method'] + '-parameter "' + mandatory_parameter + '" is missing')

		if 'id' in self.method_settings[api_method] and parameters[self.method_settings[api_method]['id']] == '':
			raise BTCException('Value for mandatory GET-parameter ' + self.method_settings[api_method]['id'] + ' is missing')

		# Prepare the nonce
		now = datetime.datetime.now()
		nonce_f = time.mktime(now.timetuple())*1e6 + now.microsecond
		nonce = str('%16.0f' % nonce_f)
		
		id        = ''
		subentity = ''

		if 'id' in self.method_settings[api_method] and self.method_settings[api_method]['id'] != '':
			if parameters[self.method_settings[api_method]['id']] != '':
				id = '/' + parameters[self.method_settings[api_method]['id']]
				parameters[self.method_settings[api_method]['id']] = ''

		if 'subentity' in self.method_settings[api_method] and self.method_settings[api_method]['subentity'] != '':
			subentity = '/' + self.method_settings[api_method]['subentity']

		post_parameters = {}
		if self.HTTP_METHOD_POST == self.method_settings[api_method]['http_method']:
			post_parameters = parameters
		
		prepared_post_parameters = ''
		for key in sorted(post_parameters):
			if prepared_post_parameters != '':
				prepared_post_parameters += '&'
			prepared_post_parameters += key + '=' + str(post_parameters[key])

		
		md5 = hashlib.md5()
		md5.update(prepared_post_parameters.encode("utf-8"))
		prepared_post_parameters_hash = md5.hexdigest()

		get_parameters ={}
		if self.HTTP_METHOD_GET == self.method_settings[api_method]['http_method']:
			get_parameters = parameters
		
		prepared_get_parameters = ''
		for key in get_parameters:
			if prepared_get_parameters != '':
				prepared_get_parameters += '&'
			prepared_get_parameters += key + '=' + str(get_parameters[key])
		if len(prepared_get_parameters) > 0:
			prepared_get_parameters = '?'+prepared_get_parameters

		http_method = self.method_settings[api_method]['http_method']
		uri         = self.options['uri'] + 'v' + str(self.options['api_version']) + '/' + self.method_settings[api_method]['entity'] + id + subentity + prepared_get_parameters
		request_headers = {
			self.HEADER_X_API_KEY : self.api_key,
			self.HEADER_X_NONCE : nonce,
			self.HEADER_X_API_SIGNATURE : ''
		}

		hmac_data = '#'.join([http_method, uri, self.api_key, nonce, prepared_post_parameters_hash])
		
		key_bytes= self.secret
		data_bytes = hmac_data
		if sys.version_info >= (3,0):
			key_bytes= bytes(self.secret, 'utf-8')
			data_bytes = bytes(hmac_data, 'utf-8')
		s_hmac = hmac.new(key_bytes,data_bytes,hashlib.sha256).hexdigest()

		request_headers[self.HEADER_X_API_SIGNATURE] = s_hmac
		result = ''
		session = requests.Session()

		if len( prepared_post_parameters ) > 0:
			result = session.post(uri,headers=request_headers, data=post_parameters).text
		else:
			result = session.get(uri,headers=request_headers).text

		if result == '':
			return result
		#	raise BTCException('no data')

		#hier noch etwas Fehlerhandling fuer die Verbindung!
		
		return json.loads(result)
		