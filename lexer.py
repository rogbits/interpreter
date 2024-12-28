import enum


class TokenType(enum.Enum):
	PROGRAM = 'program'
	PROCEDURE = 'procedure'
	VAR = 'var'
	INTEGER_TYPE = 'integer'
	REAL_TYPE = 'real'
	BEGIN = 'begin'
	END = 'end'
	ID = 'id'
	ASSIGNMENT = ':='
	SEMI = ';'
	DOT = '.'
	COLON = ':'
	COMMA = ','
	
	INTEGER_CONST = 'integer'
	REAL_CONST = 'real'
	ADD = '+'
	SUBTRACT = '-'
	MULTIPLY = '*'
	DIVIDE = '/'
	INT_DIVIDE = 'div'
	LPAREN = '('
	RPAREN = ')'
	LBRACE = '{'
	RBRACE = '}'
	SINGLE_QUOTE = "'"
	WRITELN = 'writeln'
	EOF = 'EOF'


class Token:
	def __init__(self, token_type: TokenType, value: int | float | str):
		self.token_type: TokenType = token_type
		self.value: int | str = value
	
	def __str__(self):
		return f"{self.token_type.name}::{self.value}"
	
	def __repr__(self):
		return self.__str__()


class Lexer:
	def __init__(self, text: str):
		self.text = text
		self.pos = 0
		self.pos_before_peak = 0
	
	def rewind(self):
		self.pos = self.pos_before_peak
	
	def pos_valid(self):
		return self.pos < len(self.text)
	
	def peak(self) -> Token:
		return self._next_token()
	
	def next_token(self) -> Token:
		self.pos = self.pos_before_peak
		token = self._next_token()
		self.pos_before_peak = self.pos
		return token
	
	def _next_token(self) -> Token:
		if not self.pos_valid(): return Token(token_type=TokenType.EOF, value=0)
		c = self.text[self.pos]
		if c.isalpha():
			word = ''
			while self.pos_valid() and (self.text[self.pos].isalpha() or self.text[self.pos].isdigit()):
				word += self.text[self.pos]
				self.pos += 1
			if word.lower() == 'begin':
				return Token(token_type=TokenType.BEGIN, value=0)
			if word.lower() == 'end':
				return Token(token_type=TokenType.END, value=0)
			if word.lower() == 'program':
				return Token(token_type=TokenType.PROGRAM, value=0)
			if word.lower() == 'var':
				return Token(token_type=TokenType.VAR, value=0)
			if word.lower() == 'integer':
				return Token(token_type=TokenType.INTEGER_TYPE, value=0)
			if word.lower() == 'real':
				return Token(token_type=TokenType.REAL_TYPE, value=0)
			if word.lower() == 'div':
				return Token(token_type=TokenType.INT_DIVIDE, value=0)
			if word.lower() == 'procedure':
				return Token(token_type=TokenType.PROCEDURE, value=0)
			return Token(token_type=TokenType.ID, value=word)
		if c.isdigit():
			num = ''
			is_float = False
			while self.pos_valid() and self.text[self.pos].isdigit():
				num += self.text[self.pos]
				self.pos += 1
			if self.text[self.pos] == '.':
				is_float = True
				num += self.text[self.pos]
				self.pos += 1
			while self.pos_valid() and self.text[self.pos].isdigit():
				num += self.text[self.pos]
				self.pos += 1
			if is_float:
				return Token(token_type=TokenType.REAL_CONST, value=float(num))
			else:
				return Token(token_type=TokenType.INTEGER_CONST, value=int(num))
		if c == ':' and self.text[self.pos + 1] == '=':
			self.pos += 2
			return Token(token_type=TokenType.ASSIGNMENT, value=0)
		if c == ':':
			self.pos += 1
			return Token(token_type=TokenType.COLON, value=0)
		if c == '.':
			self.pos += 1
			return Token(token_type=TokenType.DOT, value=0)
		if c == ';':
			self.pos += 1
			return Token(token_type=TokenType.SEMI, value=0)
		if c == ',':
			self.pos += 1
			return Token(token_type=TokenType.COMMA, value=0)
		if c == '+':
			self.pos += 1
			return Token(token_type=TokenType.ADD, value=0)
		if c == '-':
			self.pos += 1
			return Token(token_type=TokenType.SUBTRACT, value=0)
		if c == '*':
			self.pos += 1
			return Token(token_type=TokenType.MULTIPLY, value=0)
		if c == '/':
			self.pos += 1
			return Token(token_type=TokenType.DIVIDE, value=0)
		if c == '(':
			self.pos += 1
			return Token(token_type=TokenType.LPAREN, value=0)
		if c == ')':
			self.pos += 1
			return Token(token_type=TokenType.RPAREN, value=0)
		if c == '{':
			self.pos += 1
			while self.pos_valid() and self.text[self.pos] != '}': self.pos += 1
			self.pos += 1
			return self._next_token()
		if c.isspace():
			while self.pos_valid() and self.text[self.pos].isspace(): self.pos += 1
			return self._next_token()
		
		raise SyntaxError(f"unhandled character in lexer: {c}")
