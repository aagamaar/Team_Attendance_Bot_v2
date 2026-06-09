# utils.py
from collections import defaultdict
from datetime import datetime, timedelta

request_counts = defaultdict(list)

def is_rate_limited(user_id, limit=20, window=60):
    """Optional rate limiting"""
    now = datetime.now()
    cutoff = now - timedelta(seconds=window)
    
    request_counts[user_id] = [t for t in request_counts[user_id] if t > cutoff]
    
    if len(request_counts[user_id]) >= limit:
        return True
    
    request_counts[user_id].append(now)
    return False