import enum
import traceback


class TokenType(enum.Enum):
	INTEGER = 'integer'
	ADD = '+'
	SUBTRACT = '-'
	MULTIPLY = '*'
	DIVIDE = '/'
	LPAREN = '('
	RPAREN = ')'
	EOF = 'EOF'


class Token:
	def __init__(self, token_type: TokenType, value: int):
		self.type: TokenType = token_type
		self.value: int = value
		pass
	
	def __str__(self):
		return f"{self.type.name}::{self.value}"
	
	def __repr__(self):
		return self.__str__()


class Tokenizer:
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
		while self.pos_valid() and self.text[self.pos].isspace(): self.pos += 1
		if not self.pos_valid(): return Token(token_type=TokenType.EOF, value=0)
		c = self.text[self.pos]
		if c.isdigit():
			num = ''
			while self.pos_valid() and self.text[self.pos].isdigit():
				num += self.text[self.pos]
				self.pos += 1
			return Token(token_type=TokenType.INTEGER, value=int(num))
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
		raise SyntaxError()


class Node:
	def __init__(self, node_type: str):
		self.type = node_type


class BinOp(Node):
	def __init__(self, left: Node, op: Token, right: Node):
		super().__init__(node_type='bin_op')
		self.left: Node = left
		self.op: Token = op
		self.right: Node = right


class Num(Node):
	def __init__(self, token: Token):
		super().__init__(node_type='num')
		self.token: Token = token
		self.value: int = token.value


class Unary(Node):
	def __init__(self, token: Token, expr: Node):
		super().__init__(node_type='unary')
		self.token: Token = token
		self.expr: Node = expr


class Parser:
	def __init__(self, text: str):
		self.text: str = text
		self.pos: int = 0
		self.tokenizer: Tokenizer = Tokenizer(text=text)
		self.ct: Token = self.tokenizer.next_token()
		self.cn: Node | None = None
	
	def parse(self) -> Node:
		return self.expr()
	
	def expr(self) -> Node:
		return self.term()
	
	def term(self) -> Node:
		node = self.factor()
		while self.ct.type in {TokenType.ADD, TokenType.SUBTRACT}:
			op = self.term_op()
			node = BinOp(left=node, op=op, right=self.factor())
		return node
	
	def factor(self) -> Node:
		node = self.paren_expr()
		while self.ct.type in {TokenType.MULTIPLY, TokenType.DIVIDE}:
			op = self.factor_op()
			node = BinOp(left=node, op=op, right=self.paren_expr())
		return node
	
	def paren_expr(self) -> Node:
		if self.ct.type in {TokenType.ADD, TokenType.SUBTRACT}:
			return self.unary()
		if self.ct.type == TokenType.INTEGER:
			return self.num()
		if self.ct.type == TokenType.LPAREN:
			self.left_paren()
			result = self.expr()
			self.right_paren()
			return result
	
	def left_paren(self):
		self.eat(self.ct, [TokenType.LPAREN])
	
	def right_paren(self):
		self.eat(self.ct, [TokenType.RPAREN])
	
	def factor_op(self) -> Token:
		op = self.ct
		self.eat(op, [TokenType.MULTIPLY, TokenType.DIVIDE])
		return op
	
	def term_op(self) -> Token:
		op = self.ct
		self.eat(op, [TokenType.ADD, TokenType.SUBTRACT])
		return op
	
	def num(self) -> Num:
		n = self.ct
		self.eat(n, [TokenType.INTEGER])
		return Num(token=n)
	
	def unary(self) -> Unary:
		op = self.ct
		self.eat(op, [TokenType.ADD, TokenType.SUBTRACT])
		return Unary(token=op, expr=self.expr())
	
	def eat(self, token: Token, token_types: list[TokenType]):
		token_type_set = set(token_types)
		if token.type not in token_type_set:
			raise SyntaxError(
				f"bad token type {token.type}, "
				f"expecting {token_types}"
			)
		self.ct = self.tokenizer.next_token()


class NodeVisitor:
	def visit(self, node: Node):
		node_type = node.type
		visit_method = getattr(self, f'visit_{node_type}')
		return visit_method(node)


class Interpreter(NodeVisitor):
	def __init__(self, text: str):
		self.parser: Parser = Parser(text=text)
	
	def interpret(self):
		node = self.parser.expr()
		return self.visit(node=node)
	
	def visit_bin_op(self, bin_op_node: BinOp) -> int:
		match bin_op_node.op.type:
			case TokenType.ADD:
				return self.visit(bin_op_node.left) + self.visit(bin_op_node.right)
			case TokenType.SUBTRACT:
				return self.visit(bin_op_node.left) - self.visit(bin_op_node.right)
			case TokenType.MULTIPLY:
				return self.visit(bin_op_node.left) * self.visit(bin_op_node.right)
			case TokenType.DIVIDE:
				return self.visit(bin_op_node.left) / self.visit(bin_op_node.right)
	
	def visit_num(self, num: Num) -> int:
		return num.value
	
	def visit_unary(self, unary: Unary) -> int:
		if unary.token.type == TokenType.ADD:
			return self.visit(unary.expr)
		if unary.token.type == TokenType.SUBTRACT:
			return -self.visit(unary.expr)


def main():
	while True:
		text = ''
		try:
			text = input("calc > ")
		except EOFError:
			exit()
		except KeyboardInterrupt:
			exit()
		if not text:
			continue
		i = Interpreter(text=text)
		try:
			result = i.interpret()
			print(result)
		except Exception as e:
			print(traceback.print_exc())
			print(f"error: {type(e).__name__} {str(e)}")


main()
