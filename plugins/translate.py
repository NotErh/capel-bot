# requires googletrans
# https://pypi.org/project/googletrans/

class GoogleTranslate:
    def __init__(self):
        from googletrans import Translator
        self.translator = Translator()
    
    def translate_to_en(self, string):
        return self.translator.translate(string, dest = 'en')
        

    def translate_to_ja(self, string):
        return self.translator.translate(string, dest = 'ja')
