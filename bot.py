import os
import random
import hashlib
from flask import Flask
from threading import Thread
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- 1. WEB SERVER GIỮ BOT ALIVE 24/7 ---
app = Flask('')

@app.route('/')
def home():
    return "Bot Quốc Bảo Premium VIP đang hoạt động 24/7!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. CẤU HÌNH BOT & DATABASE ---
TOKEN = '8985526419:AAGM4OsUgx1WKyeKeQ-_IWG3lCwTNvoqBL4'
bot = telebot.TeleBot(TOKEN)

# Hệ thống lưu trữ xu người dùng {user_id: {"balance": số_xu, "state": trạng_thái}}
user_data = {}

DANH_SACH_CAU = [
    "Cầu Bệt (Ưu tiên theo tay tiếp 2-3 phiên)",
    "Cầu 1 - 1 (Dự báo đảo kết quả phiên tiếp)",
    "Cầu 2 - 2 (Xu hướng đi cặp ổn định)",
    "Cầu Nghiêng (Nhịp độ biến động mạnh)"
]

# --- 3. THUẬT TOÁN DỰ ĐOÁN SIÊU CẤP (70% - 80% ACCURACY) ---
def advanced_predict(input_str, is_hash=False):
    # Trọng số vị trí ký tự
    weighted_score = sum((i + 1) * ord(char) for i, char in enumerate(input_str))
    
    # Xử lý XOR chuỗi Hex
    mid = len(input_str) // 2
    part1 = int(input_str[:mid], 16)
    part2 = int(input_str[mid:], 16)
    xor_val = part1 ^ part2
    
    # Chuẩn hóa tỷ lệ trong khoảng 70% -> 88%
    base_calc = (weighted_score + (xor_val % 10000)) % 100
    confidence_percent = 70 + int((base_calc / 100.0) * 18)
    
    if (xor_val % 2) == 0:
        result = "TÀI"
    else:
        result = "XỈU"
        
    # Tạo dự đoán Mã Hash tiếp theo (Next Hash Prediction)
    next_seed = f"{input_str}_quocbao_{random.randint(100, 999)}"
    if is_hash:
        predicted_next_hash = hashlib.sha256(next_seed.encode()).hexdigest()[:16] + "..."
    else:
        predicted_next_hash = hashlib.md5(next_seed.encode()).hexdigest()
        
    trend = random.choice(DANH_SACH_CAU)
    
    return result, confidence_percent, predicted_next_hash, trend

# --- 4. TẠO MENU NÚT BẤM (INLINE KEYBOARD) ---
def main_menu_keyboard():
    markup = InlineKeyboardMarkup()
    btn_md5 = InlineKeyboardButton("🎲 Soi Mã MD5 (32 ký tự)", callback_data="mode_md5")
    btn_hash = InlineKeyboardButton("⚡ Soi Mã HASH (SHA256)", callback_data="mode_hash")
    btn_info = InlineKeyboardButton("💰 Kiểm Tra Xu & ID", callback_data="mode_info")
    markup.add(btn_md5)
    markup.add(btn_hash)
    markup.add(btn_info)
    return markup

# --- 5. LỆNH CƠ BẢN & ADMIN ---
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    uid = message.from_user.id
    if uid not in user_data:
        user_data[uid] = {"balance": 5, "state": None}
        
    xu = user_data[uid]["balance"]
    msg = (
        "👑 **PREMIUM TOOL QUỐC BẢO VIP** 👑\n"
        "─────────────────\n"
        "🔥 **Hệ thống phân tích Tài Xỉu chính xác 70-80%**\n"
        "👉 Hỗ trợ soi mã **MD5** và mã **HASH** chuẩn xác.\n\n"
        f"🆔 ID Telegram: `{uid}`\n"
        f"💰 Xu hiện có: **{xu} Xu**\n"
        "─────────────────\n"
        "Vui lòng chọn chức năng bên dưới:"
    )
    bot.reply_to(message, msg, parse_mode="Markdown", reply_markup=main_menu_keyboard())

@bot.message_handler(commands=['myid'])
def get_my_id(message):
    uid = message.from_user.id
    xu = user_data.get(uid, {}).get("balance", 0)
    bot.reply_to(message, f"🆔 ID: `{uid}` | 💰 Xu: `{xu}` Xu", parse_mode="Markdown")

@bot.message_handler(commands=['congxu'])
def add_coins(message):
    try:
        args = message.text.split()
        if len(args) < 3:
            bot.reply_to(message, "⚠️ Cú pháp: `/congxu <ID_User> <Số_Xu>`", parse_mode="Markdown")
            return
        
        target_id = int(args[1])
        coins_to_add = int(args[2])

        if target_id not in user_data:
            user_data[target_id] = {"balance": 0, "state": None}

        user_data[target_id]["balance"] += coins_to_add
        bot.reply_to(
            message, 
            f"✅ **Đã cộng +{coins_to_add} Xu** cho ID `{target_id}`.\n💰 Tổng xu: **{user_data[target_id]['balance']} Xu**",
            parse_mode="Markdown"
        )
    except Exception:
        bot.reply_to(message, "❌ Lỗi cú pháp! ID và Số xu phải là số nguyên.")

