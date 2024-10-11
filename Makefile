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

re:			fclean all

.PHONY:		all volume up down clean fclean re