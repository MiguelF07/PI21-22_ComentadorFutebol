import math
from entities import Position, Ball
from message import Message, Aggresion, Goal, Kick_Off, Pass, Dribble

KICK_OFF_CONTACT_DISTANCE = 0.13              # Distance to be considered contact between entities
CONTACT_DISTANCE = 0.2
AGGRESSION_DISTANCE_MARGIN = 0.3              # Distance to be considered collision between players
AGGRESSION_DISTANCE_TO_BALL = 1.2             # Just notify aggressions at maximum that distance from ball

events = {}                         

def process(entities : list, field : dict, goal : dict, curr_timestamp : float):
    """If event is detected, the positions related to the event's timestamp are deleted from all entities.
    It returns a string event"""
    ball = entities[0]
    teamA = entities[1:12] # Left (False)
    teamB = entities[12:] # Right (True)
    messages = []
    if curr_timestamp == 0.0:
        events["start"] = None
    
    # Event detection
    messages += detect_kick_off(ball, teamA, teamB, curr_timestamp)
    messages += detect_corner_shot(ball, teamA, teamB, curr_timestamp)
    # If ball is out, we have to wait for the ball to be back in game
    if not ("out" in events or "corner" in events or "goalkeeper_out" in events or "out_shot" in events or "corner_shot" in events or "goalkeeper_out_shot" in events or "goal" in events):
        messages += detect_out_goal(ball, teamA, teamB, field, goal, curr_timestamp)
        messages += detect_goal_shot(ball, field, goal, curr_timestamp)
        messages += detect_aggressions(teamA=teamA, teamB=teamB, ball=ball)
        messages += detect_pass_or_dribble(ball, entities[1:], curr_timestamp) 
        messages += detect_defense(ball, teamA, teamB, curr_timestamp)

    return messages

def detect_kick_off(ball : Ball, teamA, teamB, timestamp):
    if not "start" in events and not "goal" in events and not "out" in events:
        return []

    elif "start" in events: # start of game
        if timestamp > 15: # kick_off timeout
            events.pop("start")
            return [Kick_Off(timestamp, None)]
        player = ball.get_closest_player(teamA+teamB)
        if ball.get_distance_from(player) <= KICK_OFF_CONTACT_DISTANCE: # kick_off!
            events.pop("start")
            ball.owner = player
            return [Kick_Off(timestamp, player)]
        else: return [] # still waiting on kick_off

    elif "goal" in events:
        goal = events["goal"]
        if timestamp - goal.end > 18: # kick_off timeout
            events.pop("goal")
            return [Kick_Off(timestamp, None)]
        player = ball.get_closest_player(teamA+teamB)
        if ball.get_distance_from(player) <= KICK_OFF_CONTACT_DISTANCE: # kick_off!
            events.pop("goal")
            ball.owner = player
            return [Kick_Off(timestamp, player)]
        else: return [] # still waiting on kick_off

    elif "out" in events:
        out = events["out"]
        if timestamp - out.end > 18: # kick_off timeout
            events.pop("out")
            return [Kick_Off(timestamp, None)]
        player = ball.get_closest_player(teamA+teamB)
        if ball.get_distance_from(player) <= KICK_OFF_CONTACT_DISTANCE: # kick_off!
            events.pop("out")
            ball.owner = player
            return [Kick_Off(timestamp, player)]
        else: return [] # still waiting on kick_off

# length -> x
# width -> y
def detect_out_goal(ball : Ball, teamA, teamB, field, goal, timestamp):
    # First things first, is it outside the field?
    ball_pos = ball.positions[-1]
        
    if not (abs(ball_pos.x) > field["length"]/2 or abs(ball_pos.y) > field["width"]/2):
        return []
    
    
    # Is it a goal?
    if abs(ball_pos.y) <= goal["width"]/2 and 0 < ball_pos.z < goal["height"] and abs(ball_pos.x) > field["length"]/2:
        # It's a goal! Which team?
        team = None
        if -field["length"]/2-goal["depth"] < ball_pos.x < -field["length"]/2:
            team = "Left"
        elif field["length"]/2 < ball_pos.x < field["length"]/2+goal["depth"]:
            team = "Right"
        if team and "goal" not in events:
            messages = []
            m1 = Goal(team, timestamp, timestamp)
            events["goal"] = m1
            messages.append(m1)
            if "goal_shot" in events:
                m2 = events["goal_shot"]
                m2.end = timestamp
                events.pop("goal_shot", None)
                messages = [m2] + messages 
            return messages
            
    if "goal" not in events:
        # Who is the ball owner
        pl_teamA = ball.get_closest_player(teamA)
        pl_teamB = ball.get_closest_player(teamB)
        if ball.get_distance_from(pl_teamA) > ball.get_distance_from(pl_teamB): ball.owner = pl_teamB
        else: ball.owner = pl_teamA

        # Is it a corner?
        if abs(ball_pos.x) > field["length"]/2:
            teamRight = False if ball_pos.x < 0 else True
            # If ball exited by the opposite side of a team and hasn't been a goal
            if (teamRight == ball.owner.isTeamRight):
                # Verify if is the same corner event
                if "corner" not in events:
                    message = Message(event="corner", start=ball_pos.timestamp, end=ball_pos.timestamp)
                    events["corner"] = message
                    # print("Corner made it")
                    return [message]
            else:
                # Goal Keeper kickoff
                if "goalkeeper_out" not in events:
                    message = Message(event="out", start=ball_pos.timestamp, end=ball_pos.timestamp)
                    events["goalkeeper_out"] = message
                    # print("Out made it")
                    return [message]
            
        else: # It's an out
            if "out" not in events:
                message = Message(event="out", start=ball_pos.timestamp, end=ball_pos.timestamp)
                events["out"] = message
                #print(f"{timestamp}: Out made it")
                return [message]
    
    return []
    

