# KAOM Database Schema (PostgreSQL)

### 1. watchlist_snapshots
| Column | Type | Description |
| :--- | :--- | :--- |
| id | SERIAL (PK) | 고유 ID |
| timestamp | TIMESTAMP | 스캔 시각 |
| symbol | VARCHAR(10) | 종목코드 (인덱스) |
| gap_pct | FLOAT | 시가 갭 비율 |
| ai_bias | VARCHAR(10) | allow, watch, avoid |
| raw_data | JSONB | KIS 원시 응답 데이터 |

### 2. orders
| Column | Type | Description |
| :--- | :--- | :--- |
| id | SERIAL (PK) | 고유 ID |
| symbol | VARCHAR(10) | 종목코드 |
| order_type | VARCHAR(10) | BUY, SELL |
| price | INT | 주문 가격 |
| quantity | INT | 주문 수량 |
| status | VARCHAR(20) | PENDING, FILLED, etc. |
| kis_ord_no | VARCHAR(50) | 한투 주문번호 (Unique) |

### 3. positions
| Column | Type | Description |
| :--- | :--- | :--- |
| symbol | VARCHAR(10) (PK) | 종목코드 |
| entry_price | FLOAT | 평균 단가 |
| quantity | INT | 보유 수량 |
| pnl_pct | FLOAT | 현재 수익률 |

### 4. risk_events
| Column | Type | Description |
| :--- | :--- | :--- |
| id | SERIAL (PK) | 고유 ID |
| event_type | VARCHAR(50) | VI_BLOCK, LOSS_LIMIT_HIT, etc. |
| reason | TEXT | 상세 사유 |
| timestamp | TIMESTAMP | 발생 시각 |

---

## SQLAlchemy Migration Example
```python
# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    from app.db.models import Base
    Base.metadata.create_all(bind=engine)
```
