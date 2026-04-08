from src.utils.job_parser import JobTextParser

text = 'Head of Business DevelopmentWorld Vision AustraliaMelbourneSenior - Senior level'
result = JobTextParser.extract_components(text)
print(f'Title: {result["title"]}')  
print(f'Org: {result["organization"]}')
print(f'Location: {result["location"]}')

# Debug the parts splitting
text2 = 'Head of Business DevelopmentWorld Vision AustraliaMelbourne'
parts = []
current = []
for i, char in enumerate(text2):
    if i > 0 and text2[i-1].islower() and char.isupper():
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
print(f'Parts after split: {parts}')
print(f'Num parts: {len(parts)}')
