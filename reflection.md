# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Owner
This class represented the pet owner. I assigned it the responsibility of storing the owner’s basic information and scheduling preferences, such as available time, whether they prefer shorter tasks first, and whether low-energy mode is on.

Pet
This class represented each pet. Its responsibility was to store pet-specific information like name, species, age, and notes. It served as the connection between the owner and the care tasks.

Task
This class represented a pet care activity, such as feeding, walking, medication, or grooming. Its responsibility was to store the task details needed for scheduling, including title, duration, priority, whether it is mandatory, and whether it has been completed.

Planner
This class handled the scheduling logic. I assigned it the responsibility of checking which tasks still need to be done, scoring or prioritizing them, and generating a daily schedule based on the owner’s time and preferences.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

There is no major logic error yet, but there are three important design weaknesses:

I made a few small design changes after reviewing my initial class skeleton and considering AI-suggested improvements.

First, I updated the method designs for Task, Pet, and Owner. Originally, methods like update_task() and update_preferences() had no parameters, so it was unclear what they would change. I revised them so they can take optional values for specific attributes.

Second, I clarified the Planner output. Returning a generic dict was too vague, so I noted that the schedule result should have a clearly defined structure.

Third, I kept the four-class design simple, but I made sure the relationships between Owner, Pet, and Task were more consistent. AI feedback also suggested adding basic validation later, such as checking that task duration and available time are not negative.
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
