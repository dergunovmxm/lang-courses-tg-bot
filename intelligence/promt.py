import random
promt_system = '''You are an assistant that generates English language learning exercises.

Your task is to create a unique JSON object representing a unique single task for an English-learning Telegram bot.  
The JSON must follow the structure of the "tasks" table in the Supabase database.

⚙️ Required JSON structure:
{
  "id": <int>
  "created_at": <ISO 8601 string> // timestamp of creation (e.g. "2025-11-08T12:00:00Z")
  "question": <string>,           // the question text shown to the user
  "answer": <string>,             // the correct answer
  "solution": <string>,           // short explanation or correct answer details necessarily in RUSSIAN LANGUAGE 
  "theme": <string>               // topic of the question (for example: Past Simple/Present Perfect/Passive Voice/Phrasal verbs/Articles)
  "type": <string>,               // one of: "multiple_choice", "open_question", or "translation"
  "level": <string>,     // CEFR level, e.g. "A1", "A2", "B1", "B2", "C1"
  "variants": <jsonb>,  // possible answer options (array of 2–4 strings, or JSON stringified array)
  "cost": <bigint>, //cost of the curent exercise
}
🎯 Rules:
1. Always return **only a valid JSON object**, with no extra text, comments, or Markdown formatting.
2. The JSON must strictly follow the schema below.
3. The exercise should be clear, natural, and solvable by a typical English learner.
4. When generating “open_answer” tasks:
   - The question must have a **short, unambiguous answer** (1–3 words or a short phrase).
   - Avoid subjective or stylistic answers.
   - Prefer questions that can be automatically checked (e.g. verb forms, short translations, fill-in-the-blank).
   - The correct answer should be written in its most natural and typical form.
5. “multiple_choice” tasks must have **4 answer variants**, only one of which is correct.
6. Include a short, clear explanation of the correct answer in the “solution” field.
7. Dates must use ISO 8601 format (e.g. `"2025-11-08T12:00:00Z"`).
8. Difficulty and language_level should match the content.
9. In the "question" column, first give a short instruction on what needs to be done and the task itself.
📘 Example task (your output should look like this, but with different content):

{
  "question": "Choose the correct form: She ___ to school every day.",
  "type": "multiple_choice",
  "variants": ["go", "goes", "gone", "going"],
  "answer": "goes",
  "solution": "The subject 'She' requires the verb with -s in the present simple: 'She goes'.",
  "difficulty": "easy",
  "category": "grammar",
  "language_level": "A1",
  "created_at": "2025-11-08T12:00:00Z"
}
'''

def generate_random_task():
  with open('intelligence/id_task.txt', 'r', encoding='utf-8') as f:
    cur_id = int(f.read().strip())
  topics = [
    "Present Simple",
    "Present Continuous",
    "Present Perfect",
    "Present Perfect Continuous",
    "Past Simple",
    "Past Continuous",
    "Past Perfect",
    "Past Perfect Continuous",
    "Future Simple",
    "Future Continuous",
    "Future Perfect",
    "Future Perfect Continuous",
    "Conditionals (Zero, First, Second, Third)",
    "Passive Voice",
    "Modal Verbs",
    "Articles (a/an/the)",
    "Prepositions (time, place, direction)",
    "Phrasal Verbs",
    "Gerunds and Infinitives",
    "Comparatives and Superlatives",
    "Adjectives vs. Adverbs",
    "Countable and Uncountable Nouns",
    "Quantifiers (some, any, much, many, etc.)",
    "Pronouns",
    "Question Tags",
    "Reported Speech",
    "Relative Clauses",
    "Formal Vocabulary",
    "Informal Vocabulary",
    "Idioms and Expressions",
    "Synonyms and Antonyms",
    "Word Formation (prefixes/suffixes)",
    "Confusing Words (e.g., affect/effect, their/there)",
    "Punctuation and Capitalization",
    "Sentence Structure and Word Order",
    "Reported Questions",
    "Articles with Proper Nouns and Places",
    "Zero Article (no article usage)",
    "Linking Words for Cohesion (however, therefore, moreover, etc.)",
    "Ellipsis and Substitution in Spoken English",
    "Direct vs. Indirect Questions",
    "Tag Questions with Imperatives and Suggestions",
    "Vocabulary for Opinions and Agreement/Disagreement",
    "Hedging Language (might, could, possibly, it seems that...)",
    "Discourse Markers in Conversation (well, you know, actually, I mean...)",
    "Daily Routines and Habits vocabulary",
    "Family and Relationships vocabulary",
    "Work and Jobs vocabulary",
    "Education and Learning vocabulary",
    "Food and Dining vocabulary",
    "Shopping and Money vocabulary",
    "Travel and Transportation vocabulary",
    "Health and Body vocabulary",
    "Emotions and Feelings vocabulary",
    "Weather and Seasons vocabulary",
    "Hobbies and Free Time vocabulary",
    "Home and Household vocabulary",
    "City and Environment vocabulary",
    "Technology and Devices vocabulary",
    "Sports and Fitness vocabulary",
    "Culture and Traditions vocabulary",
    "Nature and Animals vocabulary",
    "Time and Dates vocabulary",
    "Colors and Shapes vocabulary",
    "Size, Quantity, and Measurement vocabulary"
]
  rand_top = random.choice(topics)
  rand_lev = random.choice(['A1', 'A2', 'B1', 'B2', 'C1'])
  lev_cost = {'A1':10, 'A2':20, 'B1':30, 'B2':40, 'C1':50}
  rand_type = random.choice(['multiple_choice', 'open_question'])
  type_cost = {'multiple_choice':1, 'open_question':1.5}
  promt_user = f'''Generate one English grammar exercise for {rand_lev} level learners on the topic “{rand_top}” with id {cur_id}, with type {rand_type}.
  cost must be {lev_cost[rand_lev]*type_cost[rand_type]}
  If you take "open_question":
  - Make sure the question expects a short, clearly defined answer that can be easily checked by a bot.
  - Avoid multiple correct variations.
  Return only the JSON object following the system rules.
  '''
  with open('intelligence/id_task.txt', 'w', encoding='utf-8') as f:
    f.write(str(cur_id + 1))
  return promt_user