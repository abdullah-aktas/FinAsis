__all__: list[str] = []

# Prevent duplicate module imports under both 'FinAsis.<app>' and '<app>'.
# This ensures Django apps aren't registered twice during tests and runtime.
# NOTE: This aliasing can cause model conflicts in test environments.
# Only alias if not in test mode to prevent "Conflicting models" errors.
import sys
import importlib
import os

# Skip aliasing in test environments to prevent model conflicts
_is_test = (
    'test' in sys.argv or
    'pytest' in sys.modules or
    os.environ.get('DJANGO_TEST_MODE') == '1' or
    'unittest' in sys.modules
)

def _alias_module(short_name: str, long_name: str) -> None:
	"""Alias module only if not in test mode to prevent model conflicts."""
	if _is_test:
		return  # Skip aliasing in test mode
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

if not _is_test:
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

