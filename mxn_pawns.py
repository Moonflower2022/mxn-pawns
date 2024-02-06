import math
import random
import time
import os
import pygame


def change_board_size(rows, columns):
    global rowNum
    global colNum
    global squareNum
    global squareSize
    global board

    rowNum = rows
    colNum = columns
    squareNum = math.lcm(colNum, rowNum)/colNum if colNum < rowNum else math.lcm(
        colNum, rowNum)/rowNum if rowNum is not colNum else colNum
    squareSize = 600/squareNum
    board = []

    for i in range(rowNum):
        board.insert(i, [])
        if i == 0:
            for o in range(colNum):
                board[0].insert(o, False)
        elif i == rowNum - 1:
            for o in range(colNum):
                board[rowNum - 1].insert(o, True)
        else:
            for o in range(colNum):
                board[i].insert(o, None)


def in_board(x, y):
    if 0 <= x <= colNum-1 and 0 <= y <= rowNum-1:
        return True
    return False


def move(fromPos, toPos, undoList):
    global turn
    undoList[0] = board[toPos['y']][toPos['x']]
    board[toPos['y']][toPos['x']] = board[fromPos['y']][fromPos['x']]
    board[fromPos['y']][fromPos['x']] = None
    turn = not turn


def undo_move(fromPos, toPos, undoList):
    global turn
    board[fromPos['y']][fromPos['x']] = board[toPos['y']][toPos['x']]
    board[toPos['y']][toPos['x']] = undoList[0]
    turn = not turn


def bot_move(move):
    board_move({'x': move['fromX'], 'y': move['fromY']},
               {'x': move['toX'], 'y': move['toY']})


def board_move(fromPos, toPos):
    global turn
    global lastMove
    global userMoved
    move(fromPos, toPos, [None])
    lastMove = {'from': fromPos, 'to': toPos}
    userMoved = True


def generate_movement(x, y, colorBool):
    movementArr = []
    if colorBool == True:
        if in_board(x, y - 1) and board[y-1][x] == None:
            movementArr.append(
                {'fromX': x, 'fromY': y, 'toX': x, 'toY': y - 1})
        for i in range(0, 3, 2):
            if in_board(x+1-i, y - 1) and board[y-1][x+1-i] == False:
                movementArr.append(
                    {'fromX': x, 'fromY': y, 'toX': x+1-i, 'toY': y - 1})
    else:
        if in_board(x, y + 1) and board[y+1][x] == None:
            movementArr.append(
                {'fromX': x, 'fromY': y, 'toX': x, 'toY': y + 1})
        for i in range(0, 3, 2):
            if in_board(x+1-i, y + 1) and board[y+1][x+1-i] == True:
                movementArr.append(
                    {'fromX': x, 'fromY': y, 'toX': x+1-i, 'toY': y + 1})
    return movementArr

# 0 index of returned list is if game is over or not, and 1 index is result


def check_win():
    for i in range(colNum):
        # if board[0][i] == True and board[2][i] == False:
        # print("ERRORRRRRRRRRR")
        if board[0][i] == True:
            return [True, True]
        if board[-1][i] == False:
            return [True, False]
    if len(update_movement()[0]) == 0 and turn:
        return [True, False]
    if len(update_movement()[1]) == 0 and not turn:
        return [True, True]
    return [False, None]


def score_pos():
    if check_win()[0]:
        if check_win()[1]:
            return 1
        elif not check_win()[1]:
            return -1
    return 0


def update_movement():
    # index 0 is white, 1 is black
    movement = [[], []]
    for y in range(rowNum):
        for x in range(colNum):
            if board[y][x] != None:
                pieceMovement = generate_movement(x, y, board[y][x])
                if len(pieceMovement) > 0:
                    if board[y][x]:
                        for obj in pieceMovement:
                            movement[0].append(obj)
                    else:
                        for obj in pieceMovement:
                            movement[1].append(obj)
    return movement


def is_clickable_move(piece, piecePos, clickPos):
    for moveObj in generate_movement(piecePos['x'], piecePos['y'], piece):
        if {'x': moveObj['toX'], 'y': moveObj['toY']} == clickPos:
            return True
    return False


def bots_make_moves():
    time.sleep(botSpeedSeconds)
    if gameOn:
        if whiteBotOn and turn and len(update_movement()[0]) != 0:
            bot_move(minimax(botDepth, -math.inf, math.inf, True))
        if blackBotOn and not turn and len(update_movement()[1]) != 0:
            bot_move(minimax(botDepth, -math.inf, math.inf, False))


def initializeBoard(boardArr, colNum, rowNum):
    for i in range(rowNum):
        boardArr.insert(i, [])
        if i == 0:
            for o in range(colNum):
                boardArr[0].insert(o, False)
        elif i == rowNum - 1:
            for o in range(colNum):
                boardArr[rowNum - 1].insert(o, True)
        else:
            for o in range(colNum):
                boardArr[i].insert(o, None)


