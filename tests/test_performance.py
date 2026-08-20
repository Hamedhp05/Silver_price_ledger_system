import time
import pytest
import requests
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# ============================================
# تست ۱: سرعت APIهای مختلف
# ============================================

class TestPerformance:
    
    def test_latest_price_response_time(self):
        """تست: زمان پاسخ /prices/latest زیر ۱ ثانیه باشه"""
        start_time = time.time()
        response = client.get("/prices/latest")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 1.0, f"Response time was {response_time:.3f}s (should be < 1s)"
        print(f"✅ /prices/latest: {response_time:.3f}s")
    
    def test_history_response_time(self):
        """تست: زمان پاسخ /prices/history زیر ۱ ثانیه باشه"""
        start_time = time.time()
        response = client.get("/prices/history?limit=10")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 1.0, f"Response time was {response_time:.3f}s (should be < 1s)"
        print(f"✅ /prices/history: {response_time:.3f}s")
    
    def test_chart_response_time(self):
        """تست: زمان پاسخ /prices/chart زیر ۱ ثانیه باشه"""
        start_time = time.time()
        response = client.get("/prices/chart?point_count=50")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 1.0, f"Response time was {response_time:.3f}s (should be < 1s)"
        print(f"✅ /prices/chart: {response_time:.3f}s")
    
    def test_prediction_linear_response_time(self):
        """تست: زمان پاسخ prediction زیر ۲ ثانیه باشه (چون مدل سنگین‌تره)"""
        start_time = time.time()
        response = client.get("/prediction/linear_regression")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        # برای prediction تا ۲ ثانیه هم مجازه (طبق SRS)
        assert response_time < 2.0, f"Response time was {response_time:.3f}s (should be < 2s)"
        print(f"✅ /prediction/linear_regression: {response_time:.3f}s")
    
    def test_prediction_random_forest_response_time(self):
        """تست: زمان پاسخ Random Forest زیر ۲ ثانیه باشه"""
        start_time = time.time()
        response = client.get("/prediction/random_forest")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 2.0, f"Response time was {response_time:.3f}s (should be < 2s)"
        print(f"✅ /prediction/random_forest: {response_time:.3f}s")


# ============================================
# تست ۲: Load Testing (۱۰ درخواست همزمان)
# ============================================

def test_concurrent_requests():
    """تست: ۱۰ درخواست همزمان به /prices/latest"""
    
    def make_request():
        start = time.time()
        response = client.get("/prices/latest")
        return time.time() - start
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        results = list(executor.map(lambda _: make_request(), range(10)))
    
    avg_time = sum(results) / len(results)
    max_time = max(results)
    
    assert avg_time < 1.0, f"Average response time was {avg_time:.3f}s (should be < 1s)"
    assert max_time < 2.0, f"Max response time was {max_time:.3f}s (should be < 2s)"
    
    print(f"✅ Concurrent requests (10): avg={avg_time:.3f}s, max={max_time:.3f}s")


# ============================================
# تست ۳: Scheduler Performance (اجرای دستی)
# ============================================

def test_collector_performance():
    """تست: زمان اجرای collector زیر ۲ دقیقه باشه"""
    start_time = time.time()
    
    response = client.post("/collector/run")
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    assert response.status_code == 200
    assert execution_time < 120.0, f"Collector took {execution_time:.1f}s (should be < 120s)"
    
    print(f"✅ Collector execution: {execution_time:.1f}s")


# ============================================
# تست ۴: Database Query Performance
# ============================================

def test_database_query_performance(db_session):
    """تست: سرعت کوئری دیتابیس"""
    from app.services.price_service import get_latest_price, get_price_history
    
    start = time.time()
    result = get_latest_price(db_session)
    query_time = time.time() - start
    
    assert query_time < 0.5, f"DB query took {query_time:.3f}s (should be < 0.5s)"
    print(f"✅ Database query: {query_time:.3f}s")