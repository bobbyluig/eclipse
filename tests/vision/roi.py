import numpy as np
import cv2


def new_roi(frame, c, r, w, h):
    roi = frame[r:r+h, c:c+w]
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_roi, np.array((0, 30, 32), dtype=np.uint8), np.array((180, 255, 255), dtype=np.uint8))
    roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0, 180])
    cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)

    return roi_hist

 
def run_main():
    cap = cv2.VideoCapture('cheetah.mp4')
    cap.set(cv2.CAP_PROP_POS_MSEC, (1*60 + 17.7) * 1000)

    # Read the first frame of the video
    ret, frame = cap.read()
    height, width, channels = frame.shape

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('roi.avi', fourcc, 29.0, (width, height))

    cv2.imwrite('roi.jpg', frame)

    # Set the ROI (Region of Interest). Actually, this is a
    # rectangle of the building that we're tracking
    c,r,w,h = 520,226,401,138
    track_window = (c,r,w,h)

    # Create mask and normalized histogram
    roi = frame[r:r+h, c:c+w]
    hsv_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_roi, np.array((0, 30, 32), dtype=np.uint8), np.array((180, 255, 255), dtype=np.uint8))
    roi_hist = cv2.calcHist([hsv_roi], [0], mask, [180], [0, 180])
    cv2.normalize(roi_hist, roi_hist, 0, 255, cv2.NORM_MINMAX)
    term_crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 100, 1)
    
    for i in range(int(29 * 19.4)):
        ret, frame = cap.read()

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        dst = cv2.calcBackProject([hsv], [0], roi_hist, [0,180], 1)

        ret, track_window = cv2.CamShift(dst, track_window, term_crit)
        x,y,w,h = track_window

        # roi_hist = new_roi(frame, x, y, w, h)
        cx, cy = int(x+w/2), int(y+h/2)
        cv2.circle(frame, (cx, cy), 5, (0, 0, 255), thickness=2)

        cv2.rectangle(frame, (x,y), (x+w,y+h), (0, 255, 0), 2)
        cv2.putText(frame, '(%d, %d)' % (cx, cy), (x + 5, y - 20), cv2.FONT_HERSHEY_SIMPLEX,
            1, (255,255,255), 2, cv2.LINE_AA)
        
        cv2.imshow('Tracked', frame)
        out.write(frame)

        if i == 29 * 10:
            cv2.imwrite('roi_out.jpg', frame)


        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_main()