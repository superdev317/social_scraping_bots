# MongoDB settings
DB_URI  = 'mongodb://localhost:27017/'
DB_NAME = 'newsraven'
DB_NEWS_COLLECTION_NAME = 'news'
DB_REDDIT_COLLECTION_NAME = 'reddit'
DB_DEBUG = True

# TEXT SUMMARIZATION LIMIT
NEWS_SUMMARIZATION_LIMIT = 2048    # 2 * 1024
REDDIT_SUMMARIZATION_LIMIT = 1024

# TIME LIMIT
BREAKING_TIMESTAMP_LIMIT = 86400    # 1 day in second
OPINION_TIMESTAMP_LIMIT = 259200    # 3 days in second


# custom HTTP headers
HTTP_HEADERS = {
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding':'gzip, deflate, br',
    'Accept-Language':'en-GB,en;q=0.9,en-US;q=0.8,ml;q=0.7',
    'Cache-Control':'max-age=0',
    'Connection':'keep-alive',
    'Upgrade-Insecure-Requests':'1',
    'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36'
}

# twitter config
TWITTER_CONSUMER_KEY = 'mXGCBWrQFvgy1rXTJBISAfYi9'
TWITTER_SECRET = 'kv7I2eHJCblnvCEiShW99YS6sDbK08bKWA8IUZU0fDTwko0ATq'
TWITTER_ACCESS_TOKEN_KEY = '1122251088558723072-vRvpvAMassNCRH8IshCk84P0O6002X'
TWITTER_ACCESS_TOKEN_SECRET = 'I8HsL2oz9C5SALXviHfetl9fcp71ZRrdkfUjajzOorVxb'

# state code
ARG    = 32    # Argentina
AUS    = 36    # Australia
BGD    = 50    # Bangladesh
BRA    = 76    # Brazil
BGR    = 100   # Bulgaria
CAN    = 124   # Canada
CHN    = 156   # China
CZE    = 203   # Czech Republic
EGY    = 818   # Egypt
ETH    = 231   # Ethiopia
FRA    = 250   # France
DEU    = 276   # Germany
GHA    = 288   # Ghana
HKG    = 344   # Hong Kong
HUN    = 348   # Hungary
IND    = 356   # India
IDN    = 360   # Indonesia
IRN    = 364   # Iran
ISR    = 376   # Israel
JPN    = 392   # Japan
KEN    = 404   # Kenya
PRK    = 408   # Korea, Democratic People's Republic of
KOR    = 410   # Korea, Republic of
MYS    = 458   # Malaysia
MEX    = 484   # Mexico
NGA    = 566   # Nigeria
PAK    = 586   # Pakistan
PHL    = 608   # Philippines
POL    = 616   # Poland
PRT    = 620   # Portugal
QAT    = 634   # Qatar
RUS    = 643   # Russian Federation
SAU    = 682   # Saudi Arabia
SGP    = 702   # Singapore
ZAF    = 710   # South Africa
ESP    = 724   # Spain
LKA    = 144   # Sri Lanka
SWE    = 752   # Sweden
TWN    = 158   # Taiwan
THA    = 764   # Thailand
TUR    = 792   # Turkey
ARE    = 784   # United Arab Emirates
GBR    = 826   # United Kingdom
USA    = 840   # United States