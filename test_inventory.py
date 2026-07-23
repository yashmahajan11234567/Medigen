import requests
import random
from datetime import date, timedelta

base = 'http://localhost:8000'
email = f'inv_test_{random.randint(1000,9999)}@example.com'
password = 'TestPass123!'

# Setup
r = requests.post(f'{base}/api/v1/auth/register', json={'full_name': 'Test User', 'email': email, 'password': password})
r = requests.post(f'{base}/api/v1/auth/login', json={'email': email, 'password': password})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}

print('===== INVENTORY MODULE TESTS =====')

# ===== TEST 1: List inventory (empty) =====
print('\n[TEST 1] List inventory (empty)')
r = requests.get(f'{base}/api/v1/inventory', headers=headers)
assert r.status_code == 200 and r.json()['items'] == [], f'FAIL: {r.json()}'
print('  PASS')

# ===== TEST 2: Add medicine =====
print('[TEST 2] Add medicine')
r = requests.post(f'{base}/api/v1/inventory', headers=headers, json={
    'name': 'Paracetamol 500mg', 'type': 'tablet', 'quantity': 20, 'expiry_date': '2026-12-31', 'batch_number': 'BATCH001'
})
assert r.status_code == 201 and 'id' in r.json(), f'FAIL: {r.json()}'
inv_id = r.json()['id']
medicine_id = r.json()['medicine_id']
print(f'  PASS (id={inv_id})')

# ===== TEST 3: List inventory (with item) =====
print('[TEST 3] List inventory (with item)')
r = requests.get(f'{base}/api/v1/inventory', headers=headers)
assert r.status_code == 200 and len(r.json()['items']) == 1, f'FAIL: {r.json()}'
print('  PASS')

# ===== TEST 4: Get single medicine =====
print('[TEST 4] Get single medicine')
r = requests.get(f'{base}/api/v1/inventory/{inv_id}', headers=headers)
assert r.status_code == 200 and r.json()['id'] == inv_id, f'FAIL: {r.json()}'
print('  PASS')

# ===== TEST 5: Edit medicine (update quantity) =====
print('[TEST 5] Edit medicine (update quantity)')
r = requests.put(f'{base}/api/v1/inventory/{inv_id}', headers=headers, json={'quantity': 15})
assert r.status_code == 200 and r.json()['quantity'] == 15.0, f'FAIL: {r.json()}'
print('  PASS')

# ===== TEST 6: Edit medicine (update name) =====
print('[TEST 6] Edit medicine (update name)')
r = requests.put(f'{base}/api/v1/inventory/{inv_id}', headers=headers, json={'name': 'Paracetamol 650mg'})
assert r.status_code == 200 and r.json()['name'] == 'Paracetamol 650mg', f'FAIL: {r.json()}'
print('  PASS')

# ===== TEST 7: Search (match) =====
print('[TEST 7] Search (match)')
r = requests.get(f'{base}/api/v1/inventory/search?query=Paracetamol', headers=headers)
assert r.status_code == 200 and len(r.json()['items']) == 1, f'FAIL: {r.json()}'
print('  PASS')

# ===== TEST 8: Search (no match) =====
print('[TEST 8] Search (no match)')
r = requests.get(f'{base}/api/v1/inventory/search?query=Ibuprofen', headers=headers)
assert r.status_code == 200 and len(r.json()['items']) == 0, f'FAIL: {r.json()}'
print('  PASS')

# ===== TEST 9: Filter by status =====
print('[TEST 9] Filter by status (available)')
r = requests.get(f'{base}/api/v1/inventory/filter?status=available', headers=headers)
assert r.status_code == 200 and len(r.json()['items']) == 1, f'FAIL: {r.json()}'
print('  PASS')

# ===== TEST 10: Filter by type =====
print('[TEST 10] Filter by type (tablet)')
r = requests.get(f'{base}/api/v1/inventory/filter?type=tablet', headers=headers)
assert r.status_code == 200 and len(r.json()['items']) == 1, f'FAIL: {r.json()}'
print('  PASS')

# ===== TEST 11: Summary =====
print('[TEST 11] Summary')
r = requests.get(f'{base}/api/v1/inventory/summary', headers=headers)
assert r.status_code == 200 and r.json()['total_medicines'] == 1, f'FAIL: {r.json()}'
print('  PASS')

