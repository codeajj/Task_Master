import mysql.connector
import random
import time

archery_game_state = {
    "active": False,
    "shots_left": 0,
    "score": 0
}

casino_game_state = {
    "active": False,
    "spins_left": 0
}

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="user",
        password="test",
        database="project_mars"
    )

def get_task_from_db(task_id, answer=None):
    connection = mysql.connector.connect(
        host="localhost",
        user="user",
        password="test",
        database="project_mars"
    )
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()

    if not task:
        return "Task not found", False

    if answer == "question":
        html = f"<div><strong>{task['question']}</strong><ul>"
        html += f"<li>a) {task['option_a']}</li>"
        html += f"<li>b) {task['option_b']}</li>"
        if task['option_c']:
            html += f"<li>c) {task['option_c']}</li>"
        if task['option_d']:
            html += f"<li>d) {task['option_d']}</li>"
        html += "</ul></div>"
        return html, False

    if answer == task["correct_answer"]:
        return "Correct! + 1 coin", True
    else:
        # Optional: call self.player_status() here if inside class
        return "Incorrect!", False

class GameLogic:
    def __init__(self):
        self.start_time = time.time()
        self.hp = 3; self.coins = 0; self.tries = 3 #Player status
        self.level = 0; self.tasks_done = 0; self.current_task = None #Task status
        self.task_index = { #Countries
            0: [self.task_0_0, self.task_0_1, self.task_0_2, self.task_0_3, self.task_0_4], #Argentina
            1: [self.task_1_0, self.task_1_1, self.task_1_2, self.task_1_3, self.task_1_4], #Australia
            2: [self.task_2_0, self.task_2_1, self.task_2_2, self.task_2_3, self.task_2_4], #Mongolia
            3: [self.task_3_0, self.task_3_1, self.task_3_2, self.task_3_3, self.task_3_4], #China
            4: [self.task_4_0, self.task_4_1, self.task_4_2, self.task_4_3, self.task_4_4], #Germany
            5: [self.task_5_0, self.task_5_1, self.task_5_2, self.task_5_3, self.task_5_4], #Poland
            6: [self.task_6_0, self.task_6_1, self.task_6_2, self.task_6_3, self.task_6_4], #Luxemburg
            7: [self.task_7_0, self.task_7_1, self.task_7_2, self.task_7_3, self.task_7_4], #Norway
            8: [self.task_8_0, self.task_8_1, self.task_8_2, self.task_8_3, self.task_8_4], #South Korea
            9: [self.task_9_0, self.task_9_1, self.task_9_2, self.task_9_3, self.task_9_4], #America

        }

    def end_game(self):
        player_name = "Yrjö"
        # Calculate the total time spent
        end_time = time.time()
        time_spent = end_time - self.start_time  # Time in seconds
        hours = int(time_spent // 3600)
        minutes = int((time_spent % 3600) // 60)
        seconds = int(time_spent % 60)
        time_spent_str = f"{hours:02}:{minutes:02}:{seconds:02}"

        # Save the data to the leaderboard
        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("""
                       INSERT INTO leaderboard (player_name, time_spent, level, coins, hp)
                       VALUES (%s, %s, %s, %s, %s)
                       """, (player_name, time_spent_str, self.level, self.coins, self.hp))

        connection.commit()
        connection.close()

        return "Game Over. Your progress has been saved."

    def process_input(self, user_input): #Otetaan input, tarkastetaan mitä kirjoitettu.
        user_input = user_input.lower().strip()
        #Next Task kutsu/tarkastus
        if user_input == "task":
            if self.current_task is not None:
                return "You must complete the task."
            else:
                return self.next_task()
        elif user_input == "debug_9": #DEBUG
            self.level = 9
        #Next level kutsu
        elif user_input == "next level":
            return self.next_level()
        #HP ja yritykset tieto
        elif user_input == "status":
            return self.status()
        #Ostetaan HP
        elif user_input == "buy hp":
            if self.coins >= 3:
                self.coins -= 3
                self.hp += 1
                return f"You have bought 1 HP with 3 coins. {self.coins} coins left."
            else:
                return "You do not have enough coins to buy HP."

        elif user_input == "?" or user_input == "help":
            return "Actions avaible: Task, Next Level, Status, Buy HP (cost: 3 coins)"

        elif user_input == "cigarette":
            if self.coins >= 3:
                self.hp -= 1
                self.coins -= 3
                return "You have smoked a cigarette! You lost one 1 HP and it cost 3 coins."
            else:
                return "Nuh uh"

        elif user_input == "scoreboard":
            connection = get_db_connection()
            cursor = connection.cursor()

            cursor.execute("""
                           SELECT player_name,
                                  COALESCE(time_spent, '0') AS time_spent,
                                  COALESCE(level, 0)        AS level,
                                  COALESCE(coins, 0)        AS coins,
                                  COALESCE(hp, 0)           AS hp
                           FROM leaderboard
                           ORDER BY level DESC, time_spent ASC 
                           LIMIT 10
                           """)
            result = cursor.fetchall()
            connection.close()

            if result:
                scoreboard = "<div><strong>Leaderboard:</strong><ul>"
                for row in result:
                    print(f"Row: {row}")
                    try:
                        player_name, time_spent, level, coins, hp = row
                        scoreboard += f"<li>{player_name} - Level: {level}, Time Spent: {time_spent}, Coins: {coins}, HP: {hp}</li>"
                    except ValueError as e:
                        print(f"Error unpacking row: {row}, Error: {e}")
                        scoreboard += f"<li>Error loading player data (missing values).</li>"

                scoreboard += "</ul></div>"
            else:
                scoreboard = "N/A"

            return scoreboard

        else:
            return self.handle_task_answer(user_input)


    def status(self): #Pelaaja kutsuu oman statuksen
        return f"HP: {self.hp}, Tries: {self.tries}, Coins: {self.coins}"

    def player_status(self): #Tarkastetaan yritys määrä, ja pitää ottaa hp
        if self.current_task is not None:
            self.tries -= 1
            if self.tries <= 0:
                self.hp -= 1
        if self.hp <= 0:
            self.end_game()

    def next_task(self): #Tehtyjen tarkastus
        if self.tasks_done == 5:
            return {"terminal": "All tasks completed. Proceed to the next level."}

        task = self.task_index[self.level][self.tasks_done]
        self.current_task = task
        message, _ = task("question")  #--->Kriittinen<---#

        connection = get_db_connection()
        cursor = connection.cursor()

        airport_order = [
            "Comodoro Pierrestegui Airport", "General Urquiza Airport", "La Cumbre Airport",
            "Presidente Néstor Kirchner Regional Airport",
            "Bedourie Airport", "Benalla Airport", "Boonah Airport", "Bowen Airport", "Sydney Airport",
            "Mörön Airport", "Tsetserleg Airport", "Buyant-Ukhaa International Airport", "Ulaangom Airport",
            "Ulaanbaatar Chinggis Khaan International",
            "Changzhi Airport", "Luoding Sulong Airport", "Golog Maqin Airport", "Beijing Daxing International Airport",
            "Altenburg-Nobitz Airport", "Magdeburg 'City' Airport", "Pinnow Airport", "Flugplatz Saarmund",
            "Frankfurt am Main Airport",
            "Bielsko Biala Airport", "Cewice Air Base", "Elblag Airport", "Katowice International Airport",
            "Warsaw Chopin Airport",
            "Luxembourg Airport", "Noertrange Airfield", "Useldange Glider Field",
            "Ålesund Airport, Vigra", "Sogndal Airport", "Sandane Airport, Anda", "Vardø Airport, Svartnes",
            "Oslo Airport, Gardermoen",
            "Yangyang International Airport", "Taean Airport", "Uljin Airport",
            "Cheongju International Airport/Cheongju", "Incheon International Airport",
            "Bryce Canyon Airport", "Eagle County Regional Airport", "Willow Airport", "Larsen Bay Airport",
            "John F Kennedy International Airport"
        ]

        # Select airport based on the task index (task_done keeps track of the task sequence)
        airport_index = self.level * 5 + self.tasks_done
        airport = airport_order[airport_index % len(airport_order)]  # Cycling through the list

        cursor.execute("""
                       SELECT latitude_deg, longitude_deg
                       FROM airport
                       WHERE airport.name = %s
                       """, (airport,))
        result = cursor.fetchone()

        connection.close()

        if result:
            latitude, longitude = result
        else:
            latitude, longitude = None, None

        return {
            "terminal": message,
            "latitude": latitude,
            "longitude": longitude
        }


    def next_level(self): #Seuraavaan siirtyminen
        if self.tasks_done < 5:
            return {"terminal": "No dumbass!"}
        else:
            self.level +=1
            self.tasks_done = 0
            self.hp += 1

            connection = get_db_connection()
            cursor = connection.cursor()

            country_order = [
                'Australia',
                'Mongolia',
                'China',
                'Germany',
                'Poland',
                'Luxembourg',
                'Norway',
                'South Korea',
                'United States of America'
            ]

            if self.level - 1 < len(country_order):
                next_country = country_order[self.level - 1]
                cursor.execute(
                    "SELECT name FROM country WHERE name = %s",
                    (next_country,)
                )
                result = cursor.fetchall()
            else:
                result = []

            connection.close()

            if result:
                country = result[0][0]
            else:
                country = "N/A"

            return {
                "terminal": f"Level {self.level + 1}! You've gained 1 HP!",
                "currentLevel": self.level,
                "country": country
            }

    def handle_task_answer(self, answer): #Inputin vastaan otto, käsittely.
        if self.current_task is None:
            return "You must start a new task"
        result = self.current_task(answer)

        if isinstance(result, tuple): # Turha kysyä
            message, is_correct = result
        else:
            message = result
            is_correct = message.strip().lower() == "Correct!"

        if is_correct:
            self.coins += 1
            self.tasks_done += 1
            self.tries = 3
            self.current_task = None
        return message

# Tehtävät alkaa tästä ----------------------->

    def task_0_0(self, answer):
        return get_task_from_db("0_0", answer)

    def task_0_1(self, answer):
        return get_task_from_db("0_1", answer)

    def task_0_2(self, answer):
        return get_task_from_db("0_2", answer)

    def task_0_3(self, answer):
        return get_task_from_db("0_3", answer)

    def task_0_4(self, answer):
        if answer == "question":
            return "Task 5: You bump into Messi, do you take a picture with him?", False #TODO pitää tehdä!
        elif answer == "yes":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_1_0(self, answer):
        return get_task_from_db("1_0", answer)

    def task_1_1(self, answer):
        return get_task_from_db("1_1", answer)

    def task_1_2(self, answer):
        return get_task_from_db("1_2", answer)

    def task_1_3(self, answer):
        if answer == "question":
            return "<div><strong>Task 4: A kangaroo insulted your mother, punch him?</strong><ul><li>a) Yes</li><li>b) No</li></ul></div>", False #TODO tehtävä itsessään
        elif answer == "a":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_1_4(self, answer):
        if answer == "question":
            return "Task 5: Go surfing? a) Yes b) No", False #TODO koko juttu
        elif answer == "a":
            return "Correct! + 1 coin", True
        else:
            self.player_status()
            return "Incorrect!", False

    def task_2_0(self, answer):
        return get_task_from_db("2_0", answer)

    def task_2_1(self, answer):
        return get_task_from_db("2_1", answer)

    def task_2_2(self, answer):
        return get_task_from_db("2_2", answer)

    def task_2_3(self, answer):
        global archery_game_state
        answer = answer.strip().lower()

        if answer == "question":
            return "Task 4: Would you like to attend an archery competition? (yes/no)", False

        if archery_game_state["active"]:
            if archery_game_state["shots_left"] <= 0:
                archery_game_state["active"] = False
                final_score = archery_game_state["score"]
                archery_game_state["score"] = 0
                return f"Competition finished! You scored {final_score} points.", True

            if answer == "shoot":
                archery_game_state["shots_left"] -= 1
                hit = random.random() < 0.7
                if hit:
                    points = random.choice([1, 2, 3])
                    archery_game_state["score"] += points
                    self.coins += 1
                    return f"Hit! You scored {points} points. Arrows left: {archery_game_state['shots_left']}", False
                else:
                    return f"Miss! Arrows left: {archery_game_state['shots_left']}", False
            else:
                return "Type 'shoot' to fire your next arrow", False

        elif answer == "yes":
            archery_game_state["active"] = True
            archery_game_state["shots_left"] = 3
            archery_game_state["score"] = 0
            return "Welcome to the traditional Mongolian archery competition! You have 3 arrows. Type 'shoot' to fire your first shot", False

        else:
            return "Alright, moving on", True

    def task_2_4(self, answer):
        return get_task_from_db("2_4", answer)

    def task_3_0(self, answer):
        return get_task_from_db("3_0", answer)

    def task_3_1(self, answer):
        return get_task_from_db("3_1", answer)

    def task_3_2(self, answer):
        return get_task_from_db("3_2", answer)

    def task_3_3(self, answer):
        return get_task_from_db("3_3", answer)

    def task_3_4(self, answer):
        global casino_game_state
        answer = answer.strip().lower()

        if answer == "question":
            return "<div><strong>Task 5: Welcome to Hong Kong Casino! You totally should play to slot machine!</strong><ul><li>a) Yes!</li><li>b) No</li></ul></div>", False

        if casino_game_state["active"]:
            if casino_game_state["spins_left"] <= 0:
                casino_game_state["active"] = False
                return "You're out of spins, sorry gambler", True

            if answer == "spin":
                symbols = ["apple", "bell", "lemon", "diamond", "seven"]
                spin = [random.choice(symbols) for _ in range(3)]
                result = " | ".join(spin)
                casino_game_state["spins_left"] -= 1

                if spin[0] == spin[1] == spin[2]:
                    casino_game_state["active"] = False
                    self.coins += 10
                    return f"{result} - JACKPOT!!! You win, and you're thrown out for winning too much", True
                elif spin[0] == spin[1] or spin[1] == spin[2] or spin[0] == spin[2]:
                    return f"{result} - You got a pair. Spins left: {casino_game_state['spins_left']}", False
                else:
                    return f"{result} - No luck. Spins left: {casino_game_state['spins_left']}", False
            else:
                return "Type 'spin' to start gambling!", False

        elif answer == "a":
            casino_game_state["active"] = True
            casino_game_state["spins_left"] = 3
            return "Type 'spin' to start gambling. You have 3 spins.", False
        else:
            return "Did you know 99,999% of gamblers stop beforing winning big? I guess you are one of the masses.", True

    def task_4_0(self, answer):
        answer = answer.strip().lower()

        if answer == "question":
            return "<div><strong>Task 1: Geh mir aus dem Weg! Willst du kämpfen? (he wants to fight you)</strong><ul><li>a) Flee</li><li>b) Flight</li></ul></div>", False

        if answer == "a":
            return "You have decided to ignore and walk away", True

        elif answer == "b":
            if random.random() < 0.5:
                return "You totally wrecked him! He sleeps on the ground and stole one coin from him!", True
            else:
                self.hp -= 1
                return "You tried your best, but the drunken German comes on top. -1HP", True

        else:
            return "No other options, lil bro", False

    def task_4_1(self, answer):
        return get_task_from_db("4_1", answer)

    def task_4_2(self, answer):
        if answer == "question":
            return "Task 3: AUTOBAHN HOMMELI (yes/no)", False #TODO koko juttu vaikka 30% et ajaa kolarin
        elif answer == "no":
            return "Wunderbar", True
        else:
            self.player_status()
            return "Wunderbar!", False

    def task_4_3(self, answer):
        answer = answer.strip().lower()

        if answer == "question":
            return "<div><strong>Task 4: A local challenges you to a beer drinking competition. Do you accept?</strong><ul><li>a) Yes</li><li>b) No</li></ul>", False

        if answer == "b":
            self.coins -= 5
            return "As you left the scene the drunk stole 5 coins from you!", True

        elif answer == "a":
            if random.random() < 0.5:
                return "They totally underestimated your abilities, your opponent lies deep asleep on the ground, you won!", True
            else:
                return "You blacked out way too early, they laugh as you lay nearly lifeless on the ground. -1HP", True

        else:
            return "No other options, lil bro", False

    def task_4_4(self, answer):
        return get_task_from_db("4_4", answer)

    def task_5_0(self, answer):
        return get_task_from_db("5_0", answer)

    def task_5_1(self, answer):
        return get_task_from_db("5_1", answer)

    def task_5_2(self, answer):
        return get_task_from_db("5_2", answer)

    def task_5_3(self, answer):
        answer = answer.strip().lower()

        if answer == "question":
            return "<div><strong>Task 4: Wanna try Polmos Spirytus Rektyfikowany 96% vodka?</strong><ul><li>a) Yes</li><li>b) No</li></ul>", False

        if answer == "b":
            return "Alright, moving on", True

        elif answer == "a":
            if random.random() < 0.5:
                return "It burns a little bit, but tastes truly delightful!", True
            else:
                return "It was way too strong for you, you had to take a visit to the hospital. -1HP", True

        else:
            return "No other options, lil bro", False

    def task_5_4(self, answer):
        return get_task_from_db("5_4", answer)

    def task_6_0(self, answer):
        return get_task_from_db("6_0", answer)

    def task_6_1(self, answer):
        return get_task_from_db("6_1", answer)

    def task_6_2(self, answer):
        return get_task_from_db("6_2", answer)

    def task_6_3(self, answer):
        return get_task_from_db("6_3", answer)

    def task_6_4(self, answer):
        if answer == "question":
            return "<div><strong>Task 5: Wanna go for a coffee before you leave?</strong><ul><li>a) Yes</li><li>b) No</li></ul>", False
        elif answer == "b":
            return "Alright moving on...", True
        elif answer == "a":
            self.hp += 1
            self.coins -= 3
            return "Now that was an expensive coffee! You paid 3 coins but gained one HP!", True
        else:
            self.hp -= 1
            return "You made the wrong choice, stumbled and lost one HP", False

    def task_7_0(self, answer):
        return get_task_from_db("7_0", answer)

    def task_7_1(self, answer):
        return get_task_from_db("7_1", answer)

    def task_7_2(self, answer):
        return get_task_from_db("7_2", answer)

    def task_7_3(self, answer):
        return get_task_from_db("7_3", answer)

    def task_7_4(self, answer):
        return get_task_from_db("7_4", answer)

    def task_8_0(self, answer):
        return get_task_from_db("8_0", answer)

    def task_8_1(self, answer):
        return get_task_from_db("8_1", answer)

    def task_8_2(self, answer):
        return get_task_from_db("8_2", answer)

    def task_8_3(self, answer):
        return get_task_from_db("8_3", answer)

    def task_8_4(self, answer):
        return get_task_from_db("8_4", answer)

    def task_9_0(self, answer):
        return get_task_from_db("9_0", answer)

    def task_9_1(self, answer):
        return get_task_from_db("9_1", answer)

    def task_9_2(self, answer):
        return get_task_from_db("9_2", answer)

    def task_9_3(self, answer):
        return get_task_from_db("9_3", answer)


    def task_9_4(self, answer):
        if answer == "question":
            return "<div><strong>Task 5: Start a nuclear war with Russia?</strong><ul><li>a) Yes</li><li>b) No</li></ul>", False
        elif answer == "a":
            self.end_game()
            return "End scores updated, sorry this is unfinished", True
        else:
            self.player_status()
            return "", False