from lexer import TokenType

from syntax_tree import (
	NodeVisitor,
	Program,
	Block,
	VariableDeclaration,
	Procedure,
	Variable,
	Type,
	Compound,
	AssignmentStatement,
	BinOp,
	Num,
	Unary,
	NoOp
)

from symbols import (
	SymbolTable,
	VarSymbol,
	BuiltinTypeSymbol
)


class Interpreter(NodeVisitor):
	def __init__(self):
		self.state: dict[str, int] = {}
	
	def interpret(self, program_node: Program):
		self.visit(node=program_node)
		print(self.state)
	
	def visit_program(self, program: Program):
		return self.visit(node=program.block_node)
	
	def visit_block(self, block: Block):
		for node in block.declarations:
			self.visit(node)
		return self.visit(node=block.compound)
	
	def visit_variable_declaration(self, variable_declaration: VariableDeclaration):
		built_in_symbol = self.visit(variable_declaration.type_node)
		var_symbol = VarSymbol(
			name=variable_declaration.var_node.token.value,
			type_symbol=built_in_symbol
		)
		
	def visit_type(self, type_node: Type) -> BuiltinTypeSymbol:
		raise Exception(
			f"undefined symbol "
			f"builtin for {type_node.token.token_type}"
		)
	
	def visit_procedure(self, procedure: Procedure):
		print('visiting procedure')
		pass
	
	def visit_compound(self, compound: Compound):
		for node in compound.children:
			self.visit(node=node)
	
	def visit_assignment_statement(self, assignment_statement: AssignmentStatement):
		variable_name = assignment_statement.variable.token.value
		variable_val = self.visit(node=assignment_statement.expr)
		self.state[variable_name] = variable_val
	
	def visit_bin_op(self, bin_op_node: BinOp) -> int:
		match bin_op_node.op.token_type:
			case TokenType.ADD:
				return self.visit(bin_op_node.left) + self.visit(bin_op_node.right)
			case TokenType.SUBTRACT:
				return self.visit(bin_op_node.left) - self.visit(bin_op_node.right)
			case TokenType.MULTIPLY:
				return self.visit(bin_op_node.left) * self.visit(bin_op_node.right)
			case TokenType.DIVIDE:
				return self.visit(bin_op_node.left) / self.visit(bin_op_node.right)
			case TokenType.INT_DIVIDE:
				return self.visit(bin_op_node.left) // self.visit(bin_op_node.right)
	
	def visit_variable(self, variable: Variable) -> int:
		var_name = variable.token.value
		val = self.state.get(var_name)
		if not val: raise NameError(var_name)
		return val
	
	def visit_unary(self, unary: Unary) -> int:
		if unary.token.token_type == TokenType.ADD:
			return +self.visit(unary.expr)
		if unary.token.token_type == TokenType.SUBTRACT:
			return -self.visit(unary.expr)
	
	def visit_num(self, num: Num) -> int:
		return num.value
	
	def visit_noop(self, noop: NoOp):
		print(noop.node_type)
