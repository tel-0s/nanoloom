import readline

def rlinput(prompt, prefill=''):
   readline.set_startup_hook(lambda: readline.insert_text(prefill))
   try:
      return input(prompt)
   finally:
      readline.set_startup_hook()

def to_dict(obj):
   """Recursive conversion of classes to dictionaries"""
   if hasattr(obj, '__dict__'):
      return {key: to_dict(value) for key, value in obj.__dict__.items()}
   elif isinstance(obj, list):
      return [to_dict(item) for item in obj]
   else:
      return obj