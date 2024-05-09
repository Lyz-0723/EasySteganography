import cv2
import gui
import sys
import numpy as np

if __name__ == "__main__":
    # Main function quit when app closed
    app = gui.QApplication(sys.argv)
    window = gui.Window()
    sys.exit(app.exec_())