def detect_corner_shot(ball : Ball, teamA : list, teamB : list, curr_timestamp : float):
    if "corner" in events:
        if start_outside_shot("corner", ball, teamA, teamB, curr_timestamp):
            return []
    
    elif "out" in events:
        if start_outside_shot("out", ball, teamA, teamB, curr_timestamp):
            print(f"{curr_timestamp}: Out Start")
            return []
        
    elif "goalkeeper_out" in events:
        if start_outside_shot("goalkeeper_out", ball, teamA, teamB, curr_timestamp):
            return []

    elif "corner_shot" in events:
        message = outside_shot("corner", ball, teamA, teamB, curr_timestamp)
        if message is not None:
            return [message]
    
    elif "out_shot" in events:
        message = outside_shot("out", ball, teamA, teamB, curr_timestamp)
        if message is not None:
            print(f"{curr_timestamp}: Out Shot")
            return [message]

    elif "goalkeeper_out_shot" in events:
        message = outside_shot("goalkeeper_out", ball, teamA, teamB, curr_timestamp)
        if message is not None:
            return [message]
    return []

def start_outside_shot(event : str, ball : Ball, teamA : list, teamB : list, curr_timestamp : float):
    """If a outside shot is kicked, returns True and add to the events. Returns False otherwise"""
    atk_team = teamA if ball.owner.isTeamRight else teamB

    # If attacking team has a player that entered in contact with the ball
    #for player in atk_team:
    player = ball.get_closest_player(atk_team)
    if ball.get_distance_from(player) < KICK_OFF_CONTACT_DISTANCE:
        events.pop(event)
        events[f"{event}_shot"] = {"start": curr_timestamp}
        # print(f"after {events[event + '_shot'] = }")
        return True
            
    return False

def outside_shot(event : str, ball : Ball, teamA : list, teamB : list, curr_timestamp : float):
    # The shot ends when the ball stops moving
    if has_ball_stopped(ball, teamA, teamB):
        message = Message(event=f"{event}_shot", start=events[f"{event}_shot"]["start"], end=curr_timestamp)
        events.pop(f"{event}_shot")
        return message
            
def has_ball_stopped(ball : Ball, teamA : list, teamB : list):
    """Returns True if the ball collides with some player of if its velocity is 0"""
    if ball.get_current_velocity() == 0:
        return True

    for player in teamA + teamB:
        if ball.get_distance_from(player) < CONTACT_DISTANCE:
            return True

    return False

def detect_goal_shot(ball: Ball, field : dict, goal : dict, timestamp : float):
    """Detects if a goal shot is currently happening"""
    # if ball doesn't have owner, skip detection, TODO confirm with Dinis if ok
   
    
    if not ball.owner:
        return []

    # check if ball is in goal area and the owner is correct
    if not (ball.positions[-1].x > field["length"]/4 and not ball.owner.isTeamRight or ball.positions[-1].x < -field["length"]/4 and ball.owner.isTeamRight):
        return []
    # ball velocity increases in direction of goal

    if not ball.is_in_goal_direction(not ball.owner.isTeamRight, field, goal):
        # If ball stop moving after a goal_shot
        if "goal_shot" in events:
            events["goal_shot"].end = timestamp
            events.pop("goal_shot")
        return []

    if "goal_shot" not in events:
        message = Dribble(event="goal_shot", id=ball.owner.id, start=timestamp, end=timestamp)
        events["goal_shot"] = message
    return []

def detect_defense(ball : Ball, teamA : list, teamB : list, timestamp : float):
    if not "goal_shot" in events:
        return []
    oponent_team = teamA if ball.owner.isTeamRight else teamB
        
    for player in oponent_team:
        if ball.get_distance_from(player) < CONTACT_DISTANCE:
            m1 = Dribble("defense", player.id, start=timestamp, end=timestamp)
            m2 = events["goal_shot"]
            m2.end = timestamp
            events.pop("goal_shot", None)
            ball.owner = player
            return [m1, m2]
    return []