# ===== TEST 12: Delete medicine =====
print('[TEST 12] Delete medicine')
r = requests.delete(f'{base}/api/v1/inventory/{inv_id}', headers=headers)
assert r.status_code == 200, f'FAIL: {r.status_code} {r.text}'
print('  PASS')

# ===== TEST 13: Verify deleted =====
print('[TEST 13] Verify deleted')
r = requests.get(f'{base}/api/v1/inventory', headers=headers)
assert r.status_code == 200 and len(r.json()['items']) == 0, f'FAIL: {r.json()}'
print('  PASS')

# ===== TEST 14: Add multiple types =====
print('[TEST 14] Add multiple types')
for name, mtype in [('Amoxicillin 250mg', 'capsule'), ('Cough Syrup', 'syrup'), ('Skin Cream', 'cream')]:
    r = requests.post(f'{base}/api/v1/inventory', headers=headers, json={
        'name': name, 'type': mtype, 'quantity': 10, 'expiry_date': '2026-12-31', 'batch_number': 'B001'
    })
    assert r.status_code == 201, f'FAIL: {r.status_code} {r.text}'
r = requests.get(f'{base}/api/v1/inventory', headers=headers)
# Only 3 items added in this test (previous one was deleted in test 12/13)
assert len(r.json()['items']) == 3, f'FAIL: {len(r.json()["items"])} items'
print('  PASS')

# ===== TEST 15: Filter by different types =====
print('[TEST 15] Filter by capsule')
r = requests.get(f'{base}/api/v1/inventory/filter?type=capsule', headers=headers)
assert r.status_code == 200 and len(r.json()['items']) == 1, f'FAIL: {r.json()}'
print('  PASS')

print('[TEST 16] Filter by syrup')
r = requests.get(f'{base}/api/v1/inventory/filter?type=syrup', headers=headers)
assert r.status_code == 200 and len(r.json()['items']) == 1, f'FAIL: {r.json()}'
print('  PASS')

print('[TEST 17] Filter by cream')
r = requests.get(f'{base}/api/v1/inventory/filter?type=cream', headers=headers)
assert r.status_code == 200 and len(r.json()['items']) == 1, f'FAIL: {r.json()}'
print('  PASS')

# ===== TEST 18: Filter by status finished =====
print('[TEST 18] Filter by status (finished/out_of_stock)')
# Add a tablet to test with
r = requests.post(f'{base}/api/v1/inventory', headers=headers, json={
    'name': 'Test Tablet', 'type': 'tablet', 'quantity': 10, 'expiry_date': '2026-12-31', 'batch_number': 'TAB001'
})
assert r.status_code == 201
r = requests.get(f'{base}/api/v1/inventory', headers=headers)
items = r.json()['items']
tablet_item = next(i for i in items if i['type'] == 'tablet')
r = requests.put(f'{base}/api/v1/inventory/{tablet_item["id"]}', headers=headers, json={'quantity': 0})
assert r.status_code == 200
r = requests.get(f'{base}/api/v1/inventory/filter?status=finished', headers=headers)
assert r.status_code == 200 and len(r.json()['items']) >= 1, f'FAIL: {r.json()}'
print('  PASS')

# ===== TEST 19: Filter expired =====
print('[TEST 19] Filter by status (expired)')
r = requests.post(f'{base}/api/v1/inventory', headers=headers, json={
    'name': 'Old Medicine', 'type': 'tablet', 'quantity': 5, 'expiry_date': '2020-01-01', 'batch_number': 'OLD001'
})
assert r.status_code == 201
r = requests.get(f'{base}/api/v1/inventory/filter?status=expired', headers=headers)
assert r.status_code == 200 and len(r.json()['items']) >= 1, f'FAIL: {r.json()}'
print('  PASS')

# ===== TEST 20: Filter expiring soon =====
print('[TEST 20] Filter by status (expiring_soon)')
soon = (date.today() + timedelta(days=15)).isoformat()
r = requests.post(f'{base}/api/v1/inventory', headers=headers, json={
    'name': 'Expiring Soon', 'type': 'tablet', 'quantity': 5, 'expiry_date': soon, 'batch_number': 'SOON001'
})
assert r.status_code == 201
r = requests.get(f'{base}/api/v1/inventory/filter?status=expiring_soon', headers=headers)
assert r.status_code == 200 and len(r.json()['items']) >= 1, f'FAIL: {r.json()}'
print('  PASS')

print('\n===== ALL 20 TESTS PASSED =====')