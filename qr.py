import cv2
detector = cv2.QRCodeDetector()

reval,point,s_qr = detector.detectAndDecode(cv2.imread('qr_fold.png'))
print(reval)