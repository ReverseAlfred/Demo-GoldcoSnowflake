import os

class Config:
    # Snowflake connection settings with environment variable overrides
    SNOWFLAKE_ACCOUNT = os.getenv('SNOWFLAKE_ACCOUNT', 'XIQTUJZ-DA41181')
    SNOWFLAKE_WAREHOUSE = os.getenv('SNOWFLAKE_WAREHOUSE', 'CKB_WH')
    SNOWFLAKE_DATABASE = os.getenv('SNOWFLAKE_DATABASE', 'ckb')
    SNOWFLAKE_SCHEMA = os.getenv('SNOWFLAKE_SCHEMA', 'public')
