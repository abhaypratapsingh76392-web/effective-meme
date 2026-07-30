import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import requests
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- HUGGING FACE / RENDER BYPASS ---
def custom_sender(method, url, **kwargs):
    url = url.replace("api.telegram.org", "149.154.167.220")
    kwargs['verify'] = False
    headers = kwargs.get('headers', {})
    headers['Host'] = 'api.telegram.org'
    kwargs['headers'] = headers
    return requests.request(method, url, **kwargs)

telebot.apihelper.CUSTOM_REQUEST_SENDER = custom_sender
# ---------------------------

TOKEN = "8378116514:AAHbpgQ3GE1mic5CevK7ovLA-VI4lmAKZmw"
bot = telebot.TeleBot(TOKEN)
ADMIN_CHANNEL = "@fjfjdjdu" 
FIREBASE_URL = "https://movie-ee8bb-default-rtdb.firebaseio.com"

user_states = {}

# --- FIREBASE DATABASE FUNCTIONS ---
def get_user(user_id):
    try:
        url = f"{FIREBASE_URL}/users/{user_id}.json"
        response = requests.get(url)
        data = response.json()
        if not data: return None
        return data
    except Exception as e: return None

def create_user(user_id):
    new_user = {
        "balance": 0.0,
        "upi": "Not Set",
        "last_bonus": 0,
        "total_earned": 0.0,
        "total_withdrawn": 0.0
    }
    requests.put(f"{FIREBASE_URL}/users/{user_id}.json", json=new_user)
    return new_user

def update_db(user_id, data):
    try:
        requests.patch(f"{FIREBASE_URL}/users/{user_id}.json", json=data)
    except Exception as e: pass

def save_withdrawal(user_id, amount, status):
    try:
        req_id = int(time.time() * 1000)
        url = f"{FIREBASE_URL}/withdrawals/{req_id}.json"
        data = {"user_id": user_id, "amount": amount, "status": status, "timestamp": time.time()}
        requests.put(url, json=data)
        return req_id
    except: return None

def update_withdrawal_status(req_id, status):
    try:
        requests.patch(f"{FIREBASE_URL}/withdrawals/{req_id}.json", json={"status": status})
    except: pass

def check_join(user_id):
    try:
        chat_member = bot.get_chat_member("@earnbox1", user_id)
        if chat_member.status in ['member', 'administrator', 'creator', 'restricted']:
            return True
        else: return False
    except Exception as e: return False

# --- KEYBOARDS ---
def force_sub_markup():
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📢 Join Channel", url="https://t.me/earnbox1"))
    markup.add(InlineKeyboardButton("✅ Verify", callback_data="verify_join"))
    return markup

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("🎁 Daily Bonus"), KeyboardButton("🎟️ Redeem Code"))
    markup.row(KeyboardButton("💰 My Balance"), KeyboardButton("🔗 Bonus Refer Link"))
    markup.row(KeyboardButton("📊 Status"), KeyboardButton("💳 Withdraw"))
    return markup

def back_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("🔙 Back to Main Menu"))
    return markup

def withdraw_menu_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(KeyboardButton("🏦 Set / Change UPI ID"), KeyboardButton("💸 Request Withdrawal"))
    markup.row(KeyboardButton("📋 My Withdrawal History"))
    markup.add(KeyboardButton("🔙 Back to Main Menu"))
    return markup

# --- BOT HANDLERS ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    args = message.text.split()
    user_data = get_user(user_id)
    is_new = user_data is None
    
    if is_new:
        create_user(user_id)
        if len(args) > 1:
            try:
                referrer_id = int(args[1])
                if referrer_id != user_id:
                    ref_data = get_user(referrer_id)
                    if ref_data:
                        new_bal = ref_data['balance'] + 3.0
                        new_earned = ref_data['total_earned'] + 3.0
                        update_db(referrer_id, {"balance": new_bal, "total_earned": new_earned})
                        try: bot.send_message(referrer_id, f"🎉 **Congratulations!**\nKisine aapke refer link se bot start kiya hai. Aapko **₹3** mil gaye!", parse_mode="Markdown")
                        except: pass
            except: pass
    
    if not check_join(user_id):
        bot.send_message(user_id, "BOT DAILY CODE CHANNEL JOIN ENJOY 😉", reply_markup=force_sub_markup())
        return
        
    text = (
        "🌟 **Best Earning Bot For Withdrawal UPI ID** 🌟\n\n"
        "Welcome to the most VIP earning bot! Yahan aap daily bonus, codes redeem kar, aur dosto ko refer karke real cash earn kar sakte ho.\n\n"
        "👇 Niche diye gaye options ka use karein aur earning shuru karein!"
    )
    bot.send_message(message.chat.id, text, reply_markup=main_menu(), parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "verify_join")
