class Symbol:
	def __init__(self, name: str, type_symbol: 'BuiltinTypeSymbol' = None):
		self.name: str = name
		self.type_symbol: BuiltinTypeSymbol = type_symbol
	
	def __str__(self):
		class_name = self.__class__.__name__
		if self.type_symbol:
			return f'{class_name}({self.name}|{self.type_symbol.name})'
		else:
			return f'{class_name}({self.name}|None)'
	
	def __repr__(self):
		return self.__str__()


class BuiltinTypeSymbol(Symbol):
	def __init__(self, name: str):
		super().__init__(name=name)


class VarSymbol(Symbol):
	def __init__(self, name: str, type_symbol: BuiltinTypeSymbol):
		super().__init__(name=name, type_symbol=type_symbol)


class ProcedureSymbol(Symbol):
	def __init__(self, name: str, params: list[VarSymbol]):
		super().__init__(name=name)
		self.params: list[VarSymbol] = params
	
	def __str__(self):
		class_name = self.__class__.__name__
		return f'{class_name}({self.name}|None [{' '.join(str(p) for p in self.params)}])'


class SymbolTable:
	def __init__(self, scope_name: str, scope_level: int, enclosing_scope: 'SymbolTable'):
		self.symbols: dict[str, Symbol] = {}
		self.scope_name = scope_name
		self.scope_level = scope_level
		self.enclosing_scope: SymbolTable = enclosing_scope
		if self.scope_level == 1: self.add_builtins()
	
	def add_builtins(self):
		self.add(symbol=BuiltinTypeSymbol(name="integer"))
		self.add(symbol=BuiltinTypeSymbol(name="real"))
	
	def __str__(self):
		return (
				f"{self.scope_name}@{self.scope_level}.{self.enclosing_scope and self.enclosing_scope.scope_name}: \n"
				+ ''.join([f'{v}\n' for k, v in self.symbols.items()])
		)
	
	def __repr__(self):
		return self.__str__()
	
	def machine_name(self):
		enclosing_name = (
				self.enclosing_scope
				and self.enclosing_scope.scope_name
				or None
		)
		return f"{self.scope_name}@{self.scope_level}.{enclosing_name}"
	
	def add(self, symbol: Symbol):
		self.symbols[symbol.name] = symbol
	
	def lookup(self, name: str) -> Symbol:
		s = self.symbols.get(name, None)
		if s: return s
		if self.enclosing_scope: return self.enclosing_scope.lookup(name)
		return s
	
	def local_lookup(self, name: str) -> Symbol:
		return self.symbols.get(name, None)
