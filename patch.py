import re

def patch_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Add knowledge_base.js
    if '<script src="knowledge_base.js"></script>' not in content:
        content = content.replace('<title>Gavel — Justice for All</title>',
                                  '<title>Gavel — Justice for All</title>\n  <script src="knowledge_base.js"></script>')

    # 2. Remove API Keys
    content = re.sub(r"const WIT_AI_TOKEN = '.*?';\n\s*const GEMINI_API_KEY = '.*?';.*?\n", 
                     "// API keys removed for offline mode\n", 
                     content)

    # 3. Replace the try-catch block inside sendMessage
    pattern = re.compile(r'(const typing = appendTyping\(\);\s*)try \{.*?Connection error.*?\}\s*\}', re.DOTALL)
    
    offline_logic = r"""try {
        // --- OFFLINE KNOWLEDGE BASE MATCHING ---
        const userText = text.toLowerCase().replace(/[^\w\s]/g, '');
        const userWords = new Set(userText.split(/\s+/).filter(w => w.length > 2));
        
        let bestMatch = null;
        let highestScore = 0;

        if (typeof gavelKnowledgeBase !== 'undefined') {
          for (const item of gavelKnowledgeBase) {
            const qText = (item.title + " " + item.question).toLowerCase().replace(/[^\w\s]/g, '');
            const qWords = new Set(qText.split(/\s+/).filter(w => w.length > 2));
            
            let matchCount = 0;
            for (const word of userWords) {
              if (qWords.has(word)) matchCount++;
            }
            
            const score = matchCount / Math.max(userWords.size, 1);
            
            if (score > highestScore) {
              highestScore = score;
              bestMatch = item;
            }
          }
        }
        
        let reply;
        if (bestMatch && highestScore > 0.15) {
          reply = bestMatch.answer + "\n\n*Note: This is not a final legal answer and there might be errors. Please consult a legal advisor.*";
        } else {
          reply = "I cannot answer it right now.";
        }

        setTimeout(() => {
          typing.remove();
          appendBubble('ai', 'Gavel AI', reply);
          chatHistory.push({ role: 'assistant', content: reply });
        }, 800);

      } catch (err) {
        typing.remove();
        console.error(err);
        appendBubble('ai', 'Gavel AI', 'I encountered an error.');
      }
    }"""
    
    match = pattern.search(content)
    if match:
        # replace manually to avoid escape sequence issues
        content = content[:match.start()] + match.group(1) + offline_logic + content[match.end():]
        print("Patched try-catch block.")
    else:
        print("Regex match for try-catch block failed.")

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Patched gavel_app.html successfully.")

patch_file('gavel_app.html')
