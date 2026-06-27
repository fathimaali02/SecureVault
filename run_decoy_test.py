import importlib.util
import sys
from pathlib import Path

# Load main.py as a module without executing its __main__ block
spec = importlib.util.spec_from_file_location('svmodule', 'main.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

# Create decoy vault (should write honeytrap files using UTF-8)
vault_path = Path('secure_vault_test')
mod.DecoyVault(str(vault_path))
print('DecoyVault created at', vault_path.resolve())
