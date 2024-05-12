import gui
import sys


if __name__ == "__main__":
    # Main function quit when app closed
    app = gui.QApplication(sys.argv)
    window = gui.Window()
    sys.exit(app.exec_())
