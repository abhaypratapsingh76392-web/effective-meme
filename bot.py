import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import requests
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)[span_2](start_span)[span_2](end_span)

# --- HUGGING FACE BYPASS ---
def custom_sender(method, url, **kwargs):
    url = url.replace("api.telegram.org", "149.154.167.220")[span_3](start_span)[span_3](end_span)
    kwargs['verify'] = False[span_4](start_span)[span_4](end_span)
    headers = kwargs.get('headers', {})[span_5](start_span)[span_5](end_span)
    headers['Host'] = 'api.telegram.org[span_6](start_span)'[span_6](end_span)
    kwargs['headers'] = headers[span_7](start_span)[span_7](end_span)
    return requests.request(method, url, **kwargs)[span_8](start_span)[span_8](end_span)

telebot.apihelper.CUSTOM_REQUEST_SENDER = custom_sender[span_9](start_span)[span_9](end_span)
# ---------------------------

# Bot Token (You can change this later)
TOKEN = "8378116514:AAHbpgQ3GE1mic5CevK7ovLA-VI4lmAKZmw[span_10](start_span)"[span_10](end_span)
bot = telebot.TeleBot(TOKEN)[span_11](start_span)[span_11](end_span)

ADMIN_CHANNEL = "@fjfjdjdu" # Tera admin channel[span_12](start_span)[span_12](end_span)
# UPDATED FIREBASE URL HERE 👇
FIREBASE_URL = "https://movie-ee8bb-default-rtdb.firebaseio.com"

# Temporary memory for states
user_states = {}[span_13](start_span)[span_13](end_span)

# --- FIREBASE DATABASE FUNCTIONS ---
def get_user(user_id):
    try:
        url = f"{FIREBASE_URL}/users/{user_id}.json[span_14](start_span)"[span_14](end_span)
        response = requests.get(url)[span_15](start_span)[span_15](end_span)
        data = response.json()[span_16](start_span)[span_16](end_span)
        
        if not data:
            return None # Return None for new users so we can catch referrals[span_17](start_span)[span_17](end_span)
        return data[span_18](start_span)[span_18](end_span)
    except Exception as e:
        print("Firebase Error Get:", e)[span_19](start_span)[span_19](end_span)
        return None[span_20](start_span)[span_20](end_span)

def create_user(user_id):
    new_user = {
        "balance": 0.0,[span_21](start_span)[span_21](end_span)
        "upi": "Not Set",[span_22](start_span)[span_22](end_span)
        "last_bonus": 0,[span_23](start_span)[span_23](end_span)
        "total_earned": 0.0,[span_24](start_span)[span_24](end_span)
        "total_withdrawn": 0.0[span_25](start_span)[span_25](end_span)
    }
    requests.put(f"{FIREBASE_URL}/users/{user_id}.json", json=new_user)[span_26](start_span)[span_26](end_span)
    return new_user[span_27](start_span)[span_27](end_span)

def update_db(user_id, data):
    try:
        url = f"{FIREBASE_URL}/users/{user_id}.json[span_28](start_span)"[span_28](end_span)
        requests.patch(url, json=data)[span_29](start_span)[span_29](end_span)
    except Exception as e:
        print("Firebase Error Update:", e)[span_30](start_span)[span_30](end_span)

# Save withdrawal history in Firebase
def save_withdrawal(user_id, amount, status):
    try:
        req_id = int(time.time() * 1000) # Unique ID generate karne ke liye[span_31](start_span)[span_31](end_span)
        url = f"{FIREBASE_URL}/withdrawals/{req_id}.json[span_32](start_span)"[span_32](end_span)
        data = {
            "user_id": user_id,[span_33](start_span)[span_33](end_span)
            "amount": amount,[span_34](start_span)[span_34](end_span)
            "status": status,[span_35](start_span)[span_35](end_span)
            "timestamp": time.time()[span_36](start_span)[span_36](end_span)
        }
        requests.put(url, json=data)[span_37](start_span)[span_37](end_span)
        return req_id[span_38](start_span)[span_38](end_span)
    except:
        return None[span_39](start_span)[span_39](end_span)

