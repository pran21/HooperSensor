import math
import cv2

class Detection:

    def __init__(self, box, type, score, imageHeight, imageWidth):
        self.y1 = int(max(1, box[0]*imageHeight))
        self.x1 = int(max(1, box[1]*imageWidth))
        self.y2 = int(min(imageHeight, box[2]*imageHeight))
        self.x2 = int(min(imageWidth, box[3]*imageWidth))

        self.classNum = int(type)
        self.score = score

    def getClassName(self, labels):
        return labels[self.classNum]

    def getCenter(self):
        x = (self.x1 + self.x2) / 2
        y = (self.y1 + self.y2) / 2
        return (x, y)

    def getDistance(self, otherDetection):
        (x1, y1) = self.getCenter()
        (x2, y2) = otherDetection.getCenter()
        sq1 = (x1 - x2) * (x1 - x2)
        sq2 = (y1 - y2) * (y1 - y2)
        return math.sqrt(sq1 + sq2)

    def draw(self, frame, labels):
        cv2.rectangle(frame, (self.x1, self.y1), (self.x2, self.y2), (0, 255, 0), 2)
        self.drawLabel(frame, labels)

    def drawLabel(self, frame, labels):
        label = '%s: %d%%' % (self.getClassName(labels), int(self.score * 100)) # Example: 'person: 72%'
        labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
        label_ymin = max(self.y1, labelSize[1] + 10) # Make sure not to draw label too close to top of window
        cv2.rectangle(frame, (self.x1, label_ymin-labelSize[1]-10), (self.x1+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
        cv2.putText(frame, label, (self.x1, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text


def main():
    box = [0.1, 0.1, 0.5, 0.5]
    box2 = [0.1, 0.1, 0.8, 0.8]
    type = 0
    score = 0.7
    d1 = Detection(box, type, score, 720, 1280)
    d2 = Detection(box2, type, score, 720, 1280)
    print(d1.getDistance(d2))

if __name__=="__main__":
    main()
