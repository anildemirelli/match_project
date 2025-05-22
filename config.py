# config.py

DB_CONFIG = {
    'user': 'postgres',
    'password': 'jAcABlJPfhbptKOkSKUvVClMhddYOtEF',
    'host': 'trolley.proxy.rlwy.net',
    'port': '39956',
    'database': 'railway'
}

# SQLAlchemy veritabanı bağlantı URI’si
SQLALCHEMY_DATABASE_URI = (
    f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
    f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

# Uyarı mesajlarını kapatmak için
SQLALCHEMY_TRACK_MODIFICATIONS = False
