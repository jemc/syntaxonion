import re

class SyntaxOnion:
    # Uncommon characters to use to represent occupied but dead space in a string.
    #   It must be able to be matched by the '.' character in a regexp pattern.
    # dead_chars = ['\xa7', '\xa4', '\xac'] # reserved characters: §¤¬

    @classmethod
    def dead_char(self, i): return bytes([0xac-(i+1)]).decode('unicode-escape')
    @classmethod
    def dead_patt(self, i): return self.dead_char(i) + self.dead_char(-1)+r'*'

    @classmethod
    def check_for_dead(self, text, layer):
        for c in ([-1,layer] if layer==0 else [layer]):
            c = self.dead_char(c)
            if re.search(c, text): 
                raise SyntaxError("Illegal (reserved) character '"+c+
                                    "' in input file.")

    def __init__(self, text):
        self.text = text
        self.patterns = []
        self.matchlists = []

    def peel(self, pattern):
        layer = len(self.matchlists)
        self.check_for_dead(self.text, layer)

        # self.patterns.append(pattern)

        matchlist = list(re.finditer(pattern, self.text))
        text_list = list(self.text)
        for m in matchlist:
            text_list[m.start():m.end()] = \
                self.dead_char(layer)+self.dead_char(-1)*(m.end()-m.start()-1)

        self.text = ''.join(text_list)
        self.matchlists.append(matchlist)

    def repeal(self):
        try: matchlist = self.matchlists.pop()
        except IndexError:
            raise IndexError("No more layers to repeal in"+str(self))
        
        layer = len(self.matchlists)
        for m in matchlist:
            self.text = re.sub(self.dead_patt(layer), 
                               m.group(), self.text, count=1)

    def peels(self, patterns): [self.peel(p) for p in patterns]

    def repeal_all(self): [self.repeal() for i in range(len(self.matchlists))]