def verify_callback(call):
    if check_join(call.from_user.id):
        bot.edit_message_text("✅ **Verification Successful!**", call.message.chat.id, call.message.message_id)
        bot.send_message(call.from_user.id, "Choose an option 👇", reply_markup=main_menu())
    else:
        bot.answer_callback_query(call.id, "❌ Aapne abhi tak channel join nahi kiya hai! Pehle join karein.", show_alert=True)

@bot.message_handler(func=lambda message: message.text == "🔙 Back to Main Menu")
def back_handler(message):
    user_states.pop(message.from_user.id, None)
    bot.send_message(message.chat.id, "🏡 Main menu mein wapas aa gaye:", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "🎁 Daily Bonus")
def daily_bonus(message):
    user_id = message.from_user.id
    if not check_join(user_id): return
    user = get_user(user_id)
    current_time = int(time.time())
    
    if current_time - user['last_bonus'] >= 86400:
        new_bal = user['balance'] + 2.0
        new_earned = user['total_earned'] + 2.0
        update_db(user_id, {"balance": new_bal, "last_bonus": current_time, "total_earned": new_earned})
        bot.send_message(user_id, "🎁 **Daily Bonus Claimed!**\nAapke account mein **₹2** add ho gaye hain.", parse_mode="Markdown")
    else:
        left_time = 86400 - (current_time - user['last_bonus'])
        hours = left_time // 3600
        mins = (left_time % 3600) // 60
        bot.send_message(user_id, f"⏳ Aapne aaj ka bonus le liya hai. Next bonus **{hours} hours aur {mins} minutes** baad milega.", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "🎟️ Redeem Code")
def redeem_code_start(message):
    user_id = message.from_user.id
    if not check_join(user_id): return
    user_states[user_id] = "waiting_for_redeem_code"
    text = (
        "THE CODE generate\n"
        "WEBSITE https://generate.10001mb.com/\n"
        "generate CODE AND ENTER OK\n\n"
        "ENTER YOUR CODE:"
    )
    bot.send_message(user_id, text, reply_markup=back_menu(), disable_web_page_preview=True)

@bot.message_handler(func=lambda message: message.text == "🔗 Bonus Refer Link")
def refer_link(message):
    if not check_join(message.from_user.id): return
    bot_info = bot.get_me()
    ref_link = f"https://t.me/{bot_info.username}?start={message.from_user.id}"
    text = (
        "🔗 **Aapka VIP Refer Link** 🔗\n\n"
        f"`{ref_link}`\n\n"
        "Apne dosto ko invite karein aur per refer **₹3** kamayein! Jaise hi wo aapke link se bot start karenge, paise turant mil jayenge."
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "💰 My Balance")
def my_balance(message):
    if not check_join(message.from_user.id): return
    user = get_user(message.from_user.id)
    bot.send_message(message.chat.id, f"💵 **Aapka Real Balance:** ₹{user['balance']:.2f}", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "📊 Status")
def status_menu(message):
    if not check_join(message.from_user.id): return
    user = get_user(message.from_user.id)
    text = (
        "📊 **Aapka Earning Status** 📊\n\n"
        f"💵 **Total Earned:** ₹{user['total_earned']:.2f}\n"
        f"💸 **Total Withdrawn:** ₹{user['total_withdrawn']:.2f}\n"
        f"💳 **Current Balance:** ₹{user['balance']:.2f}\n"
        f"🏦 **UPI ID:** `{user['upi']}`"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "💳 Withdraw")
def withdraw_menu(message):
    user_id = message.from_user.id
    if not check_join(user_id): return
    user = get_user(user_id)
    bot.send_message(user_id, f"💳 **Withdrawal Section**\n\n**Aapki Current UPI:** `{user['upi']}`\n**Current Balance:** ₹{user['balance']:.2f}", reply_markup=withdraw_menu_keyboard(), parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "🏦 Set / Change UPI ID")
def set_upi(message):
    user_states[message.from_user.id] = "waiting_for_upi"
    bot.send_message(message.chat.id, "🏦 Kripya apni nayi **UPI ID** send karein:", reply_markup=back_menu(), parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "💸 Request Withdrawal")
def req_withdraw(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    if user['upi'] == 'Not Set':
        bot.send_message(message.chat.id, "⚠️ Pehle apni UPI ID set karein!")
        return
    if user['balance'] < 380:
        bot.send_message(message.chat.id, "⚠️ YOUR BALANCE LOW PLEASE EARN MAXIMUM WITHDRAWAL LIMIT 380", reply_markup=main_menu())
        return
        
    user_states[user_id] = "waiting_for_amount"
    bot.send_message(message.chat.id, f"💸 **Withdrawal Limit:** Minimum ₹380\n\nAap kitna amount nikalna chahte hain? (Current Balance: ₹{user['balance']:.2f})", reply_markup=back_menu(), parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text == "📋 My Withdrawal History")
def withdrawal_history(message):
    user_id = message.from_user.id
    try:
        res = requests.get(f"{FIREBASE_URL}/withdrawals.json").json()
        if not res:
            bot.send_message(message.chat.id, "📭 Aapne abhi tak koi withdrawal request nahi lagayi hai.")
            return
            
        history = []
        for req_id, data in res.items():
            if data['user_id'] == user_id: history.append(data)
                
        if not history:
            bot.send_message(message.chat.id, "📭 Aapne abhi tak koi withdrawal request nahi lagayi hai.")
            return
            
        text = "📋 **Aapki Withdrawal History:**\n\n"
        for row in reversed(history[-10:]):
            status = row['status']
            icon = "⏳" if status == "Pending" else "✅" if status == "Completed" else "❌"
            text += f"{icon} **Amount:** ₹{row['amount']} | **Status:** {status}\n"
            
        bot.send_message(message.chat.id, text, parse_mode="Markdown")
    except:
        bot.send_message(message.chat.id, "⚠️ Server Error fetching history.")

@bot.message_handler(func=lambda message: message.from_user.id in user_states)
def handle_states(message):
    user_id = message.from_user.id
    state = user_states[user_id]
    user = get_user(user_id)
    
    if state == "waiting_for_upi":
        new_upi = message.text
        update_db(user_id, {"upi": new_upi})
        user_states.pop(user_id, None)
        bot.send_message(message.chat.id, f"✅ Aapki UPI ID successully set ho gayi hai:\n`{new_upi}`", reply_markup=withdraw_menu_keyboard(), parse_mode="Markdown")
        
    elif state == "waiting_for_redeem_code":
        code = message.text.strip()
        try:
            res = requests.get(f"{FIREBASE_URL}/nino_codes/{code}.json").json()
            if res and isinstance(res, dict):
                used_by = res.get('used_by', {})
                if str(user_id) in used_by:
                    bot.send_message(message.chat.id, "❌ Aapne yeh code pehle hi use kar liya hai (Already Used)!", reply_markup=main_menu())
                    user_states.pop(user_id, None)
                    return
                
                is_used = res.get('isUsed', False)
                max_uses = int(res.get('max_uses', 1))
                current_uses = int(res.get('current_uses', 0))
                
                if not is_used and current_uses < max_uses:
                    raw_amount = str(res.get('amount', "0")).replace('₹', '').strip()
                    amount = float(raw_amount)
                    
                    if amount > 0:
                        new_bal = user['balance'] + amount
                        new_earned = user['total_earned'] + amount
                        update_db(user_id, {"balance": new_bal, "total_earned": new_earned})
                        
                        new_uses = current_uses + 1
                        used_by[str(user_id)] = True
                        update_data = {"current_uses": new_uses, "used_by": used_by}
                        
                        if new_uses >= max_uses: update_data["isUsed"] = True
                            
                        requests.patch(f"{FIREBASE_URL}/nino_codes/{code}.json", json=update_data)
                        bot.send_message(user_id, f"✅ **Code Applied Successfully!**\nAapko ₹{amount} mil gaye.", parse_mode="Markdown", reply_markup=main_menu())
                    else:
                        bot.send_message(user_id, "⚠️ Code ka amount invalid hai.", reply_markup=main_menu())
                else: bot.send_message(user_id, "❌ Yeh Code Expired ho chuka hai ya iski Limit poori ho gayi hai!", reply_markup=main_menu())
            else: bot.send_message(user_id, "❌ Invalid Code! Kripya sahi code daalein.", reply_markup=main_menu())
        except Exception as e:
            bot.send_message(user_id, "⚠️ Server Error. Please try again later.", reply_markup=main_menu())
        user_states.pop(user_id, None)

    elif state == "waiting_for_amount":
        try:
            amount = float(message.text)
            if amount < 380:
                user_states.pop(user_id, None)
                bot.send_message(message.chat.id, "⚠️ Minimum withdrawal limit ₹380 hai.", reply_markup=main_menu())
                return
            if amount > user['balance']:
                user_states.pop(user_id, None)
                bot.send_message(message.chat.id, "⚠️ YOUR BALANCE LOW PLEASE EARN MAXIMUM WITHDRAWAL LIMIT 380", reply_markup=main_menu())
                return
            
            new_bal = user['balance'] - amount
            update_db(user_id, {"balance": new_bal})
            user_states.pop(user_id, None)
            req_id = save_withdrawal(user_id, amount, 'Pending')
            
            if req_id:
                markup = InlineKeyboardMarkup()
                markup.row(
                    InlineKeyboardButton("✅ Complete", callback_data=f"acc_{req_id}_{user_id}_{amount}"),
                    InlineKeyboardButton("❌ Reject", callback_data=f"rej_{req_id}_{user_id}_{amount}")
                )
                req_text = (
                    "🚨 **New Withdrawal Request** 🚨\n\n"
                    f"🆔 **Req ID:** #{req_id}\n"
                    f"👤 **User ID:** `{user_id}`\n"
                    f"💸 **Amount:** ₹{amount}\n"
                    f"🏦 **UPI ID:** `{user['upi']}`"
                )
                try:
                    bot.send_message(ADMIN_CHANNEL, req_text, reply_markup=markup, parse_mode="Markdown")
                    bot.send_message(message.chat.id, "✅ Aapki withdrawal request successfully submit ho chuki hai. History check karte rahein.", reply_markup=withdraw_menu_keyboard())
                except Exception as e:
                    update_db(user_id, {"balance": user['balance']})
                    requests.delete(f"{FIREBASE_URL}/withdrawals/{req_id}.json")
                    bot.send_message(message.chat.id, "⚠️ System error! Channel connect nahi ho paya. Admin ko bot fix karne ko bolein.", reply_markup=main_menu())
            else: bot.send_message(message.chat.id, "⚠️ Server Error generating request.", reply_markup=main_menu())
        except ValueError:
            user_states.pop(user_id, None)
            bot.send_message(message.chat.id, "⚠️ Kripya sahi number dalein.", reply_markup=main_menu())

@bot.callback_query_handler(func=lambda call: call.data.startswith('acc_') or call.data.startswith('rej_'))
def admin_callbacks(call):
    data = call.data.split('_')
    action = data[0]
    req_id = data[1]
    user_id = int(data[2])
    amount = float(data[3])
    
    try:
        req_status = requests.get(f"{FIREBASE_URL}/withdrawals/{req_id}/status.json").json()
        if req_status != "Pending":
            bot.answer_callback_query(call.id, "⚠️ Yeh request pehle hi process ho chuki hai!", show_alert=True)
            return
    except: return

    if action == "acc":
        update_withdrawal_status(req_id, 'Completed')
        user = get_user(user_id)
        new_withdrawn = user['total_withdrawn'] + amount
        update_db(user_id, {"total_withdrawn": new_withdrawn})
        
        bot.edit_message_text(f"{call.message.text}\n\n✅ **STATUS: COMPLETED**", call.message.chat.id, call.message.message_id)
        try: bot.send_message(user_id, f"🎉 **Withdrawal Successful!**\nAapka ₹{amount} ka withdrawal complete ho gaya hai.", parse_mode="Markdown")
        except: pass

    elif action == "rej":
        update_withdrawal_status(req_id, 'Rejected')
        user = get_user(user_id)
        new_bal = user['balance'] + amount
        update_db(user_id, {"balance": new_bal}) 
        
        bot.edit_message_text(f"{call.message.text}\n\n❌ **STATUS: REJECTED** (Amount Refunded)", call.message.chat.id, call.message.message_id)
        try: bot.send_message(user_id, f"❌ **Withdrawal Rejected!**\nAapka ₹{amount} ka withdrawal reject ho gaya hai. Pura amount wapas aa gaya hai.", parse_mode="Markdown")
        except: pass

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"VIP Earning Bot is Active!")

def run_dummy_server():
    server = HTTPServer(('0.0.0.0', 7860), DummyHandler)
    server.serve_forever()

if __name__ == "__main__":
    threading.Thread(target=run_dummy_server, daemon=True).start()
    bot.remove_webhook()
    print("VIP Earning Bot is running...")
    while True:
        try: bot.infinity_polling(skip_pending=True)
        except Exception as e: time.sleep(5)
