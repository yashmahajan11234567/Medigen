import requests
import random
from datetime import date, timedelta

base = 'http://localhost:8000'
email = f'sched_test_{random.randint(1000,9999)}@example.com'
password = 'TestPass123!'

# Setup auth
r = requests.post(f'{base}/api/v1/auth/register', json={'full_name': 'Test User', 'email': email, 'password': password})
print(f'Register: {r.status_code}')

r = requests.post(f'{base}/api/v1/auth/login', json={'email': email, 'password': password})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}
print(f'Login: {r.status_code}')

# Helper to create inventory item and get medicine_id
def create_medicine(name, mtype='tablet', qty=20):
    r = requests.post(f'{base}/api/v1/inventory', headers=headers, json={
        'name': name, 'type': mtype, 'quantity': qty, 'expiry_date': '2026-12-31', 'batch_number': 'B001'
    })
    return r.json()['id'], r.json()['medicine_id']

print('\n===== SCHEDULE MODULE TESTS =====\n')

# ===== TEST 1: Create schedule (valid) =====
print('[TEST 1] Create schedule (valid)')
med_inv_id, med_id = create_medicine('Paracetamol 500mg')
print(f'  Medicine ID: {med_id}')

r = requests.post(f'{base}/api/v1/schedule', headers=headers, json={
    'medicine_id': med_id,
    'dosage_pattern': '1-0-1',
    'dosage_amount': '1 tablet',
    'start_date': '2026-07-21',
    'end_date': '2026-07-31',
    'food_timing': 'after_food',
    'source': 'manual',
    'quantity': 30,
    'quantity_unit': 'tablet'
})
print(f'  POST /api/v1/schedule: {r.status_code}')
if r.status_code == 201:
    sched_id = r.json()['id']
    print(f'  Created schedule ID: {sched_id}')
    print(f'  Reminders: {len(r.json().get("reminders", []))}')
else:
    print(f'  FAIL: {r.text}')
    sched_id = None

# ===== TEST 2: Edit schedule (update dosage) =====
print('\n[TEST 2] Edit schedule (update dosage)')
if sched_id:
    r = requests.put(f'{base}/api/v1/schedule/{sched_id}', headers=headers, json={
        'dosage_pattern': '1-1-1',
        'dosage_amount': '1 tablet',
    })
    print(f'  PUT /api/v1/schedule/{sched_id}: {r.status_code}')
    if r.status_code == 200:
        print(f'  Updated dosage_pattern: {r.json().get("dosage_pattern")}')
    else:
        print(f'  FAIL: {r.text}')

# ===== TEST 3: Get schedule details =====
print('\n[TEST 3] Get schedule details')
if sched_id:
    r = requests.get(f'{base}/api/v1/schedule/{sched_id}', headers=headers)
    print(f'  GET /api/v1/schedule/{sched_id}: {r.status_code}')
    if r.status_code == 200:
        data = r.json()
        print(f'  medicine_name: {data.get("medicine_name")}')
        print(f'  dosage_pattern: {data.get("dosage_pattern")}')
        print(f'  reminders: {len(data.get("reminders", []))}')
        print(f'  status: {data.get("status")}')
    else:
        print(f'  FAIL: {r.text}')

# ===== TEST 4: List all schedules =====
print('\n[TEST 4] List all schedules')
r = requests.get(f'{base}/api/v1/schedule', headers=headers)
print(f'  GET /api/v1/schedule: {r.status_code}')
if r.status_code == 200:
    items = r.json().get('items', [])
    print(f'  Count: {len(items)}')
    for item in items:
        print(f'    - {item.get("medicine_name")} ({item.get("dosage_pattern")}) [{item.get("status")}]')
else:
    print(f'  FAIL: {r.text}')

# ===== TEST 5: Today's schedule =====
print('\n[TEST 5] Today\'s schedule')
r = requests.get(f'{base}/api/v1/schedule/today', headers=headers)
print(f'  GET /api/v1/schedule/today: {r.status_code}')
if r.status_code == 200:
    items = r.json().get('items', [])
    print(f'  Count: {len(items)}')
    for item in items:
        print(f'    - {item.get("medicine_name")} reminders: {len(item.get("reminders", []))}')
else:
    print(f'  FAIL: {r.text}')

# ===== TEST 6: Complete a reminder =====
print('\n[TEST 6] Complete a reminder')
if sched_id:
    # Get schedule to find a reminder_id
    r = requests.get(f'{base}/api/v1/schedule/{sched_id}', headers=headers)
    if r.status_code == 200:
        reminders = r.json().get('reminders', [])
        if reminders:
            reminder_id = reminders[0]['id']
            r = requests.post(f'{base}/api/v1/schedule/{sched_id}/complete', headers=headers, json={
                'reminder_id': reminder_id,
                'taken': True
            })
            print(f'  POST /api/v1/schedule/{sched_id}/complete: {r.status_code}')
            if r.status_code == 200:
                print(f'  Completed at: {r.json().get("completed_at")}')
            else:
                print(f'  FAIL: {r.text}')
        else:
            print('  No reminders to complete')
    else:
        print(f'  FAIL getting schedule: {r.text}')

