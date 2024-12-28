import sys
import traceback
from parser import Parser
from semantic_analyzer  import SemanticAnalyzer
from interpreter import Interpreter


def main():
	try:
		filename = sys.argv[1]
		fp = open(filename)
		text = fp.read()
		fp.close()
		
		p = Parser(text=text)
		i = Interpreter()
		s = SemanticAnalyzer()
		
		program_node = p.parse()
		s.analyze(program_node=program_node)
		print('passed symantic analysis')
		exit()
		i.interpret(program_node=program_node)
	except Exception as e:
		print(traceback.print_exc())
		print(f"error: {type(e).__name__} {str(e)}")
		exit()


main()
