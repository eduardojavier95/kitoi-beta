import telebot
from telebot.types import InlineKeyboardMarkup  # para crear botonera inline
from telebot.types import InlineKeyboardButton  # para definir botones inline


def get_btn_and_msg(obj: dict, name_key: str, with_msg: bool = True) -> dict:
    """Se generan los botones inline de cada categoria,subcategoria y opciones segun corresponda

    Args:
        obj (dict): _description_
        name_key (str): _description_

    Returns:
        dict: Diccionario de botones listo para agregar al markup
    """

    dict_botones_and_msg = {"btn": {}, "msg": ""}
    botones = {}

    categorias = get_categorias(obj)
    if categorias:
        if name_key == "categorias":
            botones = categorias
            if with_msg:
                dict_botones_and_msg["msg"] = obj[name_key][f"msg_{name_key}"]

        else:
            list_subcategorias = get_list_categorias(obj)
            if list_subcategorias:
                if name_key in list_subcategorias:
                    botones = get_subcategorias(obj, name_key)
                    if with_msg:
                        dict_botones_and_msg["msg"] = get_msg_subcategorias(
                            obj, name_key)
                else:
                    lista_categorias = get_list_categorias(obj)
                    for cat in lista_categorias:
                        if name_key in obj["categorias"]["botones_categorias"][cat][f"botones_{cat}"]:
                            botones = get_opciones(obj, cat, name_key)
                            if with_msg:
                                dict_botones_and_msg["msg"] = get_msg_opciones(
                                    obj, cat, name_key)
                                
    dict_botones_and_msg["btn"] = generar_botones(botones)

    return dict_botones_and_msg if with_msg else dict_botones_and_msg["btn"]


def generar_botones(botones: dict) -> dict:
    dict_botones = {}
    
    n = 1

    for item in botones.keys():
        dict_botones[f"b_{n}"] = InlineKeyboardButton(
            text=item.capitalize(),
            callback_data=item if type(botones[item]) is dict else None,
            url=botones[item] if type(botones[item]) is str else None
        )

        n += 1
        
    return dict_botones


def funcion_repeat(bot: telebot = None,
                   call: telebot.types.CallbackQuery = None,
                   message: telebot.types.Message = None,
                   markup: InlineKeyboardMarkup = None,
                   btn_and_msg: dict = {}) -> None:

    markup.add(*btn_and_msg["btn"].values(), row_width=2)
    b_cerrar = InlineKeyboardButton("Cerrar", callback_data="cerrar")
    markup.row(b_cerrar)

    msg = btn_and_msg["msg"]

    if call:
        cid = call.from_user.id
        mid = call.message.id

        bot.edit_message_text(msg, cid, mid, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, msg, reply_markup=markup)


def get_categorias(obj: dict) -> dict:
    return obj["categorias"]["botones_categorias"]


def get_list_categorias(obj: dict) -> list:
    return list(get_categorias(obj).keys())


def get_msg_categorias(obj: dict) -> str:
    return obj["categorias"]["msg_categorias"]


def get_subcategorias(obj: dict, name_sub: str) -> dict:
    categorias = get_categorias(obj)
    return categorias[name_sub][f"botones_{name_sub}"]


def get_list_subcategorias(obj: dict, name_sub: str) -> list:
    return list(get_subcategorias(obj=obj, name_sub=name_sub).keys())


def get_msg_subcategorias(obj: dict, name_cat: str) -> str:
    categorias = get_categorias(obj)
    return categorias[name_cat][f"msg_{name_cat}"]


def get_opciones(obj: dict, name_cat: str, name_opcion: str) -> dict:
    opciones = get_subcategorias(obj, name_cat)
    return opciones[name_opcion][f"botones_{name_opcion}"]


def get_list_opciones(obj: dict, name_sub: str, name_opcion: str) -> list:
    return list(get_opciones(obj, name_sub, name_opcion))


def get_msg_opciones(obj: dict, name_sub: str, name_opcion: str) -> str:
    subcategorias = get_subcategorias(obj, name_sub)
    return subcategorias[name_opcion][f"msg_{name_opcion}"]


def get_all_keys(obj: dict) -> list | None:

    botones = []

    if obj:
        if "categorias" in obj:
            botones.append("categorias")

            categorias = get_list_categorias(obj)
            if categorias:
                for name in categorias:
                    opciones = list(get_subcategorias(obj, name).keys())
                    botones.append(name)
                    if opciones:
                        for opc in opciones:
                            botones.append(opc)

        return botones


# def get_msg(obj: dict, name_key: str) -> str:
#     """ Obtener el mensaje de un categoria, subcategoria u opcion dada"""

#     if name_key == "categorias":
#         return obj[name_key][f"msg_{name_key}"]

#     categorias = get_categorias(obj=obj)
#     if f"msg_{name_key}" in categorias[name_key]:
#         return categorias[name_key][f"msg_{name_key}"]

#     subcategorias = get_subcategorias(obj, name_key)
#     if f"msg_{name_key}" in subcategorias[name_key]:
#         return subcategorias[name_key][f"msg_{name_key}"]
