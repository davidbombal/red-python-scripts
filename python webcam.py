import cv2

# id of the video capturing device to open. To open default camera using default backend just pass 0.
capture = cv2.VideoCapture(0)

# Check if the camera is opened successfully
if not capture.isOpened():
    print("Error: Unable to access the camera.")
    exit()

while True:
    _, frame = capture.read()
    #  We give the Window a name of "Capture from Webcam", and we also give it the frame which is an numpy object.
    cv2.imshow("Capture from Webcam", frame)
    # We know that the ASCII code for the Escape key is 27.
    if cv2.waitKey(1) == 27:
        break

# Release the capture and destroy all OpenCV Windows.
capture.release()
cv2.destroyAllWindows()
