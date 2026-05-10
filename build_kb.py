import re
import json

def parse_library(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Matches "1. Title\n   Question text"
    pattern = re.compile(r'^(\d+)\.\s+(.*?)\n\s+([^\n]+)', re.MULTILINE)
    matches = pattern.findall(content)
    
    library = {}
    for num, title, question in matches:
        library[int(num)] = {
            'title': title.strip(),
            'question': question.strip()
        }
    return library

def parse_answers(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Matches "## 1. Title\n\nAnswer text" until the next "## "
    parts = re.split(r'^##\s+(\d+)\.\s+.*?\n', content, flags=re.MULTILINE)
    
    answers = {}
    for i in range(1, len(parts), 2):
        num = int(parts[i])
        answer_text = parts[i+1].strip()
        answers[num] = answer_text
        
    return answers

def main():
    library = parse_library('prompt_library.txt')
    answers = parse_answers('prompt_answers.txt')
    
    kb = []
    for num in sorted(library.keys()):
        if num in answers:
            kb.append({
                'id': num,
                'title': library[num]['title'],
                'question': library[num]['question'],
                'answer': answers[num]
            })
        else:
            print(f"Warning: No answer found for item {num}")
            
    js_content = f"const gavelKnowledgeBase = {json.dumps(kb, indent=2, ensure_ascii=False)};\n"
    
    with open('knowledge_base.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
        
    print(f"Successfully generated knowledge_base.js with {len(kb)} items.")

if __name__ == "__main__":
    main()