def detect_aggressions(teamA : list, teamB : list, ball : Ball, distance_margin=AGGRESSION_DISTANCE_MARGIN):
    """Given teams, returns a list of Aggressions."""
    
    # {
        # aggressions: {
            # id1_id2: [
                # {start: time, end: time, has_been_printed: bool}
            # ]
        # }
    # }
    
    if "aggressions" not in events:
        events["aggressions"] = {}

    aggressions = events.get("aggressions")
    
    for entity1 in teamA:        
        key = ""
        for entity2 in teamB:
            
            isNewTimeStamp = True
            positions1 : list = entity1.get_recent_positions()
            
            for i in range(len(positions1)):
                pos1 : Position = positions1[i]
                
                positions2 : list = entity2.get_recent_positions()
                pos2 : Position = positions2[i]
                                
                distance = pos1.distance_between(pos2)

                id1 = entity1.id
                id2 = entity2.id
                key = f"{id1}_{id2}"

                if distance < distance_margin and (ball.get_distance_from(entity1) < AGGRESSION_DISTANCE_TO_BALL \
                or ball.get_distance_from(entity2) < AGGRESSION_DISTANCE_TO_BALL):
                    
                    aggression_times = aggressions.get(key)

                    if aggression_times is None:
                        aggressions[key] = []
                        
                    # If is the first aggression on key, or the last one has ended, create a new one
                    if len(aggressions[key]) == 0:
                        aggressions[key].append({"start": pos1.timestamp, "end": -1, "has_been_printed": False})
                        
                    else:
                        past = aggressions[key][-1]
                        if past["end"] != -1 and past["end"] < pos1.timestamp:
                            aggressions[key].append({"start": pos1.timestamp, "end": -1, "has_been_printed": False})
                    
                    # Remove useless aggressions from events array
                    # TODO test this more
                    if i == 0: 
                        # if it's the oldest on memory, and already surpass oldest aggression
                        # then aggression should be removed
                        oldest_aggression = aggressions[key][0]
                        
                        if oldest_aggression["end"] != -1 and oldest_aggression["end"] < pos1.timestamp:
                            aggressions[key].pop(0)                            
                    
                    isNewTimeStamp = False
            
                elif not isNewTimeStamp: # end time range condition
                    isNewTimeStamp = True    
                    aggressions.get(key)[-1]["end"] = pos1.timestamp

    aggressions_list = []
    
    # For each aggression on events, print output if hasn't been printed yet
    for k, v in aggressions.items():
        for aggression in v:
            
            # If aggression had finished (!= -1) and hasn't been printed yet, then create message
            if aggression["end"] != -1 and not aggression["has_been_printed"]:
                ids = k.split("_")
                aggression["has_been_printed"] = True
                aggressions_list += [Aggresion(ids[0], ids[1], aggression["start"], aggression["end"])]

    return aggressions_list


def detect_pass_or_dribble(ball : Ball, players : list, timestamp : float):
    """Given the entities checks if a pass or dribble is hapening"""
    
    if "goal" in events:
        if "dribble/pass" in events:
            events.pop("dribble/pass")
        return []
        
    # If Ball isn't moving then there isn't a pass/dribble or it finished
        
    if math.floor(ball.get_current_velocity() * 100) / 100.0 == 0:
        if "dribble/pass" in events:
            m = events["dribble/pass"]
            message = Dribble("dribble", m["from"], m["start"], timestamp)
            # message.end = timestamp
            # message.event = "dribble"
            # message.id = ball.owner.id
            events.pop("dribble/pass")
            return [message]

        return []
    
    for player in players:        
        # If player touch the ball
        if ball.get_distance_from(player) < CONTACT_DISTANCE:
            
            # The dribble/pass was initialized
            if "dribble/pass" not in events:
                events["dribble/pass"] = {"pos": ball.positions[-1], "from": player, "start": timestamp}
                #Pass(ball.positions[-1],  "dribble/pass", player.id, timestamp, timestamp)
                ball.owner = player
                return []

            # If the player belongs to the same team, then pass
            if player.isTeamRight == ball.owner.isTeamRight and player.id != ball.owner.id:
                m = events["dribble/pass"]
                message = Pass(m["pos"], "pass", m["from"], player, m["start"], timestamp)

                message.final_pos = ball.positions[-1]

                message.check_type()
                events.pop("dribble/pass")
                return [message]
            # If the player is an opponent then intersect
            elif player.isTeamRight != ball.owner.isTeamRight:

                # if the closest player to the ball of the same team is the owner then dribble
                event = "dribble"
                for p in players:
                    if p.isTeamRight == ball.owner.isTeamRight and ball.get_distance_from(p) < ball.get_distance_from(ball.owner):
                        event = "pass"
                        break
                
                m = events["dribble/pass"]
                if event == "dribble":
                    m1 = Dribble("dribble", m["from"], m["start"], timestamp)
                else:
                    m1 = Pass(m["pos"], "pass", m["from"], player, m["start"], timestamp)
                    m1.final_pos = ball.positions[-1]
                    m1.check_type()

                events.pop("dribble/pass")

                m2 = Message("intersect", timestamp, timestamp)
                ball.owner = player

                return [m1, m2]
    
    return []
