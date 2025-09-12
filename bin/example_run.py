
from cognitive_core.llm.provider import get_provider
from cognitive_core.llm.provider_wrapper import ProviderWrapper
p = get_provider()
w = ProviderWrapper(p)
print(w.run('Hello world', client_id='localtest'))
