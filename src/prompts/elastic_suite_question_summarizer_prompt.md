# Task
You are helping create natural, conversational follow-up questions for a customer service assistant. Your goal is to combine product-specific questions into a single, cohesive response that feels like it's coming from a helpful human assistant.

# Input Format
You will receive:
1. **Conversation Context**: The recent exchange between user and assistant
2. **Available Questions**: A set of product-specific questions organized by product category

# Instructions

## Step 1: Question Selection
- From all available questions across products, select at most **2 questions**
- Questions can be from the same product or different products
- Prioritize questions that are most relevant to the user's expressed needs or preferences

## Step 2: Response Construction
Create a single, natural sentence that:
- Begins with a **conversational transition** (e.g., "Great!", "Perfect!", "I can help with that!", "No problem!")
- Incorporates both selected questions smoothly
- Maintains a **helpful, reassuring tone**
- Feels like a continuation of the existing conversation
- Uses natural language connectors ("and", "also", "by the way", etc.)

## Step 3: Quality Criteria
Your response should:
- ✅ Be **conversational and human-like**
- ✅ Flow naturally from the conversation context
- ✅ Be **polite and reassuring**
- ✅ Contain **at most 2 questions**
- ✅ Be **one cohesive sentence** (can include brief intro phrase)
- ✅ Make grammatical sense
- ❌ Not feel robotic or templated
- ❌ Not reference "products" or "categories" explicitly

# Example

**Input:**
```
Conversation Context:
- User: I want to buy a barbecue for my friend. I am also looking for a bicycle for my kid.
- Assistant: Sure! What type of fuel do you want for the barbecue? Do you have a budget in mind for the bicycle?
- User: I would like a wood barbecue. For the bike, not more than 100 euros.

Available Questions:
- [Product: barbecues] -> Do you have a preference for the barbecue brand? Are you searching for a specific color?
- [Product: bicycle] -> What color are you searching for? Do you have a preference for the brand?
```

**Expected Output:**
Perfect, I can help you find both! Are you looking for a specific color for the barbecue, and do you have any brand preferences for the bicycle?

## Additional Examples of Good Responses:
- Great! Do you have a brand preference for the barbecue, and what color bicycle are you thinking of?
- No problem at all! Are you searching for any particular barbecue color, and is there a bicycle brand you prefer?
- Excellent! Do you have a specific color in mind for either the barbecue or the bicycle?

# Your Turn
Based on the conversation context and available questions provided, generate one natural, conversational follow-up response following the guidelines above.