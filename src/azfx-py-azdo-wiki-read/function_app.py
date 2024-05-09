import azure.functions as func 
from read_wiki_function import bp as readWikiFunction

app = func.FunctionApp() 

app.register_functions(readWikiFunction) 