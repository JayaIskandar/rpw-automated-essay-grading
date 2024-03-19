import openai
import pandas as pd
from tqdm import tqdm
import re

# Load your API key from an environment variable or secret management service
openai.api_key = "YOUR OPENAI_API_KEY"

# Load the dataset of essays
essays_df = pd.read_csv("essays.csv", sep=",")

# Define the rubric for scoring
rubric = {
    1: "Insufficient wording, poor structure, and lack of coherence.",
    2: "Basic structure and wording, but lack of depth and proper argumentation.",
    3: "Acceptable structure, wording, and argumentation, but room for improvement.",
    4: "Well-structured, coherent, and effective argumentation, with minor issues.",
    5: "Excellent structure, wording, and persuasive argumentation."
}

# Define a function to call the OpenAI API for grading
def grade_essay(essay):
    prompt = f"Grade the following essay based on this rubric:\n\n{rubric}\n\nEssay:\n{essay}\n\nGrade:"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=200,
        n=1,
        stop=None,
    )

    # Extract the grade number from the response
    response_text = response.choices[0].message.content
    grade_match = re.search(r'\d+', response_text)
    if grade_match:
        grade = int(grade_match.group())
    else:
        grade = 0

    # Extract the feedback by removing the grade number
    feedback = re.sub(r'\d+', '', response_text).strip()

    # Extract the grammatical and wording errors
    grammatical_errors = response.choices[0].message.get('content', '').split('\n\nGrammatical and wording errors:\n\n')[-1]

    return grade, feedback, grammatical_errors

# Create a new column to store the grades and feedback
essays_df["grade"] = 0
essays_df["feedback"] = ""
essays_df["errors"] = ""

# Grade each essay using the OpenAI API
for index, row in tqdm(essays_df.iterrows(), total=len(essays_df)):
    essay_text = row["essay_text"]
    grade, feedback, errors = grade_essay(essay_text)  # Unpack all three values
    essays_df.at[index, "grade"] = grade
    essays_df.at[index, "feedback"] = feedback
    essays_df.at[index, "errors"] = errors

# Save the updated DataFrame with grades and feedback
essays_df.to_csv("graded_essays.csv", index=False)