# -*- coding: utf-8 -*-
import time
import random
import threading
import requests
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict
import statistics
from decouple import config

class LoadTester:
    def __init__(self, base_url: str, num_threads: int = 10, duration: int = 60):
        self.base_url = base_url
        self.num_threads = num_threads
        self.duration = duration
        self.results: List[Dict] = []
        self.endpoints = [
            '/api/analytics/dashboard/',
            '/api/ai/predictions/',
            '/api/blockchain/transactions/',
            '/api/hr/employees/',
            '/api/virtual-company/projects/'
        ]

    def make_request(self, endpoint: str) -> Dict:
        start_time = time.time()
        try:
            response = requests.get(f"{self.base_url}{endpoint}")
            latency = time.time() - start_time
            return {
                'endpoint': endpoint,
                'status_code': response.status_code,
                'latency': latency,
                'success': response.status_code == 200
            }
        except Exception as e:
            return {
                'endpoint': endpoint,
                'status_code': 0,
                'latency': time.time() - start_time,
                'success': False,
                'error': str(e)
            }

    def worker(self):
        end_time = time.time() + self.duration
        while time.time() < end_time:
            endpoint = random.choice(self.endpoints)
            result = self.make_request(endpoint)
            self.results.append(result)
            time.sleep(random.uniform(0.1, 0.5))

    def run(self):
        print(f"Yük testi başlatılıyor: {self.num_threads} thread, {self.duration} saniye")
        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = [executor.submit(self.worker) for _ in range(self.num_threads)]
            for future in futures:
                future.result()

    def analyze_results(self):
        if not self.results:
            return

        total_requests = len(self.results)
        successful_requests = sum(1 for r in self.results if r['success'])
        latencies = [r['latency'] for r in self.results if r['success']]

        print("\nYük Testi Sonuçları:")
        print(f"Toplam İstek: {total_requests}")
        print(f"Başarılı İstek: {successful_requests}")
        print(f"Başarı Oranı: {(successful_requests/total_requests)*100:.2f}%")
        
        if latencies:
            print(f"Ortalama Yanıt Süresi: {statistics.mean(latencies)*1000:.2f} ms")
            print(f"En Yüksek Yanıt Süresi: {max(latencies)*1000:.2f} ms")
            print(f"En Düşük Yanıt Süresi: {min(latencies)*1000:.2f} ms")
            print(f"Standart Sapma: {statistics.stdev(latencies)*1000:.2f} ms")

        # Endpoint bazlı analiz
        endpoint_stats = {}
        for result in self.results:
            endpoint = result['endpoint']
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {'total': 0, 'success': 0, 'latencies': []}
            
            endpoint_stats[endpoint]['total'] += 1
            if result['success']:
                endpoint_stats[endpoint]['success'] += 1
                endpoint_stats[endpoint]['latencies'].append(result['latency'])

        print("\nEndpoint Bazlı İstatistikler:")
        for endpoint, stats in endpoint_stats.items():
            success_rate = (stats['success']/stats['total'])*100 if stats['total'] > 0 else 0
            avg_latency = statistics.mean(stats['latencies'])*1000 if stats['latencies'] else 0
            print(f"\n{endpoint}:")
            print(f"  Toplam İstek: {stats['total']}")
            print(f"  Başarı Oranı: {success_rate:.2f}%")
            print(f"  Ortalama Yanıt Süresi: {avg_latency:.2f} ms")

if __name__ == "__main__":
    base_url = config('BASE_URL', default='http://localhost:8000')
    tester = LoadTester(base_url, num_threads=20, duration=300)  # 5 dakika test
    tester.run()
    tester.analyze_results() 