import json
import os
from re import S
import threading
import time
import telebot
from telebot import apihelper
from telebot.types import InlineKeyboardMarkup  # para crear botonera inline
from telebot.types import InlineKeyboardButton  # para definir botones inline
from config import *
from utils import funcion_repeat, generar_botones, get_all_keys, get_btn_and_msg, get_categorias, get_list_categorias, get_list_subcategorias, get_subcategorias
from flask import Flask, request
from waitress import serve

pathWindows = "D:\Programacion\Proyectos\kitoibeta\data.json"
pathHeroku = "data.json"

path = pathWindows if os.path.isfile(pathWindows) else pathHeroku
nuevo_negocio = {}
with open(path, 'r') as data:
    BOTONES_CHOICE = json.loads(data.read())


"""
Las instancias de bot que estuvieron inactivas durante mucho tiempo pueden ser rechazadas
por el servidor al enviar un mensaje debido a un tiempo de espera de la última sesión 
utilizada. Agregue apihelper.SESSION_TIME_TO_LIVE = 5 * 60a su inicialización para forzar
la recreación después de 5 minutos sin actividad.
"""
session_time_to_live = apihelper.SESSION_TIME_TO_LIVE = 3 * 60

# instanciamos el bot de Telegram
bot = telebot.TeleBot(
    TELEGRAM_BOT_TOKEN,
    exception_handler=session_time_to_live
)
web_server = Flask(__name__)


@web_server.route('/', methods=['POST'])
def webhook():
    # si el POST reibido es un JSON
    if request.headers.get("content-type") == "application/json":
        update = telebot.types.Update.de_json(
            request.stream.read().decode('utf-8'))
        bot.process_new_updates([update])

        return "Ok", 200


# responde al comando /start
@bot.message_handler(commands=['start'])
def cmd_start(message) -> None:
    """Muestra un mensaje con botones inline (a continuacion del mensaje)"""
    markup = InlineKeyboardMarkup()
    b1 = InlineKeyboardButton("Categorias", callback_data="categorias")
    b_menu = InlineKeyboardButton("Menu", callback_data="menu")
    b_cerrar = InlineKeyboardButton("Cerrar", callback_data="cerrar")
    markup.add(b1)
    markup.add(b_menu, b_cerrar)
    msg = """\
        <b>Bienvenido al bot</b> que no querra volver a olvidar nunca. \n\n\
    Aqui podras buscar lo que gustes de manera mas rapida, organizado 
    por categorias, y con el mejor diseno en bots del 2022. \n \n"""
    bot.send_message(message.chat.id, msg,
                     reply_markup=markup, parse_mode="html")


# # @bot.message_handler(commands=["agregar_negocio"])
# # def cmd_agregar_negocio(message):

# #     if message.from_user.id in ADMINS:

# #         markup = InlineKeyboardMarkup()
# #         botones = generar_botones(get_categorias(BOTONES_CHOICE))
# #         markup.add(*botones.values(), row_width=2)
# #         msg = bot.reply_to(
# #             message, "Hey, puedes decirme dentro de que categoria debe estar?", reply_markup=markup)
# #         bot.register_next_step_handler(msg, elegir_subcategoria)
# #     else:
# #         help_message(message)
        


# # def elegir_subcategoria(message):

# #     try:
# #         name = message.text
# #         subcategorias = get_list_subcategorias(BOTONES_CHOICE, name)

# #         if name in subcategorias:
# #             nuevo_negocio[name] = {
# #                 f"botones_{name}": {},
# #                 f"msg_{name}": f"A continuacion le muestro las opciones dentro de {name} que tenemos disponibles"
# #             }

# #         markup = InlineKeyboardMarkup()
# #         botones = generar_botones(get_subcategorias(BOTONES_CHOICE, name))
# #         markup.add(*botones.values(), row_width=2)

# #         msg = bot.send_message(
# #             message.chat.id,
# #             "Muy bien!!! Ahora dime dentro de que categoria debe estar?",
# #             reply_to_message_id=message.message_id,
# #             reply_markup=markup)
# #         bot.register_next_step_handler(msg, procesar_categoria_negocio)

# #     except:
# #         pass


# @bot.message_handler(commands=["modificar-negocio"])
# def cmd_modificar_negocio(message):
#     pass


# @bot.message_handler(commands=["eliminar-negocio"])
# def cmd_eliminar_negocio(message):
#     pass


# @bot.message_handler(commands=["agregar-categoria, agregar-subcategoria"])
# def cmd_agregar_categoria_subcategoria(message):
#     pass


# @bot.message_handler(commands=["modificar-categoria, modificar-subcategoria"])
# def cmd_modificar_categoria_subcategoria(message):
#     pass


# @bot.message_handler(commands=["eliminar-categoria, eliminar-subcategoria"])
# def cmd_eliminar_categoria_subcategoria(message):
#     pass