def update_withdrawal_status(req_id, status):
    try:
        requests.patch(f"{FIREBASE_URL}/withdrawals/{req_id}.json", json={"status": status})[span_40](start_span)[span_40](end_span)
    except:
        pass[span_41](start_span)[span_41](end_span)

# --- REAL CHANNEL JOIN CHECKER ---
def check_join(user_id):
    try:
        chat_member = bot.get_chat_member("@earnbox1", user_id)[span_42](start_span)[span_42](end_span)
        if chat_member.status in ['member', 'administrator', 'creator', 'restricted']:[span_43](start_span)[span_43](end_span)
            return True[span_44](start_span)[span_44](end_span)
        else:
            return False[span_45](start_span)[span_45](end_span)
    except Exception as e:
        print("Join Check Error:", e)[span_46](start_span)[span_46](end_span)
        return False[span_47](start_span)[span_47](end_span)

# --- KEYBOARDS ---
def force_sub_markup():
    markup = InlineKeyboardMarkup()[span_48](start_span)[span_48](end_span)
    markup.add(InlineKeyboardButton("📢 Join Channel", url="https://t.me/earnbox1"))[span_49](start_span)[span_49](end_span)
    markup.add(InlineKeyboardButton("✅ Verify", callback_data="verify_join"))[span_50](start_span)[span_50](end_span)
    return markup[span_51](start_span)[span_51](end_span)

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)[span_52](start_span)[span_52](end_span)
    markup.row(KeyboardButton("🎁 Daily Bonus"), KeyboardButton("🎟️ Redeem Code"))[span_53](start_span)[span_53](end_span)
    markup.row(KeyboardButton("💰 My Balance"), KeyboardButton("🔗 Bonus Refer Link"))[span_54](start_span)[span_54](end_span)
    markup.row(KeyboardButton("📊 Status"), KeyboardButton("💳 Withdraw"))[span_55](start_span)[span_55](end_span)
    return markup[span_56](start_span)[span_56](end_span)

def back_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)[span_57](start_span)[span_57](end_span)
    markup.add(KeyboardButton("🔙 Back to Main Menu"))[span_58](start_span)[span_58](end_span)
    return markup[span_59](start_span)[span_59](end_span)

def withdraw_menu_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)[span_60](start_span)[span_60](end_span)
    markup.row(KeyboardButton("🏦 Set / Change UPI ID"), KeyboardButton("💸 Request Withdrawal"))[span_61](start_span)[span_61](end_span)
    markup.row(KeyboardButton("📋 My Withdrawal History"))[span_62](start_span)[span_62](end_span)
    markup.add(KeyboardButton("🔙 Back to Main Menu"))[span_63](start_span)[span_63](end_span)
    return markup[span_64](start_span)[span_64](end_span)

