import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

# ================== Load Datasets ==================
df_symptoms = pd.read_csv("DiseaseAndSymptoms.csv")
df_precautions = pd.read_csv("Disease precaution.csv")

# Build rules from DiseaseAndSymptoms.csv
rules = {}
for _, row in df_symptoms.iterrows():
    disease = row["Disease"].strip().lower()
    symptoms = {str(s).strip().lower() for s in row[1:].dropna().tolist()}
    if disease not in rules:
        rules[disease] = set()
    rules[disease].update(symptoms)

# Precaution dictionary
precautions = {}
for _, row in df_precautions.iterrows():
    disease = row["Disease"].strip().lower()
    steps = [str(p).strip() for p in row[1:].dropna().tolist()]
    precautions[disease] = steps

# ================== Diagnosis Function ==================
def diagnose():
    selected_symptoms = [symptom for symptom, var in symptom_vars.items() if var.get() == 1]

    if not selected_symptoms:
        messagebox.showwarning("No Symptoms Selected", "Please select at least one symptom.")
        return

    selected_symptoms_set = set(selected_symptoms)

    # Match with diseases
    scores = []
    for disease, symptoms in rules.items():
        match_count = len(selected_symptoms_set.intersection(symptoms))
        if match_count > 0:
            confidence = (match_count / len(symptoms)) * 100
            scores.append((disease, confidence))

    scores.sort(key=lambda x: x[1], reverse=True)

    # Prepare report
    report_box.config(state="normal")
    report_box.delete("1.0", tk.END)

    if scores:
        best_match, confidence = scores[0]
        precautions_list = precautions.get(best_match, ["No specific precautions found."])

        report = f"🩺 Most Likely Disease: {best_match.title()}\n"
        report += f"✅ Confidence: {confidence:.2f}%\n\n"
        report += "📋 Recommended Precautions:\n"
        for step in precautions_list:
            report += f"   • {step}\n"
    else:
        report = "⚠️ No matching disease found for the given symptoms."

    report_box.insert(tk.END, report)
    report_box.config(state="disabled")

# ================== Update Selected Symptoms ==================
def update_selected():
    selected_symptoms_box.config(state="normal")
    selected_symptoms_box.delete("1.0", tk.END)
    for symptom, var in symptom_vars.items():
        if var.get() == 1:
            selected_symptoms_box.insert(tk.END, f"• {symptom}\n")
    selected_symptoms_box.config(state="disabled")

# ================== GUI ==================
root = tk.Tk()
root.title("Expert System for Medical Diagnosis")
root.geometry("1200x700")

# Title
title_label = tk.Label(root, text="Expert System for Medical Diagnosis",
                       font=("Helvetica", 18, "bold"), fg="white", bg="#2E86C1", pady=10)
title_label.pack(fill=tk.X)

# Instruction
instruction = tk.Label(root, text="Search and select your symptoms, then click Diagnose",
                       font=("Helvetica", 12), bg="#D6EAF8")
instruction.pack(fill=tk.X)

# Main content frame (3 columns)
content_frame = tk.Frame(root)
content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Left frame (Symptoms checklist)
left_frame = tk.Frame(content_frame)
left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5)

# Symptom search
search_frame = tk.Frame(left_frame)
search_frame.pack(fill=tk.X, pady=5)

tk.Label(search_frame, text="🔎 Search Symptom:").pack(side=tk.LEFT)
search_entry = tk.Entry(search_frame)
search_entry.pack(side=tk.LEFT, padx=5)

# Scrollable symptom list
symptom_canvas = tk.Canvas(left_frame, width=250)
scrollbar = tk.Scrollbar(left_frame, orient="vertical", command=symptom_canvas.yview)
scrollable_frame = tk.Frame(symptom_canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: symptom_canvas.configure(scrollregion=symptom_canvas.bbox("all"))
)

symptom_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
symptom_canvas.configure(yscrollcommand=scrollbar.set)

symptom_canvas.pack(side=tk.LEFT, fill=tk.Y)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Symptom checkboxes
symptom_vars = {}
all_symptoms = sorted({s for symptoms in rules.values() for s in symptoms})

for symptom in all_symptoms:
    var = tk.IntVar()
    chk = tk.Checkbutton(scrollable_frame, text=symptom, variable=var,
                         command=update_selected, anchor="w", justify="left")
    chk.pack(fill=tk.X, anchor="w")
    symptom_vars[symptom] = var

# Middle frame (Selected Symptoms)
middle_frame = tk.Frame(content_frame, padx=10)
middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

tk.Label(middle_frame, text="✔️ Selected Symptoms", font=("Helvetica", 12, "bold")).pack(anchor="w")

selected_symptoms_box = tk.Text(middle_frame, height=25, width=40, wrap="word", state="disabled")
selected_symptoms_box.pack(fill=tk.BOTH, expand=True, pady=5)

# Right frame (Diagnosis Report)
right_frame = tk.Frame(content_frame, padx=10)
right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

tk.Label(right_frame, text="📝 Diagnosis Report", font=("Helvetica", 12, "bold")).pack(anchor="w")

report_box = tk.Text(right_frame, height=25, width=60, wrap="word", state="disabled")
report_box.pack(fill=tk.BOTH, expand=True, pady=5)

# Diagnose button
diagnose_btn = tk.Button(root, text="🔍 Diagnose", command=diagnose,
                         font=("Helvetica", 12, "bold"), bg="limegreen", fg="white")
diagnose_btn.pack(pady=10)

root.mainloop()
