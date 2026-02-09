/**
 * ============================================================================
 * K6 Load Test: Todo Application
 * ============================================================================
 * Tests 1000 concurrent users performing CRUD operations on tasks
 *
 * Performance Targets:
 *   - P95 latency: <5s for all operations
 *   - Error rate: <1%
 *   - Throughput: >100 requests/second
 *
 * Test Scenarios:
 *   - Create task (40% of requests)
 *   - List tasks with filters (30% of requests)
 *   - Update task status (20% of requests)
 *   - Delete task (10% of requests)
 *
 * Run:
 *   k6 run load-test.js
 *
 * Run with custom parameters:
 *   k6 run --vus 1000 --duration 5m load-test.js
 *
 * Generate HTML report:
 *   k6 run --out json=load-test-results.json load-test.js
 *   k6-reporter load-test-results.json --output load-test-report.html
 * ============================================================================
 */

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { randomString, randomIntBetween, randomItem } from 'https://jslib.k6.io/k6-utils/1.2.0/index.js';

// ============================================================================
// Configuration
// ============================================================================

// Load test configuration from environment or use defaults
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const FRONTEND_URL = __ENV.FRONTEND_URL || 'http://localhost:3000';

// Test users pool (simulate multiple authenticated users)
const TEST_USERS = Array.from({ length: 100 }, (_, i) => ({
  user_id: `load_test_user_${i}`,
  email: `user${i}@loadtest.com`,
  name: `Test User ${i}`
}));

// Task priorities
const PRIORITIES = ['low', 'medium', 'high', 'critical'];

// Task tags
const TAGS = ['work', 'personal', 'urgent', 'meeting', 'project', 'bug', 'feature'];

// Task statuses
const STATUSES = ['pending', 'in_progress', 'completed', 'cancelled'];

// ============================================================================
// K6 Options (Load Test Configuration)
// ============================================================================

export const options = {
  // Stages define the load profile
  stages: [
    { duration: '30s', target: 100 },    // Ramp-up to 100 users in 30s
    { duration: '30s', target: 500 },    // Ramp-up to 500 users in 30s
    { duration: '30s', target: 1000 },   // Ramp-up to 1000 users in 30s
    { duration: '5m', target: 1000 },    // Sustain 1000 users for 5 minutes
    { duration: '30s', target: 500 },    // Ramp-down to 500 users
    { duration: '30s', target: 0 },      // Ramp-down to 0 users
  ],

  // Thresholds define performance criteria
  thresholds: {
    // HTTP request duration (95th percentile must be < 5000ms)
    'http_req_duration': ['p(95)<5000'],

    // HTTP request failed rate must be < 1%
    'http_req_failed': ['rate<0.01'],

    // Requests per second should be > 100
    'http_reqs': ['rate>100'],

    // Operation-specific thresholds
    'create_task_duration': ['p(95)<5000'],
    'list_tasks_duration': ['p(95)<3000'],
    'update_task_duration': ['p(95)<4000'],
    'delete_task_duration': ['p(95)<2000'],

    // Error rates per operation
    'create_task_errors': ['rate<0.01'],
    'list_tasks_errors': ['rate<0.01'],
    'update_task_errors': ['rate<0.01'],
    'delete_task_errors': ['rate<0.01'],
  },

  // Tags for filtering results
  tags: {
    test_type: 'load_test',
    environment: __ENV.ENVIRONMENT || 'local',
  },
};

// ============================================================================
// Custom Metrics
// ============================================================================

// Operation-specific metrics
const createTaskDuration = new Trend('create_task_duration');
const listTasksDuration = new Trend('list_tasks_duration');
const updateTaskDuration = new Trend('update_task_duration');
const deleteTaskDuration = new Trend('delete_task_duration');

// Error rates per operation
const createTaskErrors = new Rate('create_task_errors');
const listTasksErrors = new Rate('list_tasks_errors');
const updateTaskErrors = new Rate('update_task_errors');
const deleteTaskErrors = new Rate('delete_task_errors');

