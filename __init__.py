__all__: list[str] = []

# Prevent duplicate module imports under both 'FinAsis.<app>' and '<app>'.
# This ensures Django apps aren't registered twice during tests and runtime.
import sys
import importlib

def _alias_module(short_name: str, long_name: str) -> None:
	try:
		if long_name in sys.modules:
			sys.modules.setdefault(short_name, sys.modules[long_name])
		elif short_name in sys.modules:
			sys.modules.setdefault(long_name, sys.modules[short_name])
		else:
			# Prefer importing the fully-qualified path first
			try:
				mod = importlib.import_module(long_name)
				sys.modules.setdefault(short_name, mod)
			except Exception:
				mod = importlib.import_module(short_name)
				sys.modules.setdefault(long_name, mod)
	except Exception:
		# Best-effort aliasing; never block imports
		pass

_APPS = [
	'accounting', 'accounts', 'advisors', 'ai_assistant', 'audit', 'billing',
	'blockchain', 'common', 'core_ui', 'corporate', 'education', 'finance',
	'integrator_gib', 'integrator_mock', 'kobi_analysis', 'locale', 'management',
	'permissions', 'developer_portal', 'partners', 'security', 'submissions',
	'tenancy', 'virtual_company', 'games'
]

for app in _APPS:
	_alias_module(app, f'FinAsis.{app}')
	# Alias common subpackages we import directly
	if app == 'games':
		for sub in ('game_app', 'ticaretin_izinde', 'trade_sim', 'finquest'):
			_alias_module(f'{app}.{sub}', f'FinAsis.{app}.{sub}')
	if app == 'finance':
		_alias_module('finance.accounting', 'FinAsis.finance.accounting')