# ===== TEST 7: Validation - Missing required fields =====
print('\n[TEST 7] Validation - Missing required fields')
r = requests.post(f'{base}/api/v1/schedule', headers=headers, json={
    'medicine_id': med_id,
    # missing dosage_pattern, food_timing, start_date, source
})
print(f'  POST /api/v1/schedule (missing fields): {r.status_code}')
if r.status_code == 422:
    print('  PASS: Returns 422 validation error')
else:
    print(f'  FAIL: Expected 422, got {r.status_code}: {r.text}')

# ===== TEST 8: Validation - Invalid dates =====
print('\n[TEST 8] Validation - Invalid dates (end before start)')
r = requests.post(f'{base}/api/v1/schedule', headers=headers, json={
    'medicine_id': med_id,
    'dosage_pattern': '1-0-1',
    'food_timing': 'after_food',
    'start_date': '2026-07-31',
    'end_date': '2026-07-21',  # before start
    'source': 'manual'
})
print(f'  POST /api/v1/schedule (invalid dates): {r.status_code}')
if r.status_code == 422:
    print('  PASS: Returns 422 validation error')
else:
    print(f'  FAIL: Expected 422, got {r.status_code}: {r.text}')

# ===== TEST 9: Validation - Invalid dosage pattern =====
print('\n[TEST 9] Validation - Invalid dosage pattern')
r = requests.post(f'{base}/api/v1/schedule', headers=headers, json={
    'medicine_id': med_id,
    'dosage_pattern': 'invalid-pattern',
    'food_timing': 'after_food',
    'start_date': '2026-07-21',
    'source': 'manual'
})
print(f'  POST /api/v1/schedule (invalid pattern): {r.status_code}')
if r.status_code == 422:
    print('  PASS: Returns 422 validation error')
else:
    print(f'  FAIL: Expected 422, got {r.status_code}: {r.text}')

# ===== TEST 10: Validation - All zero dosage =====
print('\n[TEST 10] Validation - All zero dosage pattern')
r = requests.post(f'{base}/api/v1/schedule', headers=headers, json={
    'medicine_id': med_id,
    'dosage_pattern': '0-0-0',
    'food_timing': 'after_food',
    'start_date': '2026-07-21',
    'source': 'manual'
})
print(f'  POST /api/v1/schedule (0-0-0 pattern): {r.status_code}')
if r.status_code == 422:
    print('  PASS: Returns 422 validation error')
else:
    print(f'  FAIL: Expected 422, got {r.status_code}: {r.text}')

# ===== TEST 11: Create schedule with before_food timing =====
print('\n[TEST 11] Create schedule with before_food timing')
med_inv_id2, med_id2 = create_medicine('Ibuprofen 200mg')
r = requests.post(f'{base}/api/v1/schedule', headers=headers, json={
    'medicine_id': med_id2,
    'dosage_pattern': '1-0-0',
    'dosage_amount': '1 tablet',
    'start_date': '2026-07-21',
    'end_date': '2026-07-25',
    'food_timing': 'before_food',
    'source': 'manual'
})
print(f'  POST /api/v1/schedule (before_food): {r.status_code}')
if r.status_code == 201:
    sched_id2 = r.json()['id']
    print(f'  Created schedule ID: {sched_id2}')
    print(f'  food_timing: {r.json().get("food_timing")}')
else:
    print(f'  FAIL: {r.text}')

# ===== TEST 12: Create schedule from bill (if endpoint exists) =====
print('\n[TEST 12] Create schedule from bill')
r = requests.post(f'{base}/api/v1/schedule/from-bill', headers=headers, json={
    'medicine_name': 'Paracetamol 500mg',
    'quantity': 20,
    'purchase_date': '2026-07-21',
    'expiry_date': '2026-12-31',
    'pharmacy_name': 'Test Pharmacy',
    'dosage_pattern': '1-0-1',
    'food_timing': 'after_food',
    'start_date': '2026-07-21',
    'end_date': '2026-07-31'
})
print(f'  POST /api/v1/schedule/from-bill: {r.status_code}')
if r.status_code == 201:
    print(f'  Created schedule ID: {r.json().get("id")}')
    print(f'  source: {r.json().get("source")}')
else:
    print(f'  Response: {r.text}')

# ===== TEST 13: Delete schedule =====
print('\n[TEST 13] Delete schedule')
if sched_id:
    r = requests.delete(f'{base}/api/v1/schedule/{sched_id}', headers=headers)
    print(f'  DELETE /api/v1/schedule/{sched_id}: {r.status_code}')
    if r.status_code == 200:
        print('  PASS: Schedule deleted')
    else:
        print(f'  FAIL: {r.text}')

