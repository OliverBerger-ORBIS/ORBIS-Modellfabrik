/**
 * Simple test script to verify handlers can parse test data
 */
const fs = require('fs');
const path = require('path');

// Import the built handlers
const { handleOrderCompleted } = require('./dist/handlers/orderCompletedHandler');
const { handleStock } = require('./dist/handlers/stockHandler');

console.log('=== Testing Handlers ===\n');

// Test 1: Order Completed Handler
console.log('Test 1: Order Completed Handler');
try {
  const testFile = '../../data/omf-data/test_topics/ccu_order_completed_storage_005.json';
  const data = fs.readFileSync(path.join(__dirname, testFile), 'utf8');
  const points = handleOrderCompleted('ccu/order/completed', data);
  console.log(`✓ Parsed ${points.length} points from order completed message`);
  if (points.length > 0) {
    console.log(`  Sample point: ${points[0].toLineProtocol()}`);
  }
} catch (error) {
  console.error('✗ Error:', error.message);
}

console.log('\nTest 2: Stock Handler');
try {
  const testFile = '../../data/omf-data/test_topics/_j1_txt_1_f_i_stock__000089.json';
  const data = fs.readFileSync(path.join(__dirname, testFile), 'utf8');
  const points = handleStock('/j1/txt/1/f/i/stock', data);
  console.log(`✓ Parsed ${points.length} points from stock message`);
  if (points.length > 0) {
    console.log(`  Sample point: ${points[0].toLineProtocol()}`);
  }
} catch (error) {
  console.error('✗ Error:', error.message);
}

console.log('\n=== Tests Complete ===');