// Counters for each operation type
const createTaskCounter = new Counter('create_task_count');
const listTasksCounter = new Counter('list_tasks_count');
const updateTaskCounter = new Counter('update_task_count');
const deleteTaskCounter = new Counter('delete_task_count');

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Get a random test user
 */
function getRandomUser() {
  return randomItem(TEST_USERS);
}

/**
 * Generate random task data
 */
function generateTaskData() {
  const now = new Date();
  const dueDate = new Date(now.getTime() + randomIntBetween(1, 30) * 24 * 60 * 60 * 1000);

  return {
    title: `Load Test Task ${randomString(8)}`,
    description: `This is a load test task created at ${now.toISOString()}`,
    priority: randomItem(PRIORITIES),
    tags: [randomItem(TAGS), randomItem(TAGS)],
    due_date: dueDate.toISOString(),
    recurrence_rule: null,
    reminder_offset: randomIntBetween(3600, 86400), // 1-24 hours
    status: 'pending'
  };
}

/**
 * Generate random filter query parameters
 */
function generateFilterParams() {
  const params = [];

  // Randomly add filters
  if (Math.random() > 0.5) {
    params.push(`priority=${randomItem(PRIORITIES)}`);
  }

  if (Math.random() > 0.5) {
    params.push(`status=${randomItem(STATUSES)}`);
  }

  if (Math.random() > 0.7) {
    params.push(`tags=${randomItem(TAGS)}`);
  }

  if (Math.random() > 0.8) {
    params.push(`search=${randomString(4)}`);
  }

  return params.join('&');
}

// ============================================================================
// API Operations
// ============================================================================

/**
 * Create a new task
 */
function createTask(user) {
  const url = `${BASE_URL}/api/${user.user_id}/tasks`;
  const payload = JSON.stringify(generateTaskData());

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
    tags: { operation: 'create_task' },
  };

  const response = http.post(url, payload, params);

  // Check response
  const success = check(response, {
    'create task: status is 201': (r) => r.status === 201,
    'create task: has task_id': (r) => r.json('task_id') !== undefined,
  });

  // Record metrics
  createTaskDuration.add(response.timings.duration);
  createTaskErrors.add(!success);
  createTaskCounter.add(1);

  // Return task_id if successful
  if (success && response.json('task_id')) {
    return response.json('task_id');
  }

  return null;
}

/**
 * List tasks with filters
 */
function listTasks(user) {
  const filterParams = generateFilterParams();
  const url = `${BASE_URL}/api/${user.user_id}/tasks${filterParams ? '?' + filterParams : ''}`;

  const params = {
    tags: { operation: 'list_tasks' },
  };

  const response = http.get(url, params);

  // Check response
  const success = check(response, {
    'list tasks: status is 200': (r) => r.status === 200,
    'list tasks: has tasks array': (r) => Array.isArray(r.json('tasks')),
  });

  // Record metrics
  listTasksDuration.add(response.timings.duration);
  listTasksErrors.add(!success);
  listTasksCounter.add(1);

  // Return tasks if successful
  if (success && response.json('tasks')) {
    return response.json('tasks');
  }

  return [];
}

/**
 * Update task status
 */
function updateTask(user, taskId) {
  const url = `${BASE_URL}/api/${user.user_id}/tasks/${taskId}`;
  const payload = JSON.stringify({
    status: randomItem(['in_progress', 'completed']),
    priority: randomItem(PRIORITIES),
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
    },
    tags: { operation: 'update_task' },
  };

  const response = http.patch(url, payload, params);

  // Check response
  const success = check(response, {
    'update task: status is 200': (r) => r.status === 200,
  });

  // Record metrics
  updateTaskDuration.add(response.timings.duration);
  updateTaskErrors.add(!success);
  updateTaskCounter.add(1);

  return success;
}

/**
 * Delete a task
 */
function deleteTask(user, taskId) {
  const url = `${BASE_URL}/api/${user.user_id}/tasks/${taskId}`;

  const params = {
    tags: { operation: 'delete_task' },
  };

  const response = http.del(url, null, params);

  // Check response
  const success = check(response, {
    'delete task: status is 200 or 204': (r) => r.status === 200 || r.status === 204,
  });

  // Record metrics
  deleteTaskDuration.add(response.timings.duration);
  deleteTaskErrors.add(!success);
  deleteTaskCounter.add(1);

  return success;
}

