from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime, timedelta
import asyncio

from config import OWNER_ID, MONGO_DB
from devgagan.modules.redeem_codes_db import RedeemCodesDB

# Initialize database
redeem_db = RedeemCodesDB(MONGO_DB, "restricted_bot")

@Client.on_message(filters.command("gen") & filters.user(OWNER_ID))
async def gen_command(client: Client, message: Message):
    """Handle /gen command for bot owner"""
    
    if len(message.command) != 3:
        error_msg = "❌ **Invalid format!**\n\n"
        error_msg += "**Usage:** `/gen <count> <duration>`\n\n"
        error_msg += "**Examples:**\n"
        error_msg += "• `/gen 10 7d` - 10 codes for 7 days\n"
        error_msg += "• `/gen 5 2h` - 5 codes for 2 hours\n"
        error_msg += "• `/gen 3 30m` - 3 codes for 30 minutes\n"
        error_msg += "• `/gen 1 1y` - 1 code for 1 year\n"
        error_msg += "• `/gen 15 45s` - 15 codes for 45 seconds\n\n"
        error_msg += "**Supported formats:** `d` (days), `h` (hours), `m` (minutes), `s` (seconds), `y` (years)"
        await message.reply_text(error_msg)
        return
    
    try:
        count = int(message.command[1])
        duration_str = message.command[2].lower()
        
        if count > 40:
            await message.reply_text("❌ Maximum 40 codes can be generated at once!")
            return
        
        if count < 1:
            await message.reply_text("❌ Count must be at least 1!")
            return
        
        # Parse duration with flexible format
        duration_days = redeem_db.parse_duration_to_days(duration_str)
        
        if duration_days is None:
            error_msg = "❌ **Invalid duration format!**\n\n"
            error_msg += "**Supported formats:**\n"
            error_msg += "• `7d` or `7days` - 7 days\n"
            error_msg += "• `2h` or `2hours` - 2 hours\n"
            error_msg += "• `30m` or `30minutes` - 30 minutes\n"
            error_msg += "• `45s` or `45seconds` - 45 seconds\n"
            error_msg += "• `1y` or `1year` - 1 year"
            await message.reply_text(error_msg)
            return
        
        # Generate codes
        codes = redeem_db.generate_redeem_codes(count, duration_days)
        expires_at = datetime.now() + timedelta(hours=2)
        
        # Format response
        response = f"🎟️ **{count} Premium Code(s) Generated**\n"
        response += f"⏱️ **Duration:** {redeem_db.format_duration(duration_days)}\n"
        response += f"📅 **Valid Until:** {expires_at.strftime('%d-%m-%Y %I:%M:%S %p')}\n\n"
        response += "**Redemption Codes:**\n\n"
        
        for code in codes:
            response += f"`/redeem {code}`\n"
        
        response += "\n**Note:** Users can redeem these codes using the `/redeem` command."
        
        await message.reply_text(response)
        
    except ValueError:
        await message.reply_text("❌ Invalid input! Please use correct format.")
    except Exception as e:
        await message.reply_text(f"❌ Error generating codes: {str(e)}")

@Client.on_message(filters.command("redeem"))
async def redeem_command(client: Client, message: Message):
    """Handle /redeem command for bot users"""
    
    if len(message.command) != 2:
        await message.reply_text("❌ **Usage:** `/redeem <code>`\n**Example:** `/redeem JS19MNUX`")
        return
    
    code = message.command[1].upper()
    user_id = message.from_user.id
    
    try:
        success, response_message = redeem_db.redeem_code(code, user_id)
        
        if success:
            await message.reply_text(f"🎉 **Congratulations, {message.from_user.mention}!**\n{response_message}")
        else:
            await message.reply_text(response_message)
            
    except Exception as e:
        await message.reply_text(f"❌ Error redeeming code: {str(e)}")

@Client.on_message(filters.command("codestats") & filters.user(OWNER_ID))
async def codestats_command(client: Client, message: Message):
    """Handle /codestats command for bot owner"""
    
    try:
        stats = redeem_db.get_codes_stats()
        
        response = "📊 **Redeem Codes Statistics**\n\n"
        response += f"✅ **Active Codes:** {stats['active']}\n"
        response += f"✅ **Used Codes:** {stats['used']}\n"
        response += f"⏰ **Expired Codes:** {stats['expired']}\n"
        response += f"📊 **Total Codes:** {stats['active'] + stats['used'] + stats['expired']}"
        
        await message.reply_text(response)
        
    except Exception as e:
        await message.reply_text(f"❌ Error getting stats: {str(e)}")

@Client.on_message(filters.command("cleanexpired") & filters.user(OWNER_ID))
async def cleanexpired_command(client: Client, message: Message):
    """Handle /cleanexpired command for bot owner"""
    
    try:
        deleted_count = redeem_db.clean_expired_codes()
        await message.reply_text(f"🗑️ **Cleanup Complete!**\n✅ Deleted {deleted_count} expired codes from database.")
        
    except Exception as e:
        await message.reply_text(f"❌ Error cleaning expired codes: {str(e)}")

@Client.on_message(filters.command("checkmypremium"))
async def checkmypremium_command(client: Client, message: Message):
    """Handle /checkmypremium command for users to check their premium status"""
    
    try:
        user_id = message.from_user.id
        user = redeem_db.users.find_one({"user_id": user_id})
        
        if user and user.get("is_premium") and user.get("premium_until"):
            if datetime.now() < user["premium_until"]:
                expires_at = user["premium_until"]
                time_left = expires_at - datetime.now()
                
                response = f"✅ **Premium Status: ACTIVE**\n"
                response += f"📅 **Expires On:** {expires_at.strftime('%d-%m-%Y %I:%M:%S %p')}\n"
                response += f"⏰ **Time Left:** {redeem_db.format_duration(time_left.total_seconds() / 86400)}"
                
                await message.reply_text(response)
                return
        
        await message.reply_text("❌ **Premium Status: INACTIVE**\n\nYou don't have an active premium subscription. Use `/redeem <code>` to activate premium access.")
        
    except Exception as e:
        await message.reply_text(f"❌ Error checking premium status: {str(e)}")

# Auto-cleanup expired codes every hour
async def auto_cleanup():
    """Auto cleanup expired codes every hour"""
    while True:
        try:
            await asyncio.sleep(3600)  # Wait 1 hour
            redeem_db.clean_expired_codes()
        except Exception as e:
            print(f"Auto cleanup error: {e}")

# Start auto cleanup in background
asyncio.create_task(auto_cleanup())
