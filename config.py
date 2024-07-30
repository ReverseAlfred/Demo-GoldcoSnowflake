import os

class Config:
    # Snowflake connection settings
    SNOWFLAKE_ACCOUNT = 'XIQTUJZ-DA41181'
    SNOWFLAKE_WAREHOUSE = 'ckb_wh'
    SNOWFLAKE_DATABASE = 'ckb'
    SNOWFLAKE_SCHEMA = 'public'
    
    # Cookie settings
    COOKIE_USERNAME_KEY = 'username'
    COOKIE_PASSWORD_KEY = 'password'
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    SESSION_COOKIE_SECURE = False  # Set to True in production if using HTTPS
    SESSION_COOKIE_HTTPONLY = True  # Protects cookies from client-side access
    SESSION_COOKIE_SAMESITE = 'Lax'  # Adjust as needed