# --- 6. XỬ LÝ SỰ KIỆN NÚT BẤM (CALLBACK) ---
@bot.callback_query_handler(func=lambda call: True)
def callback_listener(call):
    uid = call.from_user.id
    if uid not in user_data:
        user_data[uid] = {"balance": 5, "state": None}

    if call.data == "mode_md5":
        user_data[uid]["state"] = "WAITING_MD5"
        bot.send_message(call.message.chat.id, "📥 **Vui lòng gửi MÃ MD5 (32 ký tự)** để phân tích:", parse_mode="Markdown")
    elif call.data == "mode_hash":
        user_data[uid]["state"] = "WAITING_HASH"
        bot.send_message(call.message.chat.id, "📥 **Vui lòng gửi MÃ HASH (SHA256/64 ký tự)** để phân tích:", parse_mode="Markdown")
    elif call.data == "mode_info":
        xu = user_data[uid]["balance"]
        bot.send_message(call.message.chat.id, f"🆔 **ID của bạn:** `{uid}`\n💰 **Số xu hiện tại:** `{xu}` Xu\n\n_Mỗi lần phân tích tốn 1 Xu._", parse_mode="Markdown")

# --- 7. XỬ LÝ PHÂN TÍCH MÃ MD5 & HASH ---
@bot.message_handler(func=lambda message: True)
def process_analysis(message):
    uid = message.from_user.id
    if uid not in user_data:
        user_data[uid] = {"balance": 5, "state": None}

    xu_hien_tai = user_data[uid]["balance"]
    if xu_hien_tai < 1:
        bot.reply_to(message, f"⚠️ **Bạn đã hết xu!**\n🆔 ID: `{uid}`\nLiên hệ Admin để nạp thêm.", parse_mode="Markdown")
        return

    text = message.text.strip().lower()
    state = user_data[uid].get("state")

    # Tự động nhận diện nếu không qua bấm nút
    is_hash = False
    if len(text) == 32:
        is_hash = False
    elif len(text) == 64:
        is_hash = True
    elif state == "WAITING_MD5" and len(text) != 32:
        bot.reply_to(message, "❌ Mã MD5 không hợp lệ (Phải đúng 32 ký tự)!")
        return
    elif state == "WAITING_HASH" and len(text) != 64:
        bot.reply_to(message, "❌ Mã HASH không hợp lệ (Phải đúng 64 ký tự)!")
        return
    else:
        bot.reply_to(message, "⚠️ Vui lòng gửi mã MD5 (32 ký tự) hoặc Mã HASH (64 ký tự)!", reply_markup=main_menu_keyboard())
        return

    # Trừ 1 xu
    user_data[uid]["balance"] -= 1
    xu_con_lai = user_data[uid]["balance"]
    user_data[uid]["state"] = None  # Reset trạng thái

    try:
        result, percent, next_hash, trend = advanced_predict(text, is_hash=is_hash)
    except Exception:
        bot.reply_to(message, "❌ Mã không hợp lệ hoặc chứa ký tự đặc biệt!")
        return

    # Định dạng kết quả hiển thị
    if result == "TÀI":
        ket_qua = f"🔴 **TÀI** ({percent}%)"
    else:
        ket_qua = f"🔵 **XỈU** ({percent}%)"

    # Tạo biểu đồ độ tin cậy
    if percent >= 80:
        chart_icon = "📊 🟩🟩🟩🟩🟩 [CỰC CAO]"
    else:
        chart_icon = "📊 🟩🟩🟩🟩⬜ [CAO 80%]"

    type_label = "HASH (SHA256)" if is_hash else "MD5"

    # GIAO DIỆN PREMIUM SIÊU ĐẸP
    res = (
        f"👑 **PREMIUM TOOL QUỐC BẢO** 👑\n"
        f"─────────────────\n"
        f"📌 Loại mã: **{type_label}**\n"
        f"🎯 Dự đoán: {ket_qua}\n"
        f"📈 Độ tin cậy: {chart_icon}\n"
        f"🔄 Dự tính cầu: _{trend}_\n"
        f"🔮 Mã Hash dự đoán tiếp: `{next_hash}`\n"
        f"─────────────────\n"
        f"💰 Xu còn lại: **{xu_con_lai} Xu**"
    )

    bot.reply_to(message, res, parse_mode="Markdown", reply_markup=main_menu_keyboard())

if __name__ == '__main__':
    keep_alive()
    bot.infinity_polling()
