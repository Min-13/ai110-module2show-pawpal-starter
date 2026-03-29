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

My scheduler mainly considers time, priority, task importance, and owner preferences.

The most important constraint is the owner’s available time. The scheduler only selects tasks if their total duration fits within available_minutes, and it skips tasks that no longer fit in the remaining time.

It also considers priority and mandatory status. In score_task(), higher-priority tasks get a stronger score, and mandatory tasks receive a large bonus, so they are more likely to be selected first.

For owner preferences, I included:

prefer_short_tasks_first, which slightly boosts shorter tasks
low_energy_mode, which lowers the score of longer optional tasks
preferred_time, which helps order tasks in the final schedule and is also used for simple conflict warnings if a task cannot start at its preferred time.

The scheduler also supports filtering constraints, such as filtering by pet and status (pending, completed, or all), and it accounts for recurring tasks when deciding whether a task is due today.

I decided these constraints mattered most because they match the real problem of a busy pet owner. A useful schedule should first make sure the plan fits the time the owner actually has, then prioritize the most important care tasks, and finally adjust based on personal preferences and timing. That order makes the schedule practical, understandable, and easy to explain.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff my scheduler makes is that it uses a simple greedy approach: it first scores tasks by factors like priority, mandatory status, short-task preference, and preferred time, then selects tasks in that ranked order until the owner’s available time runs out. After that, it sorts the chosen tasks by preferred time when building the final schedule.

This means it may not always find the mathematically “best” possible schedule, because a lower-scored combination of tasks could sometimes fit the time limit better. However, that tradeoff is reasonable for this scenario because a pet care app needs to be easy to understand, fast, and predictable. For a busy pet owner, a simple schedule that prioritizes important tasks and gives clear conflict or skip warnings is more useful than a more complex optimizer that is harder to explain.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI tools mainly for brainstorming, debugging, and code explanation during this project. At the beginning, AI was helpful for brainstorming the class design, UML structure, and the main features the pet care app should include. As I started implementing the project, I also used AI to help debug problems in my code and to explain parts of the code that I did not fully understand.

The most helpful prompts were the ones that were specific and practical. For example, it was helpful to ask AI to review my class skeleton, point out possible design issues, suggest how to implement one feature at a time, or explain what a certain part of the code was doing in simpler terms. Questions like “What should this method return?”, “Is there any logic error in this design?”, and “How can I test this feature in main.py?” were especially useful because they helped me move forward without just copying code blindly.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

I did not accept one AI suggestion as-is when I asked for ways to improve my code structure. The AI suggested a more compact and “Pythonic” version, but when I looked at it, I realized it was harder for me to read and fully understand. Since I still needed to explain and maintain the code myself, I decided not to use that version directly.

To evaluate the suggestion, I compared it with my original code and asked myself whether I could clearly follow the logic, modify it later, and explain it in my own words. Even though the AI version may have been shorter or more elegant, I chose to keep a simpler structure because readability and understanding were more important for this project.

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