def minimaxTesting(depth, alpha, beta, isMaximizingPlayer):
    # Base case: evaluate board
    if depth == 0:
        return score_pos()

    # Recursive case: search possible moves
    bestMove = None
    possibleMoves = update_movement()[0 if isMaximizingPlayer else 1]
    # Set random order for possible moves
    random.shuffle(possibleMoves)
    # Set a default best move value
    bestMoveValue = -math.inf if isMaximizingPlayer else math.inf
    # Search through all possible moves
    for moveObj in possibleMoves:
        boardTakenPiece = [None]
        # Make the move, but undo before exiting loop
        move({'x': moveObj['fromX'], 'y': moveObj['fromY']}, {
             'x': moveObj['toX'], 'y': moveObj['toY']}, boardTakenPiece)
        # Recursively get the value from this move
        if check_win()[0]:
            value = score_pos()
        else:
            value = minimaxTesting(depth-1, alpha, beta,
                                   False if isMaximizingPlayer else True)

        # Log the value of this move
        # print('Max: ' if isMaximizingPlayer else 'Min: ', depth, move, value, bestMove, bestMoveValue)

        if isMaximizingPlayer:
            # Look for moves that maximize position
            if value > bestMoveValue:
                bestMoveValue = value
                bestMove = moveObj
            alpha = max(alpha, value)
        else:
            # Look for moves that minimize position
            if value < bestMoveValue:
                bestMoveValue = value
                bestMove = moveObj
            beta = min(beta, value)
        # Undo previous move
        undo_move({'x': moveObj['fromX'], 'y': moveObj['fromY']}, {
                  'x': moveObj['toX'], 'y': moveObj['toY']}, boardTakenPiece)
        # Check for alpha beta pruning
        if beta <= alpha:
            # print('Prune', alpha, beta)
            break
    return bestMoveValue


def minimax(depth, alpha, beta, isMaximizingPlayer):
    # Base case: evaluate board
    if depth == 0:
        return score_pos()

    # Recursive case: search possible moves
    bestMove = None
    possibleMoves = update_movement()[0 if isMaximizingPlayer else 1]
    # Set random order for possible moves
    random.shuffle(possibleMoves)
    # Set a default best move value
    bestMoveValue = -math.inf if isMaximizingPlayer else math.inf
    # Search through all possible moves
    for moveObj in possibleMoves:
        boardTakenPiece = [None]
        # Make the move, but undo before exiting loop
        move({'x': moveObj['fromX'], 'y': moveObj['fromY']}, {
             'x': moveObj['toX'], 'y': moveObj['toY']}, boardTakenPiece)
        # Recursively get the value from this move
        if check_win()[0]:
            value = score_pos()
        else:
            value = minimax(depth-1, alpha, beta,
                            False if isMaximizingPlayer else True)

        # Log the value of this move
        # print('Max: ' if isMaximizingPlayer else 'Min: ', depth, move, value, bestMove, bestMoveValue)

        if isMaximizingPlayer:
            # Look for moves that maximize position
            if value > bestMoveValue:
                bestMoveValue = value
                bestMove = moveObj
            alpha = max(alpha, value)
        else:
            # Look for moves that minimize position
            if value < bestMoveValue:
                bestMoveValue = value
                bestMove = moveObj
            beta = min(beta, value)
        # Undo previous move
        undo_move({'x': moveObj['fromX'], 'y': moveObj['fromY']}, {
                  'x': moveObj['toX'], 'y': moveObj['toY']}, boardTakenPiece)
        # Check for alpha beta pruning
        if beta <= alpha:
            # print('Prune', alpha, beta)
            break
    return bestMove if depth == botDepth else bestMoveValue

# white is the player that always plays first
# 1 is winning for white parity -1 is winning for black
# [1, -1, -1, 1, 1, -1, 1, 1, -1] is array of parities for a board of 3 rows and 1 - 9 columns
# [-1, -1, -1, 1, -1] is array of parities for a board of 4 rows and 1 - 5 columns


selectedPiece = None
selectedPieceCoords = None
lastMove = None
turn = True
colNum = 5
rowNum = 4
# squareNum = math.lcm(colNum, rowNum)/colNum if colNum < rowNum else math.lcm(colNum, rowNum)/rowNum if rowNum is not colNum else colNum
squareNum = max(colNum, rowNum)
squareSize = 600/squareNum
board = []
gameOn = True
whiteBotOn = False
blackBotOn = True
botDepth = 10
botSpeedSeconds = 0
userMoved = False

captureColor = pygame.Color(231, 89, 58)
moveColor = pygame.Color(124, 197, 76)
checkColor = pygame.Color(221, 70, 70)
hoverColor = pygame.Color(92, 172, 241)
selectColor = pygame.Color(45, 136, 192)
lightTileColor = pygame.Color(240, 218, 181)
darkTileColor = pygame.Color(181, 137, 98)
lastMoveFromColor = pygame.Color(172, 163, 72)
lastMoveToColor = pygame.Color(207, 210, 123)

