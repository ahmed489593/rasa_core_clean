from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import requests
from telegram import Bot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
TELEGRAM_BOT_TOKEN = "7879652010:AAGN1rW6OiFFf0OlCuUbt-2421-gzl70-Jk"
TELEGRAM_CHAT_ID = "-1002779114601"

def send_booking_to_telegram(message: str):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
SHEETBEST_API_KEY = "i9yw%NyWBNidWfSzT8Mw0HimKX3Vm-R%i1jvpcg8eOrnbT2Qrv%sw$QdL93oPUQC"
SHEETBEST_BASE_URL = f"https://sheet.best/api/sheets/{SHEETBEST_API_KEY}"
class ActionGreet(Action):
    def name(self) -> Text:
        return "action_greet"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        user_message = tracker.latest_message.get('text', '').lower()
        
        if "السلام عليكم" in user_message:
            dispatcher.utter_message(text="وعليكم السلام ورحمة الله، تفضل كيف نقدر نعاونك؟ 🤝")
        elif "صباح الخير" in user_message:
            dispatcher.utter_message(text="صباح النور 🌞، مرحبتين بيك!")
        elif "مساء الخير" in user_message:
            dispatcher.utter_message(text="مساء النور 🌙، كيف نعاونك؟")
        else:
            dispatcher.utter_message(text="مرحبتين بيك 👋 كيف نقدر نساعدك اليوم؟")
        
        return []

from rasa_sdk.events import SlotSet

class ActionAnalyzeImage(Action):
    def name(self) -> Text:
        return "action_analyze_image"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        image_url = tracker.latest_message.get("image")  # لو جت صورة عادية
        if not image_url:
            image_url = tracker.latest_message.get("text")  # fallback لو رابط نصي
        
        if not image_url:
            dispatcher.utter_message(text="ما وصلنيش صورة، حاول تبعتها من جديد 🙏")
            return []

        # جلب المنتجات من SheetBest
        products_url = f"{SHEETBEST_BASE_URL}/tabs/products"
        res = requests.get(products_url)
        products = res.json() if res.status_code == 200 else []

        matched_product = None
        for product in products:
            if product.get("image_url") and product.get("image_url") in image_url:
                matched_product = product
                break
        
        if matched_product:
            # هنا نخزن كود المنتج كـ slot رسمي
            dispatcher.utter_message(
                text=(
                    f"✅ المنتج: {matched_product.get('name')}\n"
                    f"💵 السعر: {matched_product.get('price')} دينار\n"
                    f"📏 المقاسات المتوفرة: {matched_product.get('available_sizes')}\n"
                    f"❌ المقاسات الغير متوفرة: {matched_product.get('unavailable_sizes')}"
                )
            )
            return [SlotSet("product_code", matched_product.get("product_code"))]
        else:
            dispatcher.utter_message(text="ما قدرتش نعرف المنتج من الصورة، جرب تبعتها بشكل أوضح 🙏")
            return []

class ActionCollectBooking(Action):
    def name(self) -> str:
        return "action_collect_booking"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: dict) -> list:

        events = []

        user_message = tracker.latest_message.get('text', '').lower()

        # لو فيه رقم تليفون
        if not tracker.get_slot("phone_number"):
            phone_match = re.findall(r'\b(09\d{8}|2189\d{8})\b', user_message)
            if phone_match:
                phone = phone_match[0]
                events.append(SlotSet("phone_number", phone))
                dispatcher.utter_message(text=f"تمام، خديت رقمك: {phone}")

        # لو فيه مدينة
        if not tracker.get_slot("city"):
            known_cities = ["طرابلس", "بنغازي", "مصراتة", "سبها", "زليتن", "الزاوية"]
            for city in known_cities:
                if city in user_message:
                    events.append(SlotSet("city", city))
                    dispatcher.utter_message(text=f"تمام، سجلت مدينتك: {city}")
                    break

        # لو فيه منطقة
        if not tracker.get_slot("area"):
            known_areas = ["طريق المطار", "الظهرة", "سوق الجمعة", "المدينة", "قاريونس", "البركة"]
            for area in known_areas:
                if area in user_message:
                    events.append(SlotSet("area", area))
                    dispatcher.utter_message(text=f"تمام، سجلت منطقتك: {area}")
                    break

        # لو فيه مقاس
        if not tracker.get_slot("size"):
            size_match = re.findall(r'\b(3[6-9]|4[0-6]|s|m|l|xl)\b', user_message)
            if size_match:
                size = size_match[0]
                events.append(SlotSet("size", size))
                dispatcher.utter_message(text=f"تمام، سجلت مقاسك: {size}")

        # نراجع السلوط
        product_code = tracker.get_slot("product_code")
        size = tracker.get_slot("size")
        city = tracker.get_slot("city")
        area = tracker.get_slot("area") or "غير محددة"
        phone = tracker.get_slot("phone_number")

        if product_code and size and city and phone:
            message = (
                f"🚀 *طلب حجز جديد*\n\n"
                f"📦 المنتج: {product_code}\n"
                f"📏 المقاس: {size}\n"
                f"🏙️ المدينة: {city}\n"
                f"📍 المنطقة: {area}\n"
                f"📞 الهاتف: {phone}"
            )
            try:
                send_booking_to_telegram(message)
                dispatcher.utter_message(text="👌 تم تسجيل طلبك وبعثناه للموظفين، بيكلموك قريب 🌟")
                # نفرغ السلوط باش لو فيه طلب جديد
                events += [
                    SlotSet("product_code", None),
                    SlotSet("size", None),
                    SlotSet("city", None),
                    SlotSet("area", None),
                    SlotSet("phone_number", None),
                ]
            except Exception as e:
                dispatcher.utter_message(text=f"صار خطأ في الإرسال للتليجرام: {e}")
        
        return events
