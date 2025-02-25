#!/usr/bin/env python3
"""
Utility script to fix the lambda function parameter signature in test_necromunda.py
"""

import re

def main():
    # Read the file content
    with open('test_necromunda.py', 'r') as f:
        content = f.read()
    
    # Replace all instances of lambda *args with lambda attacker, defender
    pattern = r'self\.game_logic\._get_target_cover_status = lambda \*args: "none"'
    replacement = 'self.game_logic._get_target_cover_status = lambda attacker, defender: "none"'
    modified_content = re.sub(pattern, replacement, content)
    
    # Write the changes back to the file
    with open('test_necromunda.py', 'w') as f:
        f.write(modified_content)
    
    print("Successfully updated all lambda function signatures in test_necromunda.py")

if __name__ == "__main__":
    main()