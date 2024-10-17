all:	up

up:
		docker-compose up --build -d

down:
		docker-compose down

stop:
		docker-compose stop

clean:	down
		docker container prune --force

fclean:	clean
		docker system prune --all --force
		sudo rm -rf data
		# sudo rm -f backend/app/srcs/chat/migrations/000*.py
		# sudo rm -f backend/app/srcs/game/migrations/000*.py
		# sudo rm -f backend/app/srcs/home/migrations/000*.py
		# sudo rm -f backend/app/srcs/tournaments/migrations/000*.py
		# sudo rm -f backend/app/srcs/user/migrations/000*.py

re:	clean up

.PHONY:		all up down clean fclean re