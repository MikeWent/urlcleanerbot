#!/usr/bin/env python3

from urllib.parse import urlparse, parse_qs, urlencode, urljoin
import re

from telebot import types
import telebot

try:
    with open("token.txt", "r") as f:
        telegram_token = f.read().strip()
except FileNotFoundError:
    print("Put your Telegram bot token to 'token.txt' file")
    exit(1)
bot = telebot.TeleBot(telegram_token)

def filter_query_string(domain, query):
    PARAMS_WHITELIST = ("item", "id", "text", "q")
    DOMAIN_PARAMS_WHITELIST = {
        "duckduckgo.com": ("p", "ia", "iax", "iar"),
        "google.com": ("tbm", "hl", "chips")
    }
    whitelist = PARAMS_WHITELIST + DOMAIN_PARAMS_WHITELIST.get(domain, tuple())
    params = parse_qs(query)
    filtered_params_dict = {k:v[0] for (k,v) in params.items() if k in whitelist}
    return urlencode(filtered_params_dict)
    
def cleanup(url):
    u = urlparse(url)
    domain = u.netloc.replace("www.", "")
    filtered_query = filter_query_string(domain, u.query)
    final_url = urljoin(u.scheme + "://" + u.netloc, u.path)
    final_url = urljoin(final_url, "?" + filtered_query)
    return domain, final_url
    
# Handle URLs
URL_REGEXP = r'(.*\..*/.*?\?.*)'
@bot.message_handler(regexp=URL_REGEXP)
def handle_urls(message):
    # Grab first found link
    urls = re.findall(URL_REGEXP, message.text)
    response_message = ""
    for url in urls:
        if not url.startswith("http"):
            url = "http://"+url
        response_message += cleanup(url)[0]+"\n"
    try:
        bot.reply_to(message, response_message)
    except:
        pass


# Inline mode
@bot.inline_handler(lambda query: re.match(URL_REGEXP, query.query))
def query_text(inline_query):
    domain, clean_url = cleanup(inline_query.query)
    r = [types.InlineQueryResultArticle(hash(clean_url), domain,
            types.InputTextMessageContent(clean_url),
            url=clean_url
         ),
         types.InlineQueryResultArticle(hash(clean_url)+1, domain+" (no preview)",
            types.InputTextMessageContent(
                clean_url,
                disable_web_page_preview=True
            ),
            description=clean_url
         )
    ]
    bot.answer_inline_query(inline_query.id, results=r)

bot.polling()
