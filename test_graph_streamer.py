import time

# Wait for 5 seconds
time.sleep(5)

# Define the graph text
graph_text = """graph TD
    A[Journey to Becoming a Doctor] --> B[Develop Interest in Medicine]
    B --> C[Explore Neuroscience]
    C --> D{Is Neuroscience Right?}
    D -->|Yes| E[Deepen Neuroscience Knowledge]
    D -->|No| F[Explore Other Fields]
    E --> G[Gain Experience]
    F --> G
    G --> H{Sufficient Experience?}
    H -->|Yes| I[Prepare for Medical School]
    I --> J[Prerequisite Courses]
    J --> K[Study for MCAT]
    K --> L{MCAT Score Satisfactory?}
    L -->|Yes| N[Apply to Schools]
    L -->|No| M[Retake MCAT]
    N --> O{Accepted?}
    O -->|Yes| Q[Begin Medical School]
    O -->|No| P[Improve Application]
    Q --> R[Complete Pre-Clinical Years]
    R --> S[Clinical Rotations]
    S --> T{Choose Specialty?}"""

# Print the graph text
print(graph_text)
body_text = graph_text[len('graph TD'):]

# Path to the index.html file
html_file_path = 'index.html'

# Read the existing HTML file and replace the placeholder
with open(html_file_path, 'r') as file:
    content = file.read()

# Replace the diagram definition placeholder with the actual graph text
new_content = content.replace(
    "A[loading...]", body_text
)

# Write the updated content back to the index.html file
with open(html_file_path, 'w') as file:
    file.write(new_content)
