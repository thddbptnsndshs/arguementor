argument_prompt = '''Ты сдаёшь ЕГЭ по русскому языку. Одно из заданий -- написать эссе по тексту. 
        Пользователь назовёт проблему, которая поднимается в тексте. 
        Пользователю нужно подкрепить свои умозаключения примером-аргументом из литературы. Назови произведение и его автора и объясни, как оно раскрывает проблему из текста.
        Напиши аргумент, он должен быть не длиннее 5-6 предложений.'''

literature_prompt = '''Ты сдаёшь ЕГЭ по русскому языку. Одно из заданий -- написать эссе по тексту. 
        Пользователь назовёт проблему, которая поднимается в тексте. 
        Пользователю нужно подкрепить свои умозаключения примером-аргументом из литературы. 
        Назови 5 произведений с их авторами, которые можно использовать для аргументации в сочинении по этой проблеме. К каждому произведению напиши 1-2 предложения о том, как оно относится к проблеме.
        Выведи валидный json такой структуры: {'titles': [title, title, ...], 'descriptions': [description, description, ...]}'''

# literature_prompt = '''Я пишу ЕГЭ по русскому языку. 
# Помоги мне придумать литературные сочинения для проблемы сохранения памятников. Предложи мне список произведений, из которых я могу взять аргументы. 
# Дай ответ в json-формате с полями titles и descriptions. 
# '''
arg_from_lit_prompt = '''Ты сдаёшь ЕГЭ по русскому языку. Одно из заданий -- написать эссе по тексту. 
        Пользователю нужно подкрепить свои умозаключения примером-аргументом из литературы. Аргумент должен быть не длиннее 5-6 предложений.
        В тексте поднимается проблема '''

text_analysis_prompt = '''Ты сдаёшь ЕГЭ по русскому языку. Одно из заданий -- написать эссе по тексту. 
В тексте поднимается одна или несколько проблем. Пользователь передаст тебе текст. Твоя задача -- выделить все проблемы.
Сформулируй их максимально кратко, например "проблема охраны природы" или "проблема роли детства в жизни человека". Учти, что проблема должна быть как можно более абстрактной: она не упоминается в тексте напрямую.
'''