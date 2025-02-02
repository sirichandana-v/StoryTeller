import time
from groq import Groq
import os
from dotenv import load_dotenv


load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

# Function to generate story using Groq
def generate_story(prompt):
    response = client.chat.completions.create(
        model="llama3-70b-8192",  # Use the available Groq model
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content

def main():
    print("👴 Grandpa: Well hello there, young one! What kind of story do you want to hear today?")
    story_type = input("You: ")

    prompt = f"""Tell me a {story_type} story in the voice of an old, wise grandpa. 
    Speak as if you are telling the story to a child, with warmth, humor, and dramatic pauses. 
    Pause when you want the listener to give an idea about what happens next. 
    When you want input, clearly ask something like: 'What do you think should happen next?' or 'Should the hero go left or right?'
    Always continue from the user's suggestion while keeping the grandpa storytelling style alive."""
    
    story = generate_story(prompt)
    
    while True:  # Keep the storytelling loop going
        sentences = story.split('. ')  # Reset story sentences
        for sentence in sentences:
            print("👴 Grandpa:", sentence)
            time.sleep(2)  # Simulate storytelling pace

            # Check if Grandpa is asking a question
            if "what do you think" in sentence.lower() or "should" in sentence.lower() or "what happens next" in sentence.lower():
                print("👴 Grandpa: I'm listening... what should happen next?")
                user_input = input("You: ")
                
                if user_input.lower() in ["stop", "exit", "end"]:
                    print("👴 Grandpa: Alright then, we'll continue another time! *chuckles*")
                    return  # Ends the program
                
                # Generate a new part of the story based on user input
                story = generate_story(f"""Grandpa chuckles and nods after hearing: "{user_input}". 
He strokes his beard, responding with warmth, humor, or a bit of old wisdom. 
Then, he naturally weaves the suggestion into the story and continues telling it as an old wise storyteller. 
Make sure Grandpa stays fully in character and does NOT explain what he is doing.
""")
                
                # Restart the for loop with the new story
                break  # Break out of the loop to restart with a new story

if __name__ == "__main__":
    main()
