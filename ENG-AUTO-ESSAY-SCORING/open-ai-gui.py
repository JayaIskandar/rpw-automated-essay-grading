import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from tqdm import tqdm
import re
import openai

# Load your API key from an environment variable or secret management service
openai.api_key = "YOUR OPENAI_API_KEY"

# Function to grade essay
def grade_essay(essay_text):
    prompt = f"Grade the following essay based on this rubric:\n\n{rubric}\n\nEssay:\n{essay_text}\n\nGrade:"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1000,
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

    # Extract the feedback by removing the grade number and any additional text
    feedback = re.sub(r'\d+', '', response_text)
    feedback = re.sub(r'Grammatical and wording errors:.*', '', feedback, flags=re.DOTALL).strip()

    return grade, feedback



# Function to grade essays from a file
def grade_essays_from_file():
    filename = filedialog.askopenfilename(title="Select CSV file", filetypes=[("CSV files", "*.csv")])
    if filename:
        essays_df = pd.read_csv(filename)
        for index, row in tqdm(essays_df.iterrows(), total=len(essays_df)):
            essay_text = row["essay_text"]
            grade, feedback = grade_essay(essay_text)  # Modify this line
            essays_df.at[index, "grade"] = grade
            essays_df.at[index, "feedback"] = feedback
            # Display the grade and feedback on GUI
            text_widget.insert(tk.END, f"Essay {index+1}:\nGrade: {grade}\nFeedback: {feedback}\n\n")
        essays_df.to_csv("graded_essays.csv", index=False)
        messagebox.showinfo("Success", "Essays graded and saved to graded_essays.csv")

# GUI setup
root = tk.Tk()
root.title("Essay Grader")
root.geometry("800x500")  # Set window size
root.configure(bg="#FDDC5C")  # Change background color

# Rubric
rubric = {
    1: "Insufficient wording, poor structure, and lack of coherence.",
    2: "Basic structure and wording, but lack of depth and proper argumentation.",
    3: "Acceptable structure, wording, and argumentation, but room for improvement.",
    4: "Well-structured, coherent, and effective argumentation, with minor issues.",
    5: "Excellent structure, wording, and persuasive argumentation."
}


# Button to grade essays
grade_button = tk.Button(root, text="Grade Essays from File", command=grade_essays_from_file, font=("Helvetica", 12), bg="#007bff", fg="#ffffff", relief=tk.RAISED)
grade_button.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

# Text widget to display grades and feedback
text_widget = tk.Text(root, wrap=tk.WORD, width=100, height=20, font=("Helvetica", 10), bg="#ffffff", bd=5, relief=tk.SUNKEN)
text_widget.place(relx=0.5, rely=0.5, anchor=tk.CENTER)


root.mainloop()
