-- main.lua
-- Simple Pong game (LOVE2D) with score tracking
math.randomseed(os.time())

local function randomColor()
  return { r = math.random(), g = math.random(), b = math.random() }
end

local function colorDistance(a, b)
  local dr = a.r - b.r
  local dg = a.g - b.g
  local db = a.b - b.b
  return math.sqrt(dr*dr + dg*dg + db*db)
end

local function randomDistinctColor(exclude, minDist)
  minDist = minDist or 0.35
  local c
  repeat
    c = randomColor()
  until colorDistance(c, exclude) >= minDist
  return c
end

function love.load()
  love.window.setTitle("Pong - Score")
  WINDOW_W, WINDOW_H = 800, 600
  love.window.setMode(WINDOW_W, WINDOW_H, {resizable=false})

  font = love.graphics.newFont(36)
  smallFont = love.graphics.newFont(18)
  love.graphics.setFont(font)

  -- paddles
  paddle = {
    w = 10,
    h = 80,
    speed = 300
  }

  leftP = { x = 30, y = (WINDOW_H - paddle.h) / 2 }
  rightP = { x = WINDOW_W - 30 - paddle.w, y = (WINDOW_H - paddle.h) / 2 }

  -- ball
  ball = {
    x = WINDOW_W / 2,
    y = WINDOW_H / 2,
    size = 10,
    speed = 300,
    dx = 1, -- direction x (normalized)
    dy = 0  -- direction y (normalized)
  }

  -- speed increment on each paddle hit
  PADDLE_HIT_SPEED_INC = 20

  -- colors: ensure ball and background are never the same (sufficiently different)
  bgColor = randomColor()
  ballColor = randomDistinctColor(bgColor, 0.35)

  local function changeColors()
    bgColor = randomColor()
    ballColor = randomDistinctColor(bgColor, 0.35)
  end
  -- expose to other scopes
  changeColorsFunc = changeColors

  -- scores
  score = { left = 0, right = 0 }

  -- game state: "start", "serve", "play", "done"
  state = "start"
  servingPlayer = "left"
end

local function resetBall(serving)
  ball.x = WINDOW_W / 2
  ball.y = WINDOW_H / 2
  ball.speed = 300
  -- serve toward the non-serving player (so if left is serving, ball goes right)
  if serving == "left" then
    ball.dx = 1
  else
    ball.dx = -1
  end
  -- small random vertical angle
  ball.dy = (math.random() * 2 - 1) * 0.5
  -- normalize speed vector
  local len = math.sqrt(ball.dx * ball.dx + ball.dy * ball.dy)
  ball.dx, ball.dy = ball.dx / len, ball.dy / len
end

local function clamp(y)
  if y < 0 then return 0 end
  if y + paddle.h > WINDOW_H then return WINDOW_H - paddle.h end
  return y
end

function love.update(dt)
  if state == "play" then
    -- left paddle controls: W/S
    if love.keyboard.isDown("w") then
      leftP.y = leftP.y - paddle.speed * dt
    elseif love.keyboard.isDown("s") then
      leftP.y = leftP.y + paddle.speed * dt
    end
    -- right paddle controls: up/down
    if love.keyboard.isDown("up") then
      rightP.y = rightP.y - paddle.speed * dt
    elseif love.keyboard.isDown("down") then
      rightP.y = rightP.y + paddle.speed * dt
    end

    leftP.y = clamp(leftP.y)
    rightP.y = clamp(rightP.y)

    -- move ball
    ball.x = ball.x + ball.dx * ball.speed * dt
    ball.y = ball.y + ball.dy * ball.speed * dt

    -- top/bottom collision
    if ball.y <= 0 then
      ball.y = 0
      ball.dy = -ball.dy
      changeColorsFunc()
    elseif ball.y + ball.size >= WINDOW_H then
      ball.y = WINDOW_H - ball.size
      ball.dy = -ball.dy
      changeColorsFunc()
    end

    -- paddle collisions
    local function intersects(aX, aY, aW, aH, bX, bY, bW, bH)
      return aX < bX + bW and bX < aX + aW and aY < bY + bH and bY < aY + aH
    end

    -- left paddle
    if intersects(ball.x, ball.y, ball.size, ball.size, leftP.x, leftP.y, paddle.w, paddle.h) then
      ball.x = leftP.x + paddle.w
      ball.dx = -ball.dx
      -- tweak angle based on where it hit the paddle
      local relative = (ball.y + ball.size/2) - (leftP.y + paddle.h/2)
      ball.dy = relative / (paddle.h/2)
      -- normalize
      local len = math.sqrt(ball.dx * ball.dx + ball.dy * ball.dy)
      ball.dx, ball.dy = ball.dx / len, ball.dy / len
      ball.speed = ball.speed + PADDLE_HIT_SPEED_INC -- speed up on paddle hit
      changeColorsFunc()
    end

    -- right paddle
    if intersects(ball.x, ball.y, ball.size, ball.size, rightP.x, rightP.y, paddle.w, paddle.h) then
      ball.x = rightP.x - ball.size
      ball.dx = -ball.dx
      local relative = (ball.y + ball.size/2) - (rightP.y + paddle.h/2)
      ball.dy = relative / (paddle.h/2)
      local len = math.sqrt(ball.dx * ball.dx + ball.dy * ball.dy)
      ball.dx, ball.dy = ball.dx / len, ball.dy / len
      ball.speed = ball.speed + PADDLE_HIT_SPEED_INC -- speed up on paddle hit
      changeColorsFunc()
    end

    -- scoring: ball past left or right edge
    if ball.x + ball.size < 0 then
      score.right = score.right + 1
      servingPlayer = "left"
      state = "serve"
      resetBall(servingPlayer)
    elseif ball.x > WINDOW_W then
      score.left = score.left + 1
      servingPlayer = "right"
      state = "serve"
      resetBall(servingPlayer)
    end
  elseif state == "serve" then
    -- allow paddle movement while waiting
    if love.keyboard.isDown("w") then leftP.y = clamp(leftP.y - paddle.speed * dt) end
    if love.keyboard.isDown("s") then leftP.y = clamp(leftP.y + paddle.speed * dt) end
    if love.keyboard.isDown("up") then rightP.y = clamp(rightP.y - paddle.speed * dt) end
    if love.keyboard.isDown("down") then rightP.y = clamp(rightP.y + paddle.speed * dt) end
  elseif state == "start" then
    -- allow minimal paddle movement on start screen
    if love.keyboard.isDown("w") then leftP.y = clamp(leftP.y - paddle.speed * dt) end
    if love.keyboard.isDown("s") then leftP.y = clamp(leftP.y + paddle.speed * dt) end
  end
end

function love.draw()
  love.graphics.clear(bgColor.r, bgColor.g, bgColor.b)
  love.graphics.setColor(1, 1, 1)

  -- center dashed line
  for y = 0, WINDOW_H, 20 do
    love.graphics.rectangle("fill", WINDOW_W/2 - 1, y, 2, 10)
  end

  -- paddles
  love.graphics.rectangle("fill", leftP.x, leftP.y, paddle.w, paddle.h)
  love.graphics.rectangle("fill", rightP.x, rightP.y, paddle.w, paddle.h)

  -- ball (colored)
  love.graphics.setColor(ballColor.r, ballColor.g, ballColor.b)
  love.graphics.rectangle("fill", ball.x, ball.y, ball.size, ball.size)

  -- scores (white)
  love.graphics.setColor(1, 1, 1)
  love.graphics.setFont(font)
  love.graphics.print(tostring(score.left), WINDOW_W * 0.25, 20)
  love.graphics.print(tostring(score.right), WINDOW_W * 0.75, 20)

  love.graphics.setFont(smallFont)
  if state == "start" then
    love.graphics.printf("Press Enter to Begin", 0, WINDOW_H - 40, WINDOW_W, "center")
    love.graphics.printf("W/S = Left, Up/Down = Right", 0, WINDOW_H - 20, WINDOW_W, "center")
  elseif state == "serve" then
    love.graphics.printf("Serve: " .. servingPlayer, 0, WINDOW_H - 40, WINDOW_W, "center")
    love.graphics.printf("Press Enter to Serve", 0, WINDOW_H - 20, WINDOW_W, "center")
  end
end

function love.keypressed(key)
  if key == "escape" then
    love.event.quit()
  elseif key == "return" or key == "enter" then
    if state == "start" then
      state = "serve"
      resetBall(servingPlayer)
    elseif state == "serve" then
      state = "play"
    end
  elseif key == "r" then
    -- reset scores and positions
    score.left, score.right = 0, 0
    leftP.y = (WINDOW_H - paddle.h) / 2
    rightP.y = (WINDOW_H - paddle.h) / 2
    state = "start"
    ball.x, ball.y = WINDOW_W/2, WINDOW_H/2
    ball.dx, ball.dy = 1, 0
    ball.speed = 300
    bgColor = randomColor()
    ballColor = randomDistinctColor(bgColor, 0.35)
  end
end
