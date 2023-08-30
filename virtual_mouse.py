import cv2
import mediapipe as mp
from pynput.mouse import Button, Controller
import math
import pyautogui
mouse = Controller()

cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(min_detection_confidence=0.8, min_tracking_confidence=0.5)

tipIds = [4, 8, 12, 16, 20]
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
pinch = False
(screen_width, screen_height)= pyautogui.size()


# Define a function to count fingers
def countFingers(image, hand_landmarks, handNo=0):

    if hand_landmarks:
        # Get all Landmarks of the FIRST Hand VISIBLE
        landmarks = hand_landmarks[handNo].landmark

        # Count Fingers        
        fingers = []

        for lm_index in tipIds:
                # Get Finger Tip and Bottom y Position Value
                finger_tip_y = landmarks[lm_index].y 
                finger_bottom_y = landmarks[lm_index - 2].y

                # Check if ANY FINGER is OPEN or CLOSED
                if lm_index !=4:
                    if finger_tip_y < finger_bottom_y:
                        fingers.append(1)
                        # print("FINGER with id ",lm_index," is Open")

                    if finger_tip_y > finger_bottom_y:
                        fingers.append(0)
                        # print("FINGER with id ",lm_index," is Closed")

        totalFingers = fingers.count(1)
        global pinch

        finger_tip_x = int((landmarks[8].x)*width)
        finger_tip_y = int((landmarks[8].y)*height)
        thumb_tip_x = int((landmarks[4].x)*width)
        thumb_tip_y = int((landmarks[4].y)*height)

        cv2.line(image, (finger_tip_x,finger_tip_y), (thumb_tip_x,thumb_tip_y), (0,255,0), 2)
        centre_x = int((finger_tip_x + thumb_tip_x)/ 2)
        centre_y = int((finger_tip_y + thumb_tip_y)/ 2)

        cv2.circle(image, (centre_x,centre_y), 2, (255,0,0), 2)

        distance = math.sqrt(((finger_tip_x - thumb_tip_x)**2) + ((finger_tip_y - thumb_tip_y)**2))
        print(distance)
        relative_mouse_x = (centre_x/width) * screen_width
        relative_mouse_y = (centre_y/height) * screen_height
        
        mouse.position = (relative_mouse_x,relative_mouse_y)

        if(distance > 40):
            if(pinch == True):
                pinch = False
                mouse.release(Button.left)
        if(distance <= 40):
            if(pinch == False):
                pinch = True
                mouse.release(Button.left)

# Define a function to 
def drawHandLanmarks(image, hand_landmarks):

    # Darw connections between landmark points
    if hand_landmarks:

      for landmarks in hand_landmarks:
               
        mp_drawing.draw_landmarks(image, landmarks, mp_hands.HAND_CONNECTIONS)



while True:
    success, image = cap.read()

    image = cv2.flip(image, 1)
    
    # Detect the Hands Landmarks 
    results = hands.process(image)

    # Get landmark position from the processed result
    hand_landmarks = results.multi_hand_landmarks

    # Draw Landmarks
    drawHandLanmarks(image, hand_landmarks)

    # Get Hand Fingers Position        
    countFingers(image, hand_landmarks)

    cv2.imshow("Media Controller", image)

    # Quit the window on pressing Sapcebar key
    key = cv2.waitKey(1)
    if key == 27:
        break

cv2.destroyAllWindows()
