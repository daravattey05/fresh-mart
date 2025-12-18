import re

file_path = r'c:\Users\Davith\Downloads\05-ogani-master\ogani-master\templates\shop-details.html'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Regex to match the split span tag
# Matches: <span>{{ [whitespace/newlines] product.price|floatformat:2 [whitespace/newlines] }}</span>
pattern = r'<span>\{\{\s+product\.price\|floatformat:2\s+\}\}</span>'

# Replace with single line version
fixed_content = re.sub(pattern, '<span>{{ product.price|floatformat:2 }}</span>', content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(fixed_content)

print("Regex Replace Complete.")

# Verify
if '<span>{{ product.price|floatformat:2 }}</span>' in fixed_content:
    print("VERIFICATION: SUCCESS")
else:
    print("VERIFICATION: FAILED - Could not find single line tag.")
