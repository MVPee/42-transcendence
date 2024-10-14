const canvas = document.getElementById('pong');
const ctx = canvas.getContext('2d');

const paddleWidth = 10;
const paddleHeight = 100;
const ballSize = 10;
const goalPadding = 40;

let player1PaddleY = (canvas.height - paddleHeight) / 2;
let aiPaddleY = (canvas.height - paddleHeight) / 2;
let ballX = canvas.width / 2;
let ballY = canvas.height / 2;
let ballSpeedX = 3;
let ballSpeedY = 3;

let score1 = 0;
let score2 = 0;
let isGameRunning = false;
let isGamePaused = false;

let lastAIMoveTime = 0;
const aiCalculInterval = 1000;
let futureBallY = ballY;

const iaPaddleSpeed = 1;
const paddleSpeed = 5;

const speedIncreaseInterval = 1000;
const speedIncreaseAmount = 0.1;

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
    ctx.fillRect(canvas.width - paddleWidth - goalPadding, aiPaddleY, paddleWidth, paddleHeight);
    ctx.fillRect(ballX, ballY, ballSize, ballSize);
}

function resetBall() {
    ballX = canvas.width / 2;
    ballY = canvas.height / 2;
    ballSpeedX = 3 * (Math.random() > 0.5 ? 1 : -1);
    ballSpeedY = 3;
}

let lastSpeedIncreaseTime = Date.now();

function calculateBallFutureY() {
    let futureBallX = ballX;
    let futureBallY = ballY;
    let futureBallSpeedX = ballSpeedX;
    let futureBallSpeedY = ballSpeedY;

    while (futureBallX < canvas.width - goalPadding - paddleWidth) {
        futureBallX += futureBallSpeedX;
        futureBallY += futureBallSpeedY;

        if (futureBallY <= 0 || futureBallY >= canvas.height - ballSize)
            futureBallSpeedY = -futureBallSpeedY;
        if (Math.abs(futureBallSpeedX) < 0.1 || futureBallX < 0)
            break;
    }

    return futureBallY;
}

function update() {
    if (!isGameRunning || isGamePaused) return;

    const now = Date.now();

    if (now - lastSpeedIncreaseTime > speedIncreaseInterval) {
        ballSpeedX += ballSpeedX > 0 ? speedIncreaseAmount : -speedIncreaseAmount;
        ballSpeedY += ballSpeedY > 0 ? speedIncreaseAmount : -speedIncreaseAmount;
        lastSpeedIncreaseTime = now;
    }

    ballX += ballSpeedX;
    ballY += ballSpeedY;

    if (keys['w'])
        player1PaddleY -= paddleSpeed;
    if (keys['s'])
        player1PaddleY += paddleSpeed;

    player1PaddleY = Math.max(0, Math.min(canvas.height - paddleHeight, player1PaddleY));

    if (now - lastAIMoveTime > aiCalculInterval) {
        futureBallY = calculateBallFutureY();
        lastAIMoveTime = now;
    }

    let distance = futureBallY - (aiPaddleY + paddleHeight / 2);
    if (Math.abs(distance) > iaPaddleSpeed)
        aiPaddleY += (distance > 0 ? iaPaddleSpeed : -iaPaddleSpeed);

    aiPaddleY = Math.max(0, Math.min(canvas.height - paddleHeight, aiPaddleY));

    if (ballY <= 0 || ballY >= canvas.height - ballSize)
        ballSpeedY = -ballSpeedY;

    if (ballX <= goalPadding + paddleWidth && 
        ballY + ballSize >= player1PaddleY && 
        ballY <= player1PaddleY + paddleHeight) {
        ballSpeedX = -ballSpeedX;
        ballX = goalPadding + paddleWidth;
    }
    else if (ballX >= canvas.width - paddleWidth - goalPadding - ballSize && 
        ballY + ballSize >= aiPaddleY && 
        ballY <= aiPaddleY + paddleHeight) {
        ballSpeedX = -ballSpeedX;
        ballX = canvas.width - paddleWidth - goalPadding - ballSize;
    }

    if (ballX < 5) {
        score1++;
        resetBall();
    } 
    else if (ballX > canvas.width - 5) {
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
    draw();
    gameLoop();
});

document.getElementById('pauseButton').addEventListener('click', () => {
    isGamePaused = !isGamePaused;
    document.getElementById('pauseButton').innerText = isGamePaused ? 'Resume Game' : 'Pause Game';
});

draw();
