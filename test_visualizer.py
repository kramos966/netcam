from src import CameraViewer

def main():
    w, h = 1280, 1024
    vis = CameraViewer(w, h, fullscreen=True)
    vis.mainloop()

if __name__ == "__main__":
    main()
