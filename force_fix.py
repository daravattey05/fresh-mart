import os

file_path = r'c:\Users\Davith\Downloads\05-ogani-master\ogani-master\templates\shop-details.html'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip_next = False
for i, line in enumerate(lines):
    if skip_next:
        skip_next = False
        continue
    
    # Identify the split line
    if 'data-baseprice' in line and '{{' in line and not '}}' in line:
        # Assuming the next line completes it
        next_line = lines[i+1]
        combined = line.strip() + ' ' + next_line.strip()
        # Clean up the specific tag
        combined = combined.replace('{{ product.price|floatformat:2 }}', '{{ product.price|floatformat:2 }}') 
        # Actually just ensure it's one line
        # Reconstruct the expected line
        combined = '                    <div class="product__details__price" data-baseprice="{{ product.price }}">$<span>{{ product.price|floatformat:2 }}</span></div>\n'
        new_lines.append(combined)
        skip_next = True
    elif 'data-baseprice' in line and 'product.price|floatformat:2' in line:
         # It's already correct?
         new_lines.append(line)
    else:
        new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Rewrite complete.")

# Verify
with open(file_path, 'r', encoding='utf-8') as f:
    final_content = f.read()
    if '<span>{{ product.price|floatformat:2 }}</span>' in final_content:
        print("VERIFICATION: SUCCESS - Single line found.")
    else:
        print("VERIFICATION: FAILED - Single line not found.")
