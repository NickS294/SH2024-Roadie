import os
import time

# Wait for 5 seconds
time.sleep(5)

# Define the graph text
graph_text = """graph TD
    A[16-Year-Old Aspiring Doctor] --> B[Complete High School]
    B --> C[Research Pre-Med Programs]
    C --> D[Apply to Scholarships & Financial Aid]
    B --> E[Prepare for SAT/ACT]
    D --> F[Attend College Pre-Med Track]
    F --> G[Volunteer/Shadow in Medical Settings]
    F --> H[Study for MCAT Medical College Admission Test]
    G --> I[Build Extracurriculars Clubs, Volunteering]
    H --> J[Take the MCAT]
    J --> K[Apply to Medical School]
    K --> L[Complete Medical School 4 Years]
    L --> M[Residency 3-7 Years]
    M --> N[Become a Licensed Physician]
    N --> O[Specialize in a Field]"""

# Define node information
node_info = """const nodeInfo = {
    'A': {
        'title': "Journey to Becoming a Doctor",
        'content': "This path requires **dedication**, **compassion**, and **continuous learning**."
    },
    'B': {
        'title': "Develop Interest in Medicine",
        'content': "Explore your passion through **shadowing**, **volunteering**, and **reading**."
    },
    'C': {
        'title': "Explore Neuroscience",
        'content': "Study the nervous system, focusing on **neuroanatomy** and **cognitive neuroscience**."
    },
    'D': {
        'title': "Is Neuroscience Right?",
        'content': "Consider the **research opportunities** and **challenges** involved."
    },
    'E': {
        'title': "Deepen Neuroscience Knowledge",
        'content': "Engage in **advanced coursework** and **research** for deeper insights."
    },
    'F': {
        'title': "Explore Other Fields",
        'content': "If neuroscience isn’t for you, consider other specialties like **cardiology** or **pediatrics**."
    },
    'G': {
        'title': "Gain Experience",
        'content': "Practical experience is vital for skill development."
    },
    'H': {
        'title': "Seek Mentorship",
        'content': "Find mentors in the field to guide your education and career choices."
    },
    'I': {
        'title': "Prepare for Medical School",
        'content': "Focus on **standardized tests**, **applications**, and **interviews**."
    },
    'J': {
        'title': "Medical School Experience",
        'content': "Immerse yourself in the **curriculum**, **clinical rotations**, and **networking**."
    },
    'K': {
        'title': "Choose a Specialty",
        'content': "Decide on your medical specialty based on your interests and experiences."
    },
    'L': {
        'title': "Residency Training",
        'content': "Complete residency to gain in-depth training in your chosen specialty."
    },
    'M': {
        'title': "Board Certification",
        'content': "Pass board exams to become certified in your medical specialty."
    },
    'N': {
        'title': "Continuous Education",
        'content': "Engage in **lifelong learning** through courses and seminars to stay updated."
    },
    'O': {
        'title': "Give Back",
        'content': "Contribute to the community through **outreach**, **education**, and **volunteering**."
    }
};
"""

# Get the directory of the current script
current_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to the index.html file in the current directory
html_file_path = os.path.join(current_dir, 'roadmap.html')


# Read the existing HTML file and replace the placeholders
with open(html_file_path, 'r') as file:
    content = file.read()

# Replace the diagram definition placeholder with the actual graph text
new_content = content.replace("A[Loading...]", graph_text[len('graph TD'):])
new_content = new_content.replace("""const nodeInfo = {
    A: {
      title: "", 
      content: ""
    },
    B: {
      title: "", 
      content: ""
    },
    C: {
      title: "", 
      content: ""
    },
    D: {
      title: "", 
      content: ""
    },
    E: {
      title: "", 
      content: ""
    },
    F: {
      title: "", 
      content: ""
    },
    G: {
      title: "", 
      content: ""
    },
    H: {
      title: "", 
      content: ""
    },
    I: {
      title: "", 
      content: ""
    },
    J: {
      title: "", 
      content: ""
    },
    K: {
      title: "", 
      content: ""
    },
    L: {
      title: "", 
      content: ""
    },
    M: {
      title: "", 
      content: ""
    },
    N: {
      title: "", 
      content: ""
    },
    O: {
      title: "", 
      content: ""
    }
  };""", node_info)

# Write the updated content back to the index.html file
with open(html_file_path, 'w') as file:
    file.write(new_content)
