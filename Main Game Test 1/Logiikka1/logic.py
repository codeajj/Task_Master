class GameLogic:
    def __init__(self):
        self.hp = 3
        self.level = 0
        self.tasks_done = 0 #Tarkastetaan onko min. tehty (5)
        self.current_task = None
        self.task_index = { #Indexi on kyseisen maa
            0: [self.task_0_0, self.task_0_1, self.task_0_2, self.task_0_3, self.task_0_4],
            1: [self.task_1_0, self.task_1_1, self.task_1_2, self.task_1_3, self.task_1_4]
        }
    def process_input(self, user_input): #Otetaan input, tarkastetaan mitä kirjoitettu.
        user_input = user_input.lower().strip()
        #Next Task kutsu/tarkastus
        if user_input == "task":
            if self.current_task is not None:
                return "You must complete the task."
            else:
                return self.next_task()
        #Next level kutsu
        elif user_input == "next level":
            return self.next_level()
        else:
            return self.handle_task_answer(user_input)

    def next_task(self):
        if self.tasks_done == 5:
            return "All tasks completed. Proceed to the next level."
        task = self.task_index[self.level][self.tasks_done]
        self.current_task = task
        message, _ =task("question")
        return message

    def next_level(self):
        if self.tasks_done < 5:
            return "No dumbass!"
        else:
            self.level +=1
            self.tasks_done = 0
            self.hp += 1
            return f"Level {self.level + 1}! You've gained 1 HP!"

    def handle_task_answer(self, answer):
        if self.current_task is None:
            return "You must start a new task"
        result = self.current_task(answer)

        if isinstance(result, tuple):
            message, is_correct = result
        else:
            message = result
            is_correct = message.strip().lower() == "Correct!"

        if is_correct:
            self.tasks_done += 1
            self.current_task = None
        return message

    def task_0_0(self, answer):
        if answer == "question":
            return "Task 1: What is the capital of Argentina?", False
        elif answer == "buenos aires":
            return "Correct!", True
        else:
            return "Incorrect!", False

    def task_0_1(self, answer):
        if answer == "question":
            return "Task 2: What is the national language of Argnetina?", False
        elif answer == "spanish":
            return "Correct!", True
        else:
            return "Incorrect!", False

    def task_0_2(self, answer):
        if answer == "question":
            return f"Task 3: Did Hitler escape to Argentina?\nYes, no or maybe?", False
        elif answer == "maybe":
            return "Correct! I think?", True
        else:
            return "Incorrect!", False

    def task_0_3(self, answer):
        if answer == "question":
            return "Task 4: What is the currency of Argentina?", False
        elif answer == "peso":
            return "Correct!", True
        else:
            return "Incorrect!", False

    def task_0_4(self, answer):
        if answer == "question":
            return "Task 5: You bump into Mesi, do you take a picture with him?", False
        elif answer == "yes":
            return "Correct!", True
        else:
            return "Incorrect!", False

    def task_1_0(self, answer):
        if answer == "question":
            return "Task 1: What ominous rock lies in the center of Australia?", False
        elif answer == "uluru":
            return "Correct!", True
        else:
            return "Incorrect!", False

    def task_1_1(self, answer):
        if answer == "question":
            return "What is the most populous city in Australia?", False
        elif answer == "sydney":
            return "Correct!", True
        else:
            return "Incorrect!", False

    def task_1_2(self, answer):
        if answer == "question":
            return f"Task 3: How big is Australia? a) 9 million km2 b) 7.7 million km2 or c) 2 million km2", False
        elif answer == "b":
            return "Correct! I think?", True
        else:
            return "Incorrect!", False

    def task_1_3(self, answer):
        if answer == "question":
            return "Task 4: A kangaroo insulted your mother, punch him?", False
        elif answer == "yes":
            return "Correct!", True
        else:
            return "Incorrect!", False

    def task_1_4(self, answer):
        if answer == "question":
            return "Task 5: Go surfing?", False
        elif answer == "yes":
            return "Correct!", True
        else:
            return "Incorrect!", False

