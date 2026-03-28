"""
Auto-fix suggestions for common vulnerabilities
"""

FIX_SUGGESTIONS = {
    "PY-EVAL": {
        "fix": "Use ast.literal_eval() for safe evaluation of literals, or json.loads() for JSON data",
        "example": """# Bad:
result = eval(user_input)

# Good:
import ast
result = ast.literal_eval(user_input)  # Only evaluates literals (strings, numbers, lists, etc.)

# Or for JSON:
import json
result = json.loads(user_input)"""
    },
    
    "PY-EXEC": {
        "fix": "Avoid exec() entirely. Use specific function calls or configuration-based approach",
        "example": """# Bad:
exec(user_code)

# Good:
# Use a safe evaluation library like RestrictedPython
from RestrictedPython import compile_restricted, safe_globals

code = compile_restricted(user_code, '<string>', 'exec')
exec(code, safe_globals)"""
    },
    
    "PY-SUBPROCESS-SHELL": {
        "fix": "Use shell=False and pass command as a list",
        "example": """# Bad:
subprocess.run(f"ls {user_dir}", shell=True)

# Good:
subprocess.run(["ls", user_dir], shell=False)"""
    },
    
    "PY-OS-SYSTEM": {
        "fix": "Use subprocess.run() with shell=False instead",
        "example": """# Bad:
os.system(f"rm {file_path}")

# Good:
import subprocess
subprocess.run(["rm", file_path], shell=False)"""
    },
    
    "SECRET-ASSIGNMENT": {
        "fix": "Use environment variables or a secrets management service",
        "example": """# Bad:
API_KEY = "sk-1234567890abcdef"

# Good:
import os
API_KEY = os.environ.get("API_KEY")

# Or use python-dotenv:
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("API_KEY")"""
    },
    
    "PRIVATE-KEY-BLOCK": {
        "fix": "NEVER commit private keys to version control. Store in secure vaults.",
        "example": """# Bad:
# Private key in code

# Good:
# 1. Add to .gitignore
# 2. Store in AWS Secrets Manager, HashiCorp Vault, or similar
# 3. Load at runtime:
import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='my-private-key')"""
    },
    
    "PY-SQL-FSTRING": {
        "fix": "Use parameterized queries",
        "example": """# Bad:
query = f"SELECT * FROM users WHERE id={user_id}"
cursor.execute(query)

# Good:
query = "SELECT * FROM users WHERE id=%s"
cursor.execute(query, (user_id,))

# Or with SQLAlchemy:
session.query(User).filter(User.id == user_id)"""
    },
    
    "JS-SQL-CONCAT": {
        "fix": "Use parameterized queries or an ORM",
        "example": """// Bad:
const query = `SELECT * FROM users WHERE id=${userId}`;

// Good (with parameterized queries):
const query = 'SELECT * FROM users WHERE id=?';
db.query(query, [userId]);

// Or with an ORM (Sequelize):
User.findByPk(userId);"""
    },
    
    "JS-INNERHTML": {
        "fix": "Use textContent or a sanitization library",
        "example": """// Bad:
element.innerHTML = userContent;

// Good:
element.textContent = userContent;  // Safe for text

// Or sanitize HTML:
import DOMPurify from 'dompurify';
element.innerHTML = DOMPurify.sanitize(userContent);"""
    },
    
    "PY-WEAK-RANDOM": {
        "fix": "Use secrets module for cryptographic randomness",
        "example": """# Bad:
import random
token = random.randint(0, 999999)

# Good:
import secrets
token = secrets.token_urlsafe(32)  # Cryptographically secure"""
    },
    
    "JS-MATH-RANDOM": {
        "fix": "Use crypto.randomBytes() or crypto.getRandomValues()",
        "example": """// Bad:
const token = Math.random().toString(36);

// Good (Node.js):
const crypto = require('crypto');
const token = crypto.randomBytes(32).toString('hex');

// Good (Browser):
const array = new Uint8Array(32);
crypto.getRandomValues(array);
const token = Array.from(array, b => b.toString(16).padStart(2, '0')).join('');"""
    },
    
    "JWT-VERIFY-OFF": {
        "fix": "Always verify JWT signatures and expiration",
        "example": """# Bad:
payload = jwt.decode(token, verify=False)

# Good:
payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

# JavaScript:
// Bad:
jwt.verify(token, secret, { ignoreExpiration: true });

// Good:
jwt.verify(token, secret);  // Verifies signature AND expiration"""
    },
    
    "DEBUG-TRUE": {
        "fix": "Set DEBUG=False in production, use environment variables",
        "example": """# Bad:
DEBUG = True

# Good:
import os
DEBUG = os.environ.get("DEBUG", "False") == "True"

# Or in Django settings:
DEBUG = os.getenv('DJANGO_DEBUG', 'False') == 'True'"""
    },
    
    "CORS-WILDCARD": {
        "fix": "Specify allowed origins explicitly",
        "example": """# Bad:
Access-Control-Allow-Origin: *

# Good (Flask):
from flask_cors import CORS
CORS(app, resources={r"/api/*": {"origins": ["https://example.com"]}})

# Good (Express):
const cors = require('cors');
app.use(cors({ origin: 'https://example.com' }));"""
    },
    
    "PY-PICKLE": {
        "fix": "Use JSON for data serialization with untrusted sources",
        "example": """# Bad:
import pickle
data = pickle.loads(untrusted_data)

# Good:
import json
data = json.loads(untrusted_data)

# If you need pickle for trusted data, sign it:
import hmac
import hashlib
signature = hmac.new(SECRET_KEY, pickled_data, hashlib.sha256).hexdigest()"""
    },
    
    "PY-YAML-UNSAFE": {
        "fix": "Use yaml.safe_load() instead of yaml.load()",
        "example": """# Bad:
import yaml
data = yaml.load(file)

# Good:
import yaml
data = yaml.safe_load(file)  # Only loads basic Python objects"""
    }
}

def get_fix_suggestion(rule_id):
    """Get fix suggestion for a rule ID"""
    return FIX_SUGGESTIONS.get(rule_id, {
        "fix": "Review and remediate this finding according to security best practices",
        "example": "No specific fix example available for this pattern"
    })
