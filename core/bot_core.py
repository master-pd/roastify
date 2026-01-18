"""
Advanced Bot Core with Multi-feature Support
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict

from telegram import (
    Update, 
    Bot, 
    Message, 
    Chat, 
    User,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    Application,
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ChatMemberHandler,
    filters,
    PicklePersistence
)
from telegram.constants import ParseMode, ChatType

from config import ProductionConfig
from core.session_manager import SessionManager
from core.cache_manager import CacheManager
from core.rate_limiter import RateLimiter
from modules.roast_module.generator import RoastGenerator
from modules.image_module.render_3d import ImageRenderer
from modules.group_module.manager import GroupManager
from modules.live_module.stream_manager import StreamManager
from modules.database_module.crud import DatabaseCRUD
from handlers.message_handler import MessageProcessor
from handlers.group_handler import GroupEventHandler
from utils.logger import BotLogger
from utils.error_handler import GlobalErrorHandler

class RoastifyBot:
    """Main bot class with all features"""
    
    def __init__(self, token: str):
        self.token = token
        self.config = ProductionConfig()
        self.logger = BotLogger.get_logger(__name__)
        
        # Initialize managers
        self.session_manager = SessionManager()
        self.cache_manager = CacheManager()
        self.rate_limiter = RateLimiter()
        self.db = DatabaseCRUD()
        
        # Initialize modules
        self.roast_generator = RoastGenerator()
        self.image_renderer = ImageRenderer()
        self.group_manager = GroupManager()
        self.stream_manager = StreamManager()
        
        # Initialize handlers
        self.message_processor = MessageProcessor(self)
        self.group_handler = GroupEventHandler(self)
        
        # Statistics
        self.stats = {
            'messages_processed': 0,
            'images_generated': 0,
            'roasts_sent': 0,
            'groups_managed': 0,
            'errors': 0
        }
        
    async def initialize(self):
        """Initialize bot components"""
        self.logger.info("🚀 Initializing Roastify Pro...")
        
        # Initialize database
        await self.db.initialize()
        
        # Load templates
        await self.roast_generator.load_templates()
        await self.image_renderer.load_assets()
        
        # Load group settings
        await self.group_manager.load_settings()
        
        self.logger.info("✅ Initialization complete")
        
    def create_application(self) -> Application:
        """Create Telegram application with all handlers"""
        
        # Persistence
        persistence = PicklePersistence(
            filepath="data/sessions.pickle",
            store_data=PicklePersistence.DEFAULT_STORE_DATA
        )
        
        # Build application
        application = (
            ApplicationBuilder()
            .token(self.token)
            .persistence(persistence)
            .concurrent_updates(True)
            .post_init(self.post_init)
            .post_shutdown(self.post_shutdown)
            .connection_pool_size(self.config.PERFORMANCE_CONFIG.POOL_SIZE)
            .pool_timeout(self.config.PERFORMANCE_CONFIG.TIMEOUT)
            .read_timeout(30)
            .write_timeout(30)
            .get_updates_read_timeout(30)
            .build()
        )
        
        # Add error handler
        application.add_error_handler(GlobalErrorHandler.handle_error)
        
        # Register handlers
        self.register_handlers(application)
        
        return application
        
    def register_handlers(self, application: Application):
        """Register all bot handlers"""
        
        # Command handlers
        application.add_handler(CommandHandler("start", self.command_start))
        application.add_handler(CommandHandler("help", self.command_help))
        application.add_handler(CommandHandler("stats", self.command_stats))
        application.add_handler(CommandHandler("settings", self.command_settings))
        application.add_handler(CommandHandler("broadcast", self.command_broadcast))
        application.add_handler(CommandHandler("roast", self.command_roast))
        application.add_handler(CommandHandler("image", self.command_image))
        application.add_handler(CommandHandler("live", self.command_live))
        application.add_handler(CommandHandler("admin", self.command_admin))
        
        # Message handlers
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handle_message
        ))
        
        # Group handlers
        application.add_handler(ChatMemberHandler(
            self.handle_chat_member,
            ChatMemberHandler.CHAT_MEMBER
        ))
        
        # Callback query handlers
        application.add_handler(CallbackQueryHandler(
            self.handle_callback_query
        ))
        
        # Inline query handler
        application.add_handler(MessageHandler(
            filters.StatusUpdate.NEW_CHAT_MEMBERS,
            self.handle_new_members
        ))
        
        # Poll handler
        application.add_handler(MessageHandler(
            filters.POLL,
            self.handle_poll
        ))
        
    async def command_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        # Check rate limit
        if not await self.rate_limiter.check_limit(f"start:{user.id}"):
            await update.message.reply_text("⚠️ Please wait before using this command again.")
            return
            
        welcome_text = await self.group_manager.get_welcome_message(user)
        
        keyboard = [
            [
                InlineKeyboardButton("🔥 Roast Me", callback_data="roast_me"),
                InlineKeyboardButton("🖼️ Generate Image", callback_data="generate_image")
            ],
            [
                InlineKeyboardButton("📊 Stats", callback_data="stats"),
                InlineKeyboardButton("⚙️ Settings", callback_data="settings")
            ],
            [
                InlineKeyboardButton("📖 Help", callback_data="help"),
                InlineKeyboardButton("🌟 Rate Bot", url="https://t.me/BotFather")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
        
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all text messages"""
        try:
            message = update.message
            user = update.effective_user
            chat = update.effective_chat
            
            # Update statistics
            self.stats['messages_processed'] += 1
            
            # Check if message should be processed
            if not await self.should_process_message(message):
                return
                
            # Process based on chat type
            if chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                await self.handle_group_message(update, context)
            else:
                await self.handle_private_message(update, context)
                
        except Exception as e:
            self.stats['errors'] += 1
            self.logger.error(f"Error in handle_message: {e}")
            
    async def handle_group_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle group messages"""
        message = update.message
        chat = update.effective_chat
        
        # Auto moderation
        if self.config.GROUP_CONFIG.AUTO_MODERATION:
            if await self.group_manager.check_violation(message):
                await self.group_manager.take_action(message)
                return
                
        # Check if bot is mentioned
        if self.is_bot_mentioned(message):
            await self.handle_mention(update, context)
            
        # Check for commands in groups
        if message.text and message.text.startswith('!'):
            await self.handle_group_command(update, context)
            
    async def handle_private_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle private messages"""
        message = update.message
        user = update.effective_user
        
        # Generate roast with image
        roast_data = await self.roast_generator.generate_roast(message.text)
        image_path = await self.image_renderer.render_roast_image(roast_data)
        
        # Send image
        with open(image_path, 'rb') as photo:
            sent_message = await message.reply_photo(
                photo=photo,
                caption=roast_data.get('secondary_roast', ''),
                reply_markup=self.get_vote_keyboard()
            )
            
        # Store message info
        await self.db.store_roast(
            user_id=user.id,
            message_id=sent_message.message_id,
            roast_text=roast_data['primary_roast'],
            image_path=image_path
        )
        
        self.stats['roasts_sent'] += 1
        self.stats['images_generated'] += 1
        
    async def handle_mention(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle when bot is mentioned"""
        message = update.message
        mentioned_user = message.reply_to_message.from_user if message.reply_to_message else None
        
        if mentioned_user and mentioned_user.id != message.from_user.id:
            # Roast mentioned user
            roast_data = await self.roast_generator.generate_targeted_roast(
                target=mentioned_user,
                context=message.text
            )
            
            image_path = await self.image_renderer.render_roast_image(roast_data)
            
            with open(image_path, 'rb') as photo:
                await message.reply_photo(
                    photo=photo,
                    caption=f"🎯 Targeted roast for {mentioned_user.first_name}!"
                )
                
    async def handle_new_members(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle new group members"""
        chat = update.effective_chat
        new_members = update.message.new_chat_members
        
        for member in new_members:
            if member.id == context.bot.id:
                # Bot added to group
                await self.group_manager.bot_added_to_group(chat)
            else:
                # New user joined
                await self.group_manager.user_joined_group(chat, member)
                
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        if data.startswith('vote_'):
            await self.handle_vote(query, data)
        elif data == 'roast_me':
            await self.handle_roast_me(query)
        elif data == 'generate_image':
            await self.handle_generate_image(query)
        elif data == 'stats':
            await self.handle_stats(query)
        elif data.startswith('admin_'):
            await self.handle_admin_action(query, data)
            
    async def handle_vote(self, query, data):
        """Handle vote buttons"""
        vote_type = data.split('_')[1]
        user_id = query.from_user.id
        message_id = query.message.message_id
        
        # Record vote
        await self.db.record_vote(
            user_id=user_id,
            message_id=message_id,
            vote_type=vote_type
        )
        
        # Update vote count
        votes = await self.db.get_votes(message_id)
        
        # Edit message with updated counts
        vote_text = f"✅ Vote recorded! ({votes['funny']}🔥 {votes['mid']}😐 {votes['savage']}💀)"
        await query.edit_message_caption(
            caption=f"{query.message.caption}\n\n{vote_text}"
        )
        
    async def start_live_stream(self, chat_id: int, title: str = "Roastify Live"):
        """Start live streaming"""
        stream_url = await self.stream_manager.start_stream(
            chat_id=chat_id,
            title=title
        )
        
        # Create stream message
        keyboard = [
            [
                InlineKeyboardButton("🎥 Watch Stream", url=stream_url),
                InlineKeyboardButton("💬 Join Chat", callback_data="join_chat")
            ]
        ]
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🎬 **Live Stream Started!**\n\nTitle: {title}\n\nJoin now!",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode=ParseMode.MARKDOWN
        )
        
    async def broadcast_message(self, message: str, chat_ids: List[int] = None):
        """Broadcast message to multiple chats"""
        if not chat_ids:
            chat_ids = await self.db.get_all_group_ids()
            
        success = 0
        failed = 0
        
        for chat_id in chat_ids:
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode=ParseMode.HTML
                )
                success += 1
                await asyncio.sleep(0.1)  # Rate limiting
            except Exception as e:
                failed += 1
                self.logger.error(f"Failed to send to {chat_id}: {e}")
                
        return success, failed
        
    async def get_statistics(self) -> Dict[str, Any]:
        """Get bot statistics"""
        return {
            **self.stats,
            'uptime': datetime.now() - self.start_time,
            'active_sessions': self.session_manager.active_count,
            'cache_hits': self.cache_manager.hit_count,
            'groups_managed': len(await self.db.get_all_groups()),
            'total_users': await self.db.get_user_count(),
            'daily_roasts': await self.db.get_daily_count(),
        }
        
    async def start(self):
        """Start the bot"""
        self.logger.info("Starting Roastify Pro Bot...")
        self.start_time = datetime.now()
        
        # Initialize components
        await self.initialize()
        
        # Create and run application
        application = self.create_application()
        
        # Start webhook or polling
        if self.config.API_CONFIG.WEBHOOK_URL:
            await application.bot.set_webhook(
                url=self.config.API_CONFIG.WEBHOOK_URL,
                secret_token=self.config.API_CONFIG.SECRET_KEY
            )
            self.logger.info(f"Webhook set to {self.config.API_CONFIG.WEBHOOK_URL}")
        else:
            await application.initialize()
            await application.start()
            await application.updater.start_polling()
            
        self.logger.info("✅ Bot is now running!")
        
        # Keep running
        await asyncio.Event().wait()
        
    async def stop(self):
        """Stop the bot gracefully"""
        self.logger.info("Stopping bot...")
        # Cleanup logic here
        
    # Helper methods
    async def should_process_message(self, message: Message) -> bool:
        """Check if message should be processed"""
        # Length check
        if not message.text or len(message.text.strip()) < 4:
            return False
            
        # Ignore conditions
        if message.text.strip().isdigit():
            return False
            
        if all(char in '😂🤣😭😢🥰❤️🔥' for char in message.text):
            return False
            
        # Rate limiting
        user_id = message.from_user.id
        if not await self.rate_limiter.check_limit(f"message:{user_id}"):
            return False
            
        return True
        
    def is_bot_mentioned(self, message: Message) -> bool:
        """Check if bot is mentioned"""
        if message.entities:
            for entity in message.entities:
                if entity.type == "mention" and "@roastify" in message.text.lower():
                    return True
        return False
        
    def get_vote_keyboard(self) -> InlineKeyboardMarkup:
        """Get vote keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("🔥 Funny", callback_data="vote_funny"),
                InlineKeyboardButton("😐 Mid", callback_data="vote_mid"),
                InlineKeyboardButton("💀 Savage", callback_data="vote_savage")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)