from rag_core import load_pipeline, answer_question

# Our test set: each question paired with a keyword the correct answer MUST contain.
test_cases = [
    {"question": "How much does the Aquila cost?",              "expected": "2,400"},
    {"question": "What is the name of the company mascot?",     "expected": "Pip"},
    {"question": "What is the return window for bicycles?",     "expected": "14"},
    {"question": "When was Ember Coffee founded?",              "expected": "2020"},
    {"question": "How much does the Falcon kettle cost?",       "expected": "7,200"},
    {"question": "Which kettle has a keep-warm function?",      "expected": "Eagle"},
    {"question": "Where is Summit Cycles based?",               "expected": "Turin"},
    {"question": "Who is the CEO of Brightwave?",               "expected": "could not find"},
]

print("Loading the pipeline...")
embedder, collection = load_pipeline()

passed = 0
for i, case in enumerate(test_cases, start=1):
    question = case["question"]
    expected = case["expected"]

    answer, _ = answer_question(embedder, collection, question)

    is_correct = expected.lower() in answer.lower()
    if is_correct:
        passed += 1

    mark = "PASS" if is_correct else "FAIL"
    print(f"\n[{mark}] Q{i}: {question}")
    print(f"   expected to contain: '{expected}'")
    print(f"   got: {answer.strip()[:120]}")

print(f"\n=========================================")
print(f"SCORE: {passed} / {len(test_cases)} passed")
print(f"=========================================")