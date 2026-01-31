import redis
r = redis.Redis(host='54.200.86.117', port=6379)
print(r.ping())

# from django.contrib.auth.hashers import make_password
# print(make_password("Pass@123"))