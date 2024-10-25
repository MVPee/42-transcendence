// static/game/pong.js

const canvas = document.getElementById('pong');
const ctx = canvas.getContext('2d');

const paddleWidth = 10;
const paddleHeight = 100;
const ballSize = 10;
const goalPadding = 50;

let player1PaddleY = (canvas.height - paddleHeight) / 2;
let player2PaddleY = (canvas.height - paddleHeight) / 2;
let ballX = canvas.width / 2;
let ballY = canvas.height / 2;
let ballSpeedX = 3;
let ballSpeedY = 3;
let ballRadius = 10;

let score1 = 0;
let score2 = 0;
let isGameRunning = false;
let isGamePaused = false;

const keys = {};

document.addEventListener('keydown', (event) => {
    keys[event.key] = true;
    if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
        event.preventDefault();
    }
});

document.addEventListener('keyup', (event) => {
    keys[event.key] = false;
});

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = 'white';
    ctx.fillRect(goalPadding, player1PaddleY, paddleWidth, paddleHeight);
    ctx.fillRect(canvas.width - paddleWidth - goalPadding, player2PaddleY, paddleWidth, paddleHeight);
    ctx.fillRect(ballX, ballY, ballSize, ballSize);
}

function resetBall() {
    ballX = canvas.width / 2;
    ballY = canvas.height / 2;
    ballSpeedX = 3 * (Math.random() > 0.5 ? 1 : -1);
    ballSpeedY = 3;
}

function update() {
    if (!isGameRunning || isGamePaused) return;

    ballX += ballSpeedX;
    ballY += ballSpeedY;

    if (keys['w'])
        player1PaddleY -= 5;
    if (keys['s'])
        player1PaddleY += 5;
    if (keys['ArrowUp'])
        player2PaddleY -= 5;
    if (keys['ArrowDown'])
        player2PaddleY += 5;

    player1PaddleY = Math.max(0, Math.min(canvas.height - paddleHeight, player1PaddleY));
    player2PaddleY = Math.max(0, Math.min(canvas.height - paddleHeight, player2PaddleY));

    if (ballY <= 0 || ballY >= canvas.height - ballSize)
        ballSpeedY = -ballSpeedY;

    if (ballSpeedX < 0 && ballX <= goalPadding + paddleWidth) {
        if (ballY + ballSize >= player1PaddleY && ballY <= player1PaddleY + paddleHeight) {
            ballSpeedX = -ballSpeedX;

            let deltaY = ballY - (player1PaddleY + paddleHeight / 2);
            ballSpeedY = deltaY * 0.1; 

            ballX = goalPadding + paddleWidth;
        }
    }

    else if (ballSpeedX > 0 && ballX >= canvas.width - paddleWidth - goalPadding - ballSize) {
        if (ballY + ballSize >= player2PaddleY && ballY <= player2PaddleY + paddleHeight) {
            ballSpeedX = -ballSpeedX;

            let deltaY = ballY - (player2PaddleY + paddleHeight / 2);
            ballSpeedY = deltaY * 0.1;

            ballX = canvas.width - paddleWidth - goalPadding - ballSize;
        }
    }
    
    if (ballX - ballRadius <= -ballRadius) {
        score1++;
        resetBall();
    } 
    else if (ballX + ballRadius >= canvas.width) {
        score2++;
        resetBall();
    }

    document.getElementById('score1').innerText = score2;
    document.getElementById('score2').innerText = score1;
}

function displayMessage(message) {
    const messageElement = document.getElementById('message');
    messageElement.innerText = message;
    messageElement.style.display = 'block';
    document.getElementById('replayButton').style.display = 'inline-block';
    document.getElementById('pauseButton').style.display = 'none';
}

function gameLoop() {
    if (isGameFinished) return;

    if (score1 >= 5) {
        displayMessage('AI wins!');
        isGameFinished = true;
        return;
    }
    else if (score2 >= 5) {
        displayMessage('Player 1 Wins!');
        isGameFinished = true;
        return;
    }
    draw();
    update();
    requestAnimationFrame(gameLoop);
}

document.getElementById('replayButton').addEventListener('click', () => {
    location.reload();
});

document.getElementById('startButton').addEventListener('click', () => {
    isGameRunning = true;
    isGameFinished = false;
    document.getElementById('startButton').style.display = 'none';
    document.getElementById('pauseButton').style.display = 'inline-block';
    resetBall();
    gameLoop();
});

document.getElementById('pauseButton').addEventListener('click', () => {
    isGamePaused = !isGamePaused;
    document.getElementById('pauseButton').innerText = isGamePaused ? 'Resume Game' : 'Pause Game';
});

draw();
