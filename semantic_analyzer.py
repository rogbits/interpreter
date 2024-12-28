import typing

from lexer import TokenType

from symbols import (
	BuiltinTypeSymbol,
	VarSymbol,
	ProcedureSymbol,
	SymbolTable
)

from syntax_tree import (
	NodeVisitor,
	Program,
	Block,
	VariableDeclaration,
	Variable,
	Type,
	Procedure,
	Compound,
	AssignmentStatement,
	BinOp,
	Unary,
	Num,
	NoOp,
)


class SemanticAnalyzer(NodeVisitor):
	def __init__(self):
		self.current_scope: SymbolTable | None = None
	
	def analyze(self, program_node: Program):
		self.visit(node=program_node)
	
	def visit_program(self, program_node: Program):
		self.current_scope = SymbolTable(
			scope_name='global',
			scope_level=1,
			enclosing_scope=self.current_scope
		)
		self.visit(node=program_node.block_node)
		print(self.current_scope)
		self.current_scope = self.current_scope.enclosing_scope
	
	def visit_block(self, block_node: Block):
		for node in block_node.declarations: self.visit(node=node)
		self.visit(node=block_node.compound)
	
	def visit_variable_declaration(
			self,
			variable_declaration: VariableDeclaration):
		type_symbol = self.visit(variable_declaration.type_node)
		variable_name = variable_declaration.var_node.token.value
		var_symbol = VarSymbol(
			name=variable_name,
			type_symbol=type_symbol
		)
		existing = self.current_scope.local_lookup(variable_name)
		if existing:
			raise Exception(f"error: duplicate identifier {variable_name} in {self.current_scope.machine_name()}")
		self.current_scope.add(var_symbol)
	
	def visit_type(self, type_node: Type):
		if type_node.token.token_type == TokenType.INTEGER_TYPE:
			return self.current_scope.lookup('integer')
		if type_node.token.token_type == TokenType.REAL_TYPE:
			return self.current_scope.lookup('real')
		raise Exception(
			f"undefined symbol "
			f"builtin for {type_node.token.token_type}"
		)
	
	def visit_procedure(self, procedure: Procedure):
		procedure_name = procedure.name
		procedure_symbol = ProcedureSymbol(name=procedure_name, params=[])
		self.current_scope.add(procedure_symbol)
		self.current_scope = SymbolTable(
			scope_name=procedure.name,
			scope_level=self.current_scope.scope_level + 1,
			enclosing_scope=self.current_scope
		)
		for param in procedure.params:
			type_symbol = self.current_scope.lookup(name=param.type_node.token.token_type.value)
			type_symbol = typing.cast(BuiltinTypeSymbol, type_symbol)
			var_symbol = VarSymbol(
				name=param.var_node.token.value,
				type_symbol=type_symbol
			)
			self.current_scope.add(symbol=var_symbol)
			procedure_symbol.params.append(var_symbol)
		
		self.visit(procedure.block_node)
		print(self.current_scope)
		self.current_scope = self.current_scope.enclosing_scope
	
	def visit_compound(self, compound_node: Compound):
		for node in compound_node.children:
			self.visit(node=node)
	
	def visit_assignment_statement(self, assignment_statement: AssignmentStatement):
		var_name = assignment_statement.variable.token.value
		symbol = self.current_scope.lookup(name=var_name)
		if symbol is None:
			raise NameError(var_name)
		self.visit(node=assignment_statement.expr)
	
	def visit_bin_op(self, bin_op_node: BinOp):
		self.visit(bin_op_node.left)
		self.visit(bin_op_node.right)
	
	def visit_variable(self, variable_node: Variable):
		var_name = variable_node.token.value
		symbol = self.current_scope.lookup(name=var_name)
		if symbol is None:
			raise NameError(f"{var_name} in {self.current_scope.scope_name}@{self.current_scope.scope_level}")
	
	def visit_unary(self, unary: Unary):
		self.visit(unary.expr)
	
	def visit_noop(self, noop_node: NoOp):
		pass