# responde a una lista de comandos
@bot.message_handler(
    commands=get_all_keys(BOTONES_CHOICE))
def commandos_genericos(message) -> None:
    """Muestra un mensaje con botones inline (a continuacion del mensaje)"""

    msg_text = message.text.replace("/", "").rstrip()
    markup = InlineKeyboardMarkup(row_width=2)  # instanciamos la botonera
    botones = get_all_keys(BOTONES_CHOICE)
    if msg_text in botones:
        btn_and_msg = get_btn_and_msg(BOTONES_CHOICE, msg_text)
        funcion_repeat(bot=bot,
                       message=message,
                       markup=markup,
                       btn_and_msg=btn_and_msg)


@bot.callback_query_handler(func=lambda x: True)
def respuesta_botones_inline(call) -> None:

    cid = call.from_user.id
    mid = call.message.id
    markup = InlineKeyboardMarkup(row_width=2)  # instanciamos la botonera

    all_button = get_all_keys(BOTONES_CHOICE)

    if all_button:
        if call.data in all_button:
            btn_and_msg = get_btn_and_msg(BOTONES_CHOICE, call.data)

            funcion_repeat(bot=bot,
                           call=call,
                           markup=markup,
                           btn_and_msg=btn_and_msg)

    if call.data == "cerrar":
        bot.delete_message(cid, mid)


@bot.message_handler(content_types=['text'])
def help_message(message):

    help_msg = f"""Veo que no sabes como usar kitoi_bot, dejame darte alguna ayuda para que puedas sacarle mejor provecho.\n \n\
Puede escribir el comando /categorias para buscar lo que le interese.\n\
Espero que le sea de ayuda."""

    if message.text.startswith("/"):
        msg_text = message.text.replace("/", "").rstrip()
        if msg_text not in BOTONES_CHOICE:

            bot.reply_to(message, help_msg)

    else:
        bot.reply_to(message, help_msg)




# def procesar_nombre_negocio(message):
#     try:
#         name = message.text
#         print(name)
#         categorias = BOTONES_CHOICE["categorias"]["botones_categorias"].keys()

#         for name_obj in categorias:
#             if name in BOTONES_CHOICE["categorias"]["botones_categorias"][name_obj]:
#                 bot.reply_to(message, 'oooops!! Ya existe este negocio')

#         nuevo_negocio[name] = {
#             f"opciones_{name}": {},
#             f"msg_{name}": f"A continuacion le muestro las opciones dentro de {name} que tenemos disponibles"
#         }
#         markup = InlineKeyboardMarkup()
#         botones = generar_botones(list(categorias))
#         markup.add(*botones.values(), row_width=2)
#         msg = bot.send_message(
#             message.chat.id,
#             "Muy bien!!! Ahora dime dentro de que categoria debe estar?",
#             reply_to_message_id=message.message_id,
#             reply_markup=markup)
#         bot.register_next_step_handler(msg, procesar_categoria_negocio)
#     except Exception as e:
#         bot.reply_to(
#             message, 'oooops!! Algo salio mal, por favor reintentelo mas tarde o pongase en contacto con el soporte.')


# def procesar_categoria_negocio(message):

#     try:

#         categorias = list(
#             BOTONES_CHOICE["categorias"]["botones_categorias"].keys())
#         name_categoria = message.text.lower()

#         if name_categoria in categorias:

#             opciones = BOTONES_CHOICE["categorias"]["botones_categorias"][name_categoria][f"botones_{name_categoria}"].keys(
#             )

#             markup = InlineKeyboardMarkup()
#             botones = generar_botones(list(opciones))
#             markup.add(*botones.values(), row_width=2)

#             msg = bot.send_message(message.chat.id,
#                                    "Bien!! Ya casi terminamos, por favor dime dentro de que opciones de las que tiene la categoria selecionada quieres que aparezca el negocio",
#                                    reply_to_message_id=message.message_id, reply_markup=markup)

#             bot.register_next_step_handler(msg, procesar_opcion_negocio)

#     except Exception as e:
#         bot.reply_to(
#             message, 'oooops!! Algo salio mal, por favor reintentelo mas tarde o pongase en contacto con el soporte.')


def procesar_opcion_negocio():
    pass


def iniciar_web_server():
    bot.remove_webhook()
    time.sleep(1)
    bot.set_webhook(url=f"https://{APP}.heroku.com")
    serve(web_server, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))


def iniciar_polling():
    bot.remove_webhook()
    time.sleep(1)
    bot.infinity_polling()


if __name__ == "__main__":
    """_summary_
    """
    print("Iniciando bot")
    if os.environ.get("DYNO_RAM"):
        hilo = threading.Thread(name="hilo_web_server",
                                target=iniciar_web_server)
    else:
        hilo = threading.Thread(name="hilo_polling", target=iniciar_polling)
    hilo.start()
    print("BOT INICIADO")

# "Comida cubana": "https://google.com"
