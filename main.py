from typing import List
from enum import Enum
import urllib.request

class TokenType(Enum):
    XML = 0
    RSS = 1 
    RSS_END = 2
    CHANNEL = 3
    CHANNEL_END = 4
    TITLE = 5
    LINK = 6
    DESCRIPTION = 7
    LANGUAGE = 8
    PUBDATE = 9
    LASTBUILDDATE = 9
    DOCS = 10
    GENERATOR = 11 
    MANAGINGEDITOR = 12
    WEBMASTER = 13
    ATOM_LINK = 14
    ITEM = 15
    ITEM_END = 16
    GUID = 17 
    ENCLOSURE = 18

    def from_str(in_str: str):
        return TokenType[f"{in_str.upper()}"]

class Token:

    def __init__(self, typ: TokenType, attr: str, content: str):
        self.typ = typ
        self.attr = attr
        self.content = content

    def __str__(self):
        return f"Token {{ Type: {self.typ.name}, Attributes: {self.attr}, Content: {self.content} }}"
    
    def __repr__(self):
        return f"Token {{ Type: {self.typ.name}, Attributes: {self.attr}, Content: {self.content} }}"

class XMLTokenizer:

    def __init__(self, xml: str) -> None:

        self.raw_xml = xml 
        self.tokens: List[Token] = []
    
    def parse_xml(self) -> None:

        while self.raw_xml:
            start = self.raw_xml.find("<")
            if self.raw_xml[start+1] == '?':
                end = self.raw_xml.find('>')
                if end == -1:
                    print("[ERROR] XML TAG MISSING CLOSING \'>\'")
                attr = self.raw_xml[start:end-1].split(" ")[1:]
                self.raw_xml = self.raw_xml[end+1:].lstrip()
                self.tokens.append(Token(TokenType.XML, attr, None))
                continue
            elif self.raw_xml[start+1] == '/':
                end = self.raw_xml.find('>')
                if end == -1:
                    print("[ERROR] COULDNOT FIND CLOSING '>'")
                typstr = self.raw_xml[start+2:end].split(' ')[0]
                typ = TokenType.from_str(typstr)
                match typ:
                    case TokenType.XML: 
                        self.raw_xml = self.raw_xml[end+1:].lstrip()
                        self.tokens.append(Token(typ, None, None))
                        continue
                    case TokenType.RSS | TokenType.CHANNEL | TokenType.ITEM:
                        self.raw_xml = self.raw_xml[end+1:].lstrip()
                        self.tokens.append(Token(TokenType.from_str(f"{typstr}_end"), None, None))
                        continue
                    case _:
                        if typ != self.tokens[-1].typ:
                            print(f"[ERROR] Expected closing {self.tokens[-1].typ} tag instead found closing {typ} tag")
                            break
                        
                        self.raw_xml = self.raw_xml[end+1:].lstrip()
                        continue
            else:
                end = self.raw_xml.find('>')
                if end == -1:
                    print("[ERROR] COULDNOT FIND CLOSING '>'")
                el = self.raw_xml[start+1:end].split(' ')
                typ = el[0]
                attr = el[1:]
                match typ:
                    case "rss" | "channel" | "item":
                        self.raw_xml = self.raw_xml[end+1:].lstrip()
                        self.tokens.append(Token(TokenType.from_str(typ), attr, None))
                    case "title" | "link" | "description" | "language" | "pubDate" | "lastBuildDate" | "docs" | "generator" | "managingEditor" | "webMaster" | "guid":
                        self.raw_xml = self.raw_xml[end:].lstrip()
                        start = end
                        end = self.raw_xml.find(f"</{typ}>")
                        if end == -1:
                            print(f"[ERROR] <{typ}> tag is not closed")
                        content = self.raw_xml[start:end]
                        self.raw_xml = self.raw_xml[end:].lstrip()
                        self.tokens.append(Token(TokenType.from_str(typ), attr, content))
                    case "atom:link":
                        self.raw_xml = self.raw_xml[end+1:].lstrip()
                        self.tokens.append(Token(TokenType.ATOM_LINK, attr, None))
                        continue
                    case "enclosure":
                        self.raw_xml = self.raw_xml[end+1:].lstrip()
                        self.tokens.append(Token(TokenType.ENCLOSURE, attr, None))
                    case _:
                        print(f"[ERROR] COULD NOT PARSE. UNKNOWN TOKEN TYPE: {typ}")
                        break

class XMLElement:
    pass

class XMLLexer:

    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.lexemes: List[XMLElement] = []
    
    def parse_tokens(self) -> None:

        while len(self.tokens) > 0:
            tok = self.tokens.pop(0)

            self.lexemes.append(XMLElement)
    



def main():
    
    xml = urllib.request.urlopen("https://www.rssboard.org/files/sample-rss-2.xml").read().decode('utf-8')

    tk = XMLTokenizer(xml)
    tk.parse_xml()

    print(tk.tokens)








if __name__ == "__main__":
    main()