import re

# Use EXACT test input
text = 'Head of Business DevelopmentWorld Vision AustraliaMelbourneSenior - Senior level'

# Simulate remove_level_indicators
pattern = r'\s*(Senior\s*-?\s*Senior\s*level|Junior\s*-?\s*Junior\s*level|Mid\s*-?\s*Mid\s*level|Internship|Contract.*|Consultant|Temporary|Pattern.*|GS-\d+.*|P[2-5].*|No.*education.*|Level.*\d+.*|Director General|Adviser|Expert).*$'
text = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
print('After level removal:', repr(text))
print()

# Trace through character by character
print('Character-by-character analysis:')
for i, char in enumerate(text):
    if i > 0 and text[i-1].islower() and char.isupper():
        print('Position', i, ': CASE TRANSITION from', repr(text[i-1]), 'to', repr(char))

print()
print('Expected splits around transitions...')

# Now do the actual split
parts = []
current = []
for i, char in enumerate(text):
    if i > 0 and text[i-1].islower() and char.isupper():
        print('Splitting at position', i, ':before=[' + ''.join(current) + '], after=[' + char + ']')
        if current:
            parts.append(''.join(current))
            current = [char]
        else:
            current.append(char)
    else:
        current.append(char)
if current:
    parts.append(''.join(current))

parts = [p.strip() for p in parts if p.strip()]
print()
print('Parts after split:', parts)
print('Num parts:', len(parts))

