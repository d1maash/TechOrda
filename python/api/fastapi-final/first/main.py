from fastapi import FastAPI, Request
from prometheus_client import Counter, Histogram, Gauge, make_asgi_app
import time

app = FastAPI()

# Метрики
http_requests_total = Counter(
    'http_requests_total', 'Number of HTTP requests received', ['method', 'endpoint']
)
http_requests_milliseconds = Histogram(
    'http_requests_milliseconds', 'Duration of HTTP requests in milliseconds', ['method', 'endpoint']
)
last_sum1n = Gauge('last_sum1n', 'Value stores last result of sum1n')
last_fibo = Gauge('last_fibo', 'Value stores last result of fibo')
list_size = Gauge('list_size', 'Value stores current list size')
last_calculator = Gauge('last_calculator', 'Value stores last result of calculator')
errors_calculator_total = Counter('errors_calculator_total', 'Number of errors in calculator')

# Middleware для метрик
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    method = request.method
    endpoint = request.url.path
    start_time = time.time()
    
    # Увеличиваем счетчик запросов
    http_requests_total.labels(method=method, endpoint=endpoint).inc()
    
    response = await call_next(request)
    
    # Вычисляем время выполнения и обновляем гистограмму
    duration = (time.time() - start_time) * 1000
    http_requests_milliseconds.labels(method=method, endpoint=endpoint).observe(duration)
    
    return response

# Роуты
@app.get("/sum1n")
def sum1n(n: int):
    result = sum(range(1, n + 1))
    last_sum1n.set(result)
    return {"result": result}

@app.get("/fibo")
def fibo(n: int):
    def fib(n):
        if n <= 1:
            return n
        return fib(n - 1) + fib(n - 2)
    result = fib(n)
    last_fibo.set(result)
    return {"result": result}

@app.get("/calculator")
def calculator(a: float, b: float, op: str):
    try:
        if op == '+':
            result = a + b
        elif op == '-':
            result = a - b
        elif op == '*':
            result = a * b
        elif op == '/':
            if b == 0:
                raise ZeroDivisionError
            result = a / b
        else:
            raise ValueError("Invalid operation")
        last_calculator.set(result)
        return {"result": result}
    except Exception as e:
        errors_calculator_total.inc()
        return {"error": str(e)}

@app.get("/list_size")
def get_list_size(lst: list):
    size = len(lst)
    list_size.set(size)
    return {"size": size}

# Добавляем роут /metrics
app.mount("/metrics", make_asgi_app())
