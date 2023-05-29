import cv2
import face_recognition

img = cv2.imread('photos/mouheb.png')
rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
img_encodings = face_recognition.face_encodings(rgb_img)[0]

img2 = cv2.imread('photos/mbappe.png')
rgb_img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2RGB)
img2_encodings = face_recognition.face_encodings(rgb_img2)[0]

img3 = cv2.imread('photos/messi2.png')
rgb_img3 = cv2.cvtColor(img3, cv2.COLOR_BGR2RGB)
img3_encodings = face_recognition.face_encodings(rgb_img3)[0]

img4 = cv2.imread('photos/messi3.png')
rgb_img4 = cv2.cvtColor(img4, cv2.COLOR_BGR2RGB)
img4_encodings = face_recognition.face_encodings(rgb_img4)[0]

result = face_recognition.compare_faces([img_encodings, img2_encodings, img4_encodings], img3_encodings)
print("Result: ", result)
cv2.imshow('Messi', img)
cv2.imshow('Messi2', img2)
cv2.waitKey(0)