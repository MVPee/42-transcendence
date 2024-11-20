import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.core.cache import cache
import json
from ..models import Tournament
from django.contrib.auth import get_user_model
import random

User = get_user_model()

class GameTournamentConsumer(AsyncWebsocketConsumer):
    ACCELERATION_FACTOR = 1.05

    PADDLE_SPEED = 8

    BALL_SPEED = 6

    HEIGHT = 400
    WIDTH = 600

    DISTANCE_BETWEEN_WALL_PADDLE = 30

    BALL_X = 295
    BALL_Y = 195

    BALL_HEIGHT = 5
    BALL_WIDTH = 5

    PADDLE_HEIGHT = 80
    PADDLE_WIDTH = 10

    PADDLE_MAX_HEIGHT = 400 - PADDLE_HEIGHT
    PADDLE_MIN_HEIGHT = 0

    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['id']
        self.user = self.scope['user']
        self.room_group_name = f"game_{self.game_id}_tournament"

        disconnect_key = f"player_disconnected_{self.game_id}_{self.user}"
        was_disconnected = cache.get(disconnect_key) == self.user.username
        self.player1_score = 0
        self.player2_score = 0

        try:
            self.tournament = await sync_to_async(Tournament.objects.get)(id=self.game_id)
        
            self.player1 = await sync_to_async(lambda: self.tournament.user1 if self.tournament.user1 else "Player1")()
            self.player2 = await sync_to_async(lambda: self.tournament.user2 if self.tournament.user2 else "Player2")()
            self.player3 = await sync_to_async(lambda: self.tournament.user3 if self.tournament.user3 else "Player3")()
            self.player4 = await sync_to_async(lambda: self.tournament.user4 if self.tournament.user4 else "Player4")()
            

        except Tournament.DoesNotExist:
            await self.close()

        if not cache.get(f"game_{self.game_id}_tournament_state"):
            cache.add(f"game_{self.game_id}_tournament_state", {
            'player1PaddleY': self.HEIGHT / 2 - self.PADDLE_HEIGHT / 2,
            'player2PaddleY': self.HEIGHT / 2 - self.PADDLE_HEIGHT / 2,
            'ball_x': self.BALL_X,
            'ball_y': self.BALL_Y,
            'ball_dx': self.BALL_SPEED if random.choice([True, False]) else -self.BALL_SPEED,
            'ball_dy': self.BALL_SPEED if random.choice([True, False]) else -self.BALL_SPEED,
            'player1': None,
            'player2': None,
            'player1_score': 0,
            'player2_score': 0,
            'fourth': None,
            'third': None,
            'second': None,
            'first': None,
        })

        cache.delete(disconnect_key)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        if was_disconnected and self.is_playing():
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_info",
                    "message": f"Player {self.user.username} has reconnected."
                }
            )

            # Resume the game
            game_state = cache.get(f"game_{self.game_id}_tournament_state")
            if game_state:
                game_state['paused'] = False
                cache.set(f"game_{self.game_id}_tournament_state", game_state)

        await self.accept()

        game_process_key = f"game_{self.game_id}_process_started"
        if not cache.get(game_process_key):
            cache.set(game_process_key, True)
            asyncio.create_task(self.tournamentProcess())

    async def countdown(self):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "send_countdown",
                "message": "First at 5 win the game"
            }
        )
        await asyncio.sleep(1)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "send_countdown",
                "message": "Party start in 3"
            }
        )
        await asyncio.sleep(1)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "send_countdown",
                "message": "Party start in 2"
            }
        )
        await asyncio.sleep(1)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "send_countdown",
                "message": "Party start in 1"
            }
        )
        await asyncio.sleep(1)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "send_countdown",
                "message": "GO"
            }
        )
        await asyncio.sleep(0.4)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "send_countdown",
                "message": ""
            }
        )

    async def gameProcess(self):
        await self.countdown()
        while True:
            game_state = cache.get(f"game_{self.game_id}_tournament_state")
            if not game_state:
                break

            if game_state.get('paused'):
                await asyncio.sleep(0.1)
                continue

            ball_x = game_state['ball_x']
            ball_y = game_state['ball_y']
            ball_dx = game_state['ball_dx']
            ball_dy = game_state['ball_dy']

            # Update ball position
            ball_x += ball_dx
            ball_y += ball_dy

            # Handle collision with top and bottom walls
            if ball_y <= 0 or ball_y >= self.HEIGHT - self.BALL_HEIGHT:
                ball_dy *= -1

            # Get paddle positions
            paddle1_x = 30  # Fixed x-position for paddle1 from CSS
            paddle2_x = self.WIDTH - 30 - self.PADDLE_WIDTH  # Fixed x-position for paddle2 from CSS
            paddle1_y = game_state['player1PaddleY']
            paddle2_y = game_state['player2PaddleY']


            #! Handle collision with paddles
            if ball_dx < 0:
                # Ball moving left towards Player 1's paddle
                if ball_x <= paddle1_x + self.PADDLE_WIDTH:
                    # Collision detected with Player 1's paddle
                    if paddle1_y <= ball_y + self.BALL_HEIGHT and ball_y <= paddle1_y + self.PADDLE_HEIGHT and ball_x >= self.DISTANCE_BETWEEN_WALL_PADDLE - 10:
                        ball_dx = -ball_dx * self.ACCELERATION_FACTOR
                        ball_dy *= self.ACCELERATION_FACTOR
            elif ball_dx > 0:
                # Ball moving right towards Player 2's paddle
                if ball_x + self.BALL_WIDTH >= paddle2_x:
                    # Collision detected with Player 2's paddle
                    if paddle2_y <= ball_y + self.BALL_HEIGHT and ball_y <= paddle2_y + self.PADDLE_HEIGHT and ball_x <= self.WIDTH - self.DISTANCE_BETWEEN_WALL_PADDLE + 10:
                        ball_dx = -ball_dx * self.ACCELERATION_FACTOR
                        ball_dy *= self.ACCELERATION_FACTOR

            #! Handle goal
            if ball_x <= 0:
                self.add_point_to(1)

                await self.send_score_update()

                winner = self.check_win()
                if winner:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "redirect_remaining_player",
                        }
                    )
                    break
                ball_x = self.BALL_X
                ball_y = self.BALL_Y

                ball_dx = -self.BALL_SPEED
                ball_dy = self.BALL_SPEED if random.choice([True, False]) else -self.BALL_SPEED

            elif ball_x + self.BALL_WIDTH >= self.WIDTH:
                self.add_point_to(2)

                await self.send_score_update()

                winner = self.check_win()
                if winner:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "redirect_remaining_player",
                        }
                    )
                    break
                ball_x = self.BALL_X
                ball_y = self.BALL_Y

                ball_dx = self.BALL_SPEED
                ball_dy = self.BALL_SPEED if random.choice([True, False]) else -self.BALL_SPEED

            # Update game state
            game_state['ball_x'] = ball_x
            game_state['ball_y'] = ball_y
            game_state['ball_dx'] = ball_dx
            game_state['ball_dy'] = ball_dy

            cache.set(f"game_{self.game_id}_tournament_state", game_state)
            # Send updated ball position to clients
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'update_ball_position',
                    'ball_x': ball_x,
                    'ball_y': ball_y,
                }
            )

            await asyncio.sleep(0.02)
        cache.set(f"game_{self.game_id}_tournament_state", game_state)

    async def update_ball_position(self, event):
        await self.send(text_data=json.dumps({
            'type': 'update_ball_position',
            'ball_x': event['ball_x'],
            'ball_y': event['ball_y'],
        }))

    async def receive(self, text_data):
        data = json.loads(text_data)

        if data["type"] == "movement" and data["direction"] in ('up', 'down') and self.is_playing():
            direction = data["direction"]
            game_state = cache.get(f"game_{self.game_id}_tournament_state")
            now = asyncio.get_event_loop().time()
            last_move_time = game_state.get(f'last_move_time_{self.user.username}', 0)
            time_since_last_move = now - last_move_time

            min_time_between_moves = 0.01  # 20 ms like in js

            if time_since_last_move >= min_time_between_moves:
                move_distance = self.PADDLE_SPEED

                if game_state['player1'] == self.user:
                    game_state['player1PaddleY'] += move_distance if direction == "down" else -move_distance
                    game_state['player1PaddleY'] = max(self.PADDLE_MIN_HEIGHT, min(self.PADDLE_MAX_HEIGHT, game_state['player1PaddleY']))
                elif game_state['player2'] == self.user:
                    game_state['player2PaddleY'] += move_distance if direction == "down" else -move_distance
                    game_state['player2PaddleY'] = max(self.PADDLE_MIN_HEIGHT, min(self.PADDLE_MAX_HEIGHT, game_state['player2PaddleY']))

                game_state[f'last_move_time_{self.user.username}'] = now

                cache.set(f"game_{self.game_id}_tournament_state", game_state)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "player_movement",
                        "player": self.user.username,
                        "direction": direction,
                        "player1PaddleY": game_state['player1PaddleY'],
                        "player2PaddleY": game_state['player2PaddleY'],
                    }
                )
            else:
                pass

    async def player_movement(self, event):
        # Send the movement data to client
        await self.send(text_data=json.dumps({
            "type": "player_movement",
            "player": event["player"],
            "direction": event["direction"],
            "player1PaddleY": event["player1PaddleY"],
            "player2PaddleY": event["player2PaddleY"],
        }))

    async def disconnect(self, close_code):
        if hasattr(self, 'tournament'):

            if (await self.is_playing()):
                disconnect_key = f"player_disconnected_{self.game_id}_{self.user}"
                cache.set(disconnect_key, self.user.username, timeout=20)
                # Set the game to paused
                game_state = cache.get(f"game_{self.game_id}_tournament_state")
                if game_state:
                    game_state['paused'] = True
                    cache.set(f"game_{self.game_id}_tournament_state", game_state)

                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "send_info",
                        "message": f"Player {self.user.username} has disconnected. He have 15 seconds to reconnect."
                    }
                )
                asyncio.create_task(self.wait_for_reconnection(disconnect_key, points_awarded_key))
            else:
                disconnect_key = f"player_disconnected_{self.game_id}_{self.user}"
                cache.set(disconnect_key, self.user.username, timeout=None)

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def wait_for_reconnection(self, disconnect_key, points_awarded_key):
        await asyncio.sleep(15)

        #? Protection if the match is finish
        if self.check_win() == 0:
            if cache.get(disconnect_key) == self.user.username:
                if self.tournament.user1 == self.user:
                    self.set_points_to(2, 5)
                elif self.tournament.user2 == self.user:
                    self.set_points_to(1, 5)

                cache.set(points_awarded_key, True, timeout=None)

                await self.channel_layer.group_send(
                    self.room_group_name,
                        {
                            "type": "redirect_remaining_player",
                        }
                )

    def add_point_to(self, player):
        if player == 1:
            self.player1_score += 1
        elif player == 2:
            self.player2_score += 1

    def set_points_to(self, player, points):
        if player == 1: 
            self.player1_score = points
        elif player == 2: 
            self.player2_score = points

    def check_win(self):
        if self.player1_score >= 5:
            return 1
        elif self.player2_score >= 5:
            return 2
        return 0


    async def redirect_remaining_player(self, event):
        await self.send(text_data=json.dumps({
            "type": "info",
            "info": "yescfini",
        }))

    async def send_info(self, event):
        await self.send(text_data=json.dumps({
            "type": "info",
            "info": event["message"]
        }))

    async def send_countdown(self, event):
        await self.send(text_data=json.dumps({
            "type": "countdown",
            "message": event["message"]
        }))

    async def send_score_update(self):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "update_score",
                "player1_score": self.player1_score,
                "player2_score": self.player2_score,
            }
        )

    async def update_score(self, event):
        await self.send(text_data=json.dumps({
            "type": "update_score",
            "player1_score": event["player1_score"],
            "player2_score": event["player2_score"],
        }))

    @sync_to_async
    def is_playing(self):
        game_state = cache.get(f"game_{self.game_id}_tournament_state")
        if game_state and (self.user == game_state['player1'] or self.user == game_state['player2']):
            return True
        return False

    async def reset_game_state(self):
        cache.set(f"game_{self.game_id}_tournament_state", {
        'player1PaddleY': self.HEIGHT / 2 - self.PADDLE_HEIGHT / 2,
        'player2PaddleY': self.HEIGHT / 2 - self.PADDLE_HEIGHT / 2,
        'ball_x': self.BALL_X,
        'ball_y': self.BALL_Y,
        'ball_dx': self.BALL_SPEED if random.choice([True, False]) else -self.BALL_SPEED,
        'ball_dy': self.BALL_SPEED if random.choice([True, False]) else -self.BALL_SPEED,
        'player1': None,
        'player2': None,
        'player1_score': 0,
        'player2_score': 0,
        })
        self.player1_score = 0
        self.player2_score = 0
        await self.send_score_update()

    async def wait_game_players(self, player1, player2):
        game_state = cache.get(f"game_{self.game_id}_tournament_state")    

        player1_disconnect_key = f"player_disconnected_{self.game_id}_{player1}"
        player2_disconnect_key = f"player_disconnected_{self.game_id}_{player2}"
        disconnect_keys = [(player1, player1_disconnect_key), (player2, player2_disconnect_key)]
        #! must send a message to the users not connected
        players_not_connected = [player for player, key in disconnect_keys if cache.get(key) is not None]
        #* send message
        countdown = 30
        for seconds_remaining in range(countdown, 0, -1):
            players_present = [player for player, key in disconnect_keys if cache.get(key) is None]
            players_not_connected = [player for player, key in disconnect_keys if cache.get(key) is not None]
            if (len(players_present) == 2):
                for player, key in disconnect_keys:
                    cache.delete(key)
                return players_present
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_countdown",
                    'message': ("Waiting " + ", ".join(player["username"] for player in players_not_connected) + f" {seconds_remaining}s remaining")
                }
            )
            await asyncio.sleep(1)
        return players_present

    async def play_match(self, player1, player2):
        #check if they disconnected, if yes send a message and wait
        players_present = await self.wait_game_players(player1, player2)
        if (len(players_present) < 2):
            if (len(players_present) == 1):
                if (player1 == players_present[0]): return player1, player2
                else: return player2, player1
            else:
                return (player1, player2)

        #launch game process
        await self.gameProcess()
        game_state = cache.get(f"game_{self.game_id}_tournament_state")
        if (self.check_win() == 2):
            return player2, player1
        return player1, player2

    async def tournamentProcess(self):
        leaderboard = [
            {"player": self.player1, "score": 0},
            {"player": self.player2, "score": 0},
            {"player": self.player3, "score": 0},
            {"player": self.player4, "score": 0}
        ]
        random.shuffle(leaderboard)
        for i in range(2):
            leaderboard = sorted(leaderboard, key=lambda x:x['score']) #sort based on wins
            #decide which players are going to play
            game_state = cache.get(f"game_{self.game_id}_tournament_state")
            game_state['player1'] = leaderboard[0]['player']
            game_state['player2'] = leaderboard[1]['player']
            cache.set(f"game_{self.game_id}_tournament_state", game_state)
            #check who won and update leaderboard
            leaderboard[0]['player'], leaderboard[1]['player'] = await self.play_match(game_state['player1'], game_state['player2'])
            leaderboard[0]['score']+=1
            #reset game state
            await self.reset_game_state()

            #decide which players are going to play
            game_state = cache.get(f"game_{self.game_id}_tournament_state")
            game_state['player1'] = leaderboard[2]['player']
            game_state['player2'] = leaderboard[3]['player']
            cache.set(f"game_{self.game_id}_tournament_state", game_state)
            leaderboard[2]['player'], leaderboard[3]['player'] = await self.play_match(game_state['player1'], game_state['player2'])
            leaderboard[2]['score']+=1
            #reset game state
            await self.reset_game_state()
        # award winners