// ============================================================================
// Test Scenario: Mixed Workload
// ============================================================================

export default function () {
  // Select a random user for this iteration
  const user = getRandomUser();

  // Store created task IDs for later operations
  let createdTaskIds = [];

  // Decision tree based on weighted distribution
  const action = Math.random();

  if (action < 0.40) {
    // 40% - Create task
    const taskId = createTask(user);
    if (taskId) {
      createdTaskIds.push(taskId);
    }

  } else if (action < 0.70) {
    // 30% - List tasks with filters
    const tasks = listTasks(user);

    // Randomly select a task for further operations
    if (tasks.length > 0) {
      createdTaskIds = tasks.map(t => t.task_id).slice(0, 5); // Take up to 5 tasks
    }

  } else if (action < 0.90) {
    // 20% - Update task status
    // First list tasks to get some task IDs
    const tasks = listTasks(user);

    if (tasks.length > 0) {
      const randomTask = randomItem(tasks);
      updateTask(user, randomTask.task_id);
    } else {
      // Create a task first if none exist
      const taskId = createTask(user);
      if (taskId) {
        updateTask(user, taskId);
      }
    }

  } else {
    // 10% - Delete task
    // First list tasks to get some task IDs
    const tasks = listTasks(user);

    if (tasks.length > 0) {
      const randomTask = randomItem(tasks);
      deleteTask(user, randomTask.task_id);
    }
  }

  // Think time between requests (0.5-2 seconds)
  sleep(randomIntBetween(0.5, 2));
}

// ============================================================================
// Setup and Teardown
// ============================================================================

/**
 * Setup function runs once before all VUs start
 */
export function setup() {
  console.log('============================================');
  console.log('Todo App Load Test Starting');
  console.log('============================================');
  console.log(`Base URL: ${BASE_URL}`);
  console.log(`Test Users: ${TEST_USERS.length}`);
  console.log(`Target VUs: 1000`);
  console.log(`Duration: 5 minutes sustained load`);
  console.log('============================================');

  // Verify backend is accessible
  const response = http.get(`${BASE_URL}/health`);
  if (response.status !== 200) {
    console.error('❌ Backend health check failed!');
    console.error(`Status: ${response.status}`);
    console.error(`Response: ${response.body}`);
    throw new Error('Backend is not accessible');
  }

  console.log('✓ Backend health check passed');
  console.log('============================================');

  return { startTime: new Date() };
}

/**
 * Teardown function runs once after all VUs finish
 */
export function teardown(data) {
  const endTime = new Date();
  const duration = (endTime - data.startTime) / 1000;

  console.log('============================================');
  console.log('Todo App Load Test Complete');
  console.log('============================================');
  console.log(`Total Duration: ${duration.toFixed(2)}s`);
  console.log('============================================');
  console.log('Check results above for:');
  console.log('  - P95 latency (should be <5s)');
  console.log('  - Error rate (should be <1%)');
  console.log('  - Throughput (should be >100 req/s)');
  console.log('============================================');
}

// ============================================================================
// Advanced Scenarios (Optional)
// ============================================================================

/**
 * Spike test: Sudden traffic spike
 */
export function spikeTest() {
  const user = getRandomUser();

  // Rapid fire requests
  for (let i = 0; i < 10; i++) {
    createTask(user);
  }

  sleep(0.1);
}

/**
 * Stress test: Beyond normal capacity
 */
export function stressTest() {
  const user = getRandomUser();

  // Create multiple tasks rapidly
  const taskIds = [];
  for (let i = 0; i < 5; i++) {
    const taskId = createTask(user);
    if (taskId) taskIds.push(taskId);
  }

  // List tasks multiple times
  for (let i = 0; i < 3; i++) {
    listTasks(user);
  }

  // Update all created tasks
  taskIds.forEach(id => updateTask(user, id));

  sleep(0.5);
}
