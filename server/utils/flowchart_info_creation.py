from .gpt_interface import get_gpt_response

PROMPT = """Note: (never output a markdown hyperlink). For the upcoming student career aspiration roadmap first deduce what field the content falls in (stem, healthcare, arts, business, or social sciences)
{flowchart}

You must, non negotiable, fill this up with relevant and helpful resources for oppressed students (any hyperlinks should be bolded) phrase it to be read by the student after the listed resources put a mentor section matching them to hypothetical figures in their desired field and showing their name short title and phone number (do this in the nodes where this would be beneficial and use markdown to bolden this text it should come after the resources part with the letter based nodes though). The final output should be neatly formatted with markdown methods like line breaks etc. When done only return this {{ A: {{ title: "", content: "" }}, ... (till the last node in the graph) fully fill the title and content out, non negotiable, with 0 other characters or text
"""

STR_TO_REPLACE='''{
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
  };
'''

def generate_flowchart_info(flowchart):
    prompt = PROMPT.format(flowchart=flowchart)
    messages = [{"role": "user", "content": prompt}]
    try:
        info = get_gpt_response(messages)
        return info
    except Exception as e:
        print(f"Error: {{e}}")
        return "I'm sorry, I encountered an error while generating the narrative summary."
    
