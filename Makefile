all:	up

up:
		sudo mkdir -p backend/database/data
		docker-compose up --build -d

down:
		docker-compose down

stop:
		docker-compose stop

clean:	down
		docker container prune --force

fclean:	clean
		docker system prune --all --force
		sudo rm -rf backend/database/data

re:			fclean all

.PHONY:		all volume up down clean fclean re