# --- BOT HANDLERS ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id[span_65](start_span)[span_65](end_span)
    args = message.text.split()[span_66](start_span)[span_66](end_span)
    
    # Check if user is New
    user_data = get_user(user_id)[span_67](start_span)[span_67](end_span)
    is_new = user_data is None[span_68](start_span)[span_68](end_span)
    
    if is_new:
        create_user(user_id) # Register in Firebase[span_69](start_span)[span_69](end_span)
        # --- REFERRAL SYSTEM LOGIC ---
        if len(args) > 1:
            try:
                referrer_id = int(args[1])[span_70](start_span)[span_70](end_span)
                if referrer_id != user_id:
                    ref_data = get_user(referrer_id)[span_71](start_span)[span_71](end_span)
                    if ref_data:
                        # Give ₹3 to Referrer
                        new_bal = ref_data['balance'] + 3.0[span_72](start_span)[span_72](end_span)
                        new_earned = ref_data['total_earned'] + 3.0[span_73](start_span)[span_73](end_span)
                        update_db(referrer_id, {"balance": new_bal, "total_earned": new_earned})[span_74](start_span)[span_74](end_span)
                        
                        try:
                            bot.send_message(referrer_id, f"🎉 **Congratulations!**\nKisine aapke refer link se bot start kiya hai. Aapko **₹3** mil gaye!", parse_mode="Markdown")[span_75](start_span)[span_75](end_span)
                        except: pass
            except: pass[span_76](start_span)[span_76](end_span)
    
    if not check_join(user_id):
        bot.send_message(user_id, "BOT DAILY CODE CHANNEL JOIN ENJOY 😉", reply_markup=force_sub_markup())[span_77](start_span)[span_77](end_span)
        return[span_78](start_span)[span_78](end_span)
        
    text = (
        "🌟 **Best Earning Bot For Withdrawal UPI ID** 🌟\n\n[span_79](start_span)"[span_79](end_span)
        "Welcome to the most VIP earning bot! Yahan aap daily bonus, codes redeem kar, aur dosto ko refer karke real cash earn kar sakte ho.\n\n[span_80](start_span)"[span_80](end_span)
        "👇 Niche diye gaye options ka use karein aur earning shuru karein[span_81](start_span)!"[span_81](end_span)
    )
    bot.send_message(message.chat.id, text, reply_markup=main_menu(), parse_mode="Markdown")[span_82](start_span)[span_82](end_span)

@bot.callback_query_handler(func=lambda call: call.data == "verify_join")
def verify_callback(call):
    if check_join(call.from_user.id):
        bot.edit_message_text("✅ **Verification Successful!**", call.message.chat.id, call.message.message_id)[span_83](start_span)[span_83](end_span)
        bot.send_message(call.from_user.id, "Choose an option 👇", reply_markup=main_menu())[span_84](start_span)[span_84](end_span)
    else:
        bot.answer_callback_query(call.id, "❌ Aapne abhi tak channel join nahi kiya hai! Pehle join karein.", show_alert=True)[span_85](start_span)[span_85](end_span)

@bot.message_handler(func=lambda message: message.text == "🔙 Back to Main Menu")
def back_handler(message):
    user_states.pop(message.from_user.id, None)[span_86](start_span)[span_86](end_span)
    bot.send_message(message.chat.id, "🏡 Main menu mein wapas aa gaye:", reply_markup=main_menu())[span_87](start_span)[span_87](end_span)

@bot.message_handler(func=lambda message: message.text == "🎁 Daily Bonus")
def daily_bonus(message):
    user_id = message.from_user.id[span_88](start_span)[span_88](end_span)
    if not check_join(user_id): return[span_89](start_span)[span_89](end_span)
    
    user = get_user(user_id)[span_90](start_span)[span_90](end_span)
    current_time = int(time.time())[span_91](start_span)[span_91](end_span)
    
    if current_time - user['last_bonus'] >= 86400:
        new_bal = user['balance'] + 2.0[span_92](start_span)[span_92](end_span)
        new_earned = user['total_earned'] + 2.0[span_93](start_span)[span_93](end_span)
        update_db(user_id, {"balance": new_bal, "last_bonus": current_time, "total_earned": new_earned})[span_94](start_span)[span_94](end_span)
        bot.send_message(user_id, "🎁 **Daily Bonus Claimed!**\nAapke account mein **₹2** add ho gaye hain.", parse_mode="Markdown")[span_95](start_span)[span_95](end_span)
    else:
        left_time = 86400 - (current_time - user['last_bonus'])[span_96](start_span)[span_96](end_span)
        hours = left_time // 3600[span_97](start_span)[span_97](end_span)
        mins = (left_time % 3600) // 60[span_98](start_span)[span_98](end_span)
        bot.send_message(user_id, f"⏳ Aapne aaj ka bonus le liya hai. Next bonus **{hours} hours aur {mins} minutes** baad milega.", parse_mode="Markdown")[span_99](start_span)[span_99](end_span)

