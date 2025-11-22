// =============================================================================
// K6 Load Test Script - 50,000 Concurrent Users
// =============================================================================
// Kullanım: k6 run deploy/load_test_k6.js
// =============================================================================

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const requestDuration = new Trend('request_duration');
const requestCounter = new Counter('requests');

// Test configuration
export const options = {
  stages: [
    // Warm-up phase
    { duration: '2m', target: 100 },      // Ramp up to 100 users
    { duration: '3m', target: 100 },      // Stay at 100 users
    
    // Gradual ramp-up
    { duration: '5m', target: 1000 },    // Ramp up to 1,000 users
    { duration: '5m', target: 1000 },     // Stay at 1,000 users
    
    { duration: '5m', target: 5000 },    // Ramp up to 5,000 users
    { duration: '5m', target: 5000 },     // Stay at 5,000 users
    
    { duration: '5m', target: 10000 },    // Ramp up to 10,000 users
    { duration: '5m', target: 10000 },    // Stay at 10,000 users
    
    { duration: '5m', target: 25000 },    // Ramp up to 25,000 users
    { duration: '5m', target: 25000 },     // Stay at 25,000 users
    
    { duration: '5m', target: 50000 },    // Ramp up to 50,000 users (PEAK)
    { duration: '10m', target: 50000 },   // Sustain peak load for 10 minutes
    
    // Gradual ramp-down
    { duration: '5m', target: 25000 },    // Ramp down to 25,000 users
    { duration: '5m', target: 10000 },    // Ramp down to 10,000 users
    { duration: '5m', target: 5000 },     // Ramp down to 5,000 users
    { duration: '5m', target: 1000 },     // Ramp down to 1,000 users
    { duration: '5m', target: 0 },        // Ramp down to 0
  ],
  
  thresholds: {
    // 95% of requests must complete below 500ms
    'http_req_duration': ['p(95)<500', 'p(99)<1000'],
    
    // Error rate must be below 1%
    'http_req_failed': ['rate<0.01'],
    'errors': ['rate<0.01'],
    
    // Request rate
    'http_reqs': ['rate>1000'],  // At least 1000 requests per second
    
    // Checks must pass
    'checks': ['rate>0.95'],  // 95% of checks must pass
  },
  
  // Summary output
  summaryTrendStats: ['avg', 'min', 'med', 'max', 'p(90)', 'p(95)', 'p(99)'],
};

// Base URL
const BASE_URL = __ENV.BASE_URL || 'https://finasis.com.tr';

// Test data
const endpoints = [
  '/',
  '/accounts/login/',
  '/api/dashboard/',
  '/finance/',
  '/accounting/',
];

export default function () {
  const user = {
    id: __VU,  // Virtual user ID
    iteration: __ITER,  // Iteration number
  };

  // Group: Homepage
  group('Homepage', function () {
    const res = http.get(BASE_URL, {
      tags: { name: 'Homepage' },
      headers: {
        'User-Agent': 'K6-LoadTest/1.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      },
    });
    
    const success = check(res, {
      'status is 200': (r) => r.status === 200,
      'response time < 500ms': (r) => r.timings.duration < 500,
      'has content': (r) => r.body.length > 0,
    });
    
    errorRate.add(!success);
    requestDuration.add(res.timings.duration);
    requestCounter.add(1);
    
    sleep(1);
  });

  // Group: API Endpoints
  group('API Endpoints', function () {
    const endpoint = endpoints[Math.floor(Math.random() * endpoints.length)];
    const res = http.get(`${BASE_URL}${endpoint}`, {
      tags: { name: `API-${endpoint}` },
      headers: {
        'User-Agent': 'K6-LoadTest/1.0',
        'Accept': 'application/json',
      },
    });
    
    const success = check(res, {
      'status is 200 or 302': (r) => r.status === 200 || r.status === 302,
      'response time < 1000ms': (r) => r.timings.duration < 1000,
    });
    
    errorRate.add(!success);
    requestDuration.add(res.timings.duration);
    requestCounter.add(1);
    
    sleep(2);
  });

  // Group: Static Assets
  group('Static Assets', function () {
    const staticFiles = [
      '/static/common/css/main.css',
      '/static/common/js/main.js',
    ];
    
    const file = staticFiles[Math.floor(Math.random() * staticFiles.length)];
    const res = http.get(`${BASE_URL}${file}`, {
      tags: { name: 'Static' },
      headers: {
        'User-Agent': 'K6-LoadTest/1.0',
      },
    });
    
    check(res, {
      'status is 200 or 304': (r) => r.status === 200 || r.status === 304,
    });
    
    sleep(0.5);
  });
}

// Setup function (runs once before all VUs)
export function setup() {
  console.log('🚀 Starting load test for 50,000 concurrent users');
  console.log(`📍 Target URL: ${BASE_URL}`);
  return { baseUrl: BASE_URL };
}

// Teardown function (runs once after all VUs)
export function teardown(data) {
  console.log('✅ Load test completed');
  console.log(`📍 Tested URL: ${data.baseUrl}`);
}

