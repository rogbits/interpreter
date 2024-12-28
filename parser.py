from lexer import (
	Token,
	Lexer,
	TokenType
)

from syntax_tree import (
	Node,
	Program,
	Procedure,
	Param,
	Block,
	VariableDeclaration,
	Variable,
	Type,
	Compound,
	AssignmentStatement,
	BinOp,
	Unary,
	Num,
	NoOp,
)


class Parser:
	def __init__(self, text: str):
		self.text: str = text
		self.lexer: Lexer = Lexer(text=text)
		self.ct: Token = self.lexer.next_token()
	
	def parse(self) -> Program:
		return self.prog()
	
	def prog(self) -> Program:
		"""
		program: PROGRAM id SEMI block
		"""
		self.eat(self.ct, token_types=[TokenType.PROGRAM])
		program_name = self.ct.value
		self.eat(self.ct, token_types=[TokenType.ID])
		self.eat(self.ct, token_types=[TokenType.SEMI])
		block_node = self.block()
		program_node = Program(name=program_name, block_node=block_node)
		self.eat(self.ct, token_types=[TokenType.DOT])
		return program_node
	
	def block(self) -> Block:
		"""
		block: VAR block_declarations compound_statement
		       | compound_statement
		"""
		if self.ct.token_type == TokenType.VAR:
			self.eat(self.ct, token_types=[TokenType.VAR])
			declarations = self.block_declarations()
			compound_node = self.compound_statement()
			return Block(declarations=declarations, compound_node=compound_node)
		else:
			compound_node = self.compound_statement()
			return Block(declarations=[], compound_node=compound_node)
	
	def block_declarations(self) -> list[VariableDeclaration | Procedure]:
		declarations: list[VariableDeclaration | Procedure] = []
		var_type_list = self.variable_type_list()
		for tup in var_type_list:
			declarations.append(VariableDeclaration(
				var_node=tup[0], type_node=tup[1]))
		while self.ct.token_type == TokenType.PROCEDURE:
			declarations.append(self.procedure())
			self.eat(self.ct, token_types=[TokenType.SEMI])
		return declarations
	
	def variable_type_list(self) -> list[(Variable, Type)]:
		var_type_list: list[(Variable, Type)] = []
		while self.ct.token_type == TokenType.ID:
			variables: list[Variable] = []
			while self.ct.token_type != TokenType.COLON:
				variables.append(self.variable())
				if self.ct.token_type == TokenType.COMMA:
					self.eat(self.ct, token_types=[TokenType.COMMA])
			self.eat(self.ct, token_types=[TokenType.COLON])
			type_node = Type(token=self.ct)
			self.eat(self.ct, token_types=[TokenType.INTEGER_TYPE, TokenType.REAL_TYPE])
			for var_node in variables:
				var_type_list.append((var_node, type_node))
			if self.ct.token_type == TokenType.SEMI:
				self.eat(self.ct, token_types=[TokenType.SEMI])
		return var_type_list
	
	def procedure(self) -> Procedure:
		self.eat(self.ct, token_types=[TokenType.PROCEDURE])
		procedure_name = self.ct.value
		self.eat(self.ct, token_types=[TokenType.ID])
		params = []
		if self.ct.token_type == TokenType.LPAREN:
			params = self.params()
		self.eat(self.ct, token_types=[TokenType.SEMI])
		block_node = self.block()
		return Procedure(
			name=procedure_name,
			params=params,
			block_node=block_node
		)
	
	def params(self) -> list[Param]:
		params: list[Param] = []
		self.eat(self.ct, token_types=[TokenType.LPAREN])
		variable_type_list = self.variable_type_list()
		self.eat(self.ct, token_types=[TokenType.RPAREN])
		for tup in variable_type_list:
			params.append(Param(
				var_node=tup[0],
				type_node=tup[1]
			))
		return params
	
	def compound_statement(self) -> Compound:
		self.eat(self.ct, token_types=[TokenType.BEGIN])
		nodes = self.statement_list()
		self.eat(self.ct, token_types=[TokenType.END])
		cp = Compound()
		for node in nodes: cp.add_child(node)
		return cp
	
	def statement_list(self) -> list[Node]:
		statements: list[Node] = [self.statement()]
		while self.ct.token_type == TokenType.SEMI:
			self.eat(self.ct, [TokenType.SEMI])
			statements.append(self.statement())
		return statements
	
	def statement(self) -> Node:
		if self.ct.token_type == TokenType.BEGIN:
			return self.compound_statement()
		if self.ct.token_type == TokenType.ID:
			return self.assignment_statement()
		return self.empty()
	
	def assignment_statement(self) -> Node:
		variable: Variable = self.variable()
		self.eat(self.ct, [TokenType.ASSIGNMENT])
		expr_node = self.expr()
		return AssignmentStatement(
			variable=variable,
			expr=expr_node
		)
	
	def variable(self) -> Variable:
		token = self.ct
		self.eat(token, [TokenType.ID])
		return Variable(token=token)
	
	def empty(self) -> Node:
		return NoOp()
	
	def expr(self) -> Node:
		return self.term()
	
	def term(self) -> Node:
		node = self.factor()
		while self.ct.token_type in {TokenType.ADD, TokenType.SUBTRACT}:
			op = self.term_op()
			node = BinOp(left=node, op=op, right=self.factor())
		return node
	
	def factor(self) -> Node:
		node = self.paren_expr()
		while self.ct.token_type in {TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.INT_DIVIDE}:
			op = self.factor_op()
			node = BinOp(left=node, op=op, right=self.paren_expr())
		return node
	
	def paren_expr(self) -> Node:
		if self.ct.token_type in {TokenType.ADD, TokenType.SUBTRACT}:
			return self.unary()
		if self.ct.token_type == TokenType.INTEGER_CONST:
			return self.num()
		if self.ct.token_type == TokenType.REAL_CONST:
			return self.num()
		if self.ct.token_type == TokenType.LPAREN:
			self.left_paren()
			result = self.expr()
			self.right_paren()
			return result
		if self.ct.token_type == TokenType.ID:
			return self.variable()
	
	def left_paren(self):
		self.eat(self.ct, [TokenType.LPAREN])
	
	def right_paren(self):
		self.eat(self.ct, [TokenType.RPAREN])
	
	def factor_op(self) -> Token:
		op = self.ct
		self.eat(op, [TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.INT_DIVIDE])
		return op
	
	def term_op(self) -> Token:
		op = self.ct
		self.eat(op, [TokenType.ADD, TokenType.SUBTRACT])
		return op
	
	def num(self) -> Num:
		n = self.ct
		self.eat(n, [TokenType.INTEGER_CONST, TokenType.REAL_CONST])
		return Num(token=n)
	
	def unary(self) -> Unary:
		op = self.ct
		self.eat(op, [TokenType.ADD, TokenType.SUBTRACT])
		return Unary(token=op, expr=self.expr())
	
	def eat(self, token: Token, token_types: list[TokenType]):
		token_type_set = set(token_types)
		if token.token_type not in token_type_set:
			raise SyntaxError(
				f"bad token type {token.token_type}, "
				f"expecting {token_types}"
			)
		self.ct = self.lexer.next_token()
