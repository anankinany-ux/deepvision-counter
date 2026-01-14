# Code Protection & Licensing Guide
## Customer Counter Pro - Security Implementation

This guide covers implementing licensing, code protection, and anti-piracy measures.

## Table of Contents
1. [License Key System](#license-key-system)
2. [Hardware Fingerprinting](#hardware-fingerprinting)
3. [Trial Period](#trial-period)
4. [Code Obfuscation](#code-obfuscation)
5. [Anti-Piracy Measures](#anti-piracy-measures)

---

## 1. License Key System

### Implementation Strategy

**Option A: Simple License Keys**
```python
import hashlib
import uuid

class LicenseValidator:
    def __init__(self):
        self.secret_key = "YOUR-SECRET-KEY-HERE"
    
    def generate_license(self, customer_id, expiry_date=None):
        """Generate a license key for a customer"""
        data = f"{customer_id}{self.secret_key}"
        if expiry_date:
            data += expiry_date
        
        hash_object = hashlib.sha256(data.encode())
        license_key = hash_object.hexdigest()[:24].upper()
        
        # Format: XXXX-XXXX-XXXX-XXXX-XXXX-XXXX
        formatted = '-'.join([license_key[i:i+4] for i in range(0, 24, 4)])
        return formatted
    
    def validate_license(self, license_key, customer_id):
        """Validate a license key"""
        expected = self.generate_license(customer_id)
        return license_key == expected
```

**Option B: Cloud-based Licensing (Recommended for Commercial)**
- Use services like:
  - Gumroad (https://gumroad.com) - Easy setup, handles payments
  - Paddle (https://paddle.com) - Professional, all-in-one
  - LemonSqueezy (https://lemonsqueezy.com) - Modern, developer-friendly
  - License Spring (https://licensespring.com) - Dedicated licensing platform

### Integration Steps
1. Add license check at app startup
2. Store encrypted license locally
3. Validate on each launch
4. Handle expired/invalid licenses gracefully

---

## 2. Hardware Fingerprinting

Prevent license sharing by tying licenses to specific machines:

```python
import uuid
import platform
import hashlib

def get_hardware_id():
    """Generate unique hardware fingerprint"""
    # Get MAC address
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                    for ele in range(0,8*6,8)][::-1])
    
    # Get machine info
    machine_info = f"{platform.node()}{mac}{platform.machine()}"
    
    # Generate hash
    hardware_id = hashlib.sha256(machine_info.encode()).hexdigest()[:16]
    return hardware_id.upper()

def bind_license_to_hardware(license_key):
    """Bind license to current hardware"""
    hardware_id = get_hardware_id()
    bound_key = f"{license_key}:{hardware_id}"
    
    # Store encrypted version locally
    with open('.license', 'w') as f:
        f.write(bound_key)
    
    return True
```

**Note:** Allow 2-3 activations per license for legitimate hardware changes.

---

## 3. Trial Period

Implement a 30-day trial:

```python
from datetime import datetime, timedelta
import json
import os

TRIAL_FILE = '.trial_data'
TRIAL_DAYS = 30

def check_trial_status():
    """Check if trial is valid"""
    if not os.path.exists(TRIAL_FILE):
        # First run - create trial
        start_date = datetime.now()
        trial_data = {
            'start_date': start_date.isoformat(),
            'hardware_id': get_hardware_id()
        }
        with open(TRIAL_FILE, 'w') as f:
            json.dump(trial_data, f)
        return True, TRIAL_DAYS
    
    # Load trial data
    with open(TRIAL_FILE, 'r') as f:
        trial_data = json.load(f)
    
    # Verify hardware (prevent trial reset by copying file)
    if trial_data.get('hardware_id') != get_hardware_id():
        return False, 0
    
    # Check expiry
    start_date = datetime.fromisoformat(trial_data['start_date'])
    days_elapsed = (datetime.now() - start_date).days
    days_remaining = TRIAL_DAYS - days_elapsed
    
    if days_remaining > 0:
        return True, days_remaining
    else:
        return False, 0

def show_trial_dialog(days_remaining):
    """Show trial status to user"""
    if days_remaining > 0:
        message = f"Trial: {days_remaining} days remaining"
    else:
        message = "Trial expired! Please purchase a license."
    return message
```

---

## 4. Code Obfuscation

Protect source code from reverse engineering:

### Using PyArmor (Recommended)

```bash
# Install PyArmor
pip install pyarmor

# Obfuscate the code
pyarmor obfuscate --restrict=1 counter_modern.py

# Build with obfuscated code
pyinstaller --onefile dist/counter_modern.py
```

### Using Cython (Compile to C)

```bash
# Install Cython
pip install cython

# Create setup.py
cat > setup.py << 'EOF'
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize("counter_modern.py",
                          compiler_directives={'language_level': "3"})
)
EOF

# Build
python setup.py build_ext --inplace
```

### Additional Protection Layers
1. **Strip debug symbols**: `strip` command (Unix) or UPX packer
2. **Encrypt strings**: Use base64 or custom encryption for sensitive strings
3. **Anti-debugging**: Add checks for debugger attachment
4. **Integrity checks**: Verify code hasn't been modified

---

## 5. Anti-Piracy Measures

### Server-side Validation (Best Practice)

```python
import requests
import hashlib

def validate_license_online(license_key):
    """Validate license with your server"""
    try:
        response = requests.post(
            'https://your-api.com/validate',
            json={
                'license_key': license_key,
                'hardware_id': get_hardware_id(),
                'app_version': '1.0.0'
            },
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get('valid', False)
    except:
        # Offline mode - validate locally
        return validate_license_locally(license_key)
    
    return False
```

### Periodic Validation
- Check license every 7 days
- Allow offline grace period (30 days)
- Prompt user to connect to internet

### Monitoring & Analytics
- Track activations per license
- Detect unusual patterns (multiple IPs, rapid activations)
- Implement usage analytics (with user consent)

---

## Implementation Checklist

- [ ] Choose licensing system (cloud vs. self-hosted)
- [ ] Implement license key generation
- [ ] Add hardware fingerprinting
- [ ] Create trial period mechanism
- [ ] Obfuscate code with PyArmor or Cython
- [ ] Add server-side validation (optional but recommended)
- [ ] Create license activation UI
- [ ] Test on multiple machines
- [ ] Set up license management dashboard
- [ ] Create license recovery process
- [ ] Document licensing for customers

---

## Legal Considerations

1. **EULA (End User License Agreement)**
   - Define usage rights
   - Limit liability
   - Specify refund policy

2. **Privacy Policy**
   - Disclose data collection (hardware ID, usage stats)
   - Comply with GDPR/CCPA if applicable

3. **Terms of Service**
   - Define acceptable use
   - Prohibit reverse engineering
   - Specify termination conditions

---

## Recommended Services

### For Solo Developers / Small Teams:
- **Gumroad**: Easiest to start, 10% + payment fees
- **LemonSqueezy**: Modern, dev-friendly, 5% + payment fees

### For Professional/Enterprise:
- **Paddle**: Full merchant of record, handles VAT/taxes
- **License Spring**: Dedicated licensing, complex scenarios

### Self-Hosted (Advanced):
- **Cryptolens**: .NET-based licensing API
- **Custom solution**: Full control, more work

---

## Next Steps

1. Review the DEPLOYMENT_GUIDE.md for distribution setup
2. Test licensing on clean machines
3. Set up payment processing
4. Create customer support workflow