@bot.message_handler(func=lambda message: message.text == "🎟️ Redeem Code")
def redeem_code_start(message):
    user_id = message.from_user.id[span_100](start_span)[span_100](end_span)
    if not check_join(user_id): return[span_101](start_span)[span_101](end_span)
    
    user_states[user_id] = "waiting_for_redeem_code[span_102](start_span)"[span_102](end_span)
    text = (
        "THE CODE generate\n[span_103](start_span)"[span_103](end_span)
        "WEBSITE https://generate.10001mb.com/\n[span_104](start_span)"[span_104](end_span)
        "generate CODE AND ENTER OK\n\n[span_105](start_span)"[span_105](end_span)
        "ENTER YOUR CODE:[span_106](start_span)"[span_106](end_span)
    )
    bot.send_message(user_id, text, reply_markup=back_menu(), disable_web_page_preview=True)[span_107](start_span)[span_107](end_span)

@bot.message_handler(func=lambda message: message.text == "🔗 Bonus Refer Link")
def refer_link(message):
    if not check_join(message.from_user.id): return[span_108](start_span)[span_108](end_span)
    bot_info = bot.get_me()[span_109](start_span)[span_109](end_span)
    ref_link = f"https://t.me/{bot_info.username}?start={message.from_user.id}[span_110](start_span)"[span_110](end_span)
    text = (
        "🔗 **Aapka VIP Refer Link** 🔗\n\n[span_111](start_span)"[span_111](end_span)
        f"`{ref_link}`\n\n[span_112](start_span)"[span_112](end_span)
        "Apne dosto ko invite karein aur per refer **₹3** kamayein! Jaise hi wo aapke link se bot start karenge, paise turant mil jayenge.[span_113](start_span)"[span_113](end_span)
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")[span_114](start_span)[span_114](end_span)

@bot.message_handler(func=lambda message: message.text == "💰 My Balance")
def my_balance(message):
    if not check_join(message.from_user.id): return[span_115](start_span)[span_115](end_span)
    user = get_user(message.from_user.id)[span_116](start_span)[span_116](end_span)
    bot.send_message(message.chat.id, f"💵 **Aapka Real Balance:** ₹{user['balance']:.2f}", parse_mode="Markdown")[span_117](start_span)[span_117](end_span)

@bot.message_handler(func=lambda message: message.text == "📊 Status")
def status_menu(message):
    if not check_join(message.from_user.id): return[span_118](start_span)[span_118](end_span)
    user = get_user(message.from_user.id)[span_119](start_span)[span_119](end_span)
    text = (
        "📊 **Aapka Earning Status** 📊\n\n[span_120](start_span)"[span_120](end_span)
        f"💵 **Total Earned:** ₹{user['total_earned']:.2f}\n[span_121](start_span)"[span_121](end_span)
        f"💸 **Total Withdrawn:** ₹{user['total_withdrawn']:.2f}\n[span_122](start_span)"[span_122](end_span)
        f"💳 **Current Balance:** ₹{user['balance']:.2f}\n[span_123](start_span)"[span_123](end_span)
        f"🏦 **UPI ID:** `{user['upi']}`[span_124](start_span)"[span_124](end_span)
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")[span_125](start_span)[span_125](end_span)

@bot.message_handler(func=lambda message: message.text == "💳 Withdraw")
def withdraw_menu(message):
    user_id = message.from_user.id[span_126](start_span)[span_126](end_span)
    if not check_join(user_id): return[span_127](start_span)[span_127](end_span)
    user = get_user(user_id)[span_128](start_span)[span_128](end_span)
    bot.send_message(user_id, f"💳 **Withdrawal Section**\n\n**Aapki Current UPI:** `{user['upi']}`\n**Current Balance:** ₹{user['balance']:.2f}", reply_markup=withdraw_menu_keyboard(), parse_mode="Markdown")[span_129](start_span)[span_129](end_span)

@bot.message_handler(func=lambda message: message.text == "🏦 Set / Change UPI ID")
def set_upi(message):
    user_states[message.from_user.id] = "waiting_for_upi[span_130](start_span)"[span_130](end_span)
    bot.send_message(message.chat.id, "🏦 Kripya apni nayi **UPI ID** send karein:", reply_markup=back_menu(), parse_mode="Markdown")[span_131](start_span)[span_131](end_span)

@bot.message_handler(func=lambda message: message.text == "💸 Request Withdrawal")
def req_withdraw(message):
    user_id = message.from_user.id[span_132](start_span)[span_132](end_span)
    user = get_user(user_id)[span_133](start_span)[span_133](end_span)
    if user['upi'] == 'Not Set':
        bot.send_message(message.chat.id, "⚠️ Pehle apni UPI ID set karein!")[span_134](start_span)[span_134](end_span)
        return[span_135](start_span)[span_135](end_span)
    if user['balance'] < 380:
        bot.send_message(message.chat.id, "⚠️ YOUR BALANCE LOW PLEASE EARN MAXIMUM WITHDRAWAL LIMIT 380", reply_markup=main_menu())[span_136](start_span)[span_136](end_span)
        return[span_137](start_span)[span_137](end_span)
        
    user_states[user_id] = "waiting_for_amount[span_138](start_span)"[span_138](end_span)
    bot.send_message(message.chat.id, f"💸 **Withdrawal Limit:** Minimum ₹380\n\nAap kitna amount nikalna chahte hain? (Current Balance: ₹{user['balance']:.2f})", reply_markup=back_menu(), parse_mode="Markdown")[span_139](start_span)[span_139](end_span)

@bot.message_handler(func=lambda message: message.text == "📋 My Withdrawal History")
def withdrawal_history(message):
    user_id = message.from_user.id[span_140](start_span)[span_140](end_span)
    try:
        res = requests.get(f"{FIREBASE_URL}/withdrawals.json").json()[span_141](start_span)[span_141](end_span)
        if not res:
            bot.send_message(message.chat.id, "📭 Aapne abhi tak koi withdrawal request nahi lagayi hai.")[span_142](start_span)[span_142](end_span)
            return[span_143](start_span)[span_143](end_span)
            
        history = [][span_144](start_span)[span_144](end_span)
        for req_id, data in res.items():
            if data['user_id'] == user_id:
                history.append(data)[span_145](start_span)[span_145](end_span)
                
        if not history:
            bot.send_message(message.chat.id, "📭 Aapne abhi tak koi withdrawal request nahi lagayi hai.")[span_146](start_span)[span_146](end_span)
            return[span_147](start_span)[span_147](end_span)
            
        text = "📋 **Aapki Withdrawal History:**\n\n[span_148](start_span)"[span_148](end_span)
        for row in reversed(history[-10:]): # Last 10 records[span_149](start_span)[span_149](end_span)
            status = row['status'][span_150](start_span)[span_150](end_span)
            icon = "⏳" if status == "Pending" else "✅" if status == "Completed" else "❌[span_151](start_span)"[span_151](end_span)
            text += f"{icon} **Amount:** ₹{row['amount']} | **Status:** {status}\n[span_152](start_span)"[span_152](end_span)
            
        bot.send_message(message.chat.id, text, parse_mode="Markdown")[span_153](start_span)[span_153](end_span)
    except:
        bot.send_message(message.chat.id, "⚠️ Server Error fetching history.")[span_154](start_span)[span_154](end_span)

# --- MESSAGE HANDLER W/ STATES ---
@bot.message_handler(func=lambda message: message.from_user.id in user_states)
def handle_states(message):
    user_id = message.from_user.id[span_155](start_span)[span_155](end_span)
    state = user_states[user_id][span_156](start_span)[span_156](end_span)
    user = get_user(user_id)[span_157](start_span)[span_157](end_span)
    
    if state == "waiting_for_upi":
        new_upi = message.text[span_158](start_span)[span_158](end_span)
        update_db(user_id, {"upi": new_upi})[span_159](start_span)[span_159](end_span)
        user_states.pop(user_id, None)[span_160](start_span)[span_160](end_span)
        bot.send_message(message.chat.id, f"✅ Aapki UPI ID successully set ho gayi hai:\n`{new_upi}`", reply_markup=withdraw_menu_keyboard(), parse_mode="Markdown")[span_161](start_span)[span_161](end_span)
        
    elif state == "waiting_for_redeem_code":
        code = message.text.strip()[span_162](start_span)[span_162](end_span)
        
        try:
            res = requests.get(f"{FIREBASE_URL}/nino_codes/{code}.json").json()[span_163](start_span)[span_163](end_span)
            
            if res and isinstance(res, dict):
                
                # Check karo ki User ne ye code already use toh nahi kar liya
                used_by = res.get('used_by', {})[span_164](start_span)[span_164](end_span)
                if str(user_id) in used_by:
                    bot.send_message(message.chat.id, "❌ Aapne yeh code pehle hi use kar liya hai (Already Used)!", reply_markup=main_menu())[span_165](start_span)[span_165](end_span)
                    user_states.pop(user_id, None)[span_166](start_span)[span_166](end_span)
                    return[span_167](start_span)[span_167](end_span)
                
                is_used = res.get('isUsed', False)[span_168](start_span)[span_168](end_span)
                max_uses = int(res.get('max_uses', 1))[span_169](start_span)[span_169](end_span)
                current_uses = int(res.get('current_uses', 0))[span_170](start_span)[span_170](end_span)
                
                if not is_used and current_uses < max_uses:
                    
                    raw_amount = str(res.get('amount', "0")).replace('₹', '').strip()[span_171](start_span)[span_171](end_span)
                    amount = float(raw_amount)[span_172](start_span)[span_172](end_span)
                    
                    if amount > 0:
                        new_bal = user['balance'] + amount[span_173](start_span)[span_173](end_span)
                        new_earned = user['total_earned'] + amount[span_174](start_span)[span_174](end_span)
                        update_db(user_id, {"balance": new_bal, "total_earned": new_earned})[span_175](start_span)[span_175](end_span)
                        
                        new_uses = current_uses + 1[span_176](start_span)[span_176](end_span)
                        used_by[str(user_id)] = True[span_177](start_span)[span_177](end_span)
                        update_data = {"current_uses": new_uses, "used_by": used_by}[span_178](start_span)[span_178](end_span)
                        
                        if new_uses >= max_uses:
                            update_data["isUsed"] = True[span_179](start_span)[span_179](end_span)
                            
                        requests.patch(f"{FIREBASE_URL}/nino_codes/{code}.json", json=update_data)[span_180](start_span)[span_180](end_span)
                        
                        bot.send_message(user_id, f"✅ **Code Applied Successfully!**\nAapko ₹{amount} mil gaye.", parse_mode="Markdown", reply_markup=main_menu())[span_181](start_span)[span_181](end_span)
                    else:
                        bot.send_message(user_id, "⚠️ Code ka amount invalid hai.", reply_markup=main_menu())[span_182](start_span)[span_182](end_span)
                else:
                    bot.send_message(user_id, "❌ Yeh Code Expired ho chuka hai ya iski Limit poori ho gayi hai!", reply_markup=main_menu())[span_183](start_span)[span_183](end_span)
            else:
                bot.send_message(user_id, "❌ Invalid Code! Kripya sahi code daalein.", reply_markup=main_menu())[span_184](start_span)[span_184](end_span)
                
        except Exception as e:
            print("Redeem Error:", e)[span_185](start_span)[span_185](end_span)
            bot.send_message(user_id, "⚠️ Server Error. Please try again later.", reply_markup=main_menu())[span_186](start_span)[span_186](end_span)
            
        user_states.pop(user_id, None)[span_187](start_span)[span_187](end_span)

    elif state == "waiting_for_amount":
        try:
            amount = float(message.text)[span_188](start_span)[span_188](end_span)
            if amount < 380:
                user_states.pop(user_id, None)[span_189](start_span)[span_189](end_span)
                bot.send_message(message.chat.id, "⚠️ Minimum withdrawal limit ₹380 hai.", reply_markup=main_menu())[span_190](start_span)[span_190](end_span)
                return[span_191](start_span)[span_191](end_span)
            if amount > user['balance']:
                user_states.pop(user_id, None)[span_192](start_span)[span_192](end_span)
                bot.send_message(message.chat.id, "⚠️ YOUR BALANCE LOW PLEASE EARN MAXIMUM WITHDRAWAL LIMIT 380", reply_markup=main_menu())[span_193](start_span)[span_193](end_span)
                return[span_194](start_span)[span_194](end_span)
            
            new_bal = user['balance'] - amount[span_195](start_span)[span_195](end_span)
            update_db(user_id, {"balance": new_bal})[span_196](start_span)[span_196](end_span)
            user_states.pop(user_id, None)[span_197](start_span)[span_197](end_span)
            
            req_id = save_withdrawal(user_id, amount, 'Pending')[span_198](start_span)[span_198](end_span)
            
            if req_id:
                markup = InlineKeyboardMarkup()[span_199](start_span)[span_199](end_span)
                markup.row(
                    InlineKeyboardButton("✅ Complete", callback_data=f"acc_{req_id}_{user_id}_{amount}"),[span_200](start_span)[span_200](end_span)
                    InlineKeyboardButton("❌ Reject", callback_data=f"rej_{req_id}_{user_id}_{amount}")[span_201](start_span)[span_201](end_span)
                )
                
                req_text = (
                    "🚨 **New Withdrawal Request** 🚨\n\n[span_202](start_span)"[span_202](end_span)
                    f"🆔 **Req ID:** #{req_id}\n[span_203](start_span)"[span_203](end_span)
                    f"👤 **User ID:** `{user_id}`\n[span_204](start_span)"[span_204](end_span)
                    f"💸 **Amount:** ₹{amount}\n[span_205](start_span)"[span_205](end_span)
                    f"🏦 **UPI ID:** `{user['upi']}`[span_206](start_span)"[span_206](end_span)
                )
                
                try:
                    bot.send_message(ADMIN_CHANNEL, req_text, reply_markup=markup, parse_mode="Markdown")[span_207](start_span)[span_207](end_span)
                    bot.send_message(message.chat.id, "✅ Aapki withdrawal request successfully submit ho chuki hai. History check karte rahein.", reply_markup=withdraw_menu_keyboard())[span_208](start_span)[span_208](end_span)
                except Exception as e:
                    update_db(user_id, {"balance": user['balance']})[span_209](start_span)[span_209](end_span)
                    requests.delete(f"{FIREBASE_URL}/withdrawals/{req_id}.json")[span_210](start_span)[span_210](end_span)
                    bot.send_message(message.chat.id, "⚠️ System error! Channel connect nahi ho paya. Admin ko bot fix karne ko bolein.", reply_markup=main_menu())[span_211](start_span)[span_211](end_span)
            else:
                bot.send_message(message.chat.id, "⚠️ Server Error generating request.", reply_markup=main_menu())[span_212](start_span)[span_212](end_span)
                
        except ValueError:
            user_states.pop(user_id, None)[span_213](start_span)[span_213](end_span)
            bot.send_message(message.chat.id, "⚠️ Kripya sahi number dalein.", reply_markup=main_menu())[span_214](start_span)[span_214](end_span)

# --- ADMIN CHANNEL CALLBACKS ---
@bot.callback_query_handler(func=lambda call: call.data.startswith('acc_') or call.data.startswith('rej_'))
def admin_callbacks(call):
    data = call.data.split('_')[span_215](start_span)[span_215](end_span)
    action = data[0][span_216](start_span)[span_216](end_span)
    req_id = data[1][span_217](start_span)[span_217](end_span)
    user_id = int(data[2])[span_218](start_span)[span_218](end_span)
    amount = float(data[3])[span_219](start_span)[span_219](end_span)
    
    try:
        req_status = requests.get(f"{FIREBASE_URL}/withdrawals/{req_id}/status.json").json()[span_220](start_span)[span_220](end_span)
        if req_status != "Pending":
            bot.answer_callback_query(call.id, "⚠️ Yeh request pehle hi process ho chuki hai!", show_alert=True)[span_221](start_span)[span_221](end_span)
            return[span_222](start_span)[span_222](end_span)
    except:
        return[span_223](start_span)[span_223](end_span)

    if action == "acc":
        update_withdrawal_status(req_id, 'Completed')[span_224](start_span)[span_224](end_span)
        user = get_user(user_id)[span_225](start_span)[span_225](end_span)
        new_withdrawn = user['total_withdrawn'] + amount[span_226](start_span)[span_226](end_span)
        update_db(user_id, {"total_withdrawn": new_withdrawn})[span_227](start_span)[span_227](end_span)
        
        bot.edit_message_text(f"{call.message.text}\n\n✅ **STATUS: COMPLETED**", call.message.chat.id, call.message.message_id)[span_228](start_span)[span_228](end_span)
        try:
            bot.send_message(user_id, f"🎉 **Withdrawal Successful!**\nAapka ₹{amount} ka withdrawal complete ho gaya hai (Req ID: #{req_id}).", parse_mode="Markdown")[span_229](start_span)[span_229](end_span)
        except:
            pass[span_230](start_span)[span_230](end_span)

    elif action == "rej":
        update_withdrawal_status(req_id, 'Rejected')[span_231](start_span)[span_231](end_span)
        user = get_user(user_id)[span_232](start_span)[span_232](end_span)
        new_bal = user['balance'] + amount[span_233](start_span)[span_233](end_span)
        update_db(user_id, {"balance": new_bal}) # Refund[span_234](start_span)[span_234](end_span)
        
        bot.edit_message_text(f"{call.message.text}\n\n❌ **STATUS: REJECTED** (Amount Refunded)", call.message.chat.id, call.message.message_id)[span_235](start_span)[span_235](end_span)
        try:
            bot.send_message(user_id, f"❌ **Withdrawal Rejected!**\nAapka ₹{amount} ka withdrawal reject ho gaya hai. Pura amount aapke bot balance mein wapas aa gaya hai.", parse_mode="Markdown")[span_236](start_span)[span_236](end_span)
        except:
            pass[span_237](start_span)[span_237](end_span)

# --- DUMMY SERVER FOR HUGGING FACE ---
class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)[span_238](start_span)[span_238](end_span)
        self.end_headers()[span_239](start_span)[span_239](end_span)
        self.wfile.write(b"VIP Earning Bot is Active!")[span_240](start_span)[span_240](end_span)

def run_dummy_server():
    server = HTTPServer(('0.0.0.0', 7860), DummyHandler)[span_241](start_span)[span_241](end_span)
    server.serve_forever()[span_242](start_span)[span_242](end_span)

if __name__ == "__main__":
    threading.Thread(target=run_dummy_server, daemon=True).start()[span_243](start_span)[span_243](end_span)
    bot.remove_webhook()[span_244](start_span)[span_244](end_span)
    print("VIP Earning Bot is running with Firebase Database Sync & Used Checks...")[span_245](start_span)[span_245](end_span)
    while True:
        try:
            bot.infinity_polling(skip_pending=True)[span_246](start_span)[span_246](end_span)
        except Exception as e:
            time.sleep(5)[span_247](start_span)[span_247](end_span)
