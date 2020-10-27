import config
import requests
from bs4 import BeautifulSoup
import pandas as pd
from random import randint
import telebot
from tabulate import tabulate
from telebot import types

bot = telebot.TeleBot(config.token)

pict = ['https://media.bani.md/image/201802/1280x720/a6edb419f2d45ea39d457baea11363b9.jpg',
        'https://www.profitwatch.com.au/wp-content/uploads/2020/03/nyse-stocks-dow-jones.jpg',
        'https://www.globaldomainsnews.com/wp-content/uploads/2018/12/US-stock-market-the-Dow-Jones-has-risen-by-five-per-cent.jpg',
        'https://www.investors.com/wp-content/uploads/2018/04/BIGPIC-041618-newscom.jpg']


def dow_johns_components():
    """

    :return: Dow Jones Companies real time rate data frame
    """
    url = 'https://finance.yahoo.com/quote/%5EDJI/components?p=%5EDJI'
    website = requests.get(url).text
    soup = BeautifulSoup(website, 'lxml')
    rows = soup.find_all('tr')
    fields_list = []
    # col = []
    for i in range(6):
        col = []
        col.append(rows[0].find_all('th')[i].get_text().strip())
        for row in rows[1:31]:
            r = row.find_all('td')
            col.append(r[i].get_text().strip())
        fields_list.append(col)

    d = dict()
    for i in range(6):
        d[fields_list[i][0]] = fields_list[i][1:]

    df = pd.DataFrame(d)
    df = df.set_index('Company Name')

    return df


def dow_jons_header_info():
    """

    :return: Dow Jones header info
    """
    url = 'https://finance.yahoo.com/quote/%5EDJI'
    website = requests.get(url).text
    soup = BeautifulSoup(website, 'lxml')
    dji_main = soup.find('div', class_='Mt(15px)').get_text()[6:].strip()
    price = soup.find('div', class_="My(6px) Pos(r) smartphone_Mt(6px)").get_text().strip()
    dji_name = dji_main[:28]
    changes = price[:24]
    time = price[24:]
    currency_info = dji_main[-15:]

    return dji_name, changes, time, currency_info


def currencies():
    """

    :return: data frame of real time currencies from Yahoo Finance Website
    """
    url = 'https://finance.yahoo.com/currencies/'
    web = requests.get(url).text
    soup = BeautifulSoup(web, 'lxml')
    table = soup.find('table')
    rows = table.find_all('tr')
    field_list = []
    for i in range(1, 5):
        columns = []
        columns.append(rows[0].find_all('th')[i].get_text().strip())
        for row in rows[1:28]:
            r = row.find_all('td')
            columns.append(r[i].get_text().strip())
        field_list.append(columns)

    d = dict()
    for i in range(4):
        d[field_list[i][0]] = field_list[i][1:]

    df = pd.DataFrame(d)

    return df


# начало диалога
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.from_user.id, "Hi there! Good to see you! \n"
                                           "Type /index_rate to see the Dow Jones Index current rate. \n"
                                           "Type /components to see the list of companies from Dow Jones Index. \n"
                                           "Type /currencies to see the list of available currencies. \n"
                                           "Type /info to read brief information about this bot. \n"
                                           "Type /help to see available commands.")
    bot.send_photo(message.from_user.id, pict[randint(0, 3)])


# /reset - возврат к начальной стадии
@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    bot.send_message(message.chat.id, "Let's start over! \n"
                                      "Type /index_rate to see the Dow Jones Index current rate. \n"
                                      "Type /currencies to see the list of available currencies. \n"
                                      "Type /info to read brief information about this bot. \n"
                                      "Type /help to see available commands.")
    bot.send_photo(message.from_user.id, pict[randint(0, 3)])


# /info выводит на экран короткую информацию о боте
@bot.message_handler(commands=["info"])
def cmd_info(message):
    bot.send_message(message.chat.id,
                     "This bot provides the current Dow Jones index rate, list of companies included in this "
                     "index and the rate of their price per share. \n"
                     "In addition the bot shows current rate of the most popular currencies. \n"
                     "\n"
                     "Type /index_rate to see The Dow Jones current rate. \n"
                     "Then you can ask for the list of companies with /components command and select the one you are "
                     "interested in.")
    bot.send_message(message.chat.id, 'The next step is to select a company. \n'
                                      'Enter the name of the company exactly like in the /components list. \n'
                                      'For instance: Apple Inc. \n'
                                      'When you type the name of the company I show you its current rate.')
    bot.send_message(message.chat.id, "Type /help to see the available commands. \n"
                                      "Type /reset to return to the first step.")


