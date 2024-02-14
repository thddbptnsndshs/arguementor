from copy import copy
import os
from openai import OpenAI
import json
import uuid
import pickle
from prompts import *
import sqlite3
import random

import telebot
from telebot import types

import requests

# инстанс бота
bot = telebot.TeleBot(token=os.environ["TELEBOT_TOKEN"])
client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url="https://api.proxyapi.ru/openai/v1",
)

intro_text = """Я -- бот-аргументор. Я помогу тебе встать на путь к 100 баллам за ЕГЭ по русскому и посвящу тебя в мир литературных аргументов. Твоё сочинение не обойдётся без аргумента, так позволь мне тебя направить.

ЕГЭ по русскому - это как сражение в аниме: требует умения, силы и стратегии. Подготовка к сочинению - это как тренировка героев перед битвой. Помните, что каждая попытка приближает вас к победе. Ошибки - это опыт, который делает вас сильнее.

Напиши проблему, которую ты нашёл в тексте, и мы начнём."""
restart_text = """Давай начнём заново. Какая проблема в твоём тексте?"""
chats_saver = {}
problem_saver = {}
literature_to_go = {}
titles = {}
argument = {}

def record_to_db(message):
    # Connect to the database or create it if it doesn't exist
    conn = sqlite3.connect('records.db')

    # Create a cursor object to interact with the database
    c = conn.cursor()

    # Create a table to store records
    c.execute('''CREATE TABLE IF NOT EXISTS records
                 (id INTEGER PRIMARY KEY, chat_id TEXT, problem TEXT, literature TEXT, titles TEXT, argument TEXT)''')

    # Insert a record into the table
    c.execute("INSERT INTO records (chat_id, problem, literature, titles, argument) VALUES (?, ?, ?, ?, ?)", 
              ([str(ele) for ele in [message.chat.id, 
                                     problem_saver.get(message.chat.id), 
                                     literature_to_go.get(message.chat.id), 
                                     titles.get(message.chat.id), 
                                     argument.get(message.chat.id)
                                    ]]))

    # Commit the changes to the database
    conn.commit()

    # Close the connection
    conn.close()


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message):
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(
        chat_id=message.chat.id,
        text=intro_text,
        reply_markup=markup
    )

@bot.message_handler(commands=['restart'])
def new_game_bot(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(
        chat_id=chat_id,
        text=restart_text,
        reply_markup=markup
    )
        
#     for record in [problem_saver, chats_saver, literature_to_go, titles, argument]:  
    if message.chat.id in chats_saver:
        del chats_saver[message.chat.id]
    if message.chat.id in literature_to_go:
        del literature_to_go[message.chat.id]
    if message.chat.id in problem_saver:
        del problem_saver[message.chat.id]
    if message.chat.id in titles:
        del titles[message.chat.id]
    if message.chat.id in argument:
        del argument[message.chat.id]

@bot.message_handler(content_types=['text'], func=lambda msg: 'проблема' in msg.text.lower())
def choose_option(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    itembtn1 = types.KeyboardButton('Напиши аргумент')
    itembtn2 = types.KeyboardButton('Посоветуй литературу')
    itembtn3 = types.KeyboardButton('Подскажи, как использовать произведение')
    itembtn4 = types.KeyboardButton('/restart')
    markup.add(itembtn1, itembtn2, itembtn3, itembtn4)
    problem_saver[message.chat.id] = message.text
    if message.chat.id not in chats_saver: # если чат только начался

        bot.send_message(
            chat_id=message.chat.id,
            text="Проблему понял. Чем я могу тебе с ней помочь?",
            reply_markup=markup,
        )
    
@bot.message_handler(content_types=['text'], func=lambda msg: msg.text in [
    'Напиши аргумент', 
    'Посоветуй литературу',
    'Подскажи, как использовать произведение'
])
def generate_response(message):
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(
        chat_id=message.chat.id,
        text="Сейчас подумаю... Налей мне иван-чаю.",
        reply_markup=markup,
    )
    bot.send_chat_action(chat_id=message.chat.id, action="typing")

    if message.text == 'Напиши аргумент':
        chats_saver[message.chat.id] = [
            {
                "role": "system",
                "content": argument_prompt,
            },
            {"role": "user", "content": problem_saver[message.chat.id]}
        ]
        chat_completion = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=chats_saver[message.chat.id],
        ).choices[0].message.content
        
        chats_saver[message.chat.id].append({})
        
        bot.send_message(
            chat_id=message.chat.id,
            text='Предлагаю такой аргумент:',
            reply_markup=markup,
        )
        
        argument[message.chat.id] = chat_completion
        record_to_db(message)
        
        bot.send_message(
            chat_id=message.chat.id,
            text=chat_completion,
        )
    
    elif message.text == 'Посоветуй литературу':   
        chats_saver[message.chat.id] = [
            {
                "role": "system",
                "content": literature_prompt,
            },
            {"role": "user", "content": problem_saver[message.chat.id]}
        ]
        chat_completion = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=chats_saver[message.chat.id],
            response_format={"type": "json_object"}
        ).choices[0].message.content
        
        parsed_literature = json.loads(chat_completion)
        literature_to_go[message.chat.id] = parsed_literature
        
#        literature dict {'titles': List[str], 'descriptions': List[str]}

        markup = types.ReplyKeyboardMarkup(row_width=2)
        itembtns = [types.KeyboardButton(title) for title in parsed_literature['titles']]
        markup.add(*itembtns)
        
        bot.send_message(
            chat_id=message.chat.id,
            text='Вот произведения, которые я советую по твоей проблеме:',
        )
        
        emoji = random.choice(['📓 ', '📔 ', '📒 ', '📕 ', '📗 ', '📘 ', '📙 ', '📚 ', '📖 ',])
        
        bot.send_message(
            chat_id=message.chat.id,
            text='\n\n'.join([emoji + title + '\n' + description for title, description in zip(
                parsed_literature['titles'],
                parsed_literature['descriptions']
            )]),
            reply_markup=markup,
        )
    
    elif message.text == 'Подскажи, как использовать произведение':
        markup = types.ReplyKeyboardMarkup(row_width=2)
        bot.send_message(
            chat_id=message.chat.id,
            text='Хорошо, давай подумаем, как использовать твоё произведение. Отправь мне его название (автора тоже напиши, если знаешь).',
            reply_markup=markup,
        )
                
@bot.message_handler(content_types=['text'], func=lambda msg: not (msg.text in [
    'Напиши аргумент', 
    'Посоветуй литературу',
    'Подскажи, как использовать произведение'
] or 'проблема' in msg.text))
def arg_from_lit(message):
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(
        chat_id=message.chat.id,
        text="Сейчас, момент... Ты не видел мою красную ручку?",
        reply_markup=markup,
    )
    bot.send_chat_action(chat_id=message.chat.id, action="typing")

    chats_saver[message.chat.id] = [
        {
            "role": "system",
            "content": arg_from_lit_prompt + problem_saver[message.chat.id],
        },
        {"role": "user", "content": message.text}
    ]
    chat_completion = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=chats_saver[message.chat.id],
    ).choices[0].message.content

    bot.send_message(
        chat_id=message.chat.id,
        text='Предлагаю такой аргумент:',
        reply_markup=markup,
    )
    
    argument[message.chat.id] = chat_completion
    record_to_db(message)

    bot.send_message(
        chat_id=message.chat.id,
        text=chat_completion,
    )

bot.infinity_polling()
