from channels.generic.websocket import AsyncWebsocketConsumer
from django.core.cache import cache
import json, asyncio, ssl, aiohttp, os

class Puissance4Consumer(AsyncWebsocketConsumer):

    YELLOW = 1
    RED = 2

    DOMAIN = os.getenv('DOMAIN', 'localhost')
    API_KEY = os.getenv('API_KEY', None)

    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['id']
        self.room_group_name = f'game_{self.game_id}_puissance4'
        self.user = self.scope['user']

        disconnect_key = f"player_disconnected_{self.game_id}"
        was_disconnected = cache.get(disconnect_key) == self.user.username

        if not cache.get(f"game_{self.game_id}_puissance4_state"):
            cache.set(f"game_{self.game_id}_puissance4_state", {
                'table': [[None for _ in range(6)] for _ in range(7)],
                'turn': 'yellow',
                'pause': False,
                'finish': False
            })
    
        cache.delete(disconnect_key)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        if was_disconnected:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_info",
                    "message": f"Player {self.user.username} has reconnected."
                }
            )

            # Resume the game
            game_state = cache.get(f"game_{self.game_id}_puissance4_state")
            if game_state:
                game_state['paused'] = False

                #? Send game board to the disconnected player
                for column in range(7):
                    for row in range(6):
                        color = None
                        if game_state['table'][column][row] == self.YELLOW: color = 'yellow'
                        elif game_state['table'][column][row] == self.RED: color = 'red'
                        if color is not None:
                            await self.channel_layer.group_send(
                                self.room_group_name,
                                {
                                    "type": "send_color",
                                    "column": column ,
                                    "row": row,
                                    "color": color,
                                }
                            )

                cache.set(f"game_{self.game_id}_puissance4_state", game_state)
        
        url = f"https://{self.DOMAIN}/api/game/1v1/{self.game_id}/"

        connector = aiohttp.TCPConnector(ssl=self.ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url) as response:
                if response.status == 200: self.match = await response.json()
                else:
                    await self.close()
                    return
        
        self.player1 = self.match['user1']
        self.player2 = self.match['user2']
        
        user1_score = self.match['user1_score']
        user2_score = self.match['user2_score']

        if self.user.id != self.player1['id'] and self.user.id != self.player2['id']:
            await self.close()
            return

        if user1_score >= 1 or user2_score >= 1:
            await self.close()
            return

        await self.accept()

    async def disconnect(self, close_code):
        if self.user.id != self.player1['id'] and self.user.id != self.player2['id']:
            return

        points_awarded_key = f"points_awarded_{self.game_id}"
        points_awarded = cache.get(points_awarded_key)

        if not points_awarded and hasattr(self, 'match'):
            disconnect_key = f"player_disconnected_{self.game_id}"
            cache.set(disconnect_key, self.user.username, timeout=20)

            # Set the game to paused
            game_state = cache.get(f"game_{self.game_id}_puissance4_state")
            if game_state:
                game_state['paused'] = True
                cache.set(f"game_{self.game_id}_puissance4_state", game_state)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_info",
                    "message": f"Player {self.user.username} has disconnected. He have 15 seconds to reconnect."
                }
            )

            asyncio.create_task(self.wait_for_reconnection(disconnect_key, points_awarded_key))

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def wait_for_reconnection(self, disconnect_key, points_awarded_key):
        await asyncio.sleep(15)

        #? Protection if the match is finish
        if await self.check_win() == 0:
            if cache.get(disconnect_key) == self.user.username:
                if self.player1['id'] == self.user.id:
                    await self.set_points_to(2, 1)
                    await self.set_win_to(2)
                elif self.player2['id'] == self.user.id:
                    await self.set_points_to(1, 1)
                    await self.set_win_to(1)

                cache.set(points_awarded_key, True, timeout=None)

                await self.channel_layer.group_send(
                    self.room_group_name,
                        {
                            "type": "redirect_remaining_player",
                        }
                )

    async def receive(self, text_data):
        if text_data.isnumeric() and int(text_data) >= 0 and int(text_data) <= 7:
            column = int(text_data)
            game_state = cache.get(f"game_{self.game_id}_puissance4_state")
            if game_state['turn'] == 'yellow' and self.user.id == self.player1['id'] and game_state['table'][column][0] is None:
                for row in range(5, -1, -1):
                    if game_state['table'][column][row] is None:
                        game_state['table'][column][row] = self.YELLOW
                        game_state['turn'] = 'red'
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                "type": "send_color",
                                "column": column ,
                                "row": row,
                                "color": 'yellow',
                            }
                        )
                        break

            elif game_state['turn'] == 'red' and self.user.id == self.player2['id'] and game_state['table'][column][0] is None:
                for row in range(5, -1, -1):
                    if game_state['table'][column][row] is None:
                        game_state['table'][column][row] = self.RED
                        game_state['turn'] = 'yellow'
                        await self.channel_layer.group_send(
                            self.room_group_name,
                            {
                                "type": "send_color",
                                "column": column ,
                                "row": row,
                                "color": 'red',
                            }
                        )
                        break

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "send_turn",
                    "message": f"{game_state['turn']} turn."
                }
            )

            cache.set(f"game_{self.game_id}_puissance4_state", game_state)
            winner = await self.check_puissance4()
            if winner != 0:
                await self.set_points_to(winner, 1)
                await self.set_win_to(winner)
                await self.channel_layer.group_send(
                    self.room_group_name,
                        {
                            "type": "redirect_remaining_player",
                        }
                )
                

    def check_victory(self, table, column, row, player_color):
        directions = [
            (1, 0),  # Horizontal
            (0, 1),  # Vertical
            (1, 1),  # Diagonal /
            (1, -1), # Diagonal \
        ]

        for dx, dy in directions:
            count = 1
            x, y = column, row
            while True:
                x += dx
                y += dy
                if 0 <= x < 7 and 0 <= y < 6 and table[x][y] == player_color: count += 1
                else: break

            x, y = column, row
            while True:
                x -= dx
                y -= dy
                if 0 <= x < 7 and 0 <= y < 6 and table[x][y] == player_color: count += 1
                else: break

            if count >= 4: return True
        return False

    async def check_puissance4(self):
        """
        Check the current state of the game to determine if there's a winner or a draw.

        Returns:
            int: 0 if no one has won, 1 if Yellow wins, 2 if Red wins.
        """
        game_state_key = f"game_{self.game_id}_puissance4_state"
        game_state = cache.get(game_state_key)
        table = game_state.get('table')

        for column in range(7):
            for row in range(6):
                player_color = table[column][row]
                if player_color is not None:
                    if self.check_victory(table, column, row, player_color):
                        return player_color

        #? Check for a draw
        if all(table[col][0] is not None for col in range(7)):
            print('draw detected')
            for column in range(7):
                for row in range(6):
                    table[column][row] = 0
            for column in range(7):
                for row in range(6):
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "send_color",
                            "column": column,
                            "row": row,
                            "color": 'gray',
                        }
                    )
            cache.set(f"game_{self.game_id}_puissance4_state", {
                'table': [[None for _ in range(6)] for _ in range(7)],
                'turn': 'yellow'
            })

        return 0

    async def send_color(self, event):
        await self.send(text_data=json.dumps({
            "type": "color",
            "column": event["column"],
            "row": event["row"],
            "color": event["color"]
        }))

    async def send_info(self, event):
        await self.send(text_data=json.dumps({
            "type": "info",
            "info": event["message"]
        }))

    async def send_turn(self, event):
        await self.send(text_data=json.dumps({
            "type": "turn",
            "turn": event["message"]
        }))

    async def set_points_to(self, player, points):
            game_state = cache.get(f"game_{self.game_id}_puissance4_state")
            if game_state['finish'] == True:
                return

            if player == 1: id = self.player1['id']
            elif player == 2: id = self.player2['id']

            url = f"https://{self.DOMAIN}/api/game/1v1/score/set/"

            data = {
                "id": self.game_id,
                "player_id": id,
                "score": points
            }

            connector = aiohttp.TCPConnector(ssl=self.ssl_context)
            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(url, json=data, headers={"X-API-KEY": self.API_KEY}) as response:
                    if response.status == 200: self.match = await response.json()

    async def check_win(self):
        game_state = cache.get(f"game_{self.game_id}_puissance4_state")
        if game_state['finish'] == True:
            return

        if self.match['user1_score'] >= 1:
            return 1
        elif self.match['user2_score'] >= 1:
            return 2
        return 0

    async def set_win_to(self, player):
        game_state = cache.get(f"game_{self.game_id}_puissance4_state")
        if game_state['finish'] == False:
            game_state['finish'] = True
        else:
            return
        cache.set(f"game_{self.game_id}_puissance4_state", game_state)

        if player == 1:
            win_id = self.player1['id']
            lose_id = self.player2['id']
        elif player == 2:
            win_id = self.player2['id']
            lose_id = self.player1['id']

        url_add = f"https://{self.DOMAIN}/api/users/{win_id}/elo/add/50/"
        url_rm = f"https://{self.DOMAIN}/api/users/{lose_id}/elo/remove/25/"
        
        connector = aiohttp.TCPConnector(ssl=self.ssl_context)
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(url_add, headers={"X-API-KEY": self.API_KEY}) as response:
                if response.status == 200:
                    self.match = await response.json()

            async with session.get(url_rm, headers={"X-API-KEY": self.API_KEY}) as response:
                if response.status == 200:
                    self.match = await response.json()

    async def redirect_remaining_player(self, event):
        await self.send(text_data=json.dumps({
            "type": "redirect"
        }))