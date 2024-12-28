from typing import Union
from lexer import Token


class Node:
	def __init__(self, node_type: str):
		self.node_type: str = node_type


class NodeVisitor:
	def visit(self, node: Node):
		node_type = node.node_type
		visit_method = getattr(self, f'visit_{node_type}')
		return visit_method(node)


class Program(Node):
	def __init__(self, name: str, block_node: 'Block'):
		super().__init__(node_type='program')
		self.name: str = name
		self.block_node: Block = block_node


class Block(Node):
	def __init__(self, declarations: list[Union['VariableDeclaration', 'Procedure']], compound_node: 'Compound'):
		super().__init__(node_type='block')
		self.declarations: list[VariableDeclaration | Procedure] = declarations
		self.compound: Compound = compound_node


class VariableDeclaration(Node):
	def __init__(self, var_node: 'Variable', type_node: 'Type'):
		super().__init__(node_type='variable_declaration')
		self.var_node = var_node
		self.type_node = type_node


class Procedure(Node):
	def __init__(self, name: str, params: list['Param'], block_node: 'Block'):
		super().__init__(node_type='procedure')
		self.name: str = name
		self.params: list[Param] = params
		self.block_node: Block = block_node


class Param(Node):
	def __init__(self, var_node: 'Variable', type_node: 'Type'):
		super().__init__(node_type='param')
		self.var_node = var_node
		self.type_node = type_node


class Variable(Node):
	def __init__(self, token: Token):
		super().__init__(node_type='variable')
		self.token: Token = token


class Type(Node):
	def __init__(self, token: Token):
		super().__init__(node_type='type')
		self.token: Token = token


class Compound(Node):
	def __init__(self):
		super().__init__(node_type='compound')
		self.children: list[Node] = []
	
	def add_child(self, node: Node):
		self.children.append(node)


class AssignmentStatement(Node):
	def __init__(self, variable: 'Variable', expr: Node):
		super().__init__(node_type='assignment_statement')
		self.variable: Variable = variable
		self.expr: Node = expr


class BinOp(Node):
	def __init__(self, left: Node, op: Token, right: Node):
		super().__init__(node_type='bin_op')
		self.left: Node = left
		self.op: Token = op
		self.right: Node = right


class Unary(Node):
	def __init__(self, token: Token, expr: Node):
		super().__init__(node_type='unary')
		self.token: Token = token
		self.expr: Node = expr


class Num(Node):
	def __init__(self, token: Token):
		super().__init__(node_type='num')
		self.token: Token = token
		self.value: int = token.value


class NoOp(Node):
	def __init__(self):
		super().__init__(node_type='noop')
