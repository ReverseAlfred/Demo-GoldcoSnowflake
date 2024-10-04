import os

class Config:
    # Snowflake connection settings with environment variable overrides
    SNOWFLAKE_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT', 'CMWDBMC-HB15746')
    SNOWFLAKE_WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE', 'NEWCKB_WH')
    SNOWFLAKE_DATABASE = os.getenv('SNOWFLAKE_DATABASE', 'NEWCKB')
    SNOWFLAKE_SCHEMA = os.getenv('SNOWFLAKE_SCHEMA', 'public')