# ===== TEST 14: Verify deletion =====
print('\n[TEST 14] Verify deletion')
r = requests.get(f'{base}/api/v1/schedule', headers=headers)
print(f'  GET /api/v1/schedule: {r.status_code}')
if r.status_code == 200:
    items = r.json().get('items', [])
    print(f'  Remaining schedules: {len(items)}')

# ===== TEST 15: Get deleted schedule (should 404) =====
print('\n[TEST 15] Get deleted schedule (should 404)')
if sched_id:
    r = requests.get(f'{base}/api/v1/schedule/{sched_id}', headers=headers)
    print(f'  GET /api/v1/schedule/{sched_id}: {r.status_code}')
    if r.status_code == 404:
        print('  PASS: Returns 404')
    else:
        print(f'  FAIL: Expected 404, got {r.status_code}: {r.text}')

# ===== TEST 16: Create multiple schedules, test today endpoint =====
print('\n[TEST 16] Multiple schedules - today endpoint')
today = date.today()
tomorrow = (today + timedelta(days=1)).isoformat()
today_str = today.isoformat()

med_inv_id3, med_id3 = create_medicine('Vitamin D3')
r = requests.post(f'{base}/api/v1/schedule', headers=headers, json={
    'medicine_id': med_id3,
    'dosage_pattern': '1-0-0',
    'dosage_amount': '1 capsule',
    'start_date': today_str,
    'end_date': tomorrow,
    'food_timing': 'after_food',
    'source': 'manual'
})
print(f'  Create schedule for today: {r.status_code}')

r = requests.get(f'{base}/api/v1/schedule/today', headers=headers)
print(f'  GET /api/v1/schedule/today: {r.status_code}')
if r.status_code == 200:
    items = r.json().get('items', [])
    print(f'  Today schedules: {len(items)}')
    for item in items:
        print(f'    - {item.get("medicine_name")} reminders: {len(item.get("reminders", []))}')

# ===== TEST 17: Test status field =====
print('\n[TEST 17] Schedule status field')
med_inv_id4, med_id4 = create_medicine('Aspirin 100mg')
r = requests.post(f'{base}/api/v1/schedule', headers=headers, json={
    'medicine_id': med_id4,
    'dosage_pattern': '0-1-0',
    'dosage_amount': '1 tablet',
    'start_date': '2026-07-21',
    'end_date': '2026-07-31',
    'food_timing': 'after_food',
    'source': 'manual'
})
if r.status_code == 201:
    sched = r.json()
    print(f'  Created schedule status: {sched.get("status")}')
    print(f'  source: {sched.get("source")}')

# ===== TEST 18: Update schedule status to paused =====
print('\n[TEST 18] Update schedule status to paused')
if r.status_code == 201:
    sched_id_paused = r.json()['id']
    r = requests.put(f'{base}/api/v1/schedule/{sched_id_paused}', headers=headers, json={
        'status': 'paused'
    })
    print(f'  PUT /api/v1/schedule/{sched_id_paused} (paused): {r.status_code}')
    if r.status_code == 200:
        print(f'  Updated status: {r.json().get("status")}')
    else:
        print(f'  FAIL: {r.text}')

# ===== TEST 19: Update schedule end_date =====
print('\n[TEST 19] Update schedule end_date')
if sched_id_paused:
    r = requests.put(f'{base}/api/v1/schedule/{sched_id_paused}', headers=headers, json={
        'end_date': '2026-08-15'
    })
    print(f'  PUT /api/v1/schedule/{sched_id_paused} (extend end_date): {r.status_code}')
    if r.status_code == 200:
        print(f'  New end_date: {r.json().get("end_date")}')
    else:
        print(f'  FAIL: {r.text}')

# ===== TEST 20: Reminder generation count =====
print('\n[TEST 20] Reminder generation count validation')
med_inv_id5, med_id5 = create_medicine('Test Med 5')
r = requests.post(f'{base}/api/v1/schedule', headers=headers, json={
    'medicine_id': med_id5,
    'dosage_pattern': '1-1-1',
    'dosage_amount': '1 tablet',
    'start_date': '2026-07-21',
    'end_date': '2026-07-23',  # 3 days
    'food_timing': 'after_food',
    'source': 'manual'
})
if r.status_code == 201:
    reminders = r.json().get('reminders', [])
    expected = 3 * 3  # 3 days * 3 periods (morning, afternoon, night)
    print(f'  3 days, 1-1-1 pattern: {len(reminders)} reminders (expected {expected})')
    if len(reminders) == expected:
        print('  PASS: Correct reminder count')
    else:
        print('  FAIL: Incorrect reminder count')

print('\n===== ALL TESTS COMPLETED =====')