black_pawn_image = pygame.transform.scale(pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Chess_pdt60.png")), (squareSize, squareSize))

white_pawn_image = pygame.transform.scale(pygame.image.load(os.path.join(os.path.dirname(os.path.abspath(__file__)), "Chess_plt60.png")), (squareSize, squareSize))


# pygame setup
pygame.init()
screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()
running = True
dt = 0

# setup to for finding parity in positions

# resultArr = []

# for i in range(9):
#  board = []
#  rowNum = 3
#  colNum = i + 1
#  initializeBoard(board, i + 1, 3)
#  resultArr.append(minimaxTesting (40, -math.inf, math.inf, True))

# print(resultArr)

# colNum = 5
# rowNum = 3
# board = []

initializeBoard(board, colNum, rowNum)


def draw_movement(piece, piecePos):
    for moveObj in generate_movement(piecePos['x'], piecePos['y'], piece):
        if board[moveObj['toY']][moveObj['toX']] == None:
            pygame.draw.circle(screen, moveColor, ((
                moveObj['toX'] + 1/2)*squareSize, (moveObj['toY'] + 1/2) * squareSize), squareSize/6)
        else:
            pygame.draw.circle(screen, captureColor, ((
                moveObj['toX'] + 1/2)*squareSize, (moveObj['toY'] + 1/2) * squareSize), squareSize/6)


def block_text(winnerBool):
    if winnerBool:
        print("---------------------------- WHITE WINSS --------------------------")
    else:
        print("---------------------------- Black WINSS --------------------------")


while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            clickCoords = {
                'x': int(pygame.mouse.get_pos()[0]/(600/squareNum)),
                'y': int(pygame.mouse.get_pos()[1]/(600/squareNum))
            }
            if clickCoords != None and board[clickCoords['y']][clickCoords['x']] != None and in_board(clickCoords['x'], clickCoords['y']) and turn == board[clickCoords['y']][clickCoords['x']] and gameOn:
                if selectedPieceCoords != None and selectedPieceCoords == clickCoords:
                    selectedPieceCoords = None
                    selectedPiece = None
                else:
                    selectedPieceCoords = {
                        'x': clickCoords['x'], 'y': clickCoords['y']}
                    selectedPiece = board[selectedPieceCoords['y']
                                          ][selectedPieceCoords['x']]

            if selectedPiece != None and selectedPieceCoords != None and is_clickable_move(selectedPiece, selectedPieceCoords, clickCoords):
                board_move(selectedPieceCoords, clickCoords)

                selectedPiece = None
                selectedPieceCoords = None

    screen.fill("purple")
    for y in range(rowNum):
        for x in range(colNum):
            if (x + y) % 2 == 1:
                pygame.draw.rect(screen, lightTileColor, pygame.Rect(int(
                    600/squareNum*x), int(600/squareNum*y), int(600/squareNum), int(600/squareNum)))
            else:
                pygame.draw.rect(screen, darkTileColor, pygame.Rect(int(
                    600/squareNum*x), int(600/squareNum*y), int(600/squareNum), int(600/squareNum)))
            if lastMove and lastMove['from'] == {'x': x, 'y': y}:
                pygame.draw.rect(screen, lastMoveFromColor, pygame.Rect(int(
                    600/squareNum*x), int(600/squareNum*y), int(600/squareNum), int(600/squareNum)))
            elif lastMove and lastMove['to'] == {'x': x, 'y': y}:
                pygame.draw.rect(screen, lastMoveToColor, pygame.Rect(int(
                    600/squareNum*x), int(600/squareNum*y), int(600/squareNum), int(600/squareNum)))
            if int(pygame.mouse.get_pos()[0]/(600/squareNum)) == x and int(pygame.mouse.get_pos()[1]/(600/squareNum)) == y:
                pygame.draw.rect(screen, hoverColor, pygame.Rect(int(
                    600/squareNum*x), int(600/squareNum*y), int(600/squareNum), int(600/squareNum)))
            if selectedPieceCoords and selectedPieceCoords == {'x': x, 'y': y}:
                pygame.draw.rect(screen, selectColor, pygame.Rect(int(
                    600/squareNum*x), int(600/squareNum*y), int(600/squareNum), int(600/squareNum)))

            if board[y][x] == True:
                screen.blit(white_pawn_image, (squareSize*x-2, squareSize*y))
            elif board[y][x] == False:
                screen.blit(black_pawn_image, (squareSize*x-2, squareSize*y))
    if selectedPiece != None and selectedPieceCoords != None:
        draw_movement(selectedPiece, selectedPieceCoords)
    if check_win()[0] and gameOn:
        block_text(check_win()[1])
        gameOn = False
    if userMoved and gameOn:
        bots_make_moves()
        userMoved = False
    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    dt = clock.tick(120) / 1000

pygame.quit()