# /help выводит сообщеение со списком команд
@bot.message_handler(commands=["help"])
def cmd_help(message):
    bot.send_message(message.chat.id, "/start is used to start a new dialogue. \n"
                                      "/help is used to see available commands. \n"
                                      "/reset is used to return to the first step. \n"
                                      "/components is used to show the companies from The Dow Jones Index. \n"
                                      "/index_rate is used to to see The Dow Jones current rate. \n"
                                      "/info is used to show brief information about this bot \n"
                                      "/currencies is used to show available currencies.")


# /components выводит на экран список компаний, входящих в индекс Dow Jones
@bot.message_handler(commands=["components"])
def cmd_components(message):
    a = list(dow_johns_components().index.values)  # dow_jones_components()['Company Name']
    bot.send_message(message.chat.id, "\n".join(i for i in list(a)))
    bot.send_message(message.chat.id, 'To see the rate of any company just type its name. \n'
                                      'For instance: Apple Inc.\n'
                                      'Please enter the names of the company exactly like in /components list. \n'
                                      '\n'
                                      'To return to the first step type /reset. \n'
                                      'To see available commands type /help.')


# /currencies выводит кнопки курсов валют
@bot.message_handler(commands=['currencies'])
def cmd_currencies(message):
    keyboard = types.InlineKeyboardMarkup()
    key_btc_usd = types.InlineKeyboardButton(text='Bitcoin/USD', callback_data='bitcoin_usd')
    keyboard.add(key_btc_usd)
    key_eur_usd = types.InlineKeyboardButton(text='EUR/USD', callback_data='euro_usd')
    keyboard.add(key_eur_usd)
    key_usd_jpy = types.InlineKeyboardButton(text='USD/JPY', callback_data='usd_jpy')
    keyboard.add(key_usd_jpy)
    key_gbp_usd = types.InlineKeyboardButton(text='GBP/USD', callback_data='gbp_usd')
    keyboard.add(key_gbp_usd)
    key_eur_gbp = types.InlineKeyboardButton(text='EUR/GBP', callback_data='euro_gbp')
    keyboard.add(key_eur_gbp)
    key_usd_rub = types.InlineKeyboardButton(text='USD/RUB', callback_data='usd_rub')
    keyboard.add(key_usd_rub)
    bot.send_message(message.chat.id, 'Please select the pair. \n', reply_markup=keyboard)


# обрабатываем нажатие на кнопки
@bot.callback_query_handler(func=lambda call: True)
def button_callback(call):
    if call.data == 'bitcoin_usd':
        a = currencies().loc[0]
        df_a = pd.DataFrame(a)
        bot.send_message(call.message.chat.id, tabulate(df_a, headers='firstrow', tablefmt='simple'))
    elif call.data == 'euro_usd':
        b = currencies().loc[2]
        df_b = pd.DataFrame(b)
        bot.send_message(call.message.chat.id, tabulate(df_b, headers='firstrow', tablefmt='simple'))
    elif call.data == 'usd_jpy':
        c = currencies().loc[3]
        df_c = pd.DataFrame(c)
        bot.send_message(call.message.chat.id, tabulate(df_c, headers='firstrow', tablefmt='simple'))
    elif call.data == 'gbp_usd':
        d = currencies().loc[4]
        df_dd = pd.DataFrame(d)
        bot.send_message(call.message.chat.id, tabulate(df_dd, headers='firstrow', tablefmt='simple'))
    elif call.data == 'euro_gbp':
        e = currencies().loc[9]
        df_e = pd.DataFrame(e)
        bot.send_message(call.message.chat.id, tabulate(df_e, headers='firstrow', tablefmt='simple'))
    elif call.data == 'usd_rub':
        f = currencies().loc[25]
        df_f = pd.DataFrame(f)
        bot.send_message(call.message.chat.id, tabulate(df_f, headers='firstrow', tablefmt='simple'))
    bot.send_message(call.message.chat.id, "You can can select another one or \n"
                                           "type /reset to return to the first step. \n"
                                           "Type /help to see the available commands.")


# /index_rate выводит пользователю курс индекса в реальном времени
@bot.message_handler(commands=["index_rate"])
def cmd_index_rate(message):
    bot.send_message(message.chat.id, '\n'.join(i for i in dow_jons_header_info()))
    bot.send_message(message.chat.id, "Type /components to see the companies from DJI. \n"
                                      "Type /reset to return to the first step. \n"
                                      "Type /help to see available commands.")

# вывод курса акций определенной компании и обработка ошибок
@bot.message_handler(content_types=['text'])
def enter_companies(message):
    try:
        a = dow_johns_components().loc[message.text]
        df_1 = pd.DataFrame(a)
        bot.send_message(message.chat.id, tabulate(df_1, headers='keys', tablefmt='simple'))
    except:
        bot.reply_to(message, 'Please specify your command or enter the name of the company exactly like'
                              ' in /components list.')


bot.polling(none_stop=True, interval